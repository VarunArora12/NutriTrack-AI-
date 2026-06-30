import os
import sqlite3
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
INSTANCE_DIR = BASE_DIR / "instance"
DATABASE_PATH = INSTANCE_DIR / "nutritrack.db"


def get_connection():
    """Create a SQLite connection with rows accessible like dictionaries."""
    INSTANCE_DIR.mkdir(exist_ok=True)
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def initialize_database():
    """Create and lightly migrate the SQLite database."""
    with get_connection() as connection:
        connection.executescript(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT NOT NULL UNIQUE,
                password_hash TEXT NOT NULL,
                calorie_goal INTEGER DEFAULT 2200,
                protein_goal INTEGER DEFAULT 120,
                carbs_goal INTEGER DEFAULT 260,
                fat_goal INTEGER DEFAULT 70,
                age INTEGER,
                height_cm REAL,
                weight_kg REAL,
                activity_level TEXT DEFAULT 'moderate',
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            );

            CREATE TABLE IF NOT EXISTS sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                token_hash TEXT NOT NULL UNIQUE,
                expires_at TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );

            CREATE TABLE IF NOT EXISTS meals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                food_name TEXT NOT NULL DEFAULT '',
                description TEXT NOT NULL,
                meal_type TEXT NOT NULL DEFAULT 'meal',
                serving_amount REAL DEFAULT 1,
                calories INTEGER NOT NULL,
                protein REAL NOT NULL,
                carbs REAL NOT NULL,
                fat REAL NOT NULL,
                logged_at TEXT DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id) ON DELETE CASCADE
            );
            """
        )

        _add_column_if_missing(connection, "users", "carbs_goal", "INTEGER DEFAULT 260")
        _add_column_if_missing(connection, "users", "fat_goal", "INTEGER DEFAULT 70")
        _add_column_if_missing(connection, "users", "age", "INTEGER")
        _add_column_if_missing(connection, "users", "height_cm", "REAL")
        _add_column_if_missing(connection, "users", "weight_kg", "REAL")
        _add_column_if_missing(connection, "users", "activity_level", "TEXT DEFAULT 'moderate'")
        _add_column_if_missing(connection, "meals", "food_name", "TEXT NOT NULL DEFAULT ''")
        _add_column_if_missing(connection, "meals", "description", "TEXT DEFAULT ''")
        _add_column_if_missing(connection, "meals", "meal_type", "TEXT DEFAULT 'meal'")

        connection.execute(
            """
            UPDATE meals
            SET description = food_name
            WHERE description = '' AND food_name IS NOT NULL
            """
        )


def _add_column_if_missing(connection, table_name, column_name, column_type):
    columns = connection.execute(f"PRAGMA table_info({table_name})").fetchall()
    existing_names = {column["name"] for column in columns}
    if column_name not in existing_names:
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")


def row_to_dict(row):
    if row is None:
        return None
    return {key: row[key] for key in row.keys()}


def database_status():
    return {
        "path": os.fspath(DATABASE_PATH),
        "exists": DATABASE_PATH.exists(),
    }
