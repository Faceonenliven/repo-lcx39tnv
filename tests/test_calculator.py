"""Comprehensive tests for the calculator module."""

import pytest

from src.calculator import (
    add,
    divide,
    factorial,
    fibonacci,
    modulo,
    multiply,
    power,
    subtract,
)


class TestAdd:
    def test_positive_numbers(self):
        assert add(2, 3) == 5

    def test_negative_numbers(self):
        assert add(-1, -1) == -2

    def test_mixed_signs(self):
        assert add(-1, 1) == 0

    def test_zeros(self):
        assert add(0, 0) == 0

    def test_floats(self):
        assert abs(add(0.1, 0.2) - 0.3) < 1e-9

    def test_invalid_type_string(self):
        with pytest.raises(TypeError, match="must be numbers"):
            add("hello", "world")

    def test_invalid_type_none(self):
        with pytest.raises(TypeError, match="must be numbers"):
            add(1, None)


class TestSubtract:
    def test_positive_result(self):
        assert subtract(5, 3) == 2

    def test_negative_result(self):
        assert subtract(3, 5) == -2

    def test_zeros(self):
        assert subtract(0, 0) == 0

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be numbers"):
            subtract("a", "b")


class TestMultiply:
    def test_positive(self):
        assert multiply(3, 4) == 12

    def test_by_zero(self):
        assert multiply(0, 5) == 0

    def test_negatives(self):
        assert multiply(-2, -3) == 6

    def test_mixed_signs(self):
        assert multiply(-2, 3) == -6

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be numbers"):
            multiply("abc", 3)


class TestDivide:
    def test_even_division(self):
        assert divide(10, 2) == 5

    def test_float_result(self):
        assert divide(7, 2) == 3.5

    def test_divide_by_zero(self):
        with pytest.raises(ValueError, match="Cannot divide by zero"):
            divide(5, 0)

    def test_negative_division(self):
        assert divide(-6, 3) == -2

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be numbers"):
            divide("10", 2)


class TestPower:
    def test_square(self):
        assert power(2, 2) == 4

    def test_cube(self):
        assert power(3, 3) == 27

    def test_zero_exponent(self):
        assert power(5, 0) == 1

    def test_one_exponent(self):
        assert power(7, 1) == 7

    def test_negative_exponent(self):
        assert power(2, -1) == 0.5

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be numbers"):
            power("2", 3)


class TestModulo:
    def test_basic(self):
        assert modulo(10, 3) == 1

    def test_no_remainder(self):
        assert modulo(6, 3) == 0

    def test_zero_divisor(self):
        with pytest.raises(ValueError, match="Cannot compute modulo"):
            modulo(5, 0)

    def test_negative(self):
        assert modulo(-7, 3) == 2  # Python modulo behavior

    def test_invalid_type(self):
        with pytest.raises(TypeError, match="must be numbers"):
            modulo("10", 3)


class TestFactorial:
    def test_zero(self):
        assert factorial(0) == 1

    def test_one(self):
        assert factorial(1) == 1

    def test_five(self):
        assert factorial(5) == 120

    def test_ten(self):
        assert factorial(10) == 3628800

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="not defined for negative"):
            factorial(-1)

    def test_float_raises(self):
        with pytest.raises(TypeError, match="only defined for integers"):
            factorial(3.5)


class TestFibonacci:
    def test_zero(self):
        assert fibonacci(0) == 0

    def test_one(self):
        assert fibonacci(1) == 1

    def test_ten(self):
        assert fibonacci(10) == 55

    def test_sequence(self):
        expected = [0, 1, 1, 2, 3, 5, 8, 13]
        for i, val in enumerate(expected):
            assert fibonacci(i) == val

    def test_negative_raises(self):
        with pytest.raises(ValueError, match="not defined for negative"):
            fibonacci(-1)

    def test_float_raises(self):
        with pytest.raises(TypeError, match="only defined for integers"):
            fibonacci(3.5)
