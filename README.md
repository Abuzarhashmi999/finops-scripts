# finops-scripts

Python scripts for AWS cost optimization and FinOps — finding and
reporting cloud waste. All scripts are **read-only**: they report and
recommend, never delete.

## Scripts

- **list_resources.py** — lists your live EC2 instances and S3 buckets.
- **find_idle_ec2.py** — flags running EC2 instances with low average CPU
  (likely idle) using CloudWatch metrics.
- **lab5_orphaned_ebs.py** — finds unattached ("available") EBS volumes and
  estimates the monthly storage being wasted.
- **finops_examples.py** — a toolkit of read-only audit snippets:
  stale IAM access keys, idle EC2, orphaned EBS, S3 buckets, billing-CSV
  analysis, and live spend from Cost Explorer.

## How to run

1. Python 3 with boto3 installed (`pip install boto3`)
2. AWS credentials configured (`aws configure`) with read access
3. Run any script: `python find_idle_ec2.py`
