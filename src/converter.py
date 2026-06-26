"""Converter module for unit and data format conversions."""


def celsius_to_fahrenheit(celsius):
    """Convert Celsius to Fahrenheit."""
    if not isinstance(celsius, (int, float)):
        raise TypeError("Temperature must be a number")
    return celsius * 9 / 5 + 32


def fahrenheit_to_celsius(fahrenheit):
    """Convert Fahrenheit to Celsius."""
    if not isinstance(fahrenheit, (int, float)):
        raise TypeError("Temperature must be a number")
    return (fahrenheit - 32) * 5 / 9


def km_to_miles(km):
    """Convert kilometers to miles."""
    if not isinstance(km, (int, float)):
        raise TypeError("Distance must be a number")
    if km < 0:
        raise ValueError("Distance cannot be negative")
    return km * 0.621371


def miles_to_km(miles):
    """Convert miles to kilometers."""
    if not isinstance(miles, (int, float)):
        raise TypeError("Distance must be a number")
    if miles < 0:
        raise ValueError("Distance cannot be negative")
    return miles * 1.60934


def kg_to_pounds(kg):
    """Convert kilograms to pounds."""
    if not isinstance(kg, (int, float)):
        raise TypeError("Weight must be a number")
    if kg < 0:
        raise ValueError("Weight cannot be negative")
    return kg * 2.20462


def pounds_to_kg(pounds):
    """Convert pounds to kilograms."""
    if not isinstance(pounds, (int, float)):
        raise TypeError("Weight must be a number")
    if pounds < 0:
        raise ValueError("Weight cannot be negative")
    return pounds * 0.453592


def liters_to_gallons(liters):
    """Convert liters to gallons."""
    if not isinstance(liters, (int, float)):
        raise TypeError("Volume must be a number")
    if liters < 0:
        raise ValueError("Volume cannot be negative")
    return liters * 0.264172


def gallons_to_liters(gallons):
    """Convert gallons to liters."""
    if not isinstance(gallons, (int, float)):
        raise TypeError("Volume must be a number")
    if gallons < 0:
        raise ValueError("Volume cannot be negative")
    return gallons * 3.78541


def decimal_to_binary(n):
    """Convert a non-negative integer to binary string."""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Input must be non-negative")
    if n == 0:
        return "0"
    return bin(n)[2:]


def binary_to_decimal(binary_str):
    """Convert a binary string to decimal integer."""
    if not isinstance(binary_str, str):
        raise TypeError("Input must be a string")
    if not all(c in "01" for c in binary_str):
        raise ValueError("Input must contain only 0s and 1s")
    if not binary_str:
        raise ValueError("Input must not be empty")
    return int(binary_str, 2)


def hex_to_decimal(hex_str):
    """Convert a hexadecimal string to decimal integer."""
    if not isinstance(hex_str, str):
        raise TypeError("Input must be a string")
    hex_str = hex_str.lstrip("0x").lstrip("0X")
    if not hex_str:
        return 0
    if not all(c in "0123456789abcdefABCDEF" for c in hex_str):
        raise ValueError("Input must be a valid hexadecimal string")
    return int(hex_str, 16)


def decimal_to_hex(n):
    """Convert a non-negative integer to hexadecimal string."""
    if not isinstance(n, int):
        raise TypeError("Input must be an integer")
    if n < 0:
        raise ValueError("Input must be non-negative")
    if n == 0:
        return "0"
    return hex(n)[2:]
