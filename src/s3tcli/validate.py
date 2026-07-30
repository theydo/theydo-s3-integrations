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

    seen_ids: set = set()
    persona = 0
    for f in fields:
        field_id = f.get("fieldId")
        if field_id in seen_ids:
            raise ValueError(f"Duplicate fieldId in metadata: {field_id}")
        seen_ids.add(field_id)

        # fieldType defaults to TEXT when omitted (mirrors the consumer).
        field_type = f.get("fieldType", "TEXT")
        # Column headers cannot be empty (consumer: validateAiDataSourceMetadata).
        if not f.get("fieldName"):
            raise ValueError("Column headers cannot be empty")
        # Consumer trims tagGroupTitle before checking non-empty, so a
        # whitespace-only title is equivalent to a missing one.
        if field_type == "TAG_GROUP" and not (f.get("tagGroupTitle") or "").strip():
            raise ValueError(
                "Column with type TAG_GROUP needs to have tagGroupTitle assigned"
            )
        if field_type == "PERSONA":
            persona += 1

    if persona > 1:
        raise ValueError("There can be only one column assigned to PERSONA type")

    for r in data.get("responses", []):
        seen_response_field_ids: set = set()
        for rf in r.get("responseFields", []):
            field_id = rf.get("fieldId")
            if field_id not in seen_ids:
                raise ValueError(
                    f"Response '{r.get('responseId')}' references unknown "
                    f"fieldId '{field_id}'"
                )
            if field_id in seen_response_field_ids:
                raise ValueError(f"Duplicate fieldId in responseFields: {field_id}")
            seen_response_field_ids.add(field_id)
