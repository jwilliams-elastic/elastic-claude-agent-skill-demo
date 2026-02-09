# Skill: Calculate Labor Productivity

## Domain
advanced_manufacturing

## Description
Calculates labor productivity metrics including output per hour, efficiency ratios, and identifies improvement opportunities.

## Tags
productivity, labor, manufacturing, efficiency, workforce, OEE

## Use Cases
- Productivity benchmarking
- Efficiency improvement
- Workforce planning
- Cost analysis

## Proprietary Business Rules

### Rule 1: Output Per Hour Calculation
Standard productivity metric computation.

### Rule 2: Efficiency Ratio Analysis
Actual vs standard performance comparison.

### Rule 3: Downtime Impact Assessment
Lost productivity from downtime events.

### Rule 4: Improvement Opportunity Identification
Productivity gap analysis.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `production_data` (list): Production output records
- `labor_data` (list): Labor hours and headcount
- `standard_times` (dict): Standard time allowances
- `downtime_records` (list): Downtime events
- `benchmark_data` (dict): Industry benchmarks

## Output
- `productivity_metrics` (dict): Key productivity measures
- `efficiency_analysis` (dict): Efficiency breakdown
- `downtime_impact` (dict): Productivity losses
- `trend_analysis` (dict): Performance trends
- `improvement_opportunities` (list): Optimization areas

## Implementation
The calculation logic is implemented in `productivity_calculator.py` and references data from CSV files:
- `productivity_metrics.csv` - Reference data
- `industry_benchmarks.csv` - Reference data
- `efficiency_factors.csv` - Reference data
- `performance_ratings.csv` - Reference data
- `adjustment_factors.csv` - Reference data
- `cost_components.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from productivity_calculator import calculate_productivity

result = calculate_productivity(
    analysis_id="PRD-001",
    production_data=[{"date": "2025-12-15", "units": 500, "product": "widget"}],
    labor_data=[{"date": "2025-12-15", "hours": 80, "headcount": 10}],
    standard_times={"widget": {"standard_minutes": 8}},
    downtime_records=[{"date": "2025-12-15", "minutes": 30, "reason": "setup"}],
    benchmark_data={"industry_avg_units_per_hour": 7}
)

print(f"Units Per Labor Hour: {result['productivity_metrics']['units_per_hour']}")
```

## Test Execution
```python
from productivity_calculator import calculate_productivity

result = calculate_productivity(
    analysis_id=input_data.get('analysis_id'),
    production_data=input_data.get('production_data', []),
    labor_data=input_data.get('labor_data', []),
    standard_times=input_data.get('standard_times', {}),
    downtime_records=input_data.get('downtime_records', []),
    benchmark_data=input_data.get('benchmark_data', {})
)
```
