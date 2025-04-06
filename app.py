from flask import Flask, render_template, request, redirect, url_for, session
import secrets
from users_info import save_user_profile, load_user_profile
import os

def percent(val, total):
    return f"{round((val / total) * 100)}%" if total else "N/A"

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form["username"].strip().lower()
        session["username"] = username
        return redirect(url_for('home'))
    
    return render_template("login.html")

from datetime import datetime
@app.route('/')
def home():
    username = session.get("username")
    if not username:
        return redirect(url_for('login'))

    user_profile = load_user_profile(username)
    if not user_profile:
        return redirect(url_for('profile'))
    calorie_target, macro_targets = estimate_calories(user_profile)
    today = datetime.now().strftime("%Y-%m-%d")
    log = load_daily_log(username, today)

    return render_template('index.html', username=username, log=log)

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    username = session.get("username")
    if not username:
        return redirect(url_for('login'))

    if request.method == 'POST':
        profile = {
            "height": int(request.form["height"]),
            "weight": int(request.form["weight"]),
            "age": int(request.form["age"]),
            "sex": request.form["sex"].lower(),
            "activity_level": request.form["activity_level"].lower(),
            "goal": request.form["goal"].lower(),
            "allergies": [a.strip().lower() for a in request.form["allergies"].split(",") if a.strip()],
            "dislikes": [d.strip().lower() for d in request.form["dislikes"].split(",") if d.strip()],
        }

        save_user_profile(username, profile)
        return redirect(url_for('home'))

    existing = load_user_profile(username) or {}
    return render_template("profile.html", profile=existing)

from build_prompt import build_prompt
from estimate_calories import estimate_calories
from food_loader import load_ku_food_data, filter_food_by_day
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))
model = genai.GenerativeModel(model_name="models/gemini-1.5-pro-latest")

@app.route('/mealplan')
def mealplan():
    username= session.get("username")
    if not username:
        return redirect(url_for('login'))
    profile = load_user_profile(username)

    if not profile:
        return "No profile found. Please set up your profile first."

    calorie_target, macro_targets = estimate_calories(profile)
    food_data = load_ku_food_data()
    available_today = filter_food_by_day(food_data)

    prompt = build_prompt(profile, available_today, calorie_target, macro_targets)
    response = model.generate_content(prompt)

    return render_template("mealplan.html", mealplan=response.text)

from food_logger import create_empty_log, log_food
from users_info import save_daily_log
from datetime import datetime

@app.route('/log', methods=['GET', 'POST'])
def log_page():
    username = session.get("username")
    if not username:
        return redirect(url_for('login'))
    profile = load_user_profile(username)

    if not profile:
        return "No profile found. Please set up your profile first."

    food_data = load_ku_food_data()
    available_today = filter_food_by_day(food_data)

    log = create_empty_log()

    if request.method == 'POST':
        for food in available_today:
            field_name = f"quantity_{food['name'].replace(' ', '_')}"
            qty = request.form.get(field_name, 0)

            try:
                qty = int(qty)
            except ValueError:
                qty = 0
            
            for I in range(qty):
                log_food(food, log)

        calorie_target, macro_targets = estimate_calories(profile)
        log["targets"] = macro_targets | {"calories": calorie_target}
        log["progress"] = {
            "calories": percent(log["calories"], calorie_target),
            "protein": percent(log["protein"], macro_targets["protein"]),
            "carbs": percent(log["carbs"], macro_targets["carbs"]),
            "fat": percent(log["fat"], macro_targets["fat"])
        }
        save_daily_log(username, log)

        return redirect(url_for('summary'))

    return render_template("log.html", foods=available_today)

from users_info import load_daily_log

@app.route('/summary', methods=['GET', 'POST'])
def summary():
    username = session.get("username")
    if not username:
        return redirect(url_for('login'))
    today = datetime.now().strftime("%Y-%m-%d")
    log = load_daily_log(username, today)

    if not log:
        return render_template("summary.html", log=None)

    print("Foods in log:", log["foods"])
    
    if request.method == 'POST':
        to_remove = set(map(int, request.form.getlist("remove_food")))
        log["foods"] = [f for i, f in enumerate(log["foods"]) if i not in to_remove]

        # Reset totals
        log["calories"] = sum(f["calories"] for f in log["foods"])
        log["protein"] = sum(f["protein"] for f in log["foods"])
        log["carbs"] = sum(f["carbs"] for f in log["foods"])
        log["fat"] = sum(f["fat"] for f in log["foods"])

        calorie_target = log["targets"]["calories"]
        macro_targets = {
            "protein": log["targets"]["protein"],
            "carbs": log["targets"]["carbs"],
            "fat": log["targets"]["fat"]
        }

        log["progress"] = {
            "calories": percent(log["calories"], calorie_target),
            "protein": percent(log["protein"], macro_targets["protein"]),
            "carbs": percent(log["carbs"], macro_targets["carbs"]),
            "fat": percent(log["fat"], macro_targets["fat"])
        }

        save_daily_log(username, log)

    return render_template("summary.html", log=log)

@app.route('/viewlog', methods=['GET', 'POST'])
def view_log():
    username = session.get("username")
    if not username:
        return redirect(url_for('login'))

    selected_date = None
    log = None

    if request.method == 'POST':
        selected_date = request.form["log_date"]
        log = load_daily_log(username, selected_date)

    return render_template("viewlog.html", log=log, selected_date=selected_date)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))
if __name__ == '__main__':
    app.run(debug=True)