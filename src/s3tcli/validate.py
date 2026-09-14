from pathlib import Path
import json, re, jsonschema

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

_SUPPORT_LOG_CHECKS = {
    "THEYDO_SUPPORT_LOG_CONVERSATION_V1": True,
    "THEYDO_SUPPORT_LOG_TEXT_V1":         False,
}

def _run_extra_checks(data: object) -> None:
    if not isinstance(data, dict):
        return
    keys = _RESPONSES_CHECKS.get(data.get("format"))
    if keys:
        _check_responses_file(data, *keys)

    if data.get("format") in _SUPPORT_LOG_CHECKS:
        _check_support_log_file(data, has_conversation=_SUPPORT_LOG_CHECKS[data["format"]])

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

# --- Support-log checks -------------------------------------------------------
# The consumer trims sourceSystem.name / transcript.title / tag titles / actor
# before checking non-empty (Zod `.trim().min(1)`), so a whitespace-only string
# passes the JSON Schema's `minLength: 1` but is rejected downstream. Same for
# the actor/statement control-character rules, which the consumer's own docs
# call out as "not expressible in JSON Schema" (control chars incl. C1 and the
# Unicode line/paragraph separators U+2028/U+2029).
CONTROL_CHARACTER = re.compile("[\u0000-\u001f\u007f\u0080-\u009f\u2028\u2029]")

def _reject_blank(value: str, label: str) -> None:
    if not value.strip():
        raise ValueError(f"{label} must not be blank/whitespace-only")

def _check_support_log_file(data: dict, has_conversation: bool) -> None:
    source_system = data.get("sourceSystem", {})
    _reject_blank(source_system.get("name", ""), "sourceSystem.name")

    transcript = data.get("transcript", {})
    title = transcript.get("title")
    if title is not None:
        _reject_blank(title, "transcript.title")

    for tag in transcript.get("tags") or []:
        _reject_blank(tag.get("groupTitle", ""), "transcript.tags[].groupTitle")
        _reject_blank(tag.get("title", ""), "transcript.tags[].title")

    for persona in transcript.get("personas") or []:
        _reject_blank(persona, "transcript.personas[]")

    if not has_conversation:
        return

    any_non_blank_statement = False
    for turn in transcript.get("conversation") or []:
        actor = turn.get("actor", "")
        _reject_blank(actor, "transcript.conversation[].actor")
        if CONTROL_CHARACTER.search(actor):
            raise ValueError(
                "transcript.conversation[].actor must not contain control "
                "characters or Unicode line/paragraph separators"
            )
        statement = CONTROL_CHARACTER.sub(" ", turn.get("statement", ""))
        if statement.strip():
            any_non_blank_statement = True

    if not any_non_blank_statement:
        raise ValueError(
            "transcript.conversation must contain at least one non-empty statement"
        )
