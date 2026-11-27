# connect_client.py
# Corewing — connect to a CLIENT's AWS account with read-only, TEMPORARY access.
# Uses STS AssumeRole, so you never hold the client's secret keys.
# Returns a ready boto3 Session your other FinOps scripts can use directly.

import boto3

def connect(role_arn, external_id=None, region="eu-north-1"):
    """
    Assume the client's read-only role and return a ready-to-use boto3 Session.

    role_arn    : the client's role ARN, e.g.
                  "arn:aws:iam::123456789012:role/CorewingReadOnly"
    external_id : the shared secret the client set on the role (recommended)
    region      : default region for the returned session
    """
    sts = boto3.client("sts")

    params = {
        "RoleArn": role_arn,
        "RoleSessionName": "corewing-audit",   # shows up in the client's CloudTrail
    }
    if external_id:
        params["ExternalId"] = external_id

    # Borrow the role -> get TEMPORARY credentials (expire in ~1 hour)
    creds = sts.assume_role(**params)["Credentials"]

    # Build a session from those temporary credentials
    session = boto3.Session(
        aws_access_key_id=creds["AccessKeyId"],
        aws_secret_access_key=creds["SecretAccessKey"],
        aws_session_token=creds["SessionToken"],
        region_name=region,
    )
    return session


# --- Demo: run this file directly to test a connection ---
if __name__ == "__main__":
    # Fill in the client's details. NEVER commit real values to GitHub.
    ROLE_ARN    = "arn:aws:iam::CLIENT_ACCOUNT_ID:role/CorewingReadOnly"
    EXTERNAL_ID = "change-me"

    session = connect(ROLE_ARN, EXTERNAL_ID)

    # Prove it worked: whose account are we in now?
    who = session.client("sts").get_caller_identity()
    print(f"Connected to client account: {who['Account']}")

    # Sanity check: count their running EC2 instances
    ec2 = session.client("ec2")
    reservations = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )["Reservations"]
    count = sum(len(r["Instances"]) for r in reservations)
    print(f"Running EC2 instances in their account: {count}")