"""
=============================================================================
 FinOps Practice Scripts  —  companion to your Conceptual Study Notes
 Prepared for Abuzar  ·  Cloud Health
=============================================================================

WHAT THIS IS
    Every Python example from the study notes, in one runnable file, organised
    by topic. Read each function, then run it against a real (test) account.

BEFORE YOU CAN RUN THE boto3 PARTS
    1. Python working on your machine   (python --version)
    2. pip install boto3
    3. aws configure   (enter an access key from YOUR OWN test account)
       -> use your free-tier account first, NEVER a client's, while learning.

THE ONE SAFETY RULE
    These scripts only READ and REPORT. They never delete anything.
    In a client account you find & recommend; the client approves & acts.

HOW TO RUN ONE
    Scroll to the bottom, uncomment the function you want in main(), then:
        python finops_examples.py
=============================================================================
"""

import csv
from collections import defaultdict
from datetime import datetime, timedelta, timezone

# boto3 is only needed for the AWS examples. Guard the import so the
# CSV example still runs even before boto3 is installed.
try:
    import boto3
    HAVE_BOTO3 = True
except ImportError:
    HAVE_BOTO3 = False


# ---------------------------------------------------------------------------
# 1. IAM  —  find stale access keys (a security quick-win)
#    Concept: least privilege. Old, unused keys are a risk.
# ---------------------------------------------------------------------------
def find_stale_access_keys(max_age_days=90):
    iam = boto3.client("iam")
    print(f"\n== Access keys older than {max_age_days} days ==")
    for user in iam.list_users()["Users"]:
        name = user["UserName"]
        keys = iam.list_access_keys(UserName=name)["AccessKeyMetadata"]
        for k in keys:
            age = (datetime.now(timezone.utc) - k["CreateDate"]).days
            if age > max_age_days:
                print(f"  {name}: key {k['AccessKeyId']} is {age} days old")


# ---------------------------------------------------------------------------
# 2. EC2  —  flag idle running instances (your headline script)
#    Concept: waste = provisioned but unused. Low CPU over time = idle.
# ---------------------------------------------------------------------------
def find_idle_ec2(cpu_threshold=5.0, days=14):
    ec2 = boto3.client("ec2")
    cw = boto3.client("cloudwatch")
    print(f"\n== Running EC2 with avg CPU < {cpu_threshold}% over {days} days ==")

    running = ec2.describe_instances(
        Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
    )
    for res in running["Reservations"]:
        for inst in res["Instances"]:
            iid = inst["InstanceId"]
            itype = inst["InstanceType"]
            stats = cw.get_metric_statistics(
                Namespace="AWS/EC2",
                MetricName="CPUUtilization",
                Dimensions=[{"Name": "InstanceId", "Value": iid}],
                StartTime=datetime.utcnow() - timedelta(days=days),
                EndTime=datetime.utcnow(),
                Period=86400,            # one data point per day
                Statistics=["Average"],
            )
            pts = stats["Datapoints"]
            if pts:
                avg = sum(p["Average"] for p in pts) / len(pts)
                if avg < cpu_threshold:
                    print(f"  {iid} ({itype}): avg CPU {avg:.1f}% — likely idle")


# ---------------------------------------------------------------------------
# 3. EBS  —  find orphaned volumes (best starter script; easy client win)
#    Concept: the disk outlives the server and keeps billing.
# ---------------------------------------------------------------------------
def find_orphaned_ebs(price_per_gb_month=0.08):
    ec2 = boto3.client("ec2")
    print("\n== Orphaned (unattached) EBS volumes ==")

    vols = ec2.describe_volumes(
        Filters=[{"Name": "status", "Values": ["available"]}]  # available = unattached
    )["Volumes"]

    if not vols:
        print("  None found. Nothing to clean up.")
        return

    total_gb = 0
    for v in vols:
        total_gb += v["Size"]
        print(f"  {v['VolumeId']} | {v['Size']} GB | {v['VolumeType']}")
    est = total_gb * price_per_gb_month
    print(f"  ---> {total_gb} GB orphaned  ~= ${est:.2f}/month wasted")


# ---------------------------------------------------------------------------
# 4. S3  —  list buckets (starting point for a storage audit)
#    Concept: cold data on expensive tiers should move to cheaper classes.
# ---------------------------------------------------------------------------
def list_s3_buckets():
    s3 = boto3.client("s3")
    print("\n== S3 buckets ==")
    for b in s3.list_buckets()["Buckets"]:
        print(f"  {b['Name']}")


# ---------------------------------------------------------------------------
# 5. BILLING CSV  —  read -> group by service -> sort -> top 5
#    Concept: follow the biggest numbers first. (Pure Python, no boto3.)
#    Make a test file 'billing.csv' with headers: ProductName,UnblendedCost
# ---------------------------------------------------------------------------
def top_services_from_csv(path="billing.csv", top_n=5):
    costs = defaultdict(float)                     # service -> running total
    with open(path) as f:
        for row in csv.DictReader(f):              # read the file row by row
            service = row["ProductName"]
            amount = float(row["UnblendedCost"] or 0)
            costs[service] += amount               # group (dictionary)

    top = sorted(costs.items(), key=lambda x: -x[1])[:top_n]  # sort, take top N
    print(f"\n== Top {top_n} services by cost ==")
    for service, total in top:
        print(f"  {service:30} ${total:,.2f}")


# ---------------------------------------------------------------------------
# 6. COST EXPLORER API  —  live spend by service (no CSV needed)
#    Concept: phone the bank instead of reading the statement.
# ---------------------------------------------------------------------------
def cost_by_service(start="2026-08-01", end="2026-09-01"):
    ce = boto3.client("ce")                         # ce = Cost Explorer
    print(f"\n== Spend by service {start} -> {end} ==")
    resp = ce.get_cost_and_usage(
        TimePeriod={"Start": start, "End": end},
        Granularity="MONTHLY",
        Metrics=["UnblendedCost"],
        GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
    )
    groups = resp["ResultsByTime"][0]["Groups"]
    # sort biggest first
    groups.sort(key=lambda g: -float(g["Metrics"]["UnblendedCost"]["Amount"]))
    for g in groups:
        service = g["Keys"][0]
        amount = float(g["Metrics"]["UnblendedCost"]["Amount"])
        if amount > 0:
            print(f"  {service:30} ${amount:,.2f}")


# ---------------------------------------------------------------------------
# main()  —  uncomment ONE at a time to try it.
# ---------------------------------------------------------------------------
def main():
    # ---- pure Python: works as soon as Python runs (make billing.csv first) ----
    # top_services_from_csv("billing.csv")

    # ---- AWS: need boto3 + `aws configure` with your OWN test account ----
    if not HAVE_BOTO3:
        print("boto3 not installed yet. Run:  pip install boto3")
        return

    # find_stale_access_keys()
    # find_idle_ec2()
    # find_orphaned_ebs()
    # list_s3_buckets()
    # cost_by_service()

    print("Open finops_examples.py and uncomment a function in main() to run it.")


if __name__ == "__main__":
    main()
