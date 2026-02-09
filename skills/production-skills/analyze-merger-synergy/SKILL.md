# Skill: Analyze Merger Synergy

## Domain
private_equity

## Description
Analyzes potential merger synergies including cost savings, revenue enhancement, and integration costs for M&A due diligence.

## Tags
M&A, synergy, merger, due-diligence, valuation, integration

## Use Cases
- Synergy identification
- Integration cost estimation
- Value creation modeling
- Deal validation

## Proprietary Business Rules

### Rule 1: Cost Synergy Categories
Identification of SG&A, procurement, and operational savings.

### Rule 2: Revenue Synergy Estimation
Cross-sell and market expansion opportunity analysis.

### Rule 3: Integration Cost Modeling
One-time integration expense estimation.

### Rule 4: Synergy Realization Timeline
Phased synergy achievement projections.

## Input Parameters
- `deal_id` (string): Transaction identifier
- `acquirer_financials` (dict): Acquirer financial data
- `target_financials` (dict): Target financial data
- `overlap_analysis` (dict): Business overlap assessment
- `integration_plan` (dict): Integration approach
- `market_data` (dict): Industry benchmarks

## Output
- `total_synergies` (dict): Synergy estimates by type
- `integration_costs` (float): Total integration costs
- `net_value_creation` (float): Net synergy value
- `realization_timeline` (list): Synergy phasing
- `risk_factors` (list): Synergy achievement risks

## Implementation
The analysis logic is implemented in `synergy_analyzer.py` and references data from CSV files:
- `industries.csv` - Reference data
- `default.csv` - Reference data
- `integration_costs.csv` - Reference data
- `typical_synergy_ranges.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from synergy_analyzer import analyze_synergies

result = analyze_synergies(
    deal_id="DEAL-001",
    acquirer_financials={"revenue": 500000000, "ebitda": 75000000, "employees": 2000},
    target_financials={"revenue": 150000000, "ebitda": 20000000, "employees": 600},
    overlap_analysis={"geographic": 0.3, "customer": 0.15, "vendor": 0.4},
    integration_plan={"approach": "full", "timeline_months": 24},
    market_data={"industry": "manufacturing", "avg_synergy_pct": 0.05}
)

print(f"Total Synergies: ${result['total_synergies']['total']:,.0f}")
```

## Test Execution
```python
from synergy_analyzer import analyze_synergies

result = analyze_synergies(
    deal_id=input_data.get('deal_id'),
    acquirer_financials=input_data.get('acquirer_financials', {}),
    target_financials=input_data.get('target_financials', {}),
    overlap_analysis=input_data.get('overlap_analysis', {}),
    integration_plan=input_data.get('integration_plan', {}),
    market_data=input_data.get('market_data', {})
)
```
