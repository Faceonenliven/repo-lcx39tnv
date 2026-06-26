"""Comprehensive tests for the validator module."""

import pytest

from src.validator import (
    is_strong_password,
    is_valid_email,
    is_valid_ip,
    is_valid_phone,
    is_valid_url,
    validate_age,
    validate_username,
)


class TestIsValidEmail:
    def test_valid_simple(self):
        assert is_valid_email("user@example.com") is True

    def test_valid_with_dots(self):
        assert is_valid_email("first.last@example.com") is True

    def test_valid_with_plus(self):
        assert is_valid_email("user+tag@example.com") is True

    def test_valid_subdomain(self):
        assert is_valid_email("user@sub.domain.com") is True

    def test_invalid_no_at(self):
        assert is_valid_email("userexample.com") is False

    def test_invalid_no_domain(self):
        assert is_valid_email("user@") is False

    def test_invalid_no_tld(self):
        assert is_valid_email("user@example") is False

    def test_invalid_spaces(self):
        assert is_valid_email("user @example.com") is False

    def test_non_string(self):
        assert is_valid_email(123) is False

    def test_empty_string(self):
        assert is_valid_email("") is False


class TestIsValidUrl:
    def test_valid_http(self):
        assert is_valid_url("http://example.com") is True

    def test_valid_https(self):
        assert is_valid_url("https://example.com") is True

    def test_valid_with_path(self):
        assert is_valid_url("https://example.com/path/to/page") is True

    def test_invalid_no_scheme(self):
        assert is_valid_url("example.com") is False

    def test_invalid_ftp(self):
        assert is_valid_url("ftp://example.com") is False

    def test_non_string(self):
        assert is_valid_url(None) is False

    def test_empty_string(self):
        assert is_valid_url("") is False


class TestIsValidPhone:
    def test_valid_10_digits(self):
        assert is_valid_phone("5551234567") is True

    def test_valid_with_dashes(self):
        assert is_valid_phone("555-123-4567") is True

    def test_valid_with_parens(self):
        assert is_valid_phone("(555) 123-4567") is True

    def test_valid_with_country_code(self):
        assert is_valid_phone("+15551234567") is True

    def test_invalid_too_short(self):
        assert is_valid_phone("12345") is False

    def test_invalid_letters(self):
        assert is_valid_phone("555-abc-defg") is False

    def test_non_string(self):
        assert is_valid_phone(5551234567) is False


class TestIsValidIp:
    def test_valid_localhost(self):
        assert is_valid_ip("127.0.0.1") is True

    def test_valid_standard(self):
        assert is_valid_ip("192.168.1.1") is True

    def test_valid_zeros(self):
        assert is_valid_ip("0.0.0.0") is True

    def test_valid_max(self):
        assert is_valid_ip("255.255.255.255") is True

    def test_invalid_octet_too_high(self):
        assert is_valid_ip("256.1.1.1") is False

    def test_invalid_too_few_octets(self):
        assert is_valid_ip("192.168.1") is False

    def test_invalid_too_many_octets(self):
        assert is_valid_ip("192.168.1.1.1") is False

    def test_invalid_leading_zeros(self):
        assert is_valid_ip("192.168.01.1") is False

    def test_invalid_non_numeric(self):
        assert is_valid_ip("192.168.a.1") is False

    def test_non_string(self):
        assert is_valid_ip(12345) is False

    def test_empty_string(self):
        assert is_valid_ip("") is False


class TestIsStrongPassword:
    def test_valid_strong(self):
        assert is_strong_password("Str0ng!Pass") is True

    def test_too_short(self):
        assert is_strong_password("Ab1!") is False

    def test_no_uppercase(self):
        assert is_strong_password("weakpass1!") is False

    def test_no_lowercase(self):
        assert is_strong_password("WEAKPASS1!") is False

    def test_no_digit(self):
        assert is_strong_password("WeakPass!!") is False

    def test_no_special(self):
        assert is_strong_password("WeakPass11") is False

    def test_non_string(self):
        assert is_strong_password(12345678) is False

    def test_empty(self):
        assert is_strong_password("") is False


class TestValidateAge:
    def test_valid_age(self):
        assert validate_age(25) is True

    def test_zero(self):
        assert validate_age(0) is True

    def test_max_valid(self):
        assert validate_age(150) is True

    def test_negative(self):
        with pytest.raises(ValueError, match="cannot be negative"):
            validate_age(-1)

    def test_too_old(self):
        with pytest.raises(ValueError, match="cannot exceed 150"):
            validate_age(151)

    def test_non_integer(self):
        with pytest.raises(TypeError):
            validate_age("25")

    def test_float(self):
        with pytest.raises(TypeError):
            validate_age(25.5)


class TestValidateUsername:
    def test_valid_simple(self):
        assert validate_username("john") is True

    def test_valid_with_numbers(self):
        assert validate_username("user123") is True

    def test_valid_with_underscore(self):
        assert validate_username("user_name") is True

    def test_valid_min_length(self):
        assert validate_username("abc") is True

    def test_valid_max_length(self):
        assert validate_username("a" * 20) is True

    def test_too_short(self):
        with pytest.raises(ValueError, match="at least 3"):
            validate_username("ab")

    def test_too_long(self):
        with pytest.raises(ValueError, match="not exceed 20"):
            validate_username("a" * 21)

    def test_starts_with_number(self):
        with pytest.raises(ValueError, match="start with a letter"):
            validate_username("1user")

    def test_starts_with_underscore(self):
        with pytest.raises(ValueError, match="start with a letter"):
            validate_username("_user")

    def test_special_characters(self):
        with pytest.raises(ValueError, match="alphanumeric"):
            validate_username("user@name")

    def test_non_string(self):
        with pytest.raises(TypeError):
            validate_username(123)
