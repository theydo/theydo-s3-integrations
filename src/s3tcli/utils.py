from pathlib import Path, PurePosixPath
import time

def unique_key(prefix: str, file_path: Path) -> str:
    """Return key like prefix/<epoch>-filename"""
    return str(PurePosixPath(prefix) / f"{int(time.time())}-{file_path.name}")
