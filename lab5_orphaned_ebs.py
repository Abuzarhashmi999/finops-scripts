#  STEP 1: IMPORTS
import boto3

#  STEP 2: CLIENT (connect to EC2 - EBS lives here) 
ec2 = boto3.client("ec2", region_name="eu-north-1")

#  STEP 3: RULE (price per GB per month) 
PRICE_PER_GB = 0.08   # approx gp3 price in USD per GB-month

#  STEP 4: PRINT (announce) 
print("Checking for orphaned (unattached) EBS volumes...\n")

#  STEP 5: DESCRIBE_VOLUMES (only 'available' ones) 
response = ec2.describe_volumes(
    Filters=[{"Name": "status", "Values": ["available"]}]
)

#  STEP 6: FLAG + a running total 
volumes = response["Volumes"]
total_gb = 0

#  STEP 7: LOOP through each orphaned volume 
for vol in volumes:
    vol_id = vol["VolumeId"]
    size   = vol["Size"]
    vtype  = vol["VolumeType"]
    total_gb += size
    print(f"  {vol_id} | {size} GB | {vtype}")

#  STEP 8: REPORT the totals 
if not volumes:
    print("  No orphaned volumes found. Nothing to clean up.")
else:
    est_cost = total_gb * PRICE_PER_GB
    print(f"\n  Orphaned: {total_gb} GB")
    print(f"  Estimated waste: ~${est_cost:.2f}/month")