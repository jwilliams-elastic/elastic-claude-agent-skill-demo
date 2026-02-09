# Skill: Calculate Capacity Utilization

## Domain
advanced_manufacturing

## Description
Calculates manufacturing capacity utilization metrics including OEE, bottleneck analysis, and capacity planning recommendations.

## Tags
capacity, manufacturing, OEE, production, efficiency, planning

## Use Cases
- Capacity monitoring
- OEE calculation
- Bottleneck identification
- Investment planning

## Proprietary Business Rules

### Rule 1: OEE Calculation
Overall equipment effectiveness computation.

### Rule 2: Bottleneck Analysis
Production constraint identification.

### Rule 3: Capacity Forecasting
Future capacity requirement projection.

### Rule 4: Investment Trigger
Capacity expansion threshold analysis.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `production_data` (list): Production output records
- `equipment_data` (list): Equipment specifications
- `downtime_records` (list): Downtime events
- `quality_data` (dict): Quality metrics
- `demand_forecast` (dict): Future demand

## Output
- `utilization_rate` (float): Capacity utilization
- `oee_metrics` (dict): OEE breakdown
- `bottleneck_analysis` (dict): Constraint identification
- `capacity_forecast` (dict): Future capacity needs
- `recommendations` (list): Optimization actions

## Implementation
The calculation logic is implemented in `capacity_calculator.py` and references data from `capacity_benchmarks.json`.

## Usage Example
```python
from capacity_calculator import calculate_capacity_utilization

result = calculate_capacity_utilization(
    analysis_id="CAP-001",
    production_data=[{"date": "2025-12-15", "units": 950, "line": "Line_1"}],
    equipment_data=[{"id": "Line_1", "max_capacity": 1000, "planned_hours": 16}],
    downtime_records=[{"line": "Line_1", "minutes": 45, "reason": "changeover"}],
    quality_data={"defect_rate": 0.02},
    demand_forecast={"next_quarter": 85000}
)

print(f"Utilization Rate: {result['utilization_rate']:.1%}")
```

## Test Execution
```python
from capacity_calculator import calculate_capacity_utilization

result = calculate_capacity_utilization(
    analysis_id=input_data.get('analysis_id'),
    production_data=input_data.get('production_data', []),
    equipment_data=input_data.get('equipment_data', []),
    downtime_records=input_data.get('downtime_records', []),
    quality_data=input_data.get('quality_data', {}),
    demand_forecast=input_data.get('demand_forecast', {})
)
```
