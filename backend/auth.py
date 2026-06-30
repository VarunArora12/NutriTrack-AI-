import hashlib
import secrets
from datetime import datetime, timedelta, timezone
from functools import wraps

from flask import g, jsonify, request
from werkzeug.security import check_password_hash, generate_password_hash

from database import get_connection, row_to_dict


SESSION_DAYS = 7


def hash_password(password):
    return generate_password_hash(password)


def password_matches(password_hash, password):
    return check_password_hash(password_hash, password)


def create_session(user_id):
    raw_token = secrets.token_urlsafe(48)
    token_hash = _hash_token(raw_token)
    expires_at = datetime.now(timezone.utc) + timedelta(days=SESSION_DAYS)

    with get_connection() as connection:
        connection.execute(
            """
            INSERT INTO sessions (user_id, token_hash, expires_at)
            VALUES (?, ?, ?)
            """,
            (user_id, token_hash, expires_at.isoformat()),
        )

    return raw_token


def delete_session(raw_token):
    if not raw_token:
        return

    with get_connection() as connection:
        connection.execute(
            "DELETE FROM sessions WHERE token_hash = ?",
            (_hash_token(raw_token),),
        )


def get_current_user():
    raw_token = _get_bearer_token()
    if not raw_token:
        return None

    token_hash = _hash_token(raw_token)
    now = datetime.now(timezone.utc).isoformat()

    with get_connection() as connection:
        connection.execute("DELETE FROM sessions WHERE expires_at <= ?", (now,))
        row = connection.execute(
            """
            SELECT users.*
            FROM sessions
            JOIN users ON users.id = sessions.user_id
            WHERE sessions.token_hash = ? AND sessions.expires_at > ?
            """,
            (token_hash, now),
        ).fetchone()

    return row_to_dict(row)


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        user = get_current_user()
        if user is None:
            return jsonify({"error": "Authentication required."}), 401

        g.user = user
        return view(*args, **kwargs)

    return wrapped_view


def public_user(user):
    return {
        "id": user["id"],
        "name": user["name"],
        "email": user["email"],
        "calorie_goal": user["calorie_goal"],
        "protein_goal": user["protein_goal"],
        "carbs_goal": user["carbs_goal"],
        "fat_goal": user["fat_goal"],
        "age": user["age"],
        "height_cm": user["height_cm"],
        "weight_kg": user["weight_kg"],
        "activity_level": user["activity_level"],
    }


def _get_bearer_token():
    auth_header = request.headers.get("Authorization", "")
    if not auth_header.startswith("Bearer "):
        return None
    return auth_header.replace("Bearer ", "", 1).strip()


def _hash_token(raw_token):
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()
