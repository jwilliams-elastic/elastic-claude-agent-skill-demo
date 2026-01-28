# Skill: Evaluate Equipment Lease

## Domain
machinery_equipment

## Description
Evaluates equipment lease proposals comparing lease vs buy economics, residual value analysis, and total cost of ownership.

## Tags
leasing, equipment, machinery, finance, TCO, capital-planning

## Use Cases
- Lease vs buy analysis
- Equipment financing decisions
- Residual value assessment
- Total cost comparison

## Proprietary Business Rules

### Rule 1: Net Present Value Analysis
NPV calculation for lease vs purchase comparison.

### Rule 2: Residual Value Estimation
Equipment depreciation and end-of-term value projection.

### Rule 3: Tax Benefit Analysis
Evaluation of tax implications for each financing option.

### Rule 4: Maintenance Cost Allocation
Assessment of maintenance responsibilities and costs.

## Input Parameters
- `equipment_id` (string): Equipment identifier
- `equipment_specs` (dict): Equipment details
- `lease_terms` (dict): Proposed lease terms
- `purchase_price` (float): Cash purchase price
- `usage_profile` (dict): Expected utilization
- `financial_params` (dict): Company financial parameters

## Output
- `recommendation` (string): Lease or buy recommendation
- `npv_comparison` (dict): NPV analysis results
- `tco_analysis` (dict): Total cost of ownership breakdown
- `break_even_point` (dict): Break-even analysis
- `risk_factors` (list): Identified risks

## Implementation
The evaluation logic is implemented in `lease_evaluator.py` and references data from CSV files:
- `depreciation.csv` - Reference data
- `maintenance_costs.csv` - Reference data
- `lease_market_rates.csv` - Reference data
- `utilization_factors.csv` - Reference data
- `financing_benchmarks.csv` - Reference data
- `tax_considerations.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from lease_evaluator import evaluate_lease

result = evaluate_lease(
    equipment_id="EQ-2026-001",
    equipment_specs={"type": "excavator", "model": "CAT 320", "useful_life_years": 10},
    lease_terms={"monthly_payment": 5000, "term_months": 60, "buyout": 50000},
    purchase_price=350000,
    usage_profile={"hours_per_year": 2000, "intensity": "heavy"},
    financial_params={"discount_rate": 0.08, "tax_rate": 0.25}
)

print(f"Recommendation: {result['recommendation']}")
```

## Test Execution
```python
from lease_evaluator import evaluate_lease

result = evaluate_lease(
    equipment_id=input_data.get('equipment_id'),
    equipment_specs=input_data.get('equipment_specs', {}),
    lease_terms=input_data.get('lease_terms', {}),
    purchase_price=input_data.get('purchase_price', 0),
    usage_profile=input_data.get('usage_profile', {}),
    financial_params=input_data.get('financial_params', {})
)
```
