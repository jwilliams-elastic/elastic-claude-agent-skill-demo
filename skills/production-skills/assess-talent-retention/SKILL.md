# Skill: Assess Talent Retention

## Domain
human_resources

## Description
Assesses employee retention risk using engagement signals, compensation analysis, and flight risk modeling for workforce planning.

## Tags
HR, retention, talent, workforce, analytics, engagement

## Use Cases
- Flight risk identification
- Retention program targeting
- Compensation benchmarking
- Engagement analysis

## Proprietary Business Rules

### Rule 1: Flight Risk Scoring
Multi-factor employee attrition risk model.

### Rule 2: Compensation Gap Analysis
Market compensation comparison and internal equity.

### Rule 3: Engagement Signal Analysis
Behavioral indicators of disengagement.

### Rule 4: Intervention Prioritization
High-value employee retention prioritization.

## Input Parameters
- `employee_id` (string): Employee identifier
- `employee_profile` (dict): Employee information
- `compensation_data` (dict): Current compensation
- `engagement_metrics` (dict): Engagement indicators
- `market_data` (dict): Market compensation data
- `performance_history` (list): Performance records

## Output
- `retention_risk_score` (float): Flight risk probability
- `compensation_analysis` (dict): Compensation gap assessment
- `engagement_assessment` (dict): Engagement evaluation
- `risk_factors` (list): Contributing factors
- `retention_recommendations` (list): Recommended actions

## Implementation
The assessment logic is implemented in `retention_assessor.py` and references data from CSV files:
- `retention_risk_factors.csv` - Reference data
- `engagement_indicators.csv` - Reference data
- `turnover_benchmarks.csv` - Reference data
- `replacement_cost_multipliers.csv` - Reference data
- `intervention_strategies.csv` - Reference data
- `flight_risk_thresholds.csv` - Reference data
- `tenure_risk_curve.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from retention_assessor import assess_retention

result = assess_retention(
    employee_id="EMP-001",
    employee_profile={"tenure_years": 3, "role": "engineer", "department": "technology"},
    compensation_data={"base_salary": 120000, "bonus_target": 0.15, "equity_value": 50000},
    engagement_metrics={"survey_score": 3.5, "pto_usage": 0.40, "training_hours": 10},
    market_data={"role_median": 130000, "role_p75": 150000},
    performance_history=[{"year": 2024, "rating": "exceeds"}, {"year": 2025, "rating": "exceeds"}]
)

print(f"Retention Risk: {result['retention_risk_score']}%")
```

## Test Execution
```python
from retention_assessor import assess_retention

result = assess_retention(
    employee_id=input_data.get('employee_id'),
    employee_profile=input_data.get('employee_profile', {}),
    compensation_data=input_data.get('compensation_data', {}),
    engagement_metrics=input_data.get('engagement_metrics', {}),
    market_data=input_data.get('market_data', {}),
    performance_history=input_data.get('performance_history', [])
)
```
