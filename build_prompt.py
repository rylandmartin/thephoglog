from estimate_calories import estimate_calories
def build_prompt(profile, food_list, calorie_target, macro_targets):
    height = profile["height"]
    weight = profile["weight"]
    age = profile["age"]
    sex = profile["sex"]
    activity = profile["activity_level"]
    goal = profile["goal"]
    allergies = profile["allergies"]
    dislikes = profile["dislikes"]

    allergy_str = ", ".join(allergies) if allergies else "none"
    dislike_str = ", ".join(dislikes) if dislikes else "none"

    food_descriptions = []
    for food in food_list:
        line1 = f"- {food['name']} - {food['calories']} calories, {food['protein']}g protein, {food['carbs']}g carbs, {food['fat']}g fat"
        line2 = f"     • Meal: {food['meal']} | Location: {food['location']} | Tags: {', '.join(food['tags'])}"
        food_descriptions.append(line1 + "\n" + line2)
    
    food_string = "\n".join(food_descriptions)
    
    return (
        f"You are a nutrition assistant creating a meal plan for a college student.\n\n"
        f"Student Profile:\n"
        f"- Height: {height} inches\n"
        f"- Weight: {weight} lbs\n"
        f"- Age: {age}\n"
        f"- Sex: {sex}\n"
        f"- Activity level: {activity}\n"
        f"- Goal: {goal}\n"
        f"- Allergies: {allergy_str}\n"
        f"- Dislikes: {dislike_str}\n\n"
        f"Available food today (for use in the meal plan):\n"
        f"{food_string}\n\n"
        f"Use the foods listed above as much as possible to create a meal plan totaling around {calorie_target} calories. "
        f"If no suitable options are available for a given meal or food group, you may substitute with realistic foods "
        f"a college student might have in their dorm or apartment. "
        f"Include 3 meals and 1–2 snacks. Assign foods to logical meal times based on their 'Meal' label. "
        f"Avoid allergens and disliked foods. Prioritize balance in macronutrients and variety where possible."
        f"The target macros for this plan are:\n"
        f"- Protein: {macro_targets['protein']}g\n"
        f"- Carbs: {macro_targets['carbs']}g\n"
        f"- Fat: {macro_targets['fat']}g\n\n"
    )