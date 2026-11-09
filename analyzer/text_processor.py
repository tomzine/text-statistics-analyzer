import string


def normalize_words(text: str) -> list[str] | None:
    """Clean and normalize words."""

    
    words = [
        word.strip(string.punctuation).casefold()
        for word in text.split()
    ]

    words = [word for word in words if word]
    return words


def count_word_occurrences(words: list[str], search_term: str) -> int:
    """Count how many times a word appears in the text."""

    search_term = search_term.strip().strip(string.punctuation).casefold()

    if not search_term:
        return 0

    return words.count(search_term)
