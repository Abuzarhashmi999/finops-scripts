# STEP 1     IMPORTS
import boto3
from collections import defaultdict

#STEP 2   CLIENT(COST EXPLORER)
ce = boto3.client("ce", region_name = "us-east-1")

# STEP 3  ASK AWS FOR SPEND, GROUPED BY SERVICE
response = ce.get_cost_and_usage(
    TimePeriod={"Start": "2026-04-01", "End": "2026-09-30"},
    Granularity="MONTHLY",
    Metrics=["UnblendedCost"],
    GroupBy=[{"Type": "DIMENSION", "Key": "SERVICE"}],
)
# ─── STEP 4: ADD UP each service across all months ─
costs = defaultdict(float)
for month in response["ResultsByTime"]:        # each month in the range
    for group in month["Groups"]:              # each service in that month
        service = group["Keys"][0]
        amount  = float(group["Metrics"]["UnblendedCost"]["Amount"])
        costs[service] += amount

# ─── STEP 5: SORT + REPORT ─────────────────────────
top = sorted(costs.items(), key=lambda x: -x[1])[:10]
print("=== Spend by service (live from AWS) ===\n")
if not top:
    print("  No cost data found (account has near-zero spend).")
else:
    for service, total in top:
        print(f"  {service:40} ${total:,.2f}")
    print(f"\n  Total: ${sum(costs.values()):,.2f}")