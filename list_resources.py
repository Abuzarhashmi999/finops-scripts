import boto3

# connect to EC2 in your region
ec2=boto3.client("ec2", region_name="eu-north-1")

# Ask AWS to list your instances
response= ec2.describe_instances()

print("=== Your EC2 Instances ===")
found = False
for reservation in response["Reservations"]:
    for instance in reservation["Instances"]:
        found = True
        iid = instance["InstanceId"]
        itype = instance["InstanceType"]
        state = instance["State"]["Name"]
        print(f"  {iid} | {itype} | {state}")

if not found:
    print("  No instances found (or all terminated).")

# Now list your S3 buckets
s3 = boto3.client("s3")
print("\n=== Your S3 Buckets ===")
buckets = s3.list_buckets()["Buckets"]
if buckets:
    for b in buckets:
        print(f"  {b['Name']}")
else:
    print("  No buckets found.")