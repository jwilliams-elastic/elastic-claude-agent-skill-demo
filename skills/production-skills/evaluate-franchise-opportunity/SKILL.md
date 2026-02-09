# Skill: Evaluate Franchise Opportunity

## Domain
retail

## Description
Evaluates franchise investment opportunities analyzing unit economics, territory potential, and franchisor track record for investment decisions.

## Tags
franchise, investment, retail, due-diligence, unit-economics

## Use Cases
- Franchise investment analysis
- Territory evaluation
- Unit economics modeling
- Franchisor assessment

## Proprietary Business Rules

### Rule 1: Unit Economics Validation
Analysis of per-unit profitability and payback period.

### Rule 2: Territory Potential Assessment
Market size and competitive density evaluation.

### Rule 3: Franchisor Track Record
Historical performance and franchisee satisfaction analysis.

### Rule 4: Investment Return Modeling
IRR and cash-on-cash return projections.

## Input Parameters
- `opportunity_id` (string): Opportunity identifier
- `franchise_info` (dict): Franchise concept details
- `territory_data` (dict): Market demographics
- `investment_terms` (dict): Investment requirements
- `unit_financials` (dict): Unit-level economics
- `franchisor_data` (dict): Franchisor information

## Output
- `investment_score` (float): Overall opportunity rating
- `unit_economics` (dict): Per-unit financial analysis
- `territory_assessment` (dict): Market evaluation
- `return_projections` (dict): Financial return estimates
- `risk_factors` (list): Investment risks identified

## Implementation
The evaluation logic is implemented in `franchise_evaluator.py` and references data from CSV files:
- `category_benchmarks.csv` - Reference data
- `market_factors.csv` - Reference data
- `franchisor_standards.csv` - Reference data
- `projection_params.csv` - Reference data
- `evaluation_weights.csv` - Reference data
- `investment_thresholds.csv` - Reference data
- `royalty_benchmarks.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from franchise_evaluator import evaluate_franchise

result = evaluate_franchise(
    opportunity_id="FRN-001",
    franchise_info={"brand": "FastServe", "category": "QSR", "units_nationwide": 500},
    territory_data={"population": 150000, "median_income": 65000, "competitors": 3},
    investment_terms={"franchise_fee": 45000, "buildout": 350000, "royalty_pct": 0.06},
    unit_financials={"avg_revenue": 1200000, "avg_ebitda_margin": 0.15},
    franchisor_data={"years_franchising": 15, "franchisee_satisfaction": 85}
)

print(f"Investment Score: {result['investment_score']}")
```

## Test Execution
```python
from franchise_evaluator import evaluate_franchise

result = evaluate_franchise(
    opportunity_id=input_data.get('opportunity_id'),
    franchise_info=input_data.get('franchise_info', {}),
    territory_data=input_data.get('territory_data', {}),
    investment_terms=input_data.get('investment_terms', {}),
    unit_financials=input_data.get('unit_financials', {}),
    franchisor_data=input_data.get('franchisor_data', {})
)
```
