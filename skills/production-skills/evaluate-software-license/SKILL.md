# Skill: Evaluate Software License Compliance

## Domain
technology

## Description
Audits software deployments against license entitlements to identify compliance gaps, optimize license utilization, and calculate true-up costs.

## Tags
technology, software-licensing, compliance, audit, license-optimization

## Use Cases
- License compliance audit
- True-up cost calculation
- License optimization
- Vendor negotiation support

## Proprietary Business Rules

### Rule 1: License Metric Calculation
Different license metrics (named user, concurrent, CPU, core) require specific calculation methods.

### Rule 2: Virtualization Rules
Vendor-specific virtualization licensing rules and multipliers.

### Rule 3: Edition Feature Mapping
Feature usage mapped to required license editions.

### Rule 4: Maintenance Coverage
Maintenance and support coverage validation.

## Input Parameters
- `software_product` (string): Software product name
- `vendor` (string): Software vendor
- `deployments` (list): Current deployment details
- `entitlements` (dict): Purchased license entitlements
- `usage_data` (dict): Actual usage metrics
- `virtualization_info` (dict): Virtual environment details
- `features_in_use` (list): Features being used

## Output
- `compliance_status` (string): Compliant, non-compliant, over-licensed
- `license_position` (dict): Entitlement vs deployment comparison
- `true_up_cost` (float): Estimated true-up cost
- `optimization_opportunities` (list): Cost savings opportunities
- `risk_assessment` (dict): Compliance risk factors

## Implementation
The compliance logic is implemented in `license_auditor.py` and references rules from CSV files:
- `vendors.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from license_auditor import evaluate_compliance

result = evaluate_compliance(
    software_product="Enterprise Database",
    vendor="Oracle",
    deployments=[{"server": "db-prod-01", "cores": 16, "environment": "production"}],
    entitlements={"processor_licenses": 8, "edition": "enterprise"},
    usage_data={"peak_users": 150, "avg_concurrent": 45},
    virtualization_info={"platform": "vmware", "soft_partition": True},
    features_in_use=["partitioning", "advanced_compression"]
)

print(f"Status: {result['compliance_status']}")
```

## Test Execution
```python
from license_auditor import evaluate_compliance

result = evaluate_compliance(
    software_product=input_data.get('software_product'),
    vendor=input_data.get('vendor'),
    deployments=input_data.get('deployments', []),
    entitlements=input_data.get('entitlements', {}),
    usage_data=input_data.get('usage_data', {}),
    virtualization_info=input_data.get('virtualization_info', {}),
    features_in_use=input_data.get('features_in_use', [])
)
```
