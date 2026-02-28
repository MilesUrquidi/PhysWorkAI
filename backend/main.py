from chatgpt import generate_task_steps
from camera import get_camo_feed, set_current_step

FOOD = "iced coffee"

SYSTEM_PROMPT = (
    "You are a precise real-time recipe vision assistant. "
    "When checking recipe steps, you analyze a previous frame and a current frame from a live camera feed. "
    "Always return structured JSON with COMPLETED, STATE, and ACTION fields as instructed. "
    "When the user speaks, respond briefly and helpfully. "
    "Be consistent and strict — only mark a step complete when it is clearly visible."
)

if __name__ == "__main__":
    # 1. Generate and print all steps
    print(f"\nGenerating recipe for: {FOOD}...\n")
    steps = generate_task_steps(FOOD)

    print(f"--- {FOOD.title()} Steps ---")
    for i, step in enumerate(steps):
        print(f"  {i + 1}. {step}")
    print("----------------------------\n")

    # 2. Set the first step and start
    set_current_step(steps[0])
    print(f"Starting on step 1: '{steps[0]}'\n")
    get_camo_feed(system_prompt=SYSTEM_PROMPT)
