from datetime import date, datetime, timedelta

from flask import Flask, g, jsonify, request
from flask_cors import CORS

from auth import (
    create_session,
    delete_session,
    hash_password,
    login_required,
    password_matches,
    public_user,
)
from database import (
    create_meal,
    create_user,
    database_status,
    delete_meal_for_user,
    get_user_by_email,
    list_meals_between,
    update_user_profile,
)
from nutrition import estimate_meal, sample_foods, search_foods


ALLOWED_ORIGINS = [
    "http://localhost:5001",
    "http://127.0.0.1:5001",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "dev-secret-change-before-production"

    CORS(
        app,
        resources={r"/api/*": {"origins": ALLOWED_ORIGINS}},
        supports_credentials=True,
    )

    @app.errorhandler(404)
    def not_found(_error):
        return jsonify({"error": "Endpoint not found."}), 404

    @app.errorhandler(500)
    def server_error(_error):
        return jsonify({"error": "Something went wrong on the server."}), 500

    @app.get("/api/health")
    def health_check():
        return jsonify(
            {
                "status": "ok",
                "app": "NutriTrack AI",
                "database": database_status(),
                "sample_food_count": len(sample_foods()),
            }
        )

    @app.post("/api/auth/signup")
    def signup():
        data = _json_body()

        name = _clean_text(data.get("name"))
        email = _clean_text(data.get("email")).lower()
        password = data.get("password", "")

        if len(name) < 2:
            return _bad_request("Name must be at least 2 characters.")

        if "@" not in email or "." not in email:
            return _bad_request("Enter a valid email address.")

        if len(password) < 8:
            return _bad_request("Password must be at least 8 characters.")

        if get_user_by_email(email) is not None:
            return jsonify(
                {"error": "An account with this email already exists."}
            ), 409

        user = create_user(name, email, hash_password(password))
        token = create_session(user["id"])

        return jsonify(
            {
                "token": token,
                "user": public_user(user),
            }
        ), 201

    @app.post("/api/auth/login")
    def login():
        data = _json_body()
        email = _clean_text(data.get("email")).lower()
        password = data.get("password", "")

        user = get_user_by_email(email)

        if user is None or not password_matches(user["password_hash"], password):
            return jsonify({"error": "Invalid email or password."}), 401

        token = create_session(user["id"])
        return jsonify({"token": token, "user": public_user(user)})

    @app.post("/api/auth/logout")
    @login_required
    def logout():
        auth_header = request.headers.get("Authorization", "")
        delete_session(auth_header.replace("Bearer ", "", 1).strip())
        return jsonify({"message": "Logged out successfully."})

    @app.get("/api/auth/me")
    @login_required
    def current_user():
        return jsonify({"user": public_user(g.user)})

    @app.get("/api/profile")
    @login_required
    def get_profile():
        return jsonify({"user": public_user(g.user)})

    @app.put("/api/profile")
    @login_required
    def update_profile():
        data = _json_body()
        name = _clean_text(data.get("name")) or g.user["name"]
        calorie_goal = _positive_int(data.get("calorie_goal"), "Calorie goal")
        protein_goal = _positive_int(data.get("protein_goal"), "Protein goal")
        carbs_goal = _positive_int(data.get("carbs_goal"), "Carbs goal")
        fat_goal = _positive_int(data.get("fat_goal"), "Fat goal")

        if isinstance(calorie_goal, tuple):
            return calorie_goal
        if isinstance(protein_goal, tuple):
            return protein_goal
        if isinstance(carbs_goal, tuple):
            return carbs_goal
        if isinstance(fat_goal, tuple):
            return fat_goal

        age = _optional_number(data.get("age"))
        height_cm = _optional_number(data.get("height_cm"))
        weight_kg = _optional_number(data.get("weight_kg"))
        activity_level = _clean_text(data.get("activity_level")) or "moderate"

        user = update_user_profile(
            g.user["id"],
            {
                "name": name,
                "calorie_goal": calorie_goal,
                "protein_goal": protein_goal,
                "carbs_goal": carbs_goal,
                "fat_goal": fat_goal,
                "age": age,
                "height_cm": height_cm,
                "weight_kg": weight_kg,
                "activity_level": activity_level,
            },
        )

        return jsonify({"user": public_user(user)})

    @app.get("/api/foods")
    @login_required
    def foods():
        return jsonify({"foods": search_foods(request.args.get("q", ""))})

    @app.post("/api/nutrition/estimate")
    @login_required
    def estimate():
        data = _json_body()
        description = _clean_text(data.get("description"))
        result = estimate_meal(description)
        if result is None:
            return _bad_request("Meal description is required.")
        return jsonify({"estimate": result})

    @app.get("/api/meals")
    @login_required
    def list_meals():
        day = _parse_day(request.args.get("date"))
        if isinstance(day, tuple):
            return day

        start, end = _day_bounds(day)
        meals = [_meal_response(row) for row in list_meals_between(g.user["id"], start, end)]
        return jsonify({"date": day.isoformat(), "meals": meals, "totals": _sum_meals(meals)})

    @app.post("/api/meals")
    @login_required
    def add_meal():
        data = _json_body()
        description = _clean_text(data.get("description"))
        meal_type = _clean_text(data.get("meal_type")) or "meal"
        logged_at = _parse_datetime(data.get("logged_at"))
        if isinstance(logged_at, tuple):
            return logged_at

        result = estimate_meal(description)
        if result is None:
            return _bad_request("Meal description is required.")
        if not result["items"]:
            return _bad_request(result["message"])

        totals = result["totals"]
        meal = create_meal(
            {
                "user_id": g.user["id"],
                "description": description,
                "meal_type": meal_type,
                "calories": totals["calories"],
                "protein": totals["protein"],
                "carbs": totals["carbs"],
                "fat": totals["fat"],
                "logged_at": logged_at.isoformat(timespec="seconds"),
            }
        )

        return jsonify({"meal": _meal_response(meal), "estimate": result}), 201

    @app.delete("/api/meals/<int:meal_id>")
    @login_required
    def delete_meal(meal_id):
        if not delete_meal_for_user(meal_id, g.user["id"]):
            return jsonify({"error": "Meal not found."}), 404

        return jsonify({"message": "Meal deleted."})

    @app.get("/api/dashboard/today")
    @login_required
    def dashboard_today():
        today = _parse_day(request.args.get("date"))
        if isinstance(today, tuple):
            return today

        start, end = _day_bounds(today)
        meals = _meals_between(g.user["id"], start, end)
        totals = _sum_meals(meals)
        goals = {
            "calories": g.user["calorie_goal"],
            "protein": g.user["protein_goal"],
            "carbs": g.user["carbs_goal"],
            "fat": g.user["fat_goal"],
        }

        return jsonify(
            {
                "date": today.isoformat(),
                "user": public_user(g.user),
                "meals": meals,
                "totals": totals,
                "goals": goals,
                "remaining": {
                    key: round(goals[key] - totals[key], 1)
                    for key in goals
                },
            }
        )

    @app.get("/api/analytics/week")
    @login_required
    def weekly_analytics():
        today = date.today()
        start_day = today - timedelta(days=6)
        start, _unused = _day_bounds(start_day)
        _unused, end = _day_bounds(today)
        meals = _meals_between(g.user["id"], start, end)

        days = []
        for offset in range(7):
            current_day = start_day + timedelta(days=offset)
            day_meals = [
                meal for meal in meals if meal["logged_at"].startswith(current_day.isoformat())
            ]
            totals = _sum_meals(day_meals)
            days.append(
                {
                    "date": current_day.isoformat(),
                    "label": current_day.strftime("%a"),
                    **totals,
                }
            )

        averages = {
            "calories": round(sum(day["calories"] for day in days) / 7),
            "protein": round(sum(day["protein"] for day in days) / 7, 1),
            "carbs": round(sum(day["carbs"] for day in days) / 7, 1),
            "fat": round(sum(day["fat"] for day in days) / 7, 1),
        }

        return jsonify({"days": days, "averages": averages})

    return app


def _json_body():
    return request.get_json(silent=True) or {}


def _clean_text(value):
    return str(value or "").strip()


def _bad_request(message):
    return jsonify({"error": message}), 400


def _positive_int(value, label):
    try:
        number = int(value)
    except (TypeError, ValueError):
        return _bad_request(f"{label} must be a number.")

    if number <= 0:
        return _bad_request(f"{label} must be greater than zero.")
    return number


def _optional_number(value):
    if value in ("", None):
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _parse_day(value):
    if not value:
        return date.today()
    try:
        return date.fromisoformat(value)
    except ValueError:
        return _bad_request("Date must use YYYY-MM-DD format.")


def _parse_datetime(value):
    if not value:
        return datetime.now()
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return _bad_request("Logged time must be a valid ISO date-time.")


def _day_bounds(day):
    start = datetime.combine(day, datetime.min.time())
    end = start + timedelta(days=1)
    return start.isoformat(), end.isoformat()


def _meals_between(user_id, start, end):
    return [_meal_response(row) for row in list_meals_between(user_id, start, end)]


def _meal_response(meal):
    return {
        "id": meal["id"],
        "description": meal["description"],
        "meal_type": meal["meal_type"],
        "calories": meal["calories"],
        "protein": meal["protein"],
        "carbs": meal["carbs"],
        "fat": meal["fat"],
        "logged_at": meal["logged_at"],
    }


def _sum_meals(meals):
    return {
        "calories": round(sum(meal["calories"] for meal in meals)),
        "protein": round(sum(meal["protein"] for meal in meals), 1),
        "carbs": round(sum(meal["carbs"] for meal in meals), 1),
        "fat": round(sum(meal["fat"] for meal in meals), 1),
    }


app = create_app()


if __name__ == "__main__":
    app.run(debug=True, port=5002)