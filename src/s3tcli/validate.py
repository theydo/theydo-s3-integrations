from pathlib import Path
import json, jsonschema

def validate_json(file: Path, schema: Path) -> None:
    jsonschema.validate(
        json.loads(file.read_text()),
        json.loads(schema.read_text())
    )
