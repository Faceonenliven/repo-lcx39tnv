"""Comprehensive tests for the converter module."""

import pytest

from src.converter import (
    binary_to_decimal,
    celsius_to_fahrenheit,
    decimal_to_binary,
    decimal_to_hex,
    fahrenheit_to_celsius,
    gallons_to_liters,
    hex_to_decimal,
    kg_to_pounds,
    km_to_miles,
    liters_to_gallons,
    miles_to_km,
    pounds_to_kg,
)


class TestCelsiusToFahrenheit:
    def test_freezing_point(self):
        assert celsius_to_fahrenheit(0) == 32

    def test_boiling_point(self):
        assert celsius_to_fahrenheit(100) == 212

    def test_negative(self):
        assert celsius_to_fahrenheit(-40) == -40

    def test_float_input(self):
        assert abs(celsius_to_fahrenheit(37.5) - 99.5) < 0.01

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            celsius_to_fahrenheit("100")


class TestFahrenheitToCelsius:
    def test_freezing_point(self):
        assert fahrenheit_to_celsius(32) == 0

    def test_boiling_point(self):
        assert fahrenheit_to_celsius(212) == 100

    def test_negative(self):
        assert fahrenheit_to_celsius(-40) == -40

    def test_float_input(self):
        assert abs(fahrenheit_to_celsius(99.5) - 37.5) < 0.01

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            fahrenheit_to_celsius("32")


class TestKmToMiles:
    def test_one_km(self):
        assert abs(km_to_miles(1) - 0.621371) < 0.0001

    def test_zero(self):
        assert km_to_miles(0) == 0

    def test_large_value(self):
        assert abs(km_to_miles(100) - 62.1371) < 0.001

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            km_to_miles(-5)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            km_to_miles("10")


class TestMilesToKm:
    def test_one_mile(self):
        assert abs(miles_to_km(1) - 1.60934) < 0.0001

    def test_zero(self):
        assert miles_to_km(0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            miles_to_km(-3)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            miles_to_km([1])


class TestKgToPounds:
    def test_one_kg(self):
        assert abs(kg_to_pounds(1) - 2.20462) < 0.0001

    def test_zero(self):
        assert kg_to_pounds(0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            kg_to_pounds(-1)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            kg_to_pounds(None)


class TestPoundsToKg:
    def test_one_pound(self):
        assert abs(pounds_to_kg(1) - 0.453592) < 0.0001

    def test_zero(self):
        assert pounds_to_kg(0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            pounds_to_kg(-2)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            pounds_to_kg("5")


class TestLitersToGallons:
    def test_one_liter(self):
        assert abs(liters_to_gallons(1) - 0.264172) < 0.0001

    def test_zero(self):
        assert liters_to_gallons(0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            liters_to_gallons(-1)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            liters_to_gallons({})


class TestGallonsToLiters:
    def test_one_gallon(self):
        assert abs(gallons_to_liters(1) - 3.78541) < 0.001

    def test_zero(self):
        assert gallons_to_liters(0) == 0

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            gallons_to_liters(-1)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            gallons_to_liters("2")


class TestDecimalToBinary:
    def test_zero(self):
        assert decimal_to_binary(0) == "0"

    def test_positive(self):
        assert decimal_to_binary(10) == "1010"

    def test_power_of_two(self):
        assert decimal_to_binary(8) == "1000"

    def test_one(self):
        assert decimal_to_binary(1) == "1"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            decimal_to_binary(-1)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            decimal_to_binary(3.5)


class TestBinaryToDecimal:
    def test_zero(self):
        assert binary_to_decimal("0") == 0

    def test_positive(self):
        assert binary_to_decimal("1010") == 10

    def test_one(self):
        assert binary_to_decimal("1") == 1

    def test_all_ones(self):
        assert binary_to_decimal("1111") == 15

    def test_invalid_chars(self):
        with pytest.raises(ValueError):
            binary_to_decimal("102")

    def test_empty_string(self):
        with pytest.raises(ValueError):
            binary_to_decimal("")

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            binary_to_decimal(101)


class TestHexToDecimal:
    def test_single_digit(self):
        assert hex_to_decimal("a") == 10

    def test_multi_digit(self):
        assert hex_to_decimal("ff") == 255

    def test_with_prefix(self):
        assert hex_to_decimal("0x1a") == 26

    def test_zero(self):
        assert hex_to_decimal("0") == 0

    def test_uppercase(self):
        assert hex_to_decimal("FF") == 255

    def test_invalid_hex(self):
        with pytest.raises(ValueError):
            hex_to_decimal("gg")

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            hex_to_decimal(255)


class TestDecimalToHex:
    def test_zero(self):
        assert decimal_to_hex(0) == "0"

    def test_positive(self):
        assert decimal_to_hex(255) == "ff"

    def test_sixteen(self):
        assert decimal_to_hex(16) == "10"

    def test_negative_raises(self):
        with pytest.raises(ValueError):
            decimal_to_hex(-1)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            decimal_to_hex(3.14)
