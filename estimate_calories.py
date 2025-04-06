def estimate_calories(profile):
    weight = profile["weight"]
    height = profile["height"]
    age = profile["age"]
    sex = profile["sex"]
    activity = profile["activity_level"]
    goal = profile["goal"]

    weight_kg = weight * 0.453592
    height_cm = height * 2.54

    bmr = 10 * weight_kg + 6.25 * height_cm - 5 * age + (5 if sex == "male" else -161)

    activity_multipliers = {
        "sedentary": 1.2,
        "light": 1.375,
        "moderate": 1.55,
        "active": 1.725,
        "very active": 1.9
    }

    tdee = bmr * activity_multipliers.get(activity, 1.55)

    if goal == "bulk":
        calorie_target =  int(tdee + 300)
        protein_per_lb = 1.0
        fat_pct = 0.20
    elif goal == "cut":
        calorie_target = int(tdee - 500)
        protein_per_lb = 1.2
        fat_pct = 0.25
    else: #maintain
        calorie_target =  int(tdee)
        protein_per_lb = 0.8
        fat_pct = 0.25
    
    protein_target = int(weight * protein_per_lb)
    fat_target = int((calorie_target * fat_pct) / 9)
    remaining_cals = calorie_target - (protein_target * 4 + fat_target * 9)
    carb_target = int(remaining_cals / 4)

    return calorie_target, {
        "protein": protein_target,
        "carbs": carb_target,
        "fat": fat_target
    }