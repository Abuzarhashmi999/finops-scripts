# savings_calculator.py
# Compare AWS compute pricing: On-Demand vs Savings Plan vs Spot.
# A FinOps tool to show a client how much a steady workload could save.

# --- STEP 1: Describe the workload (edit these per client) ---
ON_DEMAND_HOURLY = 0.10    # On-Demand price per instance per hour (USD), from AWS pricing
INSTANCE_COUNT   = 50      # how many instances are running
HOURS_PER_MONTH  = 730     # 24/7 running = 730 hours per month

# --- STEP 2: Typical discounts off On-Demand (real-world ranges) ---
SAVINGS_PLAN_DISCOUNT = 0.66   # ~66% off for a Compute Savings Plan (1–3 yr commit)
SPOT_DISCOUNT         = 0.70   # ~70% off for Spot (but can be interrupted)

# --- STEP 3: Calculate the monthly cost of each model ---
on_demand_cost    = ON_DEMAND_HOURLY * INSTANCE_COUNT * HOURS_PER_MONTH
savings_plan_cost = on_demand_cost * (1 - SAVINGS_PLAN_DISCOUNT)
spot_cost         = on_demand_cost * (1 - SPOT_DISCOUNT)

# --- STEP 4: Print the comparison ---
print("=== AWS Compute Pricing Comparison (per month) ===\n")
print(f"  Workload: {INSTANCE_COUNT} instances @ ${ON_DEMAND_HOURLY}/hr, {HOURS_PER_MONTH} hrs/month\n")

print(f"  {'On-Demand':<14} ${on_demand_cost:>10,.2f}   baseline, no commitment")
print(f"  {'Savings Plan':<14} ${savings_plan_cost:>10,.2f}   saves ${on_demand_cost - savings_plan_cost:>8,.2f}/mo")
print(f"  {'Spot':<14} ${spot_cost:>10,.2f}   saves ${on_demand_cost - spot_cost:>8,.2f}/mo")

# --- STEP 5: The headline recommendation ---
annual_saving = (on_demand_cost - savings_plan_cost) * 12
print(f"\n  >>> Moving the steady baseline to a Savings Plan saves ~${annual_saving:,.2f}/year.")