# ─── STEP 1: IMPORTS ───────────────────────────────
import csv                              # tool for reading CSV files
from collections import defaultdict     # a dictionary that auto-starts at 0

# ─── STEP 2: PREPARE a place to add up costs ───────
costs = defaultdict(float)              # service name -> running total

# ─── STEP 3: READ the file, row by row ─────────────
with open("billing.csv") as f:         # open the file
    for row in csv.DictReader(f):       # read each row as a dictionary
        service = row["ProductName"]    # which service (a column)
        amount  = float(row["UnblendedCost"])   # the cost (turn text into a number)
        costs[service] += amount        # add this charge to that service's total

# ─── STEP 4: SORT services by cost, biggest first ──
top5 = sorted(costs.items(), key=lambda x: -x[1])[:5]

# ─── STEP 5: REPORT the top spenders ───────────────
print("=== Top services by cost ===\n")
for service, total in top5:
    print(f"  {service:40} ${total:,.2f}")

# ─── STEP 6: REPORT the grand total ────────────────
grand_total = sum(costs.values())
print(f"\n  Total spend: ${grand_total:,.2f}")