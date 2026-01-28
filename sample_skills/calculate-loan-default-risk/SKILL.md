# Skill: Calculate Loan Default Risk

## Domain
financial_services

## Description
Calculates probability of default (PD) for loan applications using proprietary credit scoring models that incorporate traditional and alternative data sources.

## Tags
banking, credit-risk, loan-underwriting, default-prediction, financial-services

## Use Cases
- Loan application decisioning
- Portfolio risk assessment
- Pricing risk adjustment
- Regulatory capital calculation

## Proprietary Business Rules

### Rule 1: Scorecard Weighting
Proprietary weights for credit factors based on historical default correlation analysis.

### Rule 2: Segment-Specific Models
Different scoring models for prime, near-prime, and subprime segments.

### Rule 3: Behavioral Overlay
Recent payment behavior adjustments to base credit score.

### Rule 4: Concentration Limits
Industry and geographic concentration risk adjustments.

## Input Parameters
- `application_id` (string): Loan application identifier
- `credit_score` (int): FICO or equivalent score
- `debt_to_income` (float): DTI ratio
- `loan_amount` (float): Requested loan amount
- `loan_purpose` (string): Purpose of loan
- `employment_months` (int): Months at current employer
- `annual_income` (float): Annual gross income
- `existing_debt` (float): Total existing debt
- `payment_history` (dict): Recent payment behavior

## Output
- `probability_of_default` (float): PD score (0-1)
- `risk_grade` (string): Internal risk grade
- `decision` (string): Approve, decline, or refer
- `pricing_adjustment` (float): Rate adjustment bps
- `risk_factors` (list): Contributing risk factors

## Implementation
The risk calculation logic is implemented in `risk_calculator.py` and references scoring parameters from CSV files:
- `segments.csv` - Reference data
- `adjustments.csv` - Reference data
- `loan_purposes.csv` - Reference data
- `risk_grades.csv` - Reference data
- `pricing_grid.csv` - Reference data
- `decision_thresholds.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from risk_calculator import calculate_default_risk

result = calculate_default_risk(
    application_id="APP-2024-12345",
    credit_score=720,
    debt_to_income=0.35,
    loan_amount=25000,
    loan_purpose="debt_consolidation",
    employment_months=36,
    annual_income=85000,
    existing_debt=15000,
    payment_history={"late_30_count": 0, "late_60_count": 0}
)

print(f"PD: {result['probability_of_default']}")
print(f"Decision: {result['decision']}")
```

## Test Execution
```python
from risk_calculator import calculate_default_risk

result = calculate_default_risk(
    application_id=input_data.get('application_id'),
    credit_score=input_data.get('credit_score'),
    debt_to_income=input_data.get('debt_to_income'),
    loan_amount=input_data.get('loan_amount'),
    loan_purpose=input_data.get('loan_purpose'),
    employment_months=input_data.get('employment_months', 0),
    annual_income=input_data.get('annual_income'),
    existing_debt=input_data.get('existing_debt', 0),
    payment_history=input_data.get('payment_history', {})
)
```
