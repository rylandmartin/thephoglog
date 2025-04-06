import json
from datetime import datetime

def load_ku_food_data(filename="ku_food_data.json"):
    try:
        with open(filename, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        print("Food data file not found.")
        return []

def filter_food_by_day(data, day=None):
    if not day:
        day = datetime.now().strftime("%A")  # e.g. "Monday"

    return [food for food in data if day in food["days"]]
