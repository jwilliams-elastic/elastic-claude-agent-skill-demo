# Skill: Process Commission Calculation

## Domain
financial_services

## Description
Processes sales commission calculations including quota attainment, tier progression, and bonus qualifications.

## Tags
commissions, sales, compensation, incentives, quotas, payroll

## Use Cases
- Commission calculation
- Quota tracking
- Bonus determination
- Plan administration

## Proprietary Business Rules

### Rule 1: Attainment Calculation
Quota attainment and credit assignment.

### Rule 2: Tier Progression
Commission rate tier determination.

### Rule 3: Accelerator Application
Overachievement accelerator calculation.

### Rule 4: Split and Override Rules
Multi-party commission splits.

## Input Parameters
- `calculation_id` (string): Calculation identifier
- `sales_rep_id` (string): Sales rep identifier
- `sales_data` (list): Sales transactions
- `plan_rules` (dict): Commission plan terms
- `quota_data` (dict): Quota assignments
- `period` (dict): Calculation period

## Output
- `commission_amount` (float): Total commission
- `attainment` (dict): Quota attainment
- `tier_detail` (dict): Tier calculation
- `accelerator_amount` (float): Bonus commission
- `payment_schedule` (dict): Payment timing

## Implementation
The processing logic is implemented in `commission_processor.py` and references data from `commission_plans.json`.

## Usage Example
```python
from commission_processor import process_commission

result = process_commission(
    calculation_id="COM-001",
    sales_rep_id="REP-001",
    sales_data=[{"deal_id": "D-001", "amount": 100000, "close_date": "2025-12-15"}],
    plan_rules={"base_rate": 0.08, "accelerator_threshold": 1.0, "accelerator_rate": 0.12},
    quota_data={"annual_quota": 1000000, "ytd_attainment": 850000},
    period={"start": "2025-12-01", "end": "2025-12-31"}
)

print(f"Commission Amount: ${result['commission_amount']:,.0f}")
```

## Test Execution
```python
from commission_processor import process_commission

result = process_commission(
    calculation_id=input_data.get('calculation_id'),
    sales_rep_id=input_data.get('sales_rep_id'),
    sales_data=input_data.get('sales_data', []),
    plan_rules=input_data.get('plan_rules', {}),
    quota_data=input_data.get('quota_data', {}),
    period=input_data.get('period', {})
)
```
