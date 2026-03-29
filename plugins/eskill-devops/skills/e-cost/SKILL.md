---
name: e-cost
description: "Estimates cloud infrastructure costs from IaC configurations by mapping resources to pricing tiers. Use when budgeting deployments, reviewing changes for cost impact, or optimizing spend. Also applies when: 'estimate cloud costs', 'how much will this cost', 'infrastructure budget', 'cloud cost analysis'."
---

# Cloud Cost Estimation

This skill estimates monthly cloud infrastructure costs by analyzing Infrastructure-as-Code configurations, Docker Compose files, and application resource requirements. It maps declared resources to approximate pricing tiers, identifies cost drivers, and suggests optimization opportunities.

## Prerequisites

Confirm the target cloud provider (AWS, GCP, Azure) with the user. If the IaC configuration references multiple providers, note all of them. Determine whether the estimate should cover development, staging, or production environments, as resource sizing differs significantly.

### Step 1: Inventory Cloud Resources

Use `filesystem` to locate IaC configuration files and `data_file_read` to parse them.

Scan for:

- **Terraform files** (`*.tf`): Parse `resource` blocks to extract resource types and configurations.
- **CloudFormation** (`*.yaml`, `*.json` in `cloudformation/` or `cfn/`): Parse `Resources` section.
- **Docker Compose** (`docker-compose.yml`): Map services to equivalent cloud resources.
- **Kubernetes manifests**: Map resource requests to compute instance sizing.
- **Serverless configurations** (`serverless.yml`, `sam-template.yaml`): Extract function counts, memory settings, and event triggers.
- **Pulumi/CDK**: Check for `Pulumi.yaml` or `cdk.json` and parse the relevant source files.

For each resource discovered, record:

| Field | Description |
|-------|-------------|
| Resource type | e.g., aws_instance, aws_rds_instance, google_compute_instance |
| Name/identifier | The logical name in the IaC configuration |
| Instance type/size | e.g., t3.medium, db.r6g.large, n2-standard-4 |
| Count/replicas | Number of instances or desired count |
| Region | Deployment region |
| Storage | Attached disk size and type (gp3, io2, pd-ssd) |
| Network | Data transfer estimates if configurable |

### Step 2: Map Resources to Pricing Categories

Classify each resource into a pricing category for estimation.

| Category | Resource Types | Primary Cost Driver |
|----------|---------------|-------------------|
| Compute | EC2, ECS, EKS nodes, GCE, Cloud Run, Lambda | Instance hours, vCPU-seconds |
| Database | RDS, Aurora, Cloud SQL, DynamoDB, Cosmos DB | Instance hours, storage, IOPS |
| Storage | S3, GCS, Azure Blob, EBS, EFS | GB-months, request count |
| Network | Load balancers, NAT gateways, data transfer | GB transferred, hours running |
| Cache | ElastiCache, Memorystore, Azure Cache | Node hours |
| Queue | SQS, SNS, Pub/Sub, Service Bus | Message count |
| DNS | Route53, Cloud DNS, Azure DNS | Hosted zones, query count |
| CDN | CloudFront, Cloud CDN, Azure CDN | GB transferred, request count |
| Monitoring | CloudWatch, Cloud Monitoring, Azure Monitor | Metrics, logs ingested, alarms |
| Secrets | Secrets Manager, Parameter Store, Key Vault | Secret count, API calls |
| Container registry | ECR, GCR, ACR | Storage, data transfer |
| Serverless | Lambda, Cloud Functions, Azure Functions | Invocations, GB-seconds |

For resources not in IaC (e.g., DNS, monitoring), note them as potential additional costs.

### Step 3: Estimate Compute Costs

For each compute resource, calculate the monthly cost.

**EC2/GCE/Azure VM instances**:

Use `data_file_read` to extract the instance type from the IaC configuration. Apply the following reference rates (approximate, US regions):

| Instance Family | Example Type | Approx. Monthly (On-Demand) |
|----------------|--------------|---------------------------|
| General purpose (small) | t3.micro / e2-micro | $8-10 |
| General purpose (medium) | t3.medium / e2-medium | $30-35 |
| General purpose (large) | m6i.large / n2-standard-2 | $65-75 |
| General purpose (xlarge) | m6i.xlarge / n2-standard-4 | $130-150 |
| Compute optimized | c6i.large / c2-standard-4 | $60-70 |
| Memory optimized | r6i.large / n2-highmem-2 | $90-110 |

Multiply by the instance count. For Auto Scaling groups, use the desired capacity as the baseline and max capacity as the upper bound.

**Container services (ECS, EKS, GKE)**:
- ECS Fargate: Calculate from `cpu` and `memory` task definitions. Rate is approximately $0.04/vCPU-hour and $0.004/GB-hour.
- EKS/GKE: Estimate based on the worker node instance types plus the control plane fee ($0.10/hour for EKS, free tier for GKE standard).

**Serverless functions**:
- Free tier: first 1M invocations and 400,000 GB-seconds per month (AWS Lambda).
- Beyond free tier: $0.20 per 1M invocations plus $0.0000166667 per GB-second.
- Estimate invocation count from event sources (API Gateway requests, queue messages, scheduled events).

### Step 4: Estimate Database Costs

For each database resource, calculate storage and compute costs separately.

**Relational databases (RDS, Cloud SQL)**:

| DB Instance Class | Approx. Monthly (On-Demand) |
|-------------------|---------------------------|
| db.t3.micro | $15-18 |
| db.t3.medium | $55-65 |
| db.r6g.large | $180-210 |
| db.r6g.xlarge | $360-420 |

Add storage costs:
- General purpose SSD (gp3): $0.08/GB-month.
- Provisioned IOPS (io2): $0.125/GB-month plus $0.065/IOPS-month.
- Backup storage beyond the free allocation: $0.095/GB-month.

For Multi-AZ deployments, double the instance cost.
For read replicas, add the full instance cost per replica.

**NoSQL databases**:
- DynamoDB: $0.25 per WCU-month, $0.05 per RCU-month (provisioned). On-demand pricing is approximately 5x provisioned for steady workloads.
- DocumentDB/MongoDB Atlas: Price by instance type similar to RDS.

### Step 5: Estimate Storage and Network Costs

**Object storage**:
- S3 Standard: $0.023/GB-month for first 50 TB.
- S3 Infrequent Access: $0.0125/GB-month.
- Request costs: $0.005 per 1,000 PUT requests, $0.0004 per 1,000 GET requests.
- Estimate storage volume from application context (user uploads, logs, backups).

**Block storage (EBS, Persistent Disks)**:
- gp3: $0.08/GB-month (included 3,000 IOPS, 125 MB/s).
- io2: $0.125/GB-month plus IOPS charges.
- Sum all volumes attached to compute instances.

**Network**:
- Data transfer out: first 100 GB free, then $0.09/GB (AWS).
- NAT Gateway: $0.045/hour ($32/month) plus $0.045/GB processed. NAT gateways are a frequently overlooked cost driver.
- Load balancer: ALB is approximately $0.0225/hour ($16/month) plus $0.008/LCU-hour.
- VPN connections: $0.05/hour per connection ($36/month).
- Inter-region transfer: $0.02/GB.

### Step 6: Estimate Supporting Service Costs

Calculate costs for ancillary services identified in the infrastructure.

- **ElastiCache/Memorystore**: Price by node type, similar to compute instances. cache.t3.micro is approximately $12/month.
- **SQS/SNS**: First 1M requests free, then $0.40 per 1M SQS requests, $0.50 per 1M SNS publishes.
- **CloudWatch/Monitoring**: $0.30 per custom metric, $0.50/GB logs ingested, $0.10 per alarm.
- **Secrets Manager**: $0.40 per secret per month plus $0.05 per 10,000 API calls.
- **Route53**: $0.50 per hosted zone, $0.40 per 1M standard queries.
- **ECR/Container Registry**: $0.10/GB storage per month.

Sum these into a supporting services total.

### Step 7: Calculate Total Estimate

Assemble all cost components into a summary table.

Use `shell` to perform any arithmetic needed for complex calculations (summing per-resource costs, applying multipliers for replicas).

