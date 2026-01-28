# Skill: Evaluate Acquisition Target

## Domain
private_equity

## Description
Evaluates potential acquisition targets analyzing financial performance, valuation, strategic fit, and integration complexity for M&A decisions.

## Tags
M&A, acquisition, due-diligence, valuation, private-equity, investment

## Use Cases
- Target screening
- Valuation analysis
- Strategic fit assessment
- Integration planning

## Proprietary Business Rules

### Rule 1: Financial Health Score
Multi-factor financial performance assessment.

### Rule 2: Valuation Benchmarking
Multiple-based valuation against comparables.

### Rule 3: Strategic Alignment
Fit assessment against strategic criteria.

### Rule 4: Integration Risk Assessment
Complexity and risk evaluation for integration.

## Input Parameters
- `target_id` (string): Target company identifier
- `financials` (dict): Target financial statements
- `market_data` (dict): Market and industry data
- `strategic_criteria` (dict): Acquirer strategic priorities
- `comparable_transactions` (list): Recent M&A comparables
- `qualitative_factors` (dict): Non-financial factors

## Output
- `overall_score` (float): Target attractiveness score
- `valuation_range` (dict): Estimated valuation
- `financial_assessment` (dict): Financial health analysis
- `strategic_fit` (dict): Strategic alignment score
- `integration_risk` (dict): Integration complexity assessment
- `recommendation` (string): Investment recommendation

## Implementation
The evaluation logic is implemented in `target_evaluator.py` and references data from `acquisition_criteria.json`.

## Usage Example
```python
from target_evaluator import evaluate_target

result = evaluate_target(
    target_id="TGT-001",
    financials={"revenue": 50000000, "ebitda": 8000000, "growth_rate": 0.15},
    market_data={"industry": "software", "market_size": 5000000000},
    strategic_criteria={"focus_sectors": ["software"], "min_revenue": 25000000},
    comparable_transactions=[{"ev_ebitda": 12, "ev_revenue": 4}],
    qualitative_factors={"management_quality": "strong", "customer_concentration": 0.20}
)

print(f"Overall Score: {result['overall_score']}")
```

## Test Execution
```python
from target_evaluator import evaluate_target

result = evaluate_target(
    target_id=input_data.get('target_id'),
    financials=input_data.get('financials', {}),
    market_data=input_data.get('market_data', {}),
    strategic_criteria=input_data.get('strategic_criteria', {}),
    comparable_transactions=input_data.get('comparable_transactions', []),
    qualitative_factors=input_data.get('qualitative_factors', {})
)
```
