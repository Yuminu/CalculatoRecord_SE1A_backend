"""Development entry point for the calculator backend.

Run with ``python run.py`` for local development. Production deployments
use ``gunicorn --bind 0.0.0.0:5000 run:app`` (see README.md).
"""

from app import create_app

app = create_app()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
