# Skill: Analyze Cohort Retention

## Domain
technology

## Description
Analyzes customer cohort retention patterns to understand lifecycle behavior, predict churn, and optimize engagement strategies.

## Tags
retention, cohort, analytics, SaaS, customer, lifecycle

## Use Cases
- Cohort analysis
- Retention curve modeling
- LTV prediction
- Engagement optimization

## Proprietary Business Rules

### Rule 1: Cohort Definition
Time-based cohort grouping methodology.

### Rule 2: Retention Calculation
Period-over-period retention measurement.

### Rule 3: Curve Fitting
Retention curve modeling and projection.

### Rule 4: Benchmarking
Industry retention comparison.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `user_data` (list): User acquisition and activity
- `cohort_config` (dict): Cohort definition parameters
- `activity_data` (list): User activity events
- `benchmark_data` (dict): Industry benchmarks
- `analysis_period` (dict): Time range for analysis

## Output
- `retention_matrix` (dict): Cohort retention grid
- `retention_curves` (dict): Fitted retention curves
- `cohort_comparison` (dict): Cross-cohort analysis
- `ltv_projection` (dict): Lifetime value estimates
- `insights` (list): Key findings

## Implementation
The analysis logic is implemented in `cohort_analyzer.py` and references data from `retention_benchmarks.json`.

## Usage Example
```python
from cohort_analyzer import analyze_cohorts

result = analyze_cohorts(
    analysis_id="COH-001",
    user_data=[{"user_id": "U-001", "signup_date": "2025-01-15", "plan": "pro"}],
    cohort_config={"period": "monthly", "metric": "active_users"},
    activity_data=[{"user_id": "U-001", "date": "2025-02-01", "event": "login"}],
    benchmark_data={"saas_avg_m1": 0.80, "saas_avg_m6": 0.50},
    analysis_period={"start": "2025-01-01", "end": "2025-12-31"}
)

print(f"Month 1 Retention: {result['retention_matrix']['M1']:.1%}")
```

## Test Execution
```python
from cohort_analyzer import analyze_cohorts

result = analyze_cohorts(
    analysis_id=input_data.get('analysis_id'),
    user_data=input_data.get('user_data', []),
    cohort_config=input_data.get('cohort_config', {}),
    activity_data=input_data.get('activity_data', []),
    benchmark_data=input_data.get('benchmark_data', {}),
    analysis_period=input_data.get('analysis_period', {})
)
```
