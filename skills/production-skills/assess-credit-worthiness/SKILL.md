# Skill: Assess Credit Worthiness

## Domain
financial_services

## Description
Assesses borrower creditworthiness using financial analysis, credit scoring, and risk-adjusted pricing for lending decisions.

## Tags
credit, lending, underwriting, risk, scoring, banking

## Use Cases
- Credit decisioning
- Risk-based pricing
- Portfolio management
- Limit setting

## Proprietary Business Rules

### Rule 1: Credit Score Integration
Bureau score and internal score combination.

### Rule 2: Financial Ratio Analysis
Key financial health indicators.

### Rule 3: Capacity Assessment
Debt service coverage evaluation.

### Rule 4: Risk Grade Assignment
Credit risk grade determination.

## Input Parameters
- `application_id` (string): Application identifier
- `borrower_info` (dict): Borrower profile
- `financial_statements` (dict): Financial data
- `credit_bureau` (dict): Bureau information
- `collateral_info` (dict): Security details
- `loan_request` (dict): Requested terms

## Output
- `credit_score` (float): Combined credit score
- `risk_grade` (string): Assigned risk grade
- `financial_analysis` (dict): Ratio analysis
- `pricing_recommendation` (dict): Risk-adjusted pricing
- `decision` (string): Approval recommendation
- `conditions` (list): Required conditions

## Implementation
The assessment logic is implemented in `credit_assessor.py` and references data from `credit_criteria.json`.

## Usage Example
```python
from credit_assessor import assess_credit

result = assess_credit(
    application_id="APP-001",
    borrower_info={"type": "business", "years_in_business": 10, "industry": "manufacturing"},
    financial_statements={"revenue": 5000000, "ebitda": 750000, "total_debt": 1000000},
    credit_bureau={"business_score": 75, "payment_history": "satisfactory"},
    collateral_info={"type": "real_estate", "value": 2000000},
    loan_request={"amount": 500000, "term_years": 5, "purpose": "expansion"}
)

print(f"Risk Grade: {result['risk_grade']}")
```

## Test Execution
```python
from credit_assessor import assess_credit

result = assess_credit(
    application_id=input_data.get('application_id'),
    borrower_info=input_data.get('borrower_info', {}),
    financial_statements=input_data.get('financial_statements', {}),
    credit_bureau=input_data.get('credit_bureau', {}),
    collateral_info=input_data.get('collateral_info', {}),
    loan_request=input_data.get('loan_request', {})
)
```
