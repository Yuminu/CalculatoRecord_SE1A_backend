"""Route handling expression calculation."""

import logging

from flask import Blueprint, jsonify, request

from app.services import calculator as calculator_service
from app.services import history_service

logger = logging.getLogger(__name__)

calculate_bp = Blueprint("calculate", __name__)


@calculate_bp.route("/api/calculate", methods=["POST"])
def calculate_expression():
    """Validate, compute and persist a calculation.

    Returns:
        Response: On success a JSON payload with ``success``,
            ``expression``, ``result``, ``message`` and ``timestamp`` and
            HTTP 200. On failure a JSON payload with ``success`` and
            ``message`` and the matching HTTP status code.
    """
    try:
        payload = request.get_json(silent=True)
        if not isinstance(payload, dict):
            return jsonify(
                {"success": False, "message": "Invalid JSON body"}
            ), 400
        if "expression" not in payload:
            return jsonify(
                {"success": False, "message": "Expression is required"}
            ), 400

        outcome = calculator_service.calculate(payload["expression"])
        record = history_service.save_calculation(
            outcome["expression"], outcome["result"]
        )
        return jsonify(
            {
                "success": True,
                "expression": outcome["expression"],
                "result": outcome["result"],
                "message": "Calculation successful",
                "timestamp": record.created_at.strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),
            }
        ), 200

    except calculator_service.CalculatorError as error:
        logger.warning("Calculation rejected: %s", error.message)
        return jsonify(
            {"success": False, "message": error.message}
        ), 400
    except Exception:  # noqa: BLE001 - defensive API boundary
        logger.exception("Unexpected error during calculation")
        return jsonify(
            {"success": False, "message": "Internal server error"}
        ), 500
