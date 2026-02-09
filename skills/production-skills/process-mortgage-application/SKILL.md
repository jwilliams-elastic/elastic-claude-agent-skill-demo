# Skill: Process Mortgage Application

## Domain
financial_services

## Description
Processes mortgage loan applications by evaluating borrower creditworthiness, property valuation, and debt-to-income ratios against lending guidelines.

## Tags
mortgage, lending, underwriting, credit, real-estate, banking

## Use Cases
- Mortgage pre-qualification
- Loan application processing
- Credit risk assessment
- Debt-to-income analysis

## Proprietary Business Rules

### Rule 1: Credit Score Evaluation
Tiered pricing based on FICO score bands.

### Rule 2: DTI Ratio Limits
Maximum debt-to-income ratio thresholds by loan program.

### Rule 3: LTV Requirements
Loan-to-value limits and PMI requirements.

### Rule 4: Income Verification
Documentation requirements for income validation.

## Input Parameters
- `application_id` (string): Application identifier
- `borrower_info` (dict): Borrower financial profile
- `property_info` (dict): Property details
- `loan_request` (dict): Requested loan terms
- `credit_report` (dict): Credit information
- `income_documents` (list): Income verification docs

## Output
- `decision` (string): Approval decision
- `approved_amount` (float): Maximum approved loan
- `interest_rate` (float): Offered interest rate
- `conditions` (list): Approval conditions
- `risk_assessment` (dict): Risk analysis details

## Implementation
The processing logic is implemented in `mortgage_processor.py` and references data from CSV files:
- `credit_tiers.csv` - Reference data
- `ltv_limits.csv` - Reference data
- `loan_programs.csv` - Reference data
- `pmi_rates.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from mortgage_processor import process_application

result = process_application(
    application_id="MTG-2026-001",
    borrower_info={"annual_income": 120000, "employment_years": 5},
    property_info={"value": 450000, "type": "single_family"},
    loan_request={"amount": 360000, "term_years": 30},
    credit_report={"fico_score": 740, "derogatory_marks": 0},
    income_documents=[{"type": "w2", "verified": True}]
)

print(f"Decision: {result['decision']}")
```

## Test Execution
```python
from mortgage_processor import process_application

result = process_application(
    application_id=input_data.get('application_id'),
    borrower_info=input_data.get('borrower_info', {}),
    property_info=input_data.get('property_info', {}),
    loan_request=input_data.get('loan_request', {}),
    credit_report=input_data.get('credit_report', {}),
    income_documents=input_data.get('income_documents', [])
)
```
