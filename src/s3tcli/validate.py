from pathlib import Path
import json, jsonschema

def validate_json(file: Path, schema: Path) -> None:
    data = json.loads(file.read_text())
    jsonschema.validate(data, json.loads(schema.read_text()))
    _run_extra_checks(data)

# --- Format-specific cross-field checks --------------------------------------
# Constraints the consumer enforces (via Zod .refine / downstream) that JSON
# Schema cannot express. Keyed by the file's `format`; existing formats have no
# extra checks and are left untouched.
_RESPONSES_CHECKS = {
    "THEYDO_SURVEY_RESPONSES_V1":   ("surveyMetadata",   "surveyFields"),
    "THEYDO_FEEDBACK_RESPONSES_V1": ("feedbackMetadata", "feedbackFields"),
}

def _run_extra_checks(data: object) -> None:
    if not isinstance(data, dict):
        return
    keys = _RESPONSES_CHECKS.get(data.get("format"))
    if keys:
        _check_responses_file(data, *keys)

def _check_responses_file(data: dict, metadata_key: str, fields_key: str) -> None:
    fields = data.get(metadata_key, {}).get(fields_key, [])
    declared_ids = {f.get("fieldId") for f in fields}

    persona = date = 0
    for f in fields:
        # fieldType defaults to TEXT when omitted (mirrors the consumer).
        field_type = f.get("fieldType", "TEXT")
        # Column headers cannot be empty (consumer: validateAiDataSourceMetadata).
        if not f.get("fieldName"):
            raise ValueError("Column headers cannot be empty")
        if field_type == "TAG_GROUP" and not f.get("tagGroupId"):
            raise ValueError(
                "Column with type TAG_GROUP needs to have tagGroupId assigned"
            )
        if field_type == "PERSONA":
            persona += 1
        elif field_type == "DATE":
            date += 1

    if persona > 1:
        raise ValueError("There can be only one column assigned to PERSONA type")
    if date > 1:
        raise ValueError("There can be only one column assigned to DATE type")

    for r in data.get("responses", []):
        for rf in r.get("responseFields", []):
            if rf.get("fieldId") not in declared_ids:
                raise ValueError(
                    f"Response '{r.get('responseId')}' references unknown "
                    f"fieldId '{rf.get('fieldId')}'"
                )
