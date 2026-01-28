# Skill: Analyze Customer Churn

## Domain
technology

## Description
Analyzes customer churn risk using behavioral signals, usage patterns, and engagement metrics to identify at-risk accounts for retention intervention.

## Tags
churn, retention, customer-success, SaaS, analytics, machine-learning

## Use Cases
- Churn risk scoring
- Early warning detection
- Retention campaign targeting
- Customer health monitoring

## Proprietary Business Rules

### Rule 1: Engagement Decay Detection
Identification of declining usage patterns over time.

### Rule 2: Risk Signal Weighting
Weighted scoring of behavioral churn indicators.

### Rule 3: Cohort Comparison
Risk assessment relative to similar customer segments.

### Rule 4: Intervention Prioritization
Ranking of at-risk customers by value and savability.

## Input Parameters
- `customer_id` (string): Customer identifier
- `usage_metrics` (dict): Product usage data
- `engagement_history` (list): Interaction timeline
- `account_info` (dict): Customer profile
- `support_tickets` (list): Support history
- `billing_history` (list): Payment patterns

## Output
- `churn_risk_score` (float): Risk probability 0-100
- `risk_factors` (list): Contributing factors
- `risk_trend` (string): Increasing/stable/decreasing
- `recommended_actions` (list): Retention interventions
- `predicted_churn_date` (string): Estimated churn timing

## Implementation
The analysis logic is implemented in `churn_analyzer.py` and references data from CSV files:
- `usage_benchmarks.csv` - Reference data
- `engagement_windows.csv` - Reference data
- `sentiment_weights.csv` - Reference data
- `billing_thresholds.csv` - Reference data
- `savability_factors.csv` - Reference data
- `risk_weights.csv` - Reference data
- `signal_definitions.csv` - Reference data
- `intervention_playbook.csv` - Reference data
- `cohort_benchmarks.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from churn_analyzer import analyze_churn

result = analyze_churn(
    customer_id="CUST-001",
    usage_metrics={"logins_30d": 5, "features_used": 3, "api_calls": 100},
    engagement_history=[{"date": "2025-12-01", "type": "login"}],
    account_info={"mrr": 5000, "tenure_months": 18, "plan": "enterprise"},
    support_tickets=[{"date": "2025-12-15", "category": "bug", "sentiment": "negative"}],
    billing_history=[{"date": "2025-12-01", "status": "paid", "days_late": 0}]
)

print(f"Churn Risk: {result['churn_risk_score']}%")
```

## Test Execution
```python
from churn_analyzer import analyze_churn

result = analyze_churn(
    customer_id=input_data.get('customer_id'),
    usage_metrics=input_data.get('usage_metrics', {}),
    engagement_history=input_data.get('engagement_history', []),
    account_info=input_data.get('account_info', {}),
    support_tickets=input_data.get('support_tickets', []),
    billing_history=input_data.get('billing_history', [])
)
```
