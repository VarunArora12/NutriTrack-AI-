import os

from dotenv import load_dotenv
from supabase import create_client


load_dotenv()

_supabase_client = None


def get_supabase():
    """Return the configured Supabase client."""
    global _supabase_client

    if _supabase_client is not None:
        return _supabase_client

    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")

    if not supabase_url or not supabase_key:
        raise RuntimeError("SUPABASE_URL and SUPABASE_KEY must be set.")

    _supabase_client = create_client(supabase_url, supabase_key)
    return _supabase_client


def database_status():
    return {
        "provider": "supabase",
        "configured": bool(os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_KEY")),
        "url": os.getenv("SUPABASE_URL", ""),
    }


def create_user(name, email, password_hash):
    response = (
        _table("users")
        .insert(
            {
                "name": name,
                "email": email,
                "password_hash": password_hash,
                "calorie_goal": 2200,
                "protein_goal": 120,
                "carbs_goal": 260,
                "fat_goal": 70,
                "activity_level": "moderate",
            }
        )
        .execute()
    )
    return normalize_user(_single(response.data))


def get_user_by_email(email):
    response = _table("users").select("*").eq("email", email).limit(1).execute()
    return normalize_user(_first(response.data))


def get_user_by_id(user_id):
    response = _table("users").select("*").eq("id", user_id).limit(1).execute()
    return normalize_user(_first(response.data))


def update_user_profile(user_id, profile):
    response = _table("users").update(profile).eq("id", user_id).execute()
    return normalize_user(_single(response.data))


def create_session_record(user_id, token_hash, expires_at):
    _table("sessions").insert(
        {
            "user_id": user_id,
            "token_hash": token_hash,
            "expires_at": expires_at,
        }
    ).execute()


def delete_session_record(token_hash):
    _table("sessions").delete().eq("token_hash", token_hash).execute()


def delete_expired_sessions(now):
    _table("sessions").delete().lte("expires_at", now).execute()


def get_user_for_session(token_hash, now):
    response = (
        _table("sessions")
        .select("*")
        .eq("token_hash", token_hash)
        .gt("expires_at", now)
        .limit(1)
        .execute()
    )
    session = _first(response.data)
    if session is None:
        return None

    return get_user_by_id(session["user_id"])


def list_meals_between(user_id, start, end):
    response = (
        _table("meals")
        .select("*")
        .eq("user_id", user_id)
        .gte("logged_at", start)
        .lt("logged_at", end)
        .order("logged_at", desc=True)
        .execute()
    )
    return response.data or []


def create_meal(meal):
    response = _table("meals").insert(meal).execute()
    return _single(response.data)


def delete_meal_for_user(meal_id, user_id):
    existing = (
        _table("meals")
        .select("id")
        .eq("id", meal_id)
        .eq("user_id", user_id)
        .limit(1)
        .execute()
    )
    if _first(existing.data) is None:
        return False

    _table("meals").delete().eq("id", meal_id).eq("user_id", user_id).execute()
    return True


def normalize_user(user):
    if user is None:
        return None

    return {
        "id": user.get("id"),
        "name": user.get("name"),
        "email": user.get("email"),
        "password_hash": user.get("password_hash"),
        "calorie_goal": user.get("calorie_goal", 2200),
        "protein_goal": user.get("protein_goal", 120),
        "carbs_goal": user.get("carbs_goal", 260),
        "fat_goal": user.get("fat_goal", 70),
        "age": user.get("age"),
        "height_cm": user.get("height_cm"),
        "weight_kg": user.get("weight_kg"),
        "activity_level": user.get("activity_level", "moderate"),
        "created_at": user.get("created_at"),
    }


def _table(name):
    return get_supabase().table(name)


def _first(rows):
    if not rows:
        return None
    return rows[0]


def _single(rows):
    row = _first(rows)
    if row is None:
        raise RuntimeError("Supabase did not return the saved row.")
    return row
