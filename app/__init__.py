"""Flask application factory for the calculator backend."""

import logging
import os

from flask import Flask, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy

from app.config import Config

# Shared SQLAlchemy instance. Models import this object to declare tables.
db = SQLAlchemy()


def create_app(config=None):
    """Create and configure the Flask application.

    Args:
        config: Optional configuration override. It can be a dictionary of
            settings or a configuration class. Mainly used by the tests.

    Returns:
        Flask: A fully configured application instance.
    """
    app = Flask(__name__)
    app.config.from_object(Config)
    if config is not None:
        if isinstance(config, dict):
            app.config.update(config)
        else:
            app.config.from_object(config)

    # Keep Chinese characters readable if they ever appear in responses.
    app.json.ensure_ascii = False

    _ensure_data_directory(app)

    db.init_app(app)
    CORS(app, resources={r"/api/*": {"origins": app.config["CORS_ORIGINS"]}})

    _configure_logging(app)
    _register_blueprints(app)
    _register_error_handlers(app)
    _create_tables(app)
    return app


def _ensure_data_directory(app):
    """Create the directory that stores the SQLite database file.

    Args:
        app: The Flask application whose database URI is inspected.
    """
    uri = app.config.get("SQLALCHEMY_DATABASE_URI", "")
    if uri.startswith("sqlite:///"):
        db_path = uri.replace("sqlite:///", "", 1)
        directory = os.path.dirname(db_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory, exist_ok=True)


def _configure_logging(app):
    """Configure a basic logger for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    )
    app.logger.setLevel(logging.INFO)


def _register_blueprints(app):
    """Register all route blueprints on the application.

    Args:
        app: The Flask application instance.
    """
    from app.routes.calculate import calculate_bp
    from app.routes.health import health_bp
    from app.routes.history import history_bp

    app.register_blueprint(health_bp)
    app.register_blueprint(calculate_bp)
    app.register_blueprint(history_bp)


def _register_error_handlers(app):
    """Register JSON error handlers for common HTTP errors.

    Args:
        app: The Flask application instance.
    """

    @app.errorhandler(400)
    def handle_bad_request(error):
        """Return a JSON body for malformed requests."""
        return jsonify({"success": False, "message": "Bad request"}), 400

    @app.errorhandler(404)
    def handle_not_found(error):
        """Return a JSON body when a resource is missing."""
        return jsonify(
            {"success": False, "message": "Resource not found"}
        ), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(error):
        """Return a JSON body for unsupported HTTP methods."""
        return jsonify(
            {"success": False, "message": "Method not allowed"}
        ), 405

    @app.errorhandler(500)
    def handle_internal_error(error):
        """Return a JSON body for unexpected server failures."""
        app.logger.error("Internal server error: %s", error)
        return jsonify(
            {"success": False, "message": "Internal server error"}
        ), 500


def _create_tables(app):
    """Create database tables if they do not exist yet.

    Args:
        app: The Flask application instance.
    """
    with app.app_context():
        # Import models so they register with SQLAlchemy metadata.
        from app import models  # noqa: F401

        db.create_all()
