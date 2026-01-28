# Skill: Evaluate Patent Value

## Domain
technology

## Description
Evaluates patent portfolio value using citation analysis, market relevance, and licensing potential for IP management decisions.

## Tags
IP, patents, valuation, licensing, technology, legal

## Use Cases
- Patent valuation
- Portfolio optimization
- Licensing strategy
- M&A IP assessment

## Proprietary Business Rules

### Rule 1: Citation Analysis
Forward and backward citation evaluation.

### Rule 2: Market Relevance Assessment
Technology market alignment scoring.

### Rule 3: Legal Strength Evaluation
Claim breadth and validity analysis.

### Rule 4: Licensing Potential
Revenue generation opportunity assessment.

## Input Parameters
- `patent_id` (string): Patent identifier
- `patent_data` (dict): Patent information
- `citation_data` (dict): Citation metrics
- `market_data` (dict): Relevant market data
- `legal_status` (dict): Legal standing
- `comparable_licenses` (list): Licensing comparables

## Output
- `estimated_value` (dict): Value range estimate
- `citation_score` (dict): Citation analysis
- `market_relevance` (dict): Market alignment
- `legal_assessment` (dict): Legal strength
- `licensing_recommendation` (dict): Strategy recommendation

## Implementation
The evaluation logic is implemented in `patent_evaluator.py` and references data from CSV files:
- `valuation_methods.csv` - Reference data
- `royalty_rates_by_industry.csv` - Reference data
- `strength_factors.csv` - Reference data
- `life_cycle_factors.csv` - Reference data
- `discount_rates.csv` - Reference data
- `quality_scores.csv` - Reference data
- `jurisdiction_factors.csv` - Reference data
- `cost_components.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from patent_evaluator import evaluate_patent

result = evaluate_patent(
    patent_id="US10123456",
    patent_data={"filing_date": "2020-01-15", "claims": 25, "technology_area": "AI"},
    citation_data={"forward_citations": 45, "backward_citations": 30},
    market_data={"tam": 50000000000, "growth_rate": 0.25},
    legal_status={"status": "granted", "remaining_life_years": 12},
    comparable_licenses=[{"technology": "AI", "royalty_rate": 0.03}]
)

print(f"Estimated Value: ${result['estimated_value']['midpoint']:,.0f}")
```

## Test Execution
```python
from patent_evaluator import evaluate_patent

result = evaluate_patent(
    patent_id=input_data.get('patent_id'),
    patent_data=input_data.get('patent_data', {}),
    citation_data=input_data.get('citation_data', {}),
    market_data=input_data.get('market_data', {}),
    legal_status=input_data.get('legal_status', {}),
    comparable_licenses=input_data.get('comparable_licenses', [])
)
```
