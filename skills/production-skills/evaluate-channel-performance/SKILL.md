# Skill: Evaluate Channel Performance

## Domain
retail

## Description
Evaluates sales channel performance comparing metrics across channels to optimize omnichannel strategy and resource allocation.

## Tags
omnichannel, retail, sales, performance, ecommerce, analytics

## Use Cases
- Channel comparison
- Resource allocation
- Strategy optimization
- Performance benchmarking

## Proprietary Business Rules

### Rule 1: Channel Metrics Calculation
Key performance indicators by channel.

### Rule 2: Attribution Analysis
Cross-channel customer journey attribution.

### Rule 3: Efficiency Comparison
Channel cost efficiency evaluation.

### Rule 4: Investment Optimization
Channel investment recommendation.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `channel_data` (dict): Channel details
- `sales_data` (list): Sales by channel
- `cost_data` (dict): Channel operating costs
- `customer_data` (dict): Customer behavior data
- `benchmark_data` (dict): Industry benchmarks

## Output
- `channel_metrics` (dict): KPIs by channel
- `performance_ranking` (list): Channel ranking
- `efficiency_analysis` (dict): Cost efficiency
- `attribution_insights` (dict): Customer journey
- `recommendations` (list): Optimization actions

## Implementation
The evaluation logic is implemented in `channel_evaluator.py` and references data from `channel_benchmarks.json`.

## Usage Example
```python
from channel_evaluator import evaluate_channels

result = evaluate_channels(
    analysis_id="CHN-001",
    channel_data={"ecommerce": {"type": "direct"}, "retail": {"type": "owned"}},
    sales_data=[{"channel": "ecommerce", "revenue": 5000000}, {"channel": "retail", "revenue": 10000000}],
    cost_data={"ecommerce": {"operating": 500000}, "retail": {"operating": 2000000}},
    customer_data={"ecommerce": {"aov": 85}, "retail": {"aov": 65}},
    benchmark_data={"ecommerce_growth": 0.15, "retail_growth": 0.03}
)

print(f"Top Channel: {result['performance_ranking'][0]['channel']}")
```

## Test Execution
```python
from channel_evaluator import evaluate_channels

result = evaluate_channels(
    analysis_id=input_data.get('analysis_id'),
    channel_data=input_data.get('channel_data', {}),
    sales_data=input_data.get('sales_data', []),
    cost_data=input_data.get('cost_data', {}),
    customer_data=input_data.get('customer_data', {}),
    benchmark_data=input_data.get('benchmark_data', {})
)
```
