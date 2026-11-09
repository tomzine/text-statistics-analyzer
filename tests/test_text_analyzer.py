import pytest

from analyzer import load_text,normalize_words, calculate_statistics


def test_normalize_words():
    text = "Python is AMAZING!"

    result = normalize_words(text)

    assert result == ["python", "is", "amazing"]


def test_empty_text():
    text =""

    result = normalize_words(text)

    assert result == []

def test_calculate_statistics():
    text = "Ai is amazing.\n Python is powerfull!"

    words = normalize_words(text)
    results = calculate_statistics(text, words)

    assert results["number_of_lines"] == 2
    assert results["number_of_words"] == 6
    assert results["number_of_sentences"] == 2
    assert results["number_of_ai"] == 1
    assert results["unique_words"] == 5
    assert results["longest_word"] == "powerfull"
    assert results["shortest_word"] == "ai"
    assert results["averg_len"] == pytest.approx(28/6)


def test_empty_statistics():
    text = ""
    words  = normalize_words(text)

    results = calculate_statistics(text, words)

    assert results["number_of_lines"] == 0
    assert results["number_of_words"] == 0
    assert results["number_of_sentences"] == 0
    assert results["number_of_ai"] == 0
    assert results["unique_words"] == 0
    assert results["longest_word"] == "N/A"
    assert results["shortest_word"] == "N/A"
    assert results["averg_len"] == 0


def test_load_text(tmp_path):
    file_path = tmp_path / "sample.txt"

    file_path.write_text("Hello Python", encoding="utf-8")

    result = load_text(file_path)

    assert result == "Hello Python"