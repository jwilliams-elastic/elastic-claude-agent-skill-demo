# Skill: Analyze Market Basket

## Domain
retail

## Description
Analyzes market basket data to identify product associations, cross-sell opportunities, and optimal product placement strategies.

## Tags
retail, analytics, basket-analysis, cross-sell, merchandising, recommendations

## Use Cases
- Product association discovery
- Cross-sell recommendation
- Store layout optimization
- Bundle pricing strategy

## Proprietary Business Rules

### Rule 1: Association Rule Mining
Identification of frequent itemsets and association rules.

### Rule 2: Lift Calculation
Measurement of association strength beyond random chance.

### Rule 3: Temporal Patterns
Analysis of time-based purchasing patterns.

### Rule 4: Customer Segmentation
Association patterns by customer segment.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `transaction_data` (list): Transaction records
- `product_catalog` (dict): Product information
- `time_period` (dict): Analysis time range
- `min_support` (float): Minimum support threshold
- `min_confidence` (float): Minimum confidence threshold

## Output
- `association_rules` (list): Discovered rules
- `product_pairs` (list): Frequently bought together
- `recommendations` (list): Merchandising recommendations
- `segment_insights` (dict): Patterns by segment
- `summary_stats` (dict): Analysis statistics

## Implementation
The analysis logic is implemented in `basket_analyzer.py` and references data from CSV files:
- `default_parameters.csv` - Reference data
- `analysis_windows.csv` - Reference data
- `recommendation_thresholds.csv` - Reference data
- `time_patterns.csv` - Reference data
- `segment_definitions.csv` - Reference data
- `cross_sell_rules.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from basket_analyzer import analyze_basket

result = analyze_basket(
    analysis_id="MBA-001",
    transaction_data=[{"txn_id": "T001", "items": ["bread", "milk", "eggs"]}],
    product_catalog={"bread": {"category": "bakery"}, "milk": {"category": "dairy"}},
    time_period={"start": "2025-01-01", "end": "2025-12-31"},
    min_support=0.01,
    min_confidence=0.3
)

print(f"Rules Found: {len(result['association_rules'])}")
```

## Test Execution
```python
from basket_analyzer import analyze_basket

result = analyze_basket(
    analysis_id=input_data.get('analysis_id'),
    transaction_data=input_data.get('transaction_data', []),
    product_catalog=input_data.get('product_catalog', {}),
    time_period=input_data.get('time_period', {}),
    min_support=input_data.get('min_support', 0.01),
    min_confidence=input_data.get('min_confidence', 0.3)
)
```
