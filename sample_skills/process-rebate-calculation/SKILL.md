# Skill: Process Rebate Calculation

## Domain
consumer_products

## Description
Processes manufacturer rebate calculations including tier determination, accrual computation, and payment reconciliation.

## Tags
rebates, pricing, trade, CPG, accruals, incentives

## Use Cases
- Rebate tier calculation
- Accrual management
- Payment processing
- Contract compliance

## Proprietary Business Rules

### Rule 1: Tier Determination
Volume or value-based tier qualification.

### Rule 2: Accrual Calculation
Period rebate accrual computation.

### Rule 3: True-Up Processing
Year-end reconciliation and adjustment.

### Rule 4: Contract Compliance
Rebate agreement terms validation.

## Input Parameters
- `calculation_id` (string): Calculation identifier
- `customer_id` (string): Customer identifier
- `sales_data` (list): Sales transactions
- `rebate_agreement` (dict): Rebate contract terms
- `prior_accruals` (dict): Previous accruals
- `calculation_period` (dict): Period dates

## Output
- `rebate_amount` (float): Calculated rebate
- `tier_achieved` (dict): Tier qualification
- `accrual_details` (dict): Accrual breakdown
- `true_up_amount` (float): Adjustment amount
- `payment_schedule` (dict): Payment timing

## Implementation
The processing logic is implemented in `rebate_processor.py` and references data from CSV files:
- `rebate_types.csv` - Reference data
- `volume_tiers.csv` - Reference data
- `growth_tiers.csv` - Reference data
- `calculation_rules.csv` - Reference data
- `eligibility_requirements.csv` - Reference data
- `accrual_methods.csv` - Reference data
- `settlement_options.csv` - Reference data
- `audit_requirements.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from rebate_processor import process_rebate

result = process_rebate(
    calculation_id="REB-001",
    customer_id="CUST-001",
    sales_data=[{"date": "2025-12-01", "amount": 500000, "product": "Category A"}],
    rebate_agreement={"type": "volume", "tiers": [{"threshold": 1000000, "rate": 0.03}]},
    prior_accruals={"ytd_sales": 800000, "ytd_accrual": 16000},
    calculation_period={"start": "2025-12-01", "end": "2025-12-31"}
)

print(f"Rebate Amount: ${result['rebate_amount']:,.0f}")
```

## Test Execution
```python
from rebate_processor import process_rebate

result = process_rebate(
    calculation_id=input_data.get('calculation_id'),
    customer_id=input_data.get('customer_id'),
    sales_data=input_data.get('sales_data', []),
    rebate_agreement=input_data.get('rebate_agreement', {}),
    prior_accruals=input_data.get('prior_accruals', {}),
    calculation_period=input_data.get('calculation_period', {})
)
```
