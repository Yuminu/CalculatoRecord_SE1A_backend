"""Unit tests for the safe calculator service."""

import pytest

from app.services.calculator import (
    CalculatorError,
    DivisionByZeroError,
    InvalidCharacterError,
    calculate,
)


def _result(expression):
    """Return only the numeric result of an expression."""
    return calculate(expression)["result"]


@pytest.mark.parametrize(
    "expression,expected",
    [
        ("1+1", 2),
        ("3*4", 12),
        ("1+2*3", 7),
        ("(1+2)*3", 9),
        ("-5+3", -2),
        ("3*-2", -6),
        ("3.14*2", 6.28),
        ("((1+2)*(3-4))", -3),
        ("12+8", 20),
        ("5/2", 2.5),
        ("1.0+2.0", 3),
    ],
)
def test_calculate_returns_expected_result(expression, expected):
    """Basic, compound, unary and decimal expressions are computed."""
    assert _result(expression) == pytest.approx(expected)


@pytest.mark.parametrize("expression", ["1/0", "5/(3-3)", "0/0"])
def test_division_by_zero_raises(expression):
    """Dividing by zero raises a DivisionByZeroError."""
    with pytest.raises(DivisionByZeroError) as error:
        calculate(expression)
    assert error.value.message == "Division by zero"


@pytest.mark.parametrize(
    "expression",
    ["1++2", "abc", "", "   ", "1+", "(1+2", "1+2)", "2(3)", "*5", "1..2"],
)
def test_invalid_expression_raises(expression):
    """Malformed expressions raise a CalculatorError."""
    with pytest.raises(CalculatorError):
        calculate(expression)


def test_invalid_characters_raise_specific_error():
    """Illegal characters raise an InvalidCharacterError."""
    with pytest.raises(InvalidCharacterError):
        calculate("1+$2")


def test_integer_result_has_no_decimal_part():
    """Integral results are returned as plain integers (no trailing .0)."""
    value = _result("1.0+2.0")
    assert value == 3
    assert isinstance(value, int)


def test_result_rounded_to_eight_decimals():
    """Non-integral results are rounded to eight decimal places."""
    assert _result("1/3") == pytest.approx(0.33333333)
