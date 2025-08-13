from pathlib import Path
import typer, sys, boto3
from .validate import validate_json
from .aws import assume_role
from .utils import unique_key

app = typer.Typer(help="S3TCLI – validate JSON and upload to S3")

# shared options
role_opt    = typer.Option(..., "--role", help="IAM role ARN to assume")
extid_opt   = typer.Option(..., "--external-id", help="External ID")
profile_opt = typer.Option(None, "--profile", help="AWS profile (default)")
region_opt  = typer.Option(None, "--region", help="AWS region")

@app.command("test-format")
def cmd_format(
    format: Path = typer.Option(..., exists=True, dir_okay=False, help="JSON-Schema"),
    file:   Path = typer.Option(..., exists=True, dir_okay=False, help="JSON file")
):
    "Validate file against schema"
    try:
        validate_json(file, format)
        typer.echo("✔ JSON matches schema")
    except Exception as e:
        typer.echo(f"✖ Validation error: {e}", err=True); sys.exit(1)

@app.command("test-role")
def cmd_role(
    role: str = role_opt, external_id: str = extid_opt,
    profile: str | None = profile_opt, region: str | None = region_opt
):
    "Check AssumeRole"
    try:
        cfg = assume_role(role, external_id, profile, region)
        arn = boto3.client("sts", **cfg).get_caller_identity()["Arn"]
        typer.echo(f"✔ Caller identity: {arn}")
    except Exception as e:
        typer.echo(f"✖ AssumeRole failed: {e}", err=True); sys.exit(1)

@app.command("test-upload")
def cmd_upload(
    bucket: str = typer.Option(..., "--bucket"),
    prefix: str = typer.Option(..., "--prefix"),
    file:   Path = typer.Option(..., exists=True, dir_okay=False),
    format: Path | None = typer.Option(None, "--format", exists=True, dir_okay=False,
                                       help="Optional schema"),
    role: str = role_opt, external_id: str = extid_opt,
    profile: str | None = profile_opt, region: str | None = region_opt
):
    "Optionally validate then upload"
    if format:
        try: validate_json(file, format)
        except Exception as e:
            typer.echo(f"✖ Validation error: {e}", err=True); sys.exit(1)
    try:
        cfg = assume_role(role, external_id, profile, region)
        boto3.client("s3", **cfg).upload_file(
            str(file), bucket, unique_key(prefix, file)
        )
        typer.echo("✔ Upload successful")
    except Exception as e:
        typer.echo(f"✖ Upload failed: {e}", err=True); sys.exit(1)

if __name__ == "__main__":
    app()
