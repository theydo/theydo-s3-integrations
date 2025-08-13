from __future__ import annotations
import boto3, os

def assume_role(role_arn: str, external_id: str,
                profile: str | None, region: str | None):
    session = boto3.Session(profile_name=profile or None,
                            region_name=region or None)
    creds = session.client("sts").assume_role(
        RoleArn=role_arn,
        RoleSessionName="s3tcliSession",
        ExternalId=external_id,
    )["Credentials"]
    return dict(
        aws_access_key_id     = creds["AccessKeyId"],
        aws_secret_access_key = creds["SecretAccessKey"],
        aws_session_token     = creds["SessionToken"],
        region_name           = region
            or session.region_name
            or os.getenv("AWS_REGION", "eu-west-1"),
    )
