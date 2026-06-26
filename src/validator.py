"""Validator module for common data validation tasks."""

import re


def is_valid_email(email):
    """Check if a string is a valid email address."""
    if not isinstance(email, str):
        return False
    pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    return bool(re.match(pattern, email))


def is_valid_url(url):
    """Check if a string is a valid URL."""
    if not isinstance(url, str):
        return False
    pattern = r"^https?://[a-zA-Z0-9.-]+(?:\.[a-zA-Z]{2,})(?:/[^\s]*)?$"
    return bool(re.match(pattern, url))


def is_valid_phone(phone):
    """Check if a string is a valid phone number (US format)."""
    if not isinstance(phone, str):
        return False
    cleaned = re.sub(r"[\s\-\(\)]", "", phone)
    pattern = r"^\+?1?\d{10}$"
    return bool(re.match(pattern, cleaned))


def is_valid_ip(ip):
    """Check if a string is a valid IPv4 address."""
    if not isinstance(ip, str):
        return False
    parts = ip.split(".")
    if len(parts) != 4:
        return False
    for part in parts:
        try:
            num = int(part)
            if num < 0 or num > 255:
                return False
            if part != str(num):
                return False
        except ValueError:
            return False
    return True


def is_strong_password(password):
    """Check if password meets strength requirements.

    Requirements:
    - At least 8 characters long
    - Contains at least one uppercase letter
    - Contains at least one lowercase letter
    - Contains at least one digit
    - Contains at least one special character
    """
    if not isinstance(password, str):
        return False
    if len(password) < 8:
        return False
    if not re.search(r"[A-Z]", password):
        return False
    if not re.search(r"[a-z]", password):
        return False
    if not re.search(r"\d", password):
        return False
    if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
        return False
    return True


def validate_age(age):
    """Validate that age is a reasonable integer value."""
    if not isinstance(age, int):
        raise TypeError("Age must be an integer")
    if age < 0:
        raise ValueError("Age cannot be negative")
    if age > 150:
        raise ValueError("Age cannot exceed 150")
    return True


def validate_username(username):
    """Validate username format.

    Rules:
    - 3 to 20 characters
    - Only alphanumeric characters and underscores
    - Must start with a letter
    """
    if not isinstance(username, str):
        raise TypeError("Username must be a string")
    if len(username) < 3:
        raise ValueError("Username must be at least 3 characters")
    if len(username) > 20:
        raise ValueError("Username must not exceed 20 characters")
    if not username[0].isalpha():
        raise ValueError("Username must start with a letter")
    if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", username):
        raise ValueError("Username can only contain alphanumeric characters and underscores")
    return True
