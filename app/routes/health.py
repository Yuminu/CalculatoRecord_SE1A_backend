"""Health-check route used to verify the deployment."""

from flask import Blueprint, jsonify

health_bp = Blueprint("health", __name__)


@health_bp.route("/api/health", methods=["GET"])
def health():
    """Return a simple status payload confirming the API is alive.

    Returns:
        Response: JSON ``{"status": "ok", ...}`` with HTTP 200.
    """
    return jsonify(
        {
            "status": "ok",
            "message": "Calculator API is running",
        }
    ), 200
