"""String utility module providing common string operations."""


def reverse(s):
    """Reverse a string."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s[::-1]


def capitalize_words(s):
    """Capitalize the first letter of each word."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return s.title()


def count_vowels(s):
    """Count the number of vowels in a string."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return sum(1 for c in s.lower() if c in "aeiou")


def count_consonants(s):
    """Count the number of consonants in a string."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    return sum(1 for c in s.lower() if c.isalpha() and c not in "aeiou")


def is_palindrome(s):
    """Check if a string is a palindrome (ignoring case and spaces)."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    cleaned = "".join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]


def truncate(s, max_length, suffix="..."):
    """Truncate a string to max_length, appending suffix if truncated."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    if not isinstance(max_length, int) or max_length < 0:
        raise ValueError("max_length must be a non-negative integer")
    if len(s) <= max_length:
        return s
    if max_length <= len(suffix):
        return s[:max_length]
    return s[: max_length - len(suffix)] + suffix


def snake_to_camel(s):
    """Convert snake_case string to camelCase."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    components = s.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def camel_to_snake(s):
    """Convert camelCase string to snake_case."""
    if not isinstance(s, str):
        raise TypeError("Input must be a string")
    result = []
    for i, c in enumerate(s):
        if c.isupper() and i > 0:
            result.append("_")
        result.append(c.lower())
    return "".join(result)
