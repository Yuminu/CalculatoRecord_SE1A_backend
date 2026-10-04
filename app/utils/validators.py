"""Input validation helpers for calculator expressions."""

ALLOWED_CHARACTERS = set("0123456789.+-*/()")
OPERATORS = set("+-*/")
DIGITS_AND_DOT = set("0123456789.")


class ValidationError(Exception):
    """Raised when an expression fails validation.

    Attributes:
        message: Human readable description of the problem.
    """

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def validate_expression(expression):
    """Validate a raw calculator expression.

    Args:
        expression: The raw expression string sent by the client.

    Returns:
        str: The stripped, validated expression.

    Raises:
        ValidationError: If the expression is missing, empty, contains
            illegal characters, uses malformed operators or has unbalanced
            parentheses.
    """
    if expression is None or not isinstance(expression, str):
        raise ValidationError("Expression is required")

    expr = expression.strip()
    if not expr:
        raise ValidationError("Expression cannot be empty")
    if len(expr) > 200:
        raise ValidationError("Expression is too long")

    _check_characters(expr)
    _check_operators(expr)
    _check_parentheses(expr)
    return expr


def _check_characters(expr):
    """Ensure the expression only contains allowed characters.

    Args:
        expr: The expression to inspect.

    Raises:
        ValidationError: If an illegal character is found.
    """
    for char in expr:
        if char not in ALLOWED_CHARACTERS:
            raise ValidationError("Invalid characters in expression")


def _check_operators(expr):
    """Check leading, trailing and adjacent operators.

    Args:
        expr: The expression to inspect.

    Raises:
        ValidationError: If the operator layout is invalid.
    """
    first = expr[0]
    if first in "*/+":
        raise ValidationError("Invalid expression: unexpected operator")
    if first == "-":
        second = expr[1] if len(expr) > 1 else ""
        if second not in "0123456789.(":
            raise ValidationError("Invalid expression: unexpected operator")

    if expr[-1] in "+-*/(":
        raise ValidationError("Invalid expression: incomplete expression")

    # Two adjacent operators are invalid unless the second is unary minus.
    for index in range(1, len(expr)):
        previous = expr[index - 1]
        current = expr[index]
        if previous in OPERATORS and current in OPERATORS and current != "-":
            raise ValidationError(
                "Invalid expression: consecutive operators"
            )

    # Reject implicit multiplication such as "2(" or ")3".
    for index in range(1, len(expr)):
        previous = expr[index - 1]
        current = expr[index]
        if current == "(" and previous in "0123456789.)":
            raise ValidationError("Invalid expression: missing operator")
        if previous == ")" and current in "0123456789.(":
            raise ValidationError("Invalid expression: missing operator")


def _check_parentheses(expr):
    """Check that parentheses are balanced and never empty.

    Args:
        expr: The expression to inspect.

    Raises:
        ValidationError: If the parentheses are malformed.
    """
    depth = 0
    for char in expr:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                raise ValidationError(
                    "Invalid expression: unmatched parentheses"
                )
    if depth != 0:
        raise ValidationError("Invalid expression: unmatched parentheses")
    if "()" in expr:
        raise ValidationError("Invalid expression: empty parentheses")
