# Skill: Validate Transaction Limits

## Domain
financial_services

## Description
Validates financial transactions against configured limits including velocity checks, cumulative limits, and authorization rules.

## Tags
payments, limits, fraud, authorization, banking, compliance

## Use Cases
- Transaction authorization
- Limit enforcement
- Velocity checking
- Fraud prevention

## Proprietary Business Rules

### Rule 1: Single Transaction Limits
Per-transaction amount validation.

### Rule 2: Velocity Limits
Transaction frequency and cumulative checks.

### Rule 3: Customer-Specific Limits
Personalized limit application.

### Rule 4: Override Authorization
Exception handling and approval workflow.

## Input Parameters
- `transaction_id` (string): Transaction identifier
- `transaction_details` (dict): Transaction information
- `account_info` (dict): Account details
- `customer_limits` (dict): Customer-specific limits
- `transaction_history` (list): Recent transactions
- `override_request` (dict): Override details if applicable

## Output
- `authorization_result` (string): Approve/Decline/Review
- `limit_check_results` (dict): Individual limit outcomes
- `velocity_analysis` (dict): Velocity check results
- `override_required` (bool): Override needed flag
- `decline_reasons` (list): Decline reason codes

## Implementation
The validation logic is implemented in `limits_validator.py` and references data from `limit_rules.json`.

## Usage Example
```python
from limits_validator import validate_limits

result = validate_limits(
    transaction_id="TXN-001",
    transaction_details={"amount": 5000, "type": "transfer", "channel": "mobile"},
    account_info={"id": "ACCT-001", "type": "checking", "tier": "premium"},
    customer_limits={"daily_transfer": 10000, "single_transfer": 5000},
    transaction_history=[{"date": "2025-12-15", "amount": 3000, "type": "transfer"}],
    override_request=None
)

print(f"Authorization: {result['authorization_result']}")
```

## Test Execution
```python
from limits_validator import validate_limits

result = validate_limits(
    transaction_id=input_data.get('transaction_id'),
    transaction_details=input_data.get('transaction_details', {}),
    account_info=input_data.get('account_info', {}),
    customer_limits=input_data.get('customer_limits', {}),
    transaction_history=input_data.get('transaction_history', []),
    override_request=input_data.get('override_request')
)
```
