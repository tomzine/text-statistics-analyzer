from pathlib import Path


def load_text(file_path: Path)-> str | None:
    """Read a text file safely."""


    try:
        text = file_path.read_text(encoding="utf-8")
        return text
    except OSError as error:
        print(f"file error : {error}")
        return None
