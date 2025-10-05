import os
import json
import csv
import io
import re
import boto3
from urllib.parse import unquote_plus

# AWS clients
s3 = boto3.client("s3")
sns = boto3.client("sns")

# Environment variables
RAW_BUCKET = os.environ["RAW_BUCKET"]
CLEAN_BUCKET = os.environ["CLEAN_BUCKET"]
QUARANTINE_BUCKET = os.environ["QUARANTINE_BUCKET"]
SNS_TOPIC_ARN = os.environ["SNS_TOPIC_ARN"]
REQUIRED_COLUMNS = os.environ.get("REQUIRED_COLUMNS", "").split(",")

# Regex for simple email validation
RE_EMAIL = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

def normalize_headers(headers):
    """Normalize header names for consistency."""
    return [h.strip().lower().replace(" ", "_") for h in headers]

def clean_row(row: dict):
    """Trim whitespace and validate fields."""
    row = {k: (v.strip() if isinstance(v, str) else v) for k, v in row.items()}
    if "amount" in row and row["amount"]:
        try:
            row["amount"] = f"{float(row['amount']):.2f}"
        except Exception:
            raise ValueError(f"invalid amount: {row['amount']}")
    if "email" in row and row["email"] and not RE_EMAIL.match(row["email"]):
        raise ValueError(f"invalid email: {row['email']}")
    return row

def validate_required(row, required_cols):
    """Check for missing required columns."""
    missing = [c for c in required_cols if row.get(c, "") == ""]
    if missing:
        raise ValueError(f"missing required: {','.join(missing)}")

def process_csv(content: bytes, required_cols):
    """Validate and clean CSV content."""
    buf = io.StringIO(content.decode("utf-8"))
    reader = csv.DictReader(buf)
    reader.fieldnames = normalize_headers(reader.fieldnames or [])
    cleaned, bad, seen = [], [], set()

    for r in reader:
        try:
            r = {k: r.get(k, "") for k in reader.fieldnames}
            r = clean_row(r)
            validate_required(r, required_cols)
            key = (r.get("id"), r.get("email"))
            if key in seen:  # remove duplicates
                continue
            seen.add(key)
            cleaned.append(r)
        except Exception as e:
            r["_error"] = str(e)
            bad.append(r)

    return to_csv(reader.fieldnames, cleaned), (to_csv(reader.fieldnames + ["_error"], bad) if bad else None)

def to_csv(headers, rows):
    """Convert list of dicts to CSV bytes."""
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=headers, extrasaction="ignore")
    writer.writeheader()
    for r in rows:
        writer.writerow(r)
    return out.getvalue().encode("utf-8")

def lambda_handler(event, _ctx):
    """Main Lambda entry point triggered by S3 upload."""
    try:
        rec = event["Records"][0]["s3"]
        bucket = rec["bucket"]["name"]
        key = unquote_plus(rec["object"]["key"])

        obj = s3.get_object(Bucket=bucket, Key=key)
        body = obj["Body"].read()

        cleaned, bad = process_csv(body, REQUIRED_COLUMNS)

        base = key.rsplit(".", 1)[0]
        clean_key = f"{base}.clean.csv"
        s3.put_object(Bucket=CLEAN_BUCKET, Key=clean_key, Body=cleaned)

        result = {"original": f"s3://{bucket}/{key}", "clean": f"s3://{CLEAN_BUCKET}/{clean_key}"}

        if bad:
            bad_key = f"{base}.quarantine.csv"
            s3.put_object(Bucket=QUARANTINE_BUCKET, Key=bad_key, Body=bad)
            result["quarantine"] = f"s3://{QUARANTINE_BUCKET}/{bad_key}"}

        sns.publish(
            TopicArn=SNS_TOPIC_ARN,
            Subject="CSV Cleaner: File Processed",
            Message=json.dumps(result, indent=2)
        )

        print(json.dumps({"level": "info", "result": result}))
        return {"statusCode": 200, "body": json.dumps(result)}

    except Exception as e:
        print(json.dumps({"level": "error", "message": str(e)}))
        raise
