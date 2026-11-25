# rightsize_ec2.py
# Find OVERSIZED running EC2 instances (doing real work, but too big) and
# recommend a smaller size. Different from find_idle_ec2.py (idle = doing nothing).
# Read-only: it reports, it never changes anything.

import boto3
from datetime import datetime, timedelta, timezone

# --- STEP 1: Clients ---
ec2 = boto3.client("ec2")
cw  = boto3.client("cloudwatch")

# --- STEP 2: Settings (tune per client) ---
DAYS_BACK     = 14      # how far back to look at usage
AVG_THRESHOLD = 40.0    # avg CPU below this = probably oversized
MAX_THRESHOLD = 80.0    # but if max CPU goes above this, it NEEDS the headroom -> leave it

# --- STEP 3: The "size ladder" — one step down is roughly half the cost ---
SMALLER_SIZE = {
    "2xlarge": "xlarge",
    "xlarge":  "large",
    "large":   "medium",
    "medium":  "small",
    "small":   "micro",
}

# --- STEP 4: Get the running instances ---
reservations = ec2.describe_instances(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
)["Reservations"]

print(f"=== Right-sizing check: avg CPU < {AVG_THRESHOLD}% over {DAYS_BACK} days ===\n")

found_any = False

# --- STEP 5: Check each instance ---
for res in reservations:
    for inst in res["Instances"]:
        iid   = inst["InstanceId"]
        itype = inst["InstanceType"]          # e.g. "m5.xlarge"

        stats = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": iid}],
            StartTime=datetime.now(timezone.utc) - timedelta(days=DAYS_BACK),
            EndTime=datetime.now(timezone.utc),
            Period=86400,                       # one data point per day
            Statistics=["Average", "Maximum"],  # we need BOTH
        )

        points = stats["Datapoints"]
        if not points:
            continue                            # no data, skip

        avg_cpu = sum(p["Average"] for p in points) / len(points)
        max_cpu = max(p["Maximum"] for p in points)

        # The judgment: low average AND safe maximum = oversized
        if avg_cpu < AVG_THRESHOLD and max_cpu < MAX_THRESHOLD:
            family, size = itype.split(".")     # "m5", "xlarge"
            suggestion = SMALLER_SIZE.get(size)
            if suggestion:
                found_any = True
                new_type = f"{family}.{suggestion}"
                print(f"  {iid} ({itype})")
                print(f"     avg CPU {avg_cpu:.1f}%, max {max_cpu:.1f}%  -> oversized")
                print(f"     recommend: downsize to {new_type} (~50% cheaper)\n")

# --- STEP 6: Nothing found ---
if not found_any:
    print("  No oversized instances found. Everything looks right-sized.")