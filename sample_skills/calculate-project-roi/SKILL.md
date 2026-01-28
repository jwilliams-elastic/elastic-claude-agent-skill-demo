# Skill: Calculate Project ROI

## Domain
private_equity

## Description
Calculates project return on investment including NPV, IRR, and payback period analysis for capital investment decisions.

## Tags
ROI, finance, investment, NPV, IRR, capital-budgeting

## Use Cases
- Investment appraisal
- Project prioritization
- Capital allocation
- Business case development

## Proprietary Business Rules

### Rule 1: NPV Calculation
Net present value with risk-adjusted discount rate.

### Rule 2: IRR Determination
Internal rate of return calculation.

### Rule 3: Payback Analysis
Simple and discounted payback period.

### Rule 4: Sensitivity Testing
Key variable sensitivity analysis.

## Input Parameters
- `project_id` (string): Project identifier
- `initial_investment` (float): Upfront investment
- `cash_flows` (list): Projected cash flows
- `discount_rate` (float): Cost of capital
- `project_life` (int): Project duration years
- `risk_factors` (dict): Risk adjustments

## Output
- `npv` (float): Net present value
- `irr` (float): Internal rate of return
- `payback_period` (dict): Payback analysis
- `profitability_index` (float): PI ratio
- `sensitivity_analysis` (dict): Sensitivity results
- `recommendation` (string): Investment recommendation

## Implementation
The calculation logic is implemented in `roi_calculator.py` and references data from CSV files:
- `discount_rates.csv` - Reference data
- `project_categories.csv` - Reference data
- `benefit_categories.csv` - Reference data
- `cost_categories.csv` - Reference data
- `hurdle_rates.csv` - Reference data
- `payback_thresholds.csv` - Reference data
- `npv_thresholds.csv` - Reference data
- `sensitivity_scenarios.csv` - Reference data
- `risk_adjustments.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from roi_calculator import calculate_roi

result = calculate_roi(
    project_id="PRJ-001",
    initial_investment=1000000,
    cash_flows=[200000, 300000, 350000, 400000, 450000],
    discount_rate=0.10,
    project_life=5,
    risk_factors={"technology_risk": "medium", "market_risk": "low"}
)

print(f"NPV: ${result['npv']:,.0f}")
print(f"IRR: {result['irr']:.1%}")
```

## Test Execution
```python
from roi_calculator import calculate_roi

result = calculate_roi(
    project_id=input_data.get('project_id'),
    initial_investment=input_data.get('initial_investment', 0),
    cash_flows=input_data.get('cash_flows', []),
    discount_rate=input_data.get('discount_rate', 0.10),
    project_life=input_data.get('project_life', 5),
    risk_factors=input_data.get('risk_factors', {})
)
```
