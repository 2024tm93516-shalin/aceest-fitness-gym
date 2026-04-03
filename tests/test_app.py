"""
Unit tests for ACEest Fitness & Gym Flask API.
Headless and CI-safe — no display or external services required.
"""
import json
import os
import sqlite3
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app as app_module
from app import application as flask_app


class _PersistentConn:
    """Prevents sqlite3 connection from being closed between requests
    so the in-memory database survives the full test."""
    def __init__(self, conn):
        self._conn = conn

    def close(self):
        pass

    def __getattr__(self, item):
        return getattr(self._conn, item)


@pytest.fixture
def api():
    flask_app.config["TESTING"] = True

    conn = sqlite3.connect(":memory:")
    conn.row_factory = sqlite3.Row
    conn.executescript("""
        CREATE TABLE clients (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE, age INTEGER, height REAL, weight REAL,
            program TEXT, calories INTEGER, target_weight REAL, target_adherence INTEGER
        );
        CREATE TABLE progress (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT, week TEXT, adherence INTEGER
        );
        CREATE TABLE workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT, date TEXT, workout_type TEXT, duration_min INTEGER, notes TEXT
        );
        CREATE TABLE metrics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            client_name TEXT, date TEXT, weight REAL, waist REAL, bodyfat REAL
        );
    """)
    conn.commit()

    app_module.get_connection = lambda: _PersistentConn(conn)

    with flask_app.test_client() as c:
        yield c

    conn.close()


def test_health_check(api):
    res = api.get("/")
    assert res.status_code == 200
    body = json.loads(res.data)
    assert body["status"] == "running"
    assert "version" in body


def test_list_programs(api):
    res = api.get("/programs")
    assert res.status_code == 200
    body = json.loads(res.data)
    assert "Fat Loss (FL) - 3 day" in body
    assert "Beginner (BG)" in body


def test_add_client_success(api):
    res = api.post("/clients", json={
        "name": "Charlie", "age": 28, "height": 180.0,
        "weight": 85.0, "program": "Fat Loss (FL) - 3 day"
    })
    assert res.status_code == 201
    body = json.loads(res.data)
    assert body["calories"] == 1870  # 85 * 22


def test_add_client_invalid_program(api):
    res = api.post("/clients", json={"name": "Dave", "program": "InvalidPlan"})
    assert res.status_code == 400


def test_fetch_client(api):
    api.post("/clients", json={
        "name": "Emma", "weight": 65.0, "program": "Beginner (BG)"
    })
    res = api.get("/clients/Emma")
    assert res.status_code == 200
    body = json.loads(res.data)
    assert body["name"] == "Emma"


def test_fetch_client_missing(api):
    res = api.get("/clients/Nobody")
    assert res.status_code == 404


def test_log_progress(api):
    api.post("/clients", json={"name": "Frank", "program": "Beginner (BG)"})
    res = api.post("/clients/Frank/progress", json={"week": "Week 02 - 2025", "adherence": 90})
    assert res.status_code == 201


def test_log_progress_missing_week(api):
    res = api.post("/clients/Frank/progress", json={"adherence": 75})
    assert res.status_code == 400


def test_bmi_normal(api):
    api.post("/clients", json={
        "name": "Grace", "weight": 70.0, "height": 175.0, "program": "Beginner (BG)"
    })
    res = api.get("/clients/Grace/bmi")
    assert res.status_code == 200
    body = json.loads(res.data)
    assert body["bmi"] == 22.9
    assert body["category"] == "Normal"


def test_calorie_ppl(api):
    res = api.post("/clients", json={
        "name": "Henry", "weight": 75.0, "program": "Muscle Gain (MG) - PPL"
    })
    assert res.status_code == 201
    body = json.loads(res.data)
    assert body["calories"] == 2625  # 75 * 35


def test_version_defined():
    assert hasattr(app_module, "VERSION")
    assert app_module.VERSION != ""
