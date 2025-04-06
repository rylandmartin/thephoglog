import os
import json
from datetime import datetime
from dotenv import load_dotenv
import google.generativeai as genai

# --- Local Imports ---
from users_info import get_user_profile, save_daily_log, view_log_by_date, edit_profile, save_user_profile
from build_prompt import build_prompt
from food_loader import load_ku_food_data, filter_food_by_day
from estimate_calories import estimate_calories
from food_logger import create_empty_log, log_food, print_log_summary

# -----------------------------
# 1. Setup API Key and Model
# -----------------------------
load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

# -----------------------------
# 2. Helper Functions
# -----------------------------

def percent(val, total):
    return f"{round((val / total) * 100)}%" if total else "N/A"

def generate_meal_plan():
    prompt = build_prompt(user_profile, available_today, calorie_target, macro_targets)
    print("\nGemini Prompt Sent:\n")
    print(prompt)
    response = model.generate_content(prompt)
    print("\nMeal Plan:\n")
    print(response.text)

def log_foods():
    print("\nLog your food (type 'done' to finish):")

    while True:
        entry = input("> ").strip().lower()
        if entry == "done":
            break

        matches = [f for f in available_today if f["name"].lower() == entry]
        if matches:
            log_food(matches[0], log)
            print(f"Logged: {matches[0]['name']}")
        else:
            print("That food isn't in the list of available options.")

    # Save with targets + progress
    log["targets"] = macro_targets | {"calories": calorie_target}
    log["progress"] = {
        "calories": percent(log["calories"], calorie_target),
        "protein": percent(log["protein"], macro_targets["protein"]),
        "carbs": percent(log["carbs"], macro_targets["carbs"]),
        "fat": percent(log["fat"], macro_targets["fat"])
    }
    save_daily_log(username, log)
    print("Log saved.")

def menu(username, user_profile, calorie_target, macro_targets, available_today, log):
    while True:
        print("\nMain Menu:")
        print("[1] Generate new meal plan")
        print("[2] Log food eaten")
        print("[3] View today's log summary")
        print("[4] View a previous day's log")
        print("[5] Edit profile")
        print("[6] Exit")

        choice = input("> ").strip()
        if choice == "1":
            generate_meal_plan()
        elif choice == "2":
            log_foods()
        elif choice == "3":
            print_log_summary(log)
            print("\nProgress Toward Daily Goal:")
            print(f"- Calories: {log['calories']} / {calorie_target} kcal ({percent(log['calories'], calorie_target)})")
            print(f"- Protein: {log['protein']}g / {macro_targets['protein']}g ({percent(log['protein'], macro_targets['protein'])})")
            print(f"- Carbs: {log['carbs']}g / {macro_targets['carbs']}g ({percent(log['carbs'], macro_targets['carbs'])})")
            print(f"- Fat: {log['fat']}g / {macro_targets['fat']}g ({percent(log['fat'], macro_targets['fat'])})")
        elif choice == "4":
            view_log_by_date(username)
        elif choice == "5":
            updated = edit_profile(username)
            if updated:
                user_profile = updated
                calorie_target, macro_targets = estimate_calories(user_profile)
                user_profile["calorie_target"] = calorie_target
                user_profile["macro_targets"] = macro_targets
                save_user_profile(username, user_profile)
                print("Recalculated macro goals after update.")
        elif choice == "6":
            print("Exiting...")
            break
        else:
            print("Invalid choice.")

# -----------------------------
# 3. Setup User, Data, and Launch
# -----------------------------
username, user_profile = get_user_profile()
calorie_target, macro_targets = estimate_calories(user_profile)
ku_food = load_ku_food_data()
available_today = filter_food_by_day(ku_food)
log = create_empty_log()

print(f"\nAvailable foods today ({datetime.now().strftime('%A')}):")
for food in available_today:
    print(f"- {food['name']} at {food['location']} ({food['meal']})")

# Launch the menu system
menu(username, user_profile, calorie_target, macro_targets, available_today, log)