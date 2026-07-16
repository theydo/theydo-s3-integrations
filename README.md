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

### Treatment of `ownerEmail` property

1. If the property is not in the import json
   a) if the entity exists, owner is left as is
   b) if the entity does not exist it is created without owner
2. if the property is 'null' in the import json
   a) if the entity exists, owner is removed
   b) if the entity does not exist, it is created without owner
3. If the property is set in the import json
   a) the owner is updated to the user it maps to if such user exists in the workspace
   b) if no such user exists it is treated as not in the json (see 1.)

### Survey & Feedback Responses

Two formats import raw survey/feedback responses for AI mining:

- `THEYDO_SURVEY_RESPONSES_V1` — schema [`schemas/SurveyResponsesFile.schema.json`](schemas/SurveyResponsesFile.schema.json), example [`examples/survey_responses.json`](examples/survey_responses.json). Uses a `surveyMetadata` wrapper (`surveyName`, `surveyId`, `surveyFields`).
- `THEYDO_FEEDBACK_RESPONSES_V1` — schema [`schemas/FeedbackResponsesFile.schema.json`](schemas/FeedbackResponsesFile.schema.json), example [`examples/feedback_responses.json`](examples/feedback_responses.json). Uses a `feedbackMetadata` wrapper (`feedbackName`, `feedbackId`, `feedbackFields`).

The two formats are otherwise identical. Each declares its fields up front and then lists responses whose values reference those fields.

`surveyId` / `feedbackId` is a stable dedup/upsert key — re-uploading the same id updates the same data source. It is not validated; it just affects how the upload is applied.

`test-format` enforces the following. Rules 1–2 come from the JSON Schema itself; rules 3–7 are cross-field checks that JSON Schema cannot express:

1. The structure, required keys, and types declared in the schema, including that `format` matches the file's format const.
2. `responseDateTime` must be ISO-8601 in UTC ending in `Z` (e.g. `2026-01-01T00:00:00Z`). Naive datetimes and numeric offsets (e.g. `+02:00`) are rejected — convert to UTC.
3. `fieldName` must be non-empty on every field.
4. `tagGroupTitle` is required on any field whose `fieldType` is `TAG_GROUP`, and must match the name of an existing TheyDo tag group (case-insensitive) — a title that doesn't match falls back to `IGNORE`; at most one field may be `fieldType: PERSONA`.
5. Every field's `fieldId` must be unique within the metadata; a duplicate is rejected.
6. Every `responses[].responseFields[].fieldId` must reference a `fieldId` declared in the metadata fields.
7. Every `responses[].responseFields[].fieldId` must be unique within its response; a duplicate is rejected.

`fieldType` is one of `TEXT`, `TAG_GROUP`, `PERSONA`, `IGNORE`.

**Example**

```bash
s3tcli test-format \
  --format schemas/SurveyResponsesFile.schema.json \
  --file   examples/survey_responses.json

s3tcli test-format \
  --format schemas/FeedbackResponsesFile.schema.json \
  --file   examples/feedback_responses.json
```
