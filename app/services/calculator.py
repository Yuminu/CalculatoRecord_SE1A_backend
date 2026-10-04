"""Safe mathematical expression evaluation service.

The evaluator never uses ``eval``/``exec``. It parses the expression with
the :mod:`ast` module and walks the resulting syntax tree, allowing only
numeric constants, the four basic operators, parentheses and unary signs.
"""

import ast
import logging
from decimal import (
    Decimal,
    DivisionByZero,
    InvalidOperation,
    ROUND_HALF_UP,
    localcontext,
)

from app.utils.validators import ValidationError, validate_expression

logger = logging.getLogger(__name__)

# Number of decimal places kept in the final result.
RESULT_PRECISION = 8
_QUANTIZER = Decimal(1).scaleb(-RESULT_PRECISION)  # 1E-8


class CalculatorError(Exception):
    """Base error for calculation problems (maps to HTTP 400).

    Attributes:
        message: Human readable description of the problem.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class DivisionByZeroError(CalculatorError):
    """Raised when the expression tries to divide by zero."""


class InvalidExpressionError(CalculatorError):
    """Raised when the expression cannot be parsed or evaluated."""


class InvalidCharacterError(CalculatorError):
    """Raised when the expression contains illegal characters."""


def calculate(expression):
    """Validate, parse and evaluate a mathematical expression.

    Args:
        expression: Raw expression string sent by the client.

    Returns:
        dict: Dictionary with the echoed ``expression`` and the numeric
            ``result`` (an ``int`` when integral, otherwise a ``float``
            rounded to 8 decimal places).

    Raises:
        CalculatorError: For invalid input or mathematical errors such as
            division by zero.
    """
    try:
        clean_expression = validate_expression(expression)
    except ValidationError as error:
        raise _translate_validation_error(error) from error

    try:
        tree = ast.parse(clean_expression, mode="eval")
    except SyntaxError as error:
        raise InvalidExpressionError(
            "Invalid expression: {}".format(error.msg.lower())
        ) from error

    try:
        with localcontext() as context:
            context.prec = 50
            value = _evaluate_node(tree.body)
            result = _normalize(value)
    except CalculatorError:
        raise
    except (ZeroDivisionError, DivisionByZero) as error:
        raise DivisionByZeroError("Division by zero") from error
    except (InvalidOperation, OverflowError) as error:
        raise InvalidExpressionError(
            "Invalid expression: number out of range"
        ) from error
    except (TypeError, ValueError) as error:
        raise InvalidExpressionError("Invalid expression") from error

    return {"expression": clean_expression, "result": result}


def _translate_validation_error(error):
    """Convert a :class:`ValidationError` into a ``CalculatorError``.

    Args:
        error: The validation error raised by the validators module.

    Returns:
        CalculatorError: A matching calculator error instance.
    """
    if error.message == "Invalid characters in expression":
        return InvalidCharacterError(error.message)
    return InvalidExpressionError(error.message)


def _evaluate_node(node):
    """Recursively evaluate a single AST node.

    Args:
        node: The AST node to evaluate.

    Returns:
        Decimal: The numeric value of the node.

    Raises:
        InvalidExpressionError: If the node uses unsupported syntax.
    """
    if isinstance(node, ast.BinOp):
        return _evaluate_binary_operation(node)
    if isinstance(node, ast.UnaryOp):
        return _evaluate_unary_operation(node)
    if isinstance(node, ast.Constant):
        return _evaluate_constant(node)
    raise InvalidExpressionError("Invalid expression: unsupported syntax")


def _evaluate_binary_operation(node):
    """Evaluate a binary operation node (``+``, ``-``, ``*``, ``/``).

    Args:
        node: An :class:`ast.BinOp` node.

    Returns:
        Decimal: The result of the operation.

    Raises:
        DivisionByZeroError: If a division by zero is attempted.
        InvalidExpressionError: If the operator is not supported.
    """
    left = _evaluate_node(node.left)
    right = _evaluate_node(node.right)
    if isinstance(node.op, ast.Add):
        return left + right
    if isinstance(node.op, ast.Sub):
        return left - right
    if isinstance(node.op, ast.Mult):
        return left * right
    if isinstance(node.op, ast.Div):
        if right == 0:
            raise DivisionByZeroError("Division by zero")
        return left / right
    raise InvalidExpressionError("Invalid expression: unsupported operator")


def _evaluate_unary_operation(node):
    """Evaluate a unary operation node (``+`` or ``-``).

    Args:
        node: An :class:`ast.UnaryOp` node.

    Returns:
        Decimal: The result of the operation.

    Raises:
        InvalidExpressionError: If the operator is not supported.
    """
    operand = _evaluate_node(node.operand)
    if isinstance(node.op, ast.USub):
        return -operand
    if isinstance(node.op, ast.UAdd):
        return operand
    raise InvalidExpressionError("Invalid expression: unsupported operator")


def _evaluate_constant(node):
    """Evaluate a numeric constant node.

    Args:
        node: An :class:`ast.Constant` node.

    Returns:
        Decimal: The numeric value of the constant.

    Raises:
        InvalidExpressionError: If the constant is not numeric.
    """
    if isinstance(node.value, bool) or not isinstance(
        node.value, (int, float)
    ):
        raise InvalidExpressionError("Invalid expression: unsupported value")
    return Decimal(str(node.value))


def _normalize(value):
    """Round a Decimal result and remove trailing zeros.

    Args:
        value: Decimal value produced by the evaluator.

    Returns:
        int or float: ``int`` when the value is integral, otherwise a
            ``float`` rounded to :data:`RESULT_PRECISION` decimals.
    """
    with localcontext() as context:
        context.prec = 50
        quantized = value.quantize(_QUANTIZER, rounding=ROUND_HALF_UP)
    if quantized == quantized.to_integral_value():
        return int(quantized)
    return float(quantized.normalize())


# ---------------------------------------------------------------------------
# Reserved module paths for future extensions (requirements section 14).
# These classes are intentionally unimplemented placeholders.
# ---------------------------------------------------------------------------


class ScientificCalculator:
    """Reserved for future scientific functions (trigonometry, log, ...)."""

    # TODO(extension): implement sin/cos/log/... in a later iteration.
    pass


class BaseConverter:
    """Reserved for future number-base conversion (binary/octal/hex)."""

    # TODO(extension): implement base conversion in a later iteration.
    pass


class UnitConverter:
    """Reserved for future unit conversion (length, weight, ...)."""

    # TODO(extension): implement unit conversion in a later iteration.
    pass
