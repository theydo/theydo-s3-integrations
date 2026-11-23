"""ingestMode on the interview formats. Run with: python -m unittest discover -s tests"""
import copy
import json
import tempfile
import unittest
from pathlib import Path

import jsonschema

from s3tcli.validate import _run_extra_checks, validate_json

ROOT = Path(__file__).resolve().parent.parent
FORMATS = {
    "conversation": (
        ROOT / "schemas/InterviewConversationFile.schema.json",
        ROOT / "examples/interview_conversation.json",
    ),
    "text": (
        ROOT / "schemas/InterviewTextFile.schema.json",
        ROOT / "examples/interview_text.json",
    ),
}


def _payload(example: Path, ingest_mode: object = None, *, set_mode: bool) -> dict:
    data = json.loads(example.read_text())
    data.pop("ingestMode", None)
    if set_mode:
        data["ingestMode"] = ingest_mode
    return data


class InterviewIngestModeTest(unittest.TestCase):
    def _validate(self, schema: Path, data: dict) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            file = Path(tmp) / "interview.json"
            file.write_text(json.dumps(data))
            validate_json(file, schema)

    def test_valid_values_accepted(self):
        for name, (schema, example) in FORMATS.items():
            for mode in ("AUTO", "MANUAL_REVIEW"):
                with self.subTest(format=name, ingestMode=mode):
                    self._validate(schema, _payload(example, mode, set_mode=True))

    def test_absent_accepted(self):
        for name, (schema, example) in FORMATS.items():
            with self.subTest(format=name):
                self._validate(schema, _payload(example, set_mode=False))

    def test_invalid_values_rejected_by_schema(self):
        for name, (schema, example) in FORMATS.items():
            for mode in ("manual_review", "Auto", "", None, 1):
                with self.subTest(format=name, ingestMode=mode):
                    with self.assertRaises(jsonschema.ValidationError):
                        self._validate(schema, _payload(example, mode, set_mode=True))

    def test_invalid_values_rejected_by_extra_check(self):
        # The extra check holds on its own, e.g. against an older schema copy without the enum.
        for name, (_, example) in FORMATS.items():
            for mode in ("manual_review", "SKIP", None):
                with self.subTest(format=name, ingestMode=mode):
                    with self.assertRaisesRegex(
                        ValueError, r"ingestMode must be one of AUTO, MANUAL_REVIEW"
                    ):
                        _run_extra_checks(_payload(example, mode, set_mode=True))

    def test_examples_cover_both_present_and_absent(self):
        conversation = json.loads(FORMATS["conversation"][1].read_text())
        text = json.loads(FORMATS["text"][1].read_text())
        self.assertEqual(conversation.get("ingestMode"), "MANUAL_REVIEW")
        self.assertNotIn("ingestMode", text)
        for schema, example in FORMATS.values():
            validate_json(example, schema)

    def test_support_logs_unaffected(self):
        # ingestMode is interview-only; the extra check does not apply to support logs.
        data = json.loads((ROOT / "examples/support_log_conversation.json").read_text())
        _run_extra_checks(copy.deepcopy(data))


if __name__ == "__main__":
    unittest.main()
