"""History model module.

The calculation history is stored in a single table. This module exposes
the model under the ``History`` name to mirror the module layout required
by the specification. ``History`` refers to the exact same table as
``Calculation`` and does not create a second table.
"""

from app.models.calculation import Calculation

# Alias kept for clarity and future extension.
History = Calculation

__all__ = ["History"]
