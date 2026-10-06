"""Routes for reading and deleting calculation history."""

import logging

from flask import Blueprint, jsonify, request

from app.services import history_service

logger = logging.getLogger(__name__)

history_bp = Blueprint("history", __name__)


@history_bp.route("/api/history", methods=["GET"])
def list_history():
    """Return a paginated list of history records.

    Query parameters:
        limit: Maximum number of records to return (default 20).
        offset: Number of records to skip (default 0).

    Returns:
        Response: JSON ``{"success": true, "data": [...], "total": N}``.
    """
    try:
        limit = _parse_int(request.args.get("limit"), 20, 1)
        offset = _parse_int(request.args.get("offset"), 0, 0)
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400

    favorite = _parse_bool(request.args.get("favorite"))
    try:
        records, total = history_service.get_history(
            limit=limit, offset=offset, favorite=favorite
        )
        return jsonify(
            {
                "success": True,
                "data": [record.to_dict() for record in records],
                "total": total,
            }
        ), 200
    except Exception:  # noqa: BLE001 - defensive API boundary
        logger.exception("Failed to load history")
        return jsonify(
            {"success": False, "message": "Internal server error"}
        ), 500


@history_bp.route(
    "/api/history/<int:record_id>/favorite", methods=["PATCH"]
)
def toggle_favorite(record_id):
    """Toggle the favorite flag of a record.

    Args:
        record_id: The integer id taken from the URL path.

    Returns:
        Response: HTTP 200 with ``{success, is_favorite, message}`` on
            success, or HTTP 404 with a JSON body when the record is
            missing.
    """
    try:
        record = history_service.toggle_favorite(record_id)
    except Exception:  # noqa: BLE001 - defensive API boundary
        logger.exception("Failed to toggle favorite")
        return jsonify(
            {"success": False, "message": "Internal server error"}
        ), 500

    if record is None:
        return jsonify(
            {
                "success": False,
                "message": "This record has been deleted",
            }
        ), 404

    message = (
        "Added to favorites"
        if record.is_favorite
        else "Removed from favorites"
    )
    return jsonify(
        {
            "success": True,
            "is_favorite": bool(record.is_favorite),
            "message": message,
        }
    ), 200


@history_bp.route("/api/history/<int:record_id>", methods=["DELETE"])
def delete_single_history(record_id):
    """Delete a single history record.

    Args:
        record_id: The integer id taken from the URL path.

    Returns:
        Response: HTTP 204 with no body on success, or HTTP 404 with a
            JSON body when the record does not exist.
    """
    try:
        deleted = history_service.delete_history(record_id)
    except Exception:  # noqa: BLE001 - defensive API boundary
        logger.exception("Failed to delete history record")
        return jsonify(
            {"success": False, "message": "Internal server error"}
        ), 500

    if not deleted:
        return jsonify(
            {
                "success": False,
                "message": "History record not found",
            }
        ), 404
    return "", 204


@history_bp.route("/api/history", methods=["DELETE"])
def delete_all_history():
    """Delete every history record.

    Returns:
        Response: HTTP 204 with no body on success.
    """
    try:
        history_service.clear_history()
    except Exception:  # noqa: BLE001 - defensive API boundary
        logger.exception("Failed to clear history")
        return jsonify(
            {"success": False, "message": "Internal server error"}
        ), 500
    return "", 204


def _parse_int(raw_value, default, minimum):
    """Parse an optional integer query parameter safely.

    Args:
        raw_value: The raw string value from the query string (or None).
        default: Value returned when ``raw_value`` is ``None``.
        minimum: Lower bound applied to the parsed value.

    Returns:
        int: The parsed, bounded integer.

    Raises:
        ValueError: If the raw value is not a valid integer.
    """
    if raw_value is None:
        return default
    try:
        value = int(raw_value)
    except (TypeError, ValueError) as error:
        raise ValueError("Query parameter must be an integer") from error
    return max(value, minimum)


def _parse_bool(raw_value):
    """Interpret an optional query-string boolean.

    Args:
        raw_value: The raw string value from the query string (or None).

    Returns:
        bool: ``True`` for "true"/"1"/"yes" (case-insensitive), otherwise
            ``False``.
    """
    if raw_value is None:
        return False
    return raw_value.strip().lower() in ("true", "1", "yes")
