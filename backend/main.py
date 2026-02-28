from chatgpt import generate_task_steps
from camera import get_camo_feed, set_current_step

FOOD = "iced coffee"

SYSTEM_PROMPT = (
    "You are a friendly cooking assistant guiding the user through a recipe step by step. "
    "Be brief and encouraging."
)

if __name__ == "__main__":
    # 1. Generate steps
    print(f"\nGenerating steps for: {FOOD}\n")
    steps = generate_task_steps(FOOD)

    print("Steps:")
    for i, step in enumerate(steps):
        print(f"  {i + 1}. {step}")

    # 2. Set the first step so the camera knows what to look for
    set_current_step(steps[0])
    print(f"\nWatching for step 1: '{steps[0]}'\n")

    # 3. Start the camera feed
    get_camo_feed(system_prompt=SYSTEM_PROMPT)
