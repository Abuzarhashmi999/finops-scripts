# finops-scripts

Python scripts for AWS cost optimization and FinOps — finding and
reporting cloud waste.

## Scripts
- **finops_examples.py** — a toolkit of read-only audit scripts:
  - Find stale IAM access keys
  - Flag idle EC2 instances (via CloudWatch)
  - Detect orphaned EBS volumes
  - List S3 buckets
  - Analyze a billing CSV (top spenders by service)
  - Pull live spend by service from Cost Explorer

All scripts are **read-only** — they report and recommend, never delete.
