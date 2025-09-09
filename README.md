# TheyoDo x AWS S3

As a TheyDo customer you can establish an S3 integration
to automatically ingest data from any source application 
as long as it adheres to the specified json schemas.

This repository serves as documentation of:
- available [schemas](schema/)
- [examples](examples/) and example use cases
- [aws cli](#aws-cli) commands for necessary configuration
- a [cli tool](#s3tcli) to test authentication, validate and upload files

## Requirements 
- AWS Account - either own or shared by TheyDo
- S3 bucket info including prefix
- S3 role info, particularly role_arn and external_id

## AWS CLI

### Profile configuration
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
  --format      schema/SolutionsFile.schema.json \
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

---

_Notes: Paths above are relative to the repository root._


