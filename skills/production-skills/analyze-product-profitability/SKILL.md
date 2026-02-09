# Skill: Analyze Product Profitability

## Domain
consumer_products

## Description
Analyzes product-level profitability including contribution margin, cost allocation, and SKU rationalization recommendations.

## Tags
profitability, margin, products, SKU, cost, analytics

## Use Cases
- Margin analysis
- SKU rationalization
- Pricing optimization
- Cost allocation

## Proprietary Business Rules

### Rule 1: Contribution Margin Calculation
Product-level margin computation.

### Rule 2: Cost Allocation
Overhead and indirect cost assignment.

### Rule 3: Profitability Ranking
Product profitability comparison.

### Rule 4: Rationalization Recommendations
Low-profit SKU action recommendations.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `product_data` (list): Product information
- `sales_data` (list): Sales by product
- `cost_data` (dict): Cost breakdown
- `allocation_rules` (dict): Cost allocation methodology
- `profitability_thresholds` (dict): Margin targets

## Output
- `product_margins` (dict): Margin by product
- `profitability_ranking` (list): Ranked products
- `cost_analysis` (dict): Cost breakdown
- `rationalization_candidates` (list): SKUs for review
- `recommendations` (list): Optimization actions

## Implementation
The analysis logic is implemented in `profitability_analyzer.py` and references data from `profitability_rules.json`.

## Usage Example
```python
from profitability_analyzer import analyze_profitability

result = analyze_profitability(
    analysis_id="PRF-001",
    product_data=[{"sku": "SKU-001", "category": "beverages", "price": 2.99}],
    sales_data=[{"sku": "SKU-001", "units": 50000, "revenue": 149500}],
    cost_data={"SKU-001": {"cogs": 1.20, "distribution": 0.30}},
    allocation_rules={"method": "activity_based"},
    profitability_thresholds={"min_margin": 0.25}
)

print(f"SKU-001 Margin: {result['product_margins']['SKU-001']:.1%}")
```

## Test Execution
```python
from profitability_analyzer import analyze_profitability

result = analyze_profitability(
    analysis_id=input_data.get('analysis_id'),
    product_data=input_data.get('product_data', []),
    sales_data=input_data.get('sales_data', []),
    cost_data=input_data.get('cost_data', {}),
    allocation_rules=input_data.get('allocation_rules', {}),
    profitability_thresholds=input_data.get('profitability_thresholds', {})
)
```
