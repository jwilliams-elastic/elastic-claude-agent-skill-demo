# Skill: Calculate Cloud Migration ROI

## Domain
technology

## Description
Calculates comprehensive ROI and TCO analysis for cloud migration initiatives, comparing on-premises costs against public cloud, private cloud, and hybrid scenarios. Incorporates infrastructure, licensing, labor, opportunity costs, and risk-adjusted benefits to support CIO investment decisions.

## Business Rules
This skill implements enterprise cloud economics modeling:

1. **Infrastructure Cost Model**: Compute, storage, network, and facility costs with 3-year depreciation
2. **Labor Arbitrage**: Cloud reduces infrastructure FTE requirements by 30-50% but increases cloud engineering needs by 15-25%
3. **Licensing Optimization**: BYOL vs. cloud-native licensing comparison with true-up risk factors
4. **Migration Cost Phases**: Discovery (5%), Planning (10%), Migration (60%), Optimization (25%) of total migration budget
5. **Risk Adjustment**: Apply 15% contingency for lift-and-shift, 25% for re-platform, 40% for re-architect
6. **Benefit Realization Timeline**: Infrastructure savings Month 1, labor savings Month 6, agility benefits Month 12

## Input Parameters
- `workload_name` (string): Name of workload/application being migrated
- `migration_strategy` (string): "rehost", "replatform", "refactor", "repurchase", "retain"
- `current_infra_annual_cost` (float): Current annual infrastructure cost ($)
- `current_license_annual_cost` (float): Current annual software licensing cost ($)
- `current_fte_count` (float): Current FTEs supporting this workload
- `avg_fte_cost` (float): Average fully-loaded FTE cost ($)
- `compute_units` (int): Number of compute instances/VMs
- `storage_tb` (float): Storage requirements in TB
- `data_transfer_tb_monthly` (float): Monthly data transfer in TB
- `cloud_provider` (string): "aws", "azure", "gcp"
- `target_architecture` (string): "iaas", "paas", "saas", "serverless"
- `compliance_requirements` (list): List of compliance frameworks (e.g., ["SOC2", "HIPAA"])
- `migration_timeline_months` (int): Planned migration duration

## Output
Returns a comprehensive ROI analysis with:
- `recommendation` (string): "proceed", "conditional", "defer"
- `total_3yr_savings` (float): Net savings over 3 years
- `roi_percentage` (float): 3-year ROI percentage
- `payback_months` (int): Months to positive ROI
- `tco_comparison` (dict): Side-by-side TCO for current vs. cloud
- `cost_breakdown` (dict): Detailed cost categories (compute, storage, network, labor, migration)
- `risk_factors` (list): Key risks with mitigation recommendations
- `sensitivity_analysis` (dict): ROI under optimistic/pessimistic scenarios
- `hidden_costs` (list): Often-overlooked costs to budget for

## Usage Example
```python
from cloud_roi import calculate_migration_roi

result = calculate_migration_roi(
    workload_name="ERP System",
    migration_strategy="replatform",
    current_infra_annual_cost=2500000,
    current_license_annual_cost=800000,
    current_fte_count=12,
    avg_fte_cost=150000,
    compute_units=50,
    storage_tb=100,
    data_transfer_tb_monthly=5,
    cloud_provider="azure",
    target_architecture="paas",
    compliance_requirements=["SOC2", "GDPR"],
    migration_timeline_months=18
)
```

## Tags
technology, cloud, migration, roi, tco, cio, aws, azure, gcp, infrastructure

## Implementation
The ROI calculation logic is implemented in `cloud_roi.py` and references:
- `cloud_pricing.csv` - Cloud provider pricing by service
- `labor_factors.csv` - FTE adjustment factors by architecture
- `migration_cost_factors.csv` - Migration cost multipliers by strategy
- `risk_contingency.csv` - Risk adjustment percentages
