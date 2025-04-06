import os
import json
from datetime import datetime

BASE_PATH = "users_info"

def ensure_user_folder(username):
    user_folder = os.path.join(BASE_PATH, username)
    logs_folder = os.path.join(user_folder, "logs")
    os.makedirs(logs_folder, exist_ok=True)
    return user_folder, logs_folder

def load_user_profile(username):
    user_folder, _ = ensure_user_folder(username)
    profile_path = os.path.join(user_folder, "profile.json")

    if os.path.exists(profile_path):
        with open(profile_path, "r") as f:
            return json.load(f)
    else:
        return None

def save_user_profile(username, profile):
    user_folder, _ = ensure_user_folder(username)
    profile_path = os.path.join(user_folder, "profile.json")

    with open(profile_path, "w") as f:
        json.dump(profile, f, indent=2)

def create_user_profile():
    print("\nNo profile found. Let’s create one!\n")

    height = int(input("Enter your height in inches: "))
    weight = int(input("Enter your weight in lbs: "))
    age = int(input("Enter your age: "))
    sex = input("Enter your sex (male/female): ").strip().lower()
    activity_level = input("Activity level (sedentary, light, moderate, active, very active): ").strip().lower()
    goal = input("Goal (bulk, cut, maintain): ").strip().lower()
    allergies = input("List any allergies (comma separated): ").strip().lower().split(",")
    dislikes = input("List any food dislikes (comma separated): ").strip().lower().split(",")

    allergies = [a.strip() for a in allergies if a.strip()]
    dislikes = [d.strip() for d in dislikes if d.strip()]

    return {
        "height": height,
        "weight": weight,
        "age": age,
        "sex": sex,
        "activity_level": activity_level,
        "goal": goal,
        "allergies": allergies,
        "dislikes": dislikes
    }

def get_user_profile():
    username = input("Enter your username: ").strip().lower()
    profile = load_user_profile(username)

    if profile:
        print(f"Welcome back, {username}!\n")
    else:
        profile = create_user_profile()
        save_user_profile(username, profile)
        print(f"\nProfile saved for {username}!\n")

    return username, profile

def save_daily_log(username, log_data):
    _, logs_folder = ensure_user_folder(username)
    today = datetime.now().strftime("%Y-%m-%d")
    log_path = os.path.join(logs_folder, f"{today}.json")

    with open(log_path, "w") as f:
        json.dump(log_data, f, indent=2)

def load_daily_log(username, date_str):
    _, logs_folder = ensure_user_folder(username)
    log_path = os.path.join(logs_folder, f"{date_str}.json")

    if os.path.exists(log_path):
        with open(log_path, "r") as f:
            return json.load(f)
    else:
        return None

def view_log_by_date(username):
    date_str = input("Enter a date to view log (YYYY-MM-DD): ").strip()
    log = load_daily_log(username, date_str)

    if log:
        print(f"\nLog for {date_str}:")
        print(f"- Calories: {log['calories']}")
        print(f"- Protein: {log['protein']}g")
        print(f"- Carbs: {log['carbs']}g")
        print(f"- Fat: {log['fat']}g")
        print(f"- Foods: {', '.join(log['foods'])}")
    else:
        print(f"No log found for date {date_str}.")
    
def edit_profile(username):
    profile = load_user_profile(username)
    if not profile:
        print("No profile found.")
        return
    
    print("\nEdit your profile (press Enter to keep current value):")
    
    def prompt(field, old_value, cast=str):
        new_value = input(f"{field} [{old_value}]: ").strip()
        return cast(new_value) if new_value else old_value
    
    profile["height"] = prompt("Height (inches)", profile["height"], int)
    profile["weight"] = prompt("Weight (lbs)", profile["weight"], int)
    profile["age"] = prompt("Age", profile["age"], int)
    profile["sex"] = prompt("Sex (male/female)", profile["sex"])
    profile["activity_level"] = prompt("Activity level", profile["activity_level"])
    profile["goal"] = prompt("Goal (bulk/cut/maintain)", profile["goal"])
    new_allergies = input(f"Allergies (comma separated) [{', '.join(profile['allergies'])}]: ").strip().lower()
    if new_allergies:
        profile["allergies"] = [a.strip() for a in new_allergies.split(",") if a.strip()]
    
    new_dislikes = input(f"Dislikes (comma separated) [{', '.join(profile['dislikes'])}]: ").strip().lower()
    if new_dislikes:
        profile["dislikes"] = [d.strip() for d in new_dislikes.split(",") if d.strip()]

    save_user_profile(username, profile)
    print("Profile updated.")
    return profile