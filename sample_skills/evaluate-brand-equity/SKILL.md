# Skill: Evaluate Brand Equity

## Domain
consumer_products

## Description
Evaluates brand equity through awareness metrics, perception analysis, and financial valuation for brand management decisions.

## Tags
brand, marketing, valuation, consumer, equity, research

## Use Cases
- Brand valuation
- Brand health tracking
- Competitive positioning
- M&A brand assessment

## Proprietary Business Rules

### Rule 1: Brand Awareness Measurement
Aided and unaided awareness scoring.

### Rule 2: Brand Perception Analysis
Attribute and sentiment evaluation.

### Rule 3: Financial Valuation
Brand contribution to enterprise value.

### Rule 4: Competitive Benchmarking
Relative brand strength assessment.

## Input Parameters
- `brand_id` (string): Brand identifier
- `awareness_data` (dict): Awareness metrics
- `perception_data` (dict): Brand perception surveys
- `financial_data` (dict): Revenue and margin data
- `competitor_data` (list): Competitive brand metrics
- `market_data` (dict): Market context

## Output
- `brand_equity_score` (float): Overall brand equity
- `awareness_metrics` (dict): Awareness analysis
- `perception_analysis` (dict): Brand perception
- `financial_value` (float): Estimated brand value
- `competitive_position` (dict): Market positioning

## Implementation
The evaluation logic is implemented in `brand_evaluator.py` and references data from CSV files:
- `equity_dimensions.csv` - Reference data
- `valuation_methods.csv` - Reference data
- `performance_ratings.csv` - Reference data
- `industry_benchmarks.csv` - Reference data
- `nps_interpretation.csv` - Reference data
- `nps_benchmarks.csv` - Reference data
- `price_premium_factors.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from brand_evaluator import evaluate_brand

result = evaluate_brand(
    brand_id="BRAND-001",
    awareness_data={"aided": 0.85, "unaided": 0.45, "top_of_mind": 0.20},
    perception_data={"quality": 4.2, "value": 3.8, "trust": 4.0},
    financial_data={"revenue": 500000000, "brand_premium": 0.15},
    competitor_data=[{"brand": "Competitor A", "awareness": 0.75}],
    market_data={"category_size": 5000000000, "growth_rate": 0.05}
)

print(f"Brand Equity Score: {result['brand_equity_score']}")
```

## Test Execution
```python
from brand_evaluator import evaluate_brand

result = evaluate_brand(
    brand_id=input_data.get('brand_id'),
    awareness_data=input_data.get('awareness_data', {}),
    perception_data=input_data.get('perception_data', {}),
    financial_data=input_data.get('financial_data', {}),
    competitor_data=input_data.get('competitor_data', []),
    market_data=input_data.get('market_data', {})
)
```
