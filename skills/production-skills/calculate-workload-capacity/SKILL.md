# Skill: Calculate Workload Capacity

## Domain
technology

## Description
Calculates infrastructure workload capacity analyzing resource utilization, forecasting demand, and identifying scaling requirements.

## Tags
capacity, infrastructure, cloud, DevOps, scaling, performance

## Use Cases
- Capacity planning
- Resource optimization
- Scaling decisions
- Cost forecasting

## Proprietary Business Rules

### Rule 1: Utilization Analysis
CPU, memory, storage, and network utilization assessment.

### Rule 2: Demand Forecasting
Workload growth prediction using historical trends.

### Rule 3: Headroom Calculation
Available capacity and buffer requirements.

### Rule 4: Scaling Recommendations
Right-sizing and scaling trigger identification.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `resource_metrics` (list): Infrastructure metrics
- `workload_data` (dict): Application workload info
- `historical_usage` (list): Historical utilization
- `growth_factors` (dict): Expected growth drivers
- `sla_requirements` (dict): Performance SLAs

## Output
- `current_utilization` (dict): Current resource usage
- `capacity_forecast` (dict): Future capacity needs
- `headroom_analysis` (dict): Available headroom
- `scaling_recommendations` (list): Scaling actions
- `cost_projection` (dict): Capacity cost forecast

## Implementation
The calculation logic is implemented in `capacity_calculator.py` and references data from `capacity_thresholds.json`.

## Usage Example
```python
from capacity_calculator import calculate_capacity

result = calculate_capacity(
    analysis_id="CAP-001",
    resource_metrics=[{"resource": "cpu", "avg_utilization": 0.65, "peak": 0.85}],
    workload_data={"application": "web_app", "instances": 10},
    historical_usage=[{"date": "2025-11", "cpu_avg": 0.60}],
    growth_factors={"user_growth_rate": 0.15, "feature_launches": 2},
    sla_requirements={"max_cpu_utilization": 0.80, "response_time_ms": 200}
)

print(f"Current CPU Utilization: {result['current_utilization']['cpu']}")
```

## Test Execution
```python
from capacity_calculator import calculate_capacity

result = calculate_capacity(
    analysis_id=input_data.get('analysis_id'),
    resource_metrics=input_data.get('resource_metrics', []),
    workload_data=input_data.get('workload_data', {}),
    historical_usage=input_data.get('historical_usage', []),
    growth_factors=input_data.get('growth_factors', {}),
    sla_requirements=input_data.get('sla_requirements', {})
)
```
