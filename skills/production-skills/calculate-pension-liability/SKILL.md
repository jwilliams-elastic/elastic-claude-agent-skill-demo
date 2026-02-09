# Skill: Calculate Pension Liability

## Domain
financial_services

## Description
Calculates defined benefit pension plan liabilities using actuarial methods including PBO, ABO, and funding status assessment.

## Tags
pension, actuarial, benefits, liability, funding, ERISA

## Use Cases
- Pension obligation calculation
- Funding status assessment
- Actuarial assumption validation
- Regulatory reporting

## Proprietary Business Rules

### Rule 1: PBO Calculation
Projected benefit obligation using projected salary growth.

### Rule 2: Discount Rate Selection
Appropriate discount rate determination.

### Rule 3: Mortality Table Application
Life expectancy assumptions for benefit payments.

### Rule 4: Funding Status Assessment
Comparison of plan assets to liabilities.

## Input Parameters
- `plan_id` (string): Plan identifier
- `participant_data` (list): Plan participant census
- `plan_provisions` (dict): Benefit formula details
- `actuarial_assumptions` (dict): Valuation assumptions
- `asset_values` (dict): Plan asset data
- `valuation_date` (string): Valuation date

## Output
- `pbo` (float): Projected benefit obligation
- `abo` (float): Accumulated benefit obligation
- `funding_status` (dict): Funded percentage and shortfall
- `expense_components` (dict): Pension expense breakdown
- `sensitivity_analysis` (dict): Assumption sensitivity

## Implementation
The calculation logic is implemented in `pension_calculator.py` and references data from CSV files:
- `default_assumptions.csv` - Reference data
- `discount_rate_guidance.csv` - Reference data
- `mortality_tables.csv` - Reference data
- `benefit_formulas.csv` - Reference data
- `erisa_requirements.csv` - Reference data
- `accounting_standards.csv` - Reference data
- `asset_allocation_benchmarks.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from pension_calculator import calculate_pension

result = calculate_pension(
    plan_id="PEN-001",
    participant_data=[{"id": "EMP-001", "age": 55, "service_years": 25, "salary": 100000}],
    plan_provisions={"formula": "final_average", "benefit_pct": 0.015},
    actuarial_assumptions={"discount_rate": 0.055, "salary_growth": 0.03},
    asset_values={"market_value": 50000000, "expected_return": 0.07},
    valuation_date="2025-12-31"
)

print(f"PBO: ${result['pbo']:,.0f}")
```

## Test Execution
```python
from pension_calculator import calculate_pension

result = calculate_pension(
    plan_id=input_data.get('plan_id'),
    participant_data=input_data.get('participant_data', []),
    plan_provisions=input_data.get('plan_provisions', {}),
    actuarial_assumptions=input_data.get('actuarial_assumptions', {}),
    asset_values=input_data.get('asset_values', {}),
    valuation_date=input_data.get('valuation_date')
)
```
