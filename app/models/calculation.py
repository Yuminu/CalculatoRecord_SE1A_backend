"""Calculation history model."""

from datetime import datetime

from app import db


class Calculation(db.Model):
    """A single calculation record persisted in the database."""

    __tablename__ = "calculation_history"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    expression = db.Column(db.Text, nullable=False)
    result = db.Column(db.Float, nullable=False)
    is_favorite = db.Column(db.Boolean, nullable=False, default=False)
    note = db.Column(db.String(50), nullable=True)
    # Reserved for the future "statistics / bookkeeping" extension.
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now)

    def to_dict(self):
        """Return a JSON-serializable representation of the record.

        The returned keys match the API contract in section 5.2.2 of the
        requirements document exactly.

        Returns:
            dict: Record fields ready to be returned by the API.
        """
        return {
            "id": self.id,
            "expression": self.expression,
            "result": self.result,
            "is_favorite": bool(self.is_favorite),
            "note": self.note,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S"),
        }

    def __repr__(self):
        """Return a debug-friendly string representation."""
        return "<Calculation id={} expression={!r}>".format(
            self.id, self.expression
        )
