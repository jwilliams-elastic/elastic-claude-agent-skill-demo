# Skill: Validate AML Transaction

## Domain
financial_services

## Description
Validates transactions against anti-money laundering rules including suspicious activity detection, sanctions screening, and regulatory reporting triggers.

## Tags
AML, compliance, sanctions, BSA, financial-crime, KYC

## Use Cases
- Transaction monitoring
- Suspicious activity detection
- Sanctions screening
- SAR filing determination

## Proprietary Business Rules

### Rule 1: Pattern Detection
Identification of structuring, layering, and other suspicious patterns.

### Rule 2: Sanctions Screening
OFAC and international sanctions list matching.

### Rule 3: Risk Scoring
Transaction risk scoring based on multiple factors.

### Rule 4: SAR Threshold Analysis
Determination of SAR filing requirements.

## Input Parameters
- `transaction_id` (string): Transaction identifier
- `transaction_details` (dict): Transaction information
- `customer_info` (dict): Customer profile
- `account_history` (list): Recent account activity
- `counterparty_info` (dict): Counterparty details
- `geographic_data` (dict): Location information

## Output
- `risk_score` (float): Transaction risk score
- `alerts` (list): Generated alerts
- `sanctions_result` (dict): Sanctions screening results
- `sar_recommendation` (dict): SAR filing determination
- `required_actions` (list): Required compliance actions

## Implementation
The validation logic is implemented in `aml_validator.py` and references data from CSV files:
- `transaction_thresholds.csv` - Reference data
- `risk_scoring.csv` - Reference data
- `red_flags.csv` - Reference data
- `alert_thresholds.csv` - Reference data
- `velocity_rules.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from aml_validator import validate_aml

result = validate_aml(
    transaction_id="TXN-2026-001",
    transaction_details={"amount": 9500, "type": "wire", "currency": "USD"},
    customer_info={"id": "CUST-001", "risk_rating": "medium", "occupation": "import_export"},
    account_history=[{"date": "2025-12-01", "amount": 9200, "type": "wire"}],
    counterparty_info={"name": "ABC Corp", "country": "AE"},
    geographic_data={"origin_country": "US", "destination_country": "AE"}
)

print(f"Risk Score: {result['risk_score']}")
```

## Test Execution
```python
from aml_validator import validate_aml

result = validate_aml(
    transaction_id=input_data.get('transaction_id'),
    transaction_details=input_data.get('transaction_details', {}),
    customer_info=input_data.get('customer_info', {}),
    account_history=input_data.get('account_history', []),
    counterparty_info=input_data.get('counterparty_info', {}),
    geographic_data=input_data.get('geographic_data', {})
)
```
