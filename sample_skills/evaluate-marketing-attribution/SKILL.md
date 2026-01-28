# Skill: Evaluate Marketing Attribution

## Domain
technology

## Description
Evaluates marketing campaign effectiveness using multi-touch attribution models to optimize marketing spend and channel allocation.

## Tags
marketing, attribution, analytics, ROI, digital, campaigns

## Use Cases
- Campaign ROI analysis
- Channel effectiveness
- Budget allocation
- Conversion path analysis

## Proprietary Business Rules

### Rule 1: Multi-Touch Attribution
First-touch, last-touch, and algorithmic attribution models.

### Rule 2: Channel Contribution
Individual channel impact on conversions.

### Rule 3: ROI Calculation
Return on marketing investment by channel.

### Rule 4: Budget Optimization
Optimal budget allocation recommendations.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `conversion_data` (list): Conversion events
- `touchpoint_data` (list): Marketing touchpoints
- `spend_data` (dict): Marketing spend by channel
- `attribution_model` (string): Model type to use
- `lookback_window` (int): Attribution window days

## Output
- `channel_attribution` (dict): Attribution by channel
- `conversion_paths` (list): Common conversion paths
- `roi_by_channel` (dict): ROI metrics
- `optimization_recommendations` (list): Budget recommendations
- `model_comparison` (dict): Multi-model results

## Implementation
The evaluation logic is implemented in `attribution_evaluator.py` and references data from CSV files:
- `attribution_models.csv` - Reference data
- `channel_categories.csv` - Reference data
- `conversion_windows.csv` - Reference data
- `roi_benchmarks.csv` - Reference data
- `incrementality_factors.csv` - Reference data
- `funnel_stages.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from attribution_evaluator import evaluate_attribution

result = evaluate_attribution(
    analysis_id="ATT-001",
    conversion_data=[{"id": "CV-001", "value": 100, "timestamp": "2025-12-15"}],
    touchpoint_data=[{"conversion_id": "CV-001", "channel": "paid_search", "timestamp": "2025-12-10"}],
    spend_data={"paid_search": 50000, "social": 30000, "email": 10000},
    attribution_model="linear",
    lookback_window=30
)

print(f"Paid Search Attribution: {result['channel_attribution']['paid_search']}")
```

## Test Execution
```python
from attribution_evaluator import evaluate_attribution

result = evaluate_attribution(
    analysis_id=input_data.get('analysis_id'),
    conversion_data=input_data.get('conversion_data', []),
    touchpoint_data=input_data.get('touchpoint_data', []),
    spend_data=input_data.get('spend_data', {}),
    attribution_model=input_data.get('attribution_model', 'linear'),
    lookback_window=input_data.get('lookback_window', 30)
)
```