```
## Monthly Cost Estimate

| Category | Resources | Monthly Low | Monthly High |
|----------|-----------|-------------|-------------|
| Compute | <list> | $XXX | $XXX |
| Database | <list> | $XXX | $XXX |
| Storage | <list> | $XXX | $XXX |
| Network | <list> | $XXX | $XXX |
| Cache | <list> | $XXX | $XXX |
| Serverless | <list> | $XXX | $XXX |
| Supporting | <list> | $XXX | $XXX |
| **Total** | | **$XXX** | **$XXX** |
```

Provide both a low estimate (minimum resources, reserved pricing where applicable) and a high estimate (on-demand pricing, maximum auto-scaling).

Calculate the annualized cost for budget planning: monthly total multiplied by 12.

### Step 8: Identify Cost Optimization Opportunities

Review the resource inventory for common optimization patterns.

| Optimization | Potential Savings | Applies When |
|-------------|------------------|--------------|
| Reserved instances (1-year) | 30-40% | Steady-state workloads running 24/7 |
| Reserved instances (3-year) | 50-60% | Long-term committed workloads |
| Spot/Preemptible instances | 60-90% | Fault-tolerant batch processing, CI/CD |
| Right-sizing | 20-50% | Instances consistently under 30% utilization |
| Graviton/ARM instances | 20% | Workloads compatible with ARM architecture |
| Storage tiering | 40-70% | Infrequently accessed data on standard tier |
| NAT Gateway alternatives | 80-90% | VPC endpoints for AWS service traffic |
| Committed use discounts | 30-55% | GCP workloads with predictable usage |
| Savings Plans | 20-40% | AWS compute with flexible instance types |

For each applicable optimization, calculate the estimated savings and note any trade-offs or prerequisites.

### Step 9: Compare Environments

If the configuration defines multiple environments (dev, staging, production), estimate each separately and present a comparison.

| Component | Dev | Staging | Production |
|-----------|-----|---------|------------|
| Compute | $XX | $XX | $XX |
| Database | $XX | $XX | $XX |
| Storage | $XX | $XX | $XX |
| Network | $XX | $XX | $XX |
| **Total** | **$XX** | **$XX** | **$XX** |

Highlight where development or staging environments could be reduced (smaller instances, fewer replicas, spot instances) to save costs without affecting production reliability.

### Step 10: Generate Cost Report

Write the complete cost estimate to a file using `filesystem`.

Structure the report:

```
# Cloud Infrastructure Cost Estimate

**Project**: <name>
**Provider**: <AWS/GCP/Azure>
**Date**: <YYYY-MM-DD>
**Environment**: <dev/staging/production>

## Summary
<total monthly and annual estimate with confidence range>

## Resource Inventory
<detailed table of all resources and their costs>

## Cost Breakdown by Category
<category-level summaries with charts described in text>

## Optimization Recommendations
<prioritized savings opportunities>

## Assumptions and Limitations
<list of pricing assumptions, excluded costs, and estimation caveats>

## Environment Comparison (if applicable)
<side-by-side cost comparison across environments>
```

Include a disclaimer that the estimate is based on published list prices and actual costs may vary due to negotiated discounts, data transfer patterns, API call volumes, and regional pricing differences.

## Edge Cases

- **Multi-cloud deployments**: If the project uses multiple providers, estimate each provider separately and sum them. Note any cross-cloud data transfer costs.
- **Free tier eligibility**: New AWS/GCP/Azure accounts have free tier benefits for the first 12 months. Note which resources fall within the free tier and when the free tier expires.
- **Spot/Preemptible pricing volatility**: Spot instance prices fluctuate. Use the average spot price for the instance type rather than the current price.
- **Data transfer unknowns**: Network costs depend heavily on traffic volume, which is often unknown at the IaC level. Provide estimates at several traffic levels (low: 100 GB/month, medium: 1 TB/month, high: 10 TB/month) and let the user select the most appropriate.
- **Marketplace or BYOL software**: Some IaC configurations deploy third-party software with separate licensing costs. Flag these and note that the license cost is not included in the estimate.
- **Currency**: All estimates default to USD. Note if the user requires a different currency and apply the appropriate conversion.

## Related Skills

- **e-terra** (eskill-devops): Run e-terra before this skill to understand the infrastructure components being estimated.
- **e-infra** (eskill-devops): Run e-infra alongside this skill to correlate cost estimates with infrastructure design decisions.
