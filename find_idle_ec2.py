import boto3
from datetime import datetime, timedelta

# Connect to EC2 and CloudWatch in your region
ec2 = boto3.client("ec2", region_name="eu-north-1")
cw = boto3.client("cloudwatch", region_name="eu-north-1")

# How we define "idle" and how far back to look
CPU_THRESHOLD = 5.0   # percent — below this average = likely idle
DAYS_BACK = 1         # how many days of data to check

print(f"Checking running instances for avg CPU < {CPU_THRESHOLD}% "
      f"over the last {DAYS_BACK} day(s)...\n")

# Get all RUNNING instances
running = ec2.describe_instances(
    Filters=[{"Name": "instance-state-name", "Values": ["running"]}]
)

found_any = False
for reservation in running["Reservations"]:
    for inst in reservation["Instances"]:
        found_any = True
        iid = inst["InstanceId"]
        itype = inst["InstanceType"]

        # Ask CloudWatch for this instance's CPU usage
        stats = cw.get_metric_statistics(
            Namespace="AWS/EC2",
            MetricName="CPUUtilization",
            Dimensions=[{"Name": "InstanceId", "Value": iid}],
            StartTime=datetime.utcnow() - timedelta(days=DAYS_BACK),
            EndTime=datetime.utcnow(),
            Period=3600,              # one data point per hour
            Statistics=["Average"],
        )

        points = stats["Datapoints"]
        if not points:
            print(f"  {iid} ({itype}): no CPU data yet "
                  f"(instance may be too new)")
            continue

        avg_cpu = sum(p["Average"] for p in points) / len(points)
        status = "IDLE — review" if avg_cpu < CPU_THRESHOLD else "active"
        print(f"  {iid} ({itype}): avg CPU {avg_cpu:.1f}%  ->  {status}")

if not found_any:
    print("  No running instances found.")