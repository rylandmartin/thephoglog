def create_empty_log():
    return {
        "calories": 0,
        "protein": 0,
        "carbs": 0,
        "fat": 0,
        "foods": []
    }

def log_food(food, log):
    log["calories"] += food["calories"]
    log["protein"] += food["protein"]
    log["carbs"] += food["carbs"]
    log["fat"] += food["fat"]
    log["foods"].append(food)

def print_log_summary(log):
    print("\nToday's Nutrition Summary:")
    print(f"- Calories: {log['calories']} kcal")
    print(f"- Protein: {log['protein']} g")
    print(f"- Carbs: {log['carbs']} g")
    print(f"- Fat: {log['fat']} g")
    print(f"- Foods logged: {', '.join(log['foods']) if log['foods'] else 'None yet'}")