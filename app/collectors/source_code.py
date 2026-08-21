from pathlib import Path

def collect_source_code(file_path: str | Path) -> dict:
    """Reads a Python source file and returns its content and metadata."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    with open(path, "r", encoding="utf-8") as f:
        content = f.read()
    
    return {
        "content": content,
        "source_path": str(path)
    }
