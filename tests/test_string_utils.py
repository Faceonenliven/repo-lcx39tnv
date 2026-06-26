"""Comprehensive tests for the string_utils module."""

import pytest

from src.string_utils import (
    camel_to_snake,
    capitalize_words,
    count_consonants,
    count_vowels,
    is_palindrome,
    reverse,
    snake_to_camel,
    truncate,
)


class TestReverse:
    def test_basic(self):
        assert reverse("hello") == "olleh"

    def test_empty(self):
        assert reverse("") == ""

    def test_single_char(self):
        assert reverse("a") == "a"

    def test_palindrome(self):
        assert reverse("racecar") == "racecar"

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            reverse(123)


class TestCapitalizeWords:
    def test_basic(self):
        assert capitalize_words("hello world") == "Hello World"

    def test_already_capitalized(self):
        assert capitalize_words("Hello World") == "Hello World"

    def test_single_word(self):
        assert capitalize_words("python") == "Python"

    def test_empty(self):
        assert capitalize_words("") == ""

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            capitalize_words(42)


class TestCountVowels:
    def test_basic(self):
        assert count_vowels("hello") == 2

    def test_all_vowels(self):
        assert count_vowels("aeiou") == 5

    def test_no_vowels(self):
        assert count_vowels("rhythm") == 0

    def test_uppercase(self):
        assert count_vowels("HELLO") == 2

    def test_empty(self):
        assert count_vowels("") == 0

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            count_vowels(None)


class TestCountConsonants:
    def test_basic(self):
        assert count_consonants("hello") == 3

    def test_all_consonants(self):
        assert count_consonants("bcdfg") == 5

    def test_no_consonants(self):
        assert count_consonants("aeiou") == 0

    def test_with_spaces(self):
        assert count_consonants("hi there") == 4

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            count_consonants(123)


class TestIsPalindrome:
    def test_simple_palindrome(self):
        assert is_palindrome("racecar") is True

    def test_not_palindrome(self):
        assert is_palindrome("hello") is False

    def test_with_spaces(self):
        assert is_palindrome("A man a plan a canal Panama") is True

    def test_with_punctuation(self):
        assert is_palindrome("Was it a car or a cat I saw?") is True

    def test_empty(self):
        assert is_palindrome("") is True

    def test_single_char(self):
        assert is_palindrome("x") is True

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            is_palindrome(12321)


class TestTruncate:
    def test_no_truncation_needed(self):
        assert truncate("hi", 10) == "hi"

    def test_truncation(self):
        assert truncate("hello world", 8) == "hello..."

    def test_exact_length(self):
        assert truncate("hello", 5) == "hello"

    def test_very_short_max(self):
        assert truncate("hello", 2) == "he"

    def test_custom_suffix(self):
        assert truncate("hello world", 8, suffix="~") == "hello w~"

    def test_invalid_max_length(self):
        with pytest.raises(ValueError):
            truncate("hello", -1)

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            truncate(123, 5)


class TestSnakeToCamel:
    def test_basic(self):
        assert snake_to_camel("hello_world") == "helloWorld"

    def test_multiple_words(self):
        assert snake_to_camel("one_two_three") == "oneTwoThree"

    def test_single_word(self):
        assert snake_to_camel("hello") == "hello"

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            snake_to_camel(123)


class TestCamelToSnake:
    def test_basic(self):
        assert camel_to_snake("helloWorld") == "hello_world"

    def test_multiple_words(self):
        assert camel_to_snake("oneTwoThree") == "one_two_three"

    def test_single_word(self):
        assert camel_to_snake("hello") == "hello"

    def test_starts_with_upper(self):
        assert camel_to_snake("HelloWorld") == "hello_world"

    def test_invalid_type(self):
        with pytest.raises(TypeError):
            camel_to_snake(123)
