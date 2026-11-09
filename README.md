
# Text Statistics Analyzer

A Python application that analyzes text files
and calculates useful statistics.

## Features

- Count lines, words and characters
- Count sentences
- Count AI occurrences
- Find unique words
- Find the longest and shortest words
- Calculate average word length
- Find the three longest words
- Display the five most frequent words
- Handle file errors

## Project Structure

```text
foundtion/
├── analyzer/
│   ├── __init__.py
│   ├── file_handler.py
│   ├── text_processor.py
│   └── statistics.py
├── tests/
│   └── test_text_analyzer.py
├── main.py
├── text.txt
└── pyproject.toml
```

## Requirements

- Python 3.12+
- uv

## Installation

```bash
uv sync
```

## Run the application

```bash
uv run main.py
```

## Run tests

```bash
uv run pytest -v
```

## Technologies

- Python
- pathlib
- collections.Counter
- pytest
- Git and GitHub
