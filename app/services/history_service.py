"""Persistence helpers for calculation history."""

import logging

from flask import current_app

from app import db
from app.models.calculation import Calculation

logger = logging.getLogger(__name__)


def save_calculation(expression, result):
    """Persist a successful calculation and enforce the record limit.

    Args:
        expression: The validated expression that was evaluated.
        result: The numeric result of the calculation.

    Returns:
        Calculation: The newly created and committed record.
    """
    record = Calculation(expression=expression, result=result)
    db.session.add(record)
    db.session.commit()
    _enforce_history_limit()
    return record


def _enforce_history_limit():
    """Delete the oldest records when the maximum count is exceeded."""
    limit = current_app.config.get("MAX_HISTORY_RECORDS", 100)
    total = Calculation.query.count()
    if total <= limit:
        return

    extra = total - limit
    old_records = (
        Calculation.query.order_by(Calculation.id.asc()).limit(extra).all()
    )
    for record in old_records:
        db.session.delete(record)
    db.session.commit()
    logger.info("Trimmed %s oldest history record(s)", extra)


def get_history(limit=20, offset=0, favorite=None):
    """Return a page of history records and the total count.

    Args:
        limit: Maximum number of records to return (default 20).
        offset: Number of records to skip (default 0).
        favorite: When ``True`` only favorite records are returned; when
            ``None`` or ``False`` no favorite filter is applied.

    Returns:
        tuple: ``(records, total)`` where ``records`` is a list of
            :class:`Calculation` ordered from newest to oldest.
    """
    query = Calculation.query
    if favorite:
        query = query.filter(Calculation.is_favorite.is_(True))
    query = query.order_by(Calculation.id.desc())
    total = query.count()
    records = query.offset(offset).limit(limit).all()
    return records, total


def get_record(record_id):
    """Return a single record by id.

    Args:
        record_id: The primary key of the record.

    Returns:
        Calculation or None: The matching record, or ``None`` if missing.
    """
    return db.session.get(Calculation, record_id)


def toggle_favorite(record_id):
    """Flip the favorite flag of a record.

    Args:
        record_id: The primary key of the record.

    Returns:
        Calculation or None: The updated record, or ``None`` if the
            record does not exist.
    """
    record = get_record(record_id)
    if record is None:
        return None
    record.is_favorite = not bool(record.is_favorite)
    db.session.commit()
    return record


def delete_history(record_id):
    """Delete a single record.

    Args:
        record_id: The primary key of the record to delete.

    Returns:
        bool: ``True`` when a record was deleted, ``False`` otherwise.
    """
    record = get_record(record_id)
    if record is None:
        return False
    db.session.delete(record)
    db.session.commit()
    return True


def clear_history():
    """Delete every history record.

    Returns:
        int: The number of deleted records.
    """
    deleted = Calculation.query.delete()
    db.session.commit()
    return deleted
