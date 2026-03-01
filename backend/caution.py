import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()
client = OpenAI()


def get_safety_caution(step: str) -> dict | None:
    """
    Generate a safety caution and prevention tip for a recipe step if relevant.
    Returns {"caution": str, "tip": str}, or None if the step has no safety concerns.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a kitchen safety expert. Given a recipe step, decide if it poses a physical risk. "
                    "Risks include: sharp tools (knives, graters, peelers), heat (oven, stove, boiling water, hot pans), "
                    "fire, steam, hot oil, or anything that could burn, cut, or injure someone. "
                    "If yes, reply with JSON: {\"caution\": \"<5 words max>\", \"tip\": \"<7 words max>\"}. "
                    "If no risk, reply with only: none"
                )
            },
            {"role": "user", "content": f"Recipe step: {step}"}
        ],
        temperature=0.3,
        response_format={"type": "text"},
    )

    result = response.choices[0].message.content.strip()
    if result.lower() == "none":
        return None

    try:
        cleaned = result.replace("```json", "").replace("```", "").strip()
        return json.loads(cleaned)
    except Exception:
        return {"caution": result, "tip": None}


def get_allergens(step: str) -> list[str] | None:
    """
    Detect common allergens present in a recipe step.
    Returns a list of allergen names, or None if none found.
    Common allergens: gluten, dairy, eggs, nuts, peanuts, soy, fish, shellfish, sesame.
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a food allergen expert. Given a recipe step, identify any of the 9 major allergens present: "
                    "gluten, dairy, eggs, tree nuts, peanuts, soy, fish, shellfish, sesame. "
                    "Reply with a JSON array of allergen names found (e.g. [\"gluten\", \"dairy\"]). "
                    "If none are present, reply with only: none"
                )
            },
            {"role": "user", "content": f"Recipe step: {step}"}
        ],
        temperature=0.3,
        response_format={"type": "text"},
    )

    result = response.choices[0].message.content.strip()
    if result.lower() == "none":
        return None

    try:
        cleaned = result.replace("```json", "").replace("```", "").strip()
        allergens = json.loads(cleaned)
        return allergens if allergens else None
    except Exception:
        return None


def get_recipe_allergens(food: str) -> list[str] | None:
    """
    Scan a whole dish/drink for ALL potentially allergenic ingredients.
    Returns a list of specific allergen names, or None if none found.
    Covers both the 9 major allergens and specific ingredients (e.g. kiwi, avocado, mustard).
    """
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a food allergen expert. Given a dish or drink, identify ALL specific ingredients "
                    "someone might be allergic to. Include major allergens (peanuts, tree nuts, dairy, eggs, "
                    "gluten, soy, fish, shellfish, sesame) AND specific ingredients (e.g. kiwi, strawberry, "
                    "avocado, mustard, celery, mango, cinnamon). Be specific — list individual ingredients, "
                    "not broad categories. Reply with a JSON array of lowercase strings "
                    "(e.g. [\"peanuts\", \"wheat\", \"kiwi\"]). If no allergens, reply with only: none"
                )
            },
            {"role": "user", "content": f"Dish: {food}"}
        ],
        temperature=0.3,
        response_format={"type": "text"},
    )

    result = response.choices[0].message.content.strip()
    if result.lower() == "none":
        return None

    try:
        cleaned = result.replace("```json", "").replace("```", "").strip()
        allergens = json.loads(cleaned)
        return allergens if allergens else None
    except Exception:
        return None


if __name__ == "__main__":
    step = input("Enter a recipe step: ")

    caution = get_safety_caution(step)
    print(f"[safety] {caution}")
    if caution:
        print(f"\n⚠️  {caution['caution']}")
        if caution.get("tip"):
            print(f"💡 {caution['tip']}")

    allergens = get_allergens(step)
    print(f"\n[allergens] {allergens}")
    if allergens:
        print(f"\n🥜 Allergens: {', '.join(allergens)}")
