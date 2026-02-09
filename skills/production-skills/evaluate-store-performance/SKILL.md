# Skill: Evaluate Store Performance

## Domain
retail

## Description
Evaluates retail store performance using sales metrics, operational efficiency, and customer experience indicators for portfolio optimization.

## Tags
retail, store, performance, sales, operations, analytics

## Use Cases
- Store benchmarking
- Performance ranking
- Closure decisions
- Investment prioritization

## Proprietary Business Rules

### Rule 1: Sales Performance Metrics
Revenue and comp sales analysis.

### Rule 2: Operational Efficiency
Labor, shrink, and expense ratios.

### Rule 3: Customer Metrics
Traffic, conversion, and satisfaction.

### Rule 4: Portfolio Classification
Store tier and action classification.

## Input Parameters
- `store_id` (string): Store identifier
- `sales_data` (dict): Sales performance
- `operational_data` (dict): Operational metrics
- `customer_data` (dict): Customer metrics
- `market_data` (dict): Trade area demographics
- `benchmark_data` (dict): Performance benchmarks

## Output
- `performance_score` (float): Overall rating
- `sales_analysis` (dict): Sales metrics
- `operational_assessment` (dict): Efficiency analysis
- `customer_assessment` (dict): Customer metrics
- `classification` (string): Store tier
- `recommendations` (list): Performance actions

## Implementation
The evaluation logic is implemented in `store_evaluator.py` and references data from `store_benchmarks.json`.

## Usage Example
```python
from store_evaluator import evaluate_store

result = evaluate_store(
    store_id="STR-001",
    sales_data={"revenue": 5000000, "comp_growth": 0.03, "transactions": 150000},
    operational_data={"labor_pct": 0.12, "shrink_pct": 0.01, "sqft": 25000},
    customer_data={"traffic": 200000, "conversion": 0.75, "nps": 45},
    market_data={"population": 100000, "median_income": 65000},
    benchmark_data={"avg_sales_sqft": 180, "avg_conversion": 0.70}
)

print(f"Store Performance Score: {result['performance_score']}")
```

## Test Execution
```python
from store_evaluator import evaluate_store

result = evaluate_store(
    store_id=input_data.get('store_id'),
    sales_data=input_data.get('sales_data', {}),
    operational_data=input_data.get('operational_data', {}),
    customer_data=input_data.get('customer_data', {}),
    market_data=input_data.get('market_data', {}),
    benchmark_data=input_data.get('benchmark_data', {})
)
```
