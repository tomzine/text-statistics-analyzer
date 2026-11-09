import string


def normalize_words(text: str) -> list[str] | None:
    """Clean and normalize words."""

    
    words = [
        word.strip(string.punctuation).casefold()
        for word in text.split()
    ]

    words = [word for word in words if word]
    return words