from openai import OpenAI
from dotenv import load_dotenv
import base64
import cv2

load_dotenv()

client = OpenAI()

# Rolling conversation history — text only (images are not stored to save tokens)
# Each entry is {"role": "user"|"assistant", "content": str}
conversation_history = []
MAX_HISTORY = 20  # max messages kept (= 10 back-and-forth exchanges)


def ai_text_output(prompt):
    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[
            {"role": "user", "content": prompt}
        ]
    )
    print(response.choices[0].message.content)


def transcribe_audio(wav_buffer):
    """
    Transcribe a WAV audio buffer using OpenAI Whisper API.

    Args:
        wav_buffer: BytesIO object containing a valid WAV file.

    Returns:
        str: Transcribed text, or empty string if nothing detected.
    """
    wav_buffer.seek(0)
    transcript = client.audio.transcriptions.create(
        model="whisper-1",
        file=("audio.wav", wav_buffer, "audio/wav"),
    )
    return transcript.text.strip()


def _encode_frame(frame):
    """Encode a cv2 BGR frame to a base64 JPEG string."""
    _, buf = cv2.imencode(".jpg", frame, [cv2.IMWRITE_JPEG_QUALITY, 75])
    return base64.b64encode(buf).decode("utf-8")


def ai_vision_audio_query(text_prompt, frame=None, system_prompt=None, stream=False, remember=True):
    """
    Send transcribed speech + an optional video frame to GPT-4o,
    with rolling conversation history for context.

    Args:
        text_prompt:   Transcribed speech or any text query.
        frame:         Optional numpy BGR array (cv2 frame) to include as image context.
        system_prompt: Optional system message to set model behaviour.
        stream:        If True, yields response text chunks; otherwise returns full string.
        remember:      If True, appends this exchange to conversation history.
                       Set False for passive video-only snapshots so they don't
                       pollute the conversational context.

    Returns:
        str (stream=False) or generator of str chunks (stream=True).
    """
    messages = []

    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})

    # Inject prior conversation (text-only — images not stored to save tokens)
    messages.extend(conversation_history)

    # Build the current user message (with image if available)
    if frame is not None:
        image_b64 = _encode_frame(frame)
        content = [
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/jpeg;base64,{image_b64}",
                    "detail": "low",
                },
            },
            {"type": "text", "text": text_prompt},
        ]
    else:
        content = text_prompt

    messages.append({"role": "user", "content": content})

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        stream=stream,
    )

    if stream:
        def _gen():
            full_response = []
            for chunk in response:
                delta = chunk.choices[0].delta.content
                if delta:
                    full_response.append(delta)
                    yield delta
            if remember:
                _append_history(text_prompt, "".join(full_response))
        return _gen()
    else:
        result = response.choices[0].message.content
        if remember:
            _append_history(text_prompt, result)
        return result


def _append_history(user_text, assistant_text):
    """Append an exchange to conversation_history and trim to MAX_HISTORY."""
    conversation_history.append({"role": "user", "content": user_text})
    conversation_history.append({"role": "assistant", "content": assistant_text})
    if len(conversation_history) > MAX_HISTORY:
        # Drop oldest pair to stay within the window
        del conversation_history[:2]