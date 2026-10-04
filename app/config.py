"""Configuration settings for the calculator backend."""

import os

# Absolute path to the project root (the parent of the ``app`` package).
BASE_DIR = os.path.abspath(os.path.dirname(os.path.dirname(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
DATABASE_PATH = os.path.join(DATA_DIR, "calculator.db")


class Config:
    """Default application configuration."""

    # SQLite database stored in the ``data`` directory of the project.
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE_PATH.replace("\\", "/")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # Maximum number of history records kept in the database.
    MAX_HISTORY_RECORDS = 100

    # Origins allowed by CORS. ``*`` allows any origin (fine for a course
    # project); set the CORS_ORIGINS environment variable to restrict it.
    CORS_ORIGINS = os.environ.get("CORS_ORIGINS", "*")

    # Secret key reserved for future session / form features.
    SECRET_KEY = os.environ.get("SECRET_KEY", "calculator-dev-secret")
