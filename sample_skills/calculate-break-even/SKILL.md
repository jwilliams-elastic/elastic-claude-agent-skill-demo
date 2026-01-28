# Skill: Calculate Break Even

## Domain
financial_services

## Description
Calculates break-even analysis for products, projects, and investments including sensitivity analysis and margin of safety.

## Tags
finance, break-even, profitability, analysis, planning, budgeting

## Use Cases
- Product pricing decisions
- Project feasibility
- Investment analysis
- Sensitivity testing

## Proprietary Business Rules

### Rule 1: Break-Even Point Calculation
Unit and revenue break-even determination.

### Rule 2: Contribution Margin Analysis
Variable cost and margin breakdown.

### Rule 3: Sensitivity Analysis
Impact of cost and price changes.

### Rule 4: Margin of Safety
Risk buffer calculation.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `fixed_costs` (dict): Fixed cost breakdown
- `variable_costs` (dict): Variable cost per unit
- `pricing_data` (dict): Price and volume assumptions
- `scenarios` (list): Sensitivity scenarios
- `time_horizon` (dict): Analysis period

## Output
- `break_even_units` (int): Units to break even
- `break_even_revenue` (float): Revenue to break even
- `contribution_margin` (dict): Margin analysis
- `margin_of_safety` (float): Safety percentage
- `sensitivity_results` (dict): Scenario analysis

## Implementation
The calculation logic is implemented in `breakeven_calculator.py` and references data from `cost_structures.json`.

## Usage Example
```python
from breakeven_calculator import calculate_breakeven

result = calculate_breakeven(
    analysis_id="BEA-001",
    fixed_costs={"rent": 50000, "salaries": 200000, "utilities": 25000},
    variable_costs={"materials": 15, "labor": 10, "shipping": 3},
    pricing_data={"unit_price": 50, "expected_volume": 20000},
    scenarios=[{"name": "price_increase", "price_change": 0.10}],
    time_horizon={"period": "annual"}
)

print(f"Break-Even Units: {result['break_even_units']:,}")
```

## Test Execution
```python
from breakeven_calculator import calculate_breakeven

result = calculate_breakeven(
    analysis_id=input_data.get('analysis_id'),
    fixed_costs=input_data.get('fixed_costs', {}),
    variable_costs=input_data.get('variable_costs', {}),
    pricing_data=input_data.get('pricing_data', {}),
    scenarios=input_data.get('scenarios', []),
    time_horizon=input_data.get('time_horizon', {})
)
```
