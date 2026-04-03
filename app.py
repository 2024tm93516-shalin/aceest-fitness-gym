from flask import Flask, request, jsonify
import os
import sqlite3

VERSION = "2.0.0"
DATABASE = os.environ.get("DATABASE", "aceest_gym.db")

application = Flask(__name__)

FITNESS_PLANS = {
    "Fat Loss (FL) - 3 day":  {"multiplier": 22, "info": "3-day full-body fat loss program"},
    "Fat Loss (FL) - 5 day":  {"multiplier": 24, "info": "5-day split for higher volume fat loss"},
    "Muscle Gain (MG) - PPL": {"multiplier": 35, "info": "Push/Pull/Legs hypertrophy split"},
    "Beginner (BG)":          {"multiplier": 26, "info": "3-day beginner full-body routine"},
}

# alias so Flask registers routes on 'app' name expected by werkzeug
app = application


def get_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn


def setup_database():
    conn = get_connection()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, age INTEGER, height REAL, weight REAL,
            program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER
        );
        CREATE TABLE IF NOT EXISTS progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT, week TEXT, adherence INTEGER
        );
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT
        );
        CREATE TABLE IF NOT EXISTS metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL
        );
    """)
    conn.commit()
    conn.close()


@application.route("/")
def health():
    return jsonify({"service": "ACEest Fitness & Gym", "version": VERSION, "status": "running"})


@application.route("/programs", methods=["GET"])
def list_plans():
    return jsonify(FITNESS_PLANS)


@application.route("/clients", methods=["POST"])
def add_client():
    payload = request.get_json()
    name = (payload.get("name") or "").strip()
    plan = payload.get("program", "")
    if not name or plan not in FITNESS_PLANS:
        return jsonify({"error": "name and valid program are required"}), 400
    weight = payload.get("weight")
    daily_calories = int(weight * FITNESS_PLANS[plan]["multiplier"]) if weight else None
    conn = get_connection()
    try:
        conn.execute("""
            INSERT OR REPLACE INTO clients
            (name, age, height, weight, program, calories, target_weight, target_adherence)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (name, payload.get("age"), payload.get("height"), weight,
              plan, daily_calories, payload.get("target_weight"), payload.get("target_adherence")))
        conn.commit()
        return jsonify({"message": f"Client '{name}' saved", "calories": daily_calories}), 201
    except Exception as err:
        return jsonify({"error": str(err)}), 500
    finally:
        conn.close()


@application.route("/clients/<name>", methods=["GET"])
def fetch_client(name):
    conn = get_connection()
    record = conn.execute("SELECT * FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if not record:
        return jsonify({"error": "Client not found"}), 404
    return jsonify(dict(record))


@application.route("/clients/<name>/progress", methods=["POST"])
def log_progress(name):
    payload = request.get_json()
    adherence = payload.get("adherence")
    week = payload.get("week")
    if adherence is None or not week:
        return jsonify({"error": "adherence and week are required"}), 400
    conn = get_connection()
    conn.execute("INSERT INTO progress (client_name, week, adherence) VALUES (?, ?, ?)",
                 (name, week, int(adherence)))
    conn.commit()
    conn.close()
    return jsonify({"message": "Progress logged"}), 201


@application.route("/clients/<name>/bmi", methods=["GET"])
def calculate_bmi(name):
    conn = get_connection()
    record = conn.execute("SELECT weight, height FROM clients WHERE name=?", (name,)).fetchone()
    conn.close()
    if not record or not record["weight"] or not record["height"]:
        return jsonify({"error": "Client not found or missing weight/height"}), 404
    bmi_value = round(record["weight"] / (record["height"] / 100) ** 2, 1)
    categories = [
        (18.5, "Underweight"),
        (25.0, "Normal"),
        (30.0, "Overweight"),
    ]
    bmi_category = "Obese"
    for threshold, label in categories:
        if bmi_value < threshold:
            bmi_category = label
            break
    return jsonify({"bmi": bmi_value, "category": bmi_category})


if __name__ == "__main__":
    setup_database()
    application.run(host="0.0.0.0", port=5000, debug=False)
