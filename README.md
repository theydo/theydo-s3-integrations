# TheyDo x AWS S3

As a TheyDo customer you can setup an S3 integration
to automatically ingest data from any source application
as long as it adheres to the specified json schemas.

This repository serves as documentation of:

- available [schemas](schemas/)
- [examples](examples/) and example use cases
- [aws cli](#aws-cli) commands for necessary configuration
- a [cli tool](#s3tcli) to test authentication, validate and upload files

## Required Configuration Variables

### AWS Account & Authentication

- **AWS Account** - your AWS account, share your **account id** with us to get started. If AWS is not yet part of your infrastructure, reach out and we will be able to provide a solution.
- **AWS Region** - Target region (typically `eu-west-1`) - shared by TheyDo
- **Role ARN** - The Amazon Resource Name of the role to assume (format: `arn:aws:iam::<account>:role/<name>`) - shared by TheyDo
    - this role allows an external account to access 'Bucket Name/Bucket Prefix'
- **External ID** - Required by the role's trust policy for additional security - shared by TheyDo

### S3 Bucket Configuration

- **Bucket Name** - Target S3 bucket name (e.g., `theydo-ext-dev-eu-west-1`) - shared by TheyDo
- **Bucket Prefix** - Key prefix/folder path within the bucket where files will be uploaded - shared by TheyDo

### Role permissions

Role permissions are strictly limited to what is needed to upload files to the bucket prefix.
This means that tools like [S3 Browser](https://s3browser.com/) will not be successful in connecting to the bucket as they require a bigger permission scope.

## AWS CLI

### Profile configuration example for static credentials

You need to know your <aws_access_key_id> and <aws_secret_access_key> to provide in the first step.

```
aws configure --profile <source_profile>
aws configure set region eu-west-1 --profile <source_profile>

aws configure set source_profile <source_profile> --profile <role_profile>
aws configure set region eu-west-1 --profile <role_profile>
aws configure set role_arn <role_arn> --profile <role_profile>
aws configure set external_id <external_id> --profile <role_profile>
```

### Profile verification

```
aws sts get-caller-identity --profile <role_profile>
```

### Commands

```
aws s3 ls s3://<bucket_name>/<bucket_prefix> --summarize --profile jb-test-role
aws s3 cp <local_file_name> s3://<bucket_name>/<bucket_prefix>/<remote_file_name> --profile <role_profile>
```

## S3TCLI

A lightweight command‑line helper for:

- validating JSON files against a JSON Schema
- testing that an **AssumeRole** configuration works
- (optionally) validating again and uploading to Amazon S3

---

### Quick start

```bash
make            # boots an isolated Python 3.12 env and installs the CLI
s3tcli --help
```

The commands below require the configuration of a profile as described [above](#profile-configuration).

---

### Commands

#### 1) `test-format` — Validate a JSON file

**Arguments**

- `--format PATH` — Path to the JSON Schema file.
- `--file PATH` — Path to the JSON document to validate.

**Example**

```bash
s3tcli test-format \
  --format schema/SolutionsFile.schema.json \
  --file   examples/solutions.json
```

---

#### 2) `test-role` — Verify that AssumeRole works

**Arguments**

- `--role ARN` — Role to assume (e.g., `arn:aws:iam::<account>:role/<name>`).
- `--external-id STRING` — External ID required by the role’s trust policy.
- `--profile NAME` — Local AWS credentials profile to use.
- `--region CODE` — AWS region (e.g., `eu-west-1`).

**Example**

```bash
s3tcli test-role \
  --role        arn:aws:iam::830965594115:role/.N2Y1M2siZ2QtOYU3MS05YzUzLWI2OGYtODVkZmU9ZmVlY2Yy. \
  --external-id 1f377dc0-a39a-493a-ae61-a32e9b64d4d7 \
  --profile     kristjan-s3-test \
  --region      eu-west-1
```

_On success, the CLI prints the caller identity for the assumed role._

---

#### 3) `test-upload` — Validate then upload to S3

**Arguments**

- `--bucket NAME` — Target S3 bucket (e.g., `theydo-ext-dev-eu-west-1`).
- `--prefix KEYPREFIX` — Key prefix/folder under which to upload.
- `--file PATH` — Path to the JSON document to upload.
- `--format PATH` — Path to the JSON Schema used for validation.
- `--role ARN` — Role to assume.
- `--external-id STRING` — External ID for the role.
- `--profile NAME` — AWS credentials profile.
- `--region CODE` — AWS region.

**Example**

```bash
s3tcli test-upload \
  --bucket      theydo-ext-dev-eu-west-1 \
  --prefix      .N2Y1M2siZ2QtOYU3MS05YzUzLWI2OGYtODVkZmU9ZmVlY2Yy. \
  --file        examples/solutions.json \
  --format      schemas/SolutionsFile.schema.json \
  --role        arn:aws:iam::830965594115:role/.N2Y1M2siZ2QtOYU3MS05YzUzLWI2OGYtODVkZmU9ZmVlY2Yy. \
  --external-id 1f377dc0-a39a-493a-ae61-a32e9b64d4d7 \
  --profile     kristjan-s3-test \
  --region      eu-west-1
```

The CLI composes a key like:

```
.N2Y1M2siZ2QtOYU3MS05YzUzLWI2OGYtODVkZmU9ZmVlY2Yy./1691425012-solutions.json
```

…and prints “Upload successful” on completion.

## Specific Schema Ingestion Rules

### Import Key and Overrides

Applies to `THEYDO_INSIGHTS_V1`, `THEYDO_OPPORTUNITIES_V1`, and `THEYDO_SOLUTIONS_V1`.

These are JSON formats, and the rules below rely on that: JSON can distinguish a key that is omitted from one that is explicitly `null`. A CSV-based import has no way to express an omitted field — every row carries a value for every column — so CSV imports always set every field.

Records are matched by `importKey`, which is unique per workspace: an unknown `importKey` creates the entity, a known one updates it. Every record must include `importKey` and `title` — `title` is required on every import, including re-imports. All other fields are optional and follow the rule below.

| In your JSON | On create              | On update (existing `importKey`)                      |
| ------------ | ---------------------- | ----------------------------------------------------- |
| key omitted  | field empty / no links | **left unchanged** — existing data preserved          |
| `null`       | field empty / no links | **cleared** — value removed / all links removed       |
| value        | set                    | **replaced** — a list replaces the linked set exactly |

- `""` and `0` are values, not clears — they are stored as-is.
- For list fields, `null` and `[]` are equivalent: both remove all links.

### Fields with special matching behavior

| Field                      | Behavior                                                                                                                                                                                                                                                                                                                       |
| -------------------------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `ownerEmail`               | Matched against existing workspace users by email. Imports **never create users**. If the email doesn't match any user, the current owner is left unchanged (a typo never wipes ownership); on create the entity simply has no owner. `null` clears the owner; omitted leaves it.                                              |
| `personas` (insights only) | Takes full persona share URLs (`…/p/<shareKey>`), matched against **existing** personas in the workspace. Imports **never create personas**. Unknown personas are dropped from the list. If a non-empty list matches nothing at all, existing persona links are left untouched — send `[]` or `null` to explicitly unlink all. |
| `status`, `type`           | Matched against an existing category by title, **or a new category is created** if no match exists.                                                                                                                                                                                                                            |
| `tags`, `groupTags`        | One merged set: bare `tags` go into the default "Tags" group. "Omitted = leave unchanged" holds only when **both** are omitted — sending either one replaces the entire merged set. Missing tags and tag groups **are created**.                                                                                               |
| `empathyScore`             | Rounded to one decimal. A value outside `[-2, 2]` is ignored (treated as omitted — it neither fails the file nor changes the stored score).                                                                                                                                                                                    |

The same principle holds across all import formats, including the survey & feedback formats below: **users and personas are matched, never created** by an import, while **tags, tag groups, and categories are created** when missing. The survey & feedback formats match personas by a different mechanism (a best-effort AI match — see [Field types](#field-types)) but likewise never create one.

### Survey & Feedback Responses

Two formats import raw survey/feedback responses for AI mining:

- `THEYDO_SURVEY_RESPONSES_V1` — schema [`schemas/SurveyResponsesFile.schema.json`](schemas/SurveyResponsesFile.schema.json), example [`examples/survey_responses.json`](examples/survey_responses.json). Uses a `surveyMetadata` wrapper (`surveyName`, `surveyId`, `surveyFields`).
- `THEYDO_FEEDBACK_RESPONSES_V1` — schema [`schemas/FeedbackResponsesFile.schema.json`](schemas/FeedbackResponsesFile.schema.json), example [`examples/feedback_responses.json`](examples/feedback_responses.json). Uses a `feedbackMetadata` wrapper (`feedbackName`, `feedbackId`, `feedbackFields`).

The two formats are otherwise identical. Each declares its fields up front and then lists responses whose values reference those fields.

`surveyId` / `feedbackId` is a stable dedup/upsert key — re-uploading the same id updates the same data source. It is not validated; it just affects how the upload is applied.

#### Field types

Each declared field has a `fieldType` of `TEXT`, `TAG_GROUP`, `PERSONA`, or `IGNORE` (default `TEXT`):

- **`TEXT`** — imported as plain text, no special handling.
- **`TAG_GROUP`** — each response's value for this field is coded as a tag inside the tag group named by the field's `tagGroupTitle`. A _tag group_ is a named category of tags used to classify feedback (e.g. a "Sentiment" tag group containing tags like Positive/Neutral/Negative). `tagGroupTitle` is matched case-insensitively against tag groups that already exist in the target workspace; if no match is found, **a new tag group is created automatically with that exact title** — so a typo in `tagGroupTitle` silently creates a stray tag group rather than raising an error or being ignored.
- **`PERSONA`** — each response's value (an existing customer/user segment defined in the workspace, e.g. "Power User" or "New Customer") is given to TheyDo's AI, together with the workspace's existing personas, as a hint for which persona each response's quote should be linked to. Unlike `TAG_GROUP`, this is a best-effort AI match against existing personas, not an exact/deterministic lookup — there's no guaranteed match and no persona is created if there isn't a good one. At most one field per file may use `fieldType: PERSONA`.
- **`IGNORE`** — the column is present in the source data but is skipped on import.

#### `convertAllRowsToQuotes`

An optional boolean on `surveyMetadata` / `feedbackMetadata` that controls how TheyDo's AI turns responses into _quotes_ (the atomic unit of customer feedback in TheyDo):

- **`false` (default)** — the AI reads each response's text and decides what to extract, producing zero, one, or several quotes per response. Best for long free-text or transcript-style answers.
- **`true`** — skips AI extraction entirely and imports every response row as exactly one quote, verbatim. Best when each response is already a short, atomic answer (e.g. a single survey question) that doesn't need AI interpretation.

#### Validation rules

`test-format` enforces the following. Rules 1–2 come from the JSON Schema itself; rules 3–7 are cross-field checks that JSON Schema cannot express:

1. The structure, required keys, and types declared in the schema, including that `format` matches the file's format const.
2. `responseDateTime` must be ISO-8601 in UTC ending in `Z` (e.g. `2026-01-01T00:00:00Z`). Naive datetimes and numeric offsets (e.g. `+02:00`) are rejected — convert to UTC.
3. `fieldName` must be non-empty on every field.
4. `tagGroupTitle` is required on any field whose `fieldType` is `TAG_GROUP`. At most one field may be `fieldType: PERSONA`.
5. Every field's `fieldId` must be unique within the metadata; a duplicate is rejected.
6. Every `responses[].responseFields[].fieldId` must reference a `fieldId` declared in the metadata fields.
7. Every `responses[].responseFields[].fieldId` must be unique within its response; a duplicate is rejected.

Note: the schema declares `additionalProperties: false`, so `test-format` rejects unknown keys — this is stricter than actual ingest, which silently ignores unknown keys rather than rejecting the file. Run `test-format` to catch typos before upload; ingest itself won't flag them.

**Example**

```bash
s3tcli test-format \
  --format schemas/SurveyResponsesFile.schema.json \
  --file   examples/survey_responses.json

s3tcli test-format \
  --format schemas/FeedbackResponsesFile.schema.json \
  --file   examples/feedback_responses.json
```

### Support Logs

**One JSON file per ticket or call.** Each file becomes exactly one Data Hub source, and its
transcript body is written out as a plain-text file for Journey AI to read. Two formats are
available — pick one per customer based on whether their export has speaker turns:

- `THEYDO_SUPPORT_LOG_CONVERSATION_V1` (prefer) — schema [`schemas/SupportLogConversationFile.schema.json`](schemas/SupportLogConversationFile.schema.json), example [`examples/support_log_conversation.json`](examples/support_log_conversation.json). Body is an ordered array of `{ actor, statement }` turns, flattened to `actor: statement` lines. Preferred because the prompt can cleanly exclude agent speech when extracting quotes.
- `THEYDO_SUPPORT_LOG_TEXT_V1` (fallback) — schema [`schemas/SupportLogTextFile.schema.json`](schemas/SupportLogTextFile.schema.json), example [`examples/support_log_text.json`](examples/support_log_text.json). Body is a single `text` blob, passed through verbatim. Offer this only when mapping to turns would block the integration — quote quality degrades without speaker prefixes. A connection can enable both formats at once.

Both formats share the same envelope:

| Field | Req. | Rules | Notes |
|---|---|---|---|
| `format` | yes | Exactly `THEYDO_SUPPORT_LOG_CONVERSATION_V1` or `THEYDO_SUPPORT_LOG_TEXT_V1` | Routes the file to the right converter and versions the contract. |
| `sourceSystem.id` | yes | `[A-Za-z0-9.-]`, 1–128 chars | Stable id of the origin system (e.g. Zendesk, Salesforce). Namespaces `transcript.id` so two systems can both emit ticket "12345" without colliding. |
| `sourceSystem.name` | yes | Non-empty (after trimming) | Human label, e.g. "Zendesk EU support". |
| `transcript.id` | yes | `[A-Za-z0-9.-]`, 1–128 chars; stable across re-exports | The idempotency key, combined with `sourceSystem.id`. Re-sending the same pair is a silent no-op, not an update — a correction needs a new id. |
| `transcript.title` | no | Non-empty (after trimming) if present | Data Hub source title; falls back to `transcript.id`. |
| `transcript.occurredAt` | yes | ISO-8601 in UTC ending in `Z` | When the interaction happened, not when it was exported. Naive datetimes and numeric offsets are rejected. |
| `transcript.conversation[]` | CONVERSATION only | 1–5000 turns; at least one non-blank `statement` | Turn order is meaningful. |
| `transcript.conversation[].actor` | yes | Non-empty (after trimming), max 64 chars, no control characters or Unicode line/paragraph separators | `agent`/`customer` etc. — the prompt uses this to skip agent speech. |
| `transcript.conversation[].statement` | yes | Any string; control characters and line/paragraph separators are replaced with a space on flattening | Individual turns may be blank as long as at least one in the file is not. |
| `transcript.conversation[].occurredAt` | no | ISO-8601 in UTC ending in `Z` | Accepted and kept as a `[timestamp]` prefix on the flattened line; not used for anything else yet. |
| `transcript.text` | TEXT only | Non-empty, max 1,000,000 chars | Passed through verbatim. |
| `transcript.tags[]` | no | Max 50; `{ groupTitle, title }`, both non-empty after trimming, `groupTitle` max 200 chars | Attaches to the Data Hub source, not to individual quotes. Unknown groups/titles are created. |
| `transcript.personas[]` | no | Max 20; non-empty persona **names** | Matched case-insensitively against existing personas; never created, unmatched names are dropped. |

**Give support logs their own connection.** If any JSON format is enabled on a connection, the
whole connection is processed as JSON — mixing support logs into a connection that also carries a
CSV format breaks the CSV path. A support-log-only connection also gets a dedicated,
higher-throughput queue; mixing formats keeps it on the shared, capped one.

#### Validation rules

`test-format` enforces the following. Rule 1 comes from the JSON Schema itself; the rest are
cross-field/runtime checks the JSON Schema cannot express, added to `validate.py` to mirror what
the consumer actually enforces:

1. The structure, required keys, and types declared in the schema, including that `format`
   matches the file's format const, and (CONVERSATION only) that `conversation` has 1–5000 items.
2. `sourceSystem.name`, `transcript.title` (if present), `transcript.tags[].groupTitle`,
   `transcript.tags[].title`, and each `transcript.personas[]` entry must not be whitespace-only.
   **Discrepancy:** the consumer trims these before checking non-empty, so a string of only spaces
   satisfies the JSON Schema's `minLength: 1` but is rejected downstream — `test-format` closes
   that gap.
3. (CONVERSATION only) `transcript.conversation[].actor` must not be whitespace-only, and must not
   contain control characters or the Unicode line/paragraph separators U+2028/U+2029.
   **Discrepancy:** the consumer's own docs state this rule "is not expressible in JSON Schema, so
   it will not show up in producer-side validation" — `test-format` adds it explicitly.
4. (CONVERSATION only) at least one `statement` in `transcript.conversation[]` must be non-blank
   after control characters are replaced with a space — an all-blank conversation (or one whose
   only content is control characters) would otherwise create a live, empty Data Hub source.

**Known, accepted gap — not fixed here:** both schemas declare `additionalProperties: false`, so
`test-format` rejects unknown keys, but real ingest silently drops them instead of rejecting the
file (a misspelled `tagz` produces an untagged ticket with no error). `test-format` is
intentionally stricter than ingest here, exactly as with the survey/feedback formats above — run it
to catch typos before upload, since ingest itself won't flag them.

**Example**

```bash
s3tcli test-format \
  --format schemas/SupportLogConversationFile.schema.json \
  --file   examples/support_log_conversation.json

s3tcli test-format \
  --format schemas/SupportLogTextFile.schema.json \
  --file   examples/support_log_text.json
```
