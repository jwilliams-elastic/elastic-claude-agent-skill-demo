# Skill: Validate Credit Exposure

## Domain
financial_services

## Description
Validates counterparty credit exposure calculations including potential future exposure, credit limits, and collateral adequacy for risk management.

## Tags
credit-risk, exposure, counterparty, collateral, limits, trading

## Use Cases
- Credit limit monitoring
- PFE calculation validation
- Collateral adequacy check
- Exposure aggregation

## Proprietary Business Rules

### Rule 1: Exposure Calculation
Mark-to-market plus potential future exposure.

### Rule 2: Netting Validation
Validation of netting agreement application.

### Rule 3: Collateral Coverage
Assessment of collateral against exposure.

### Rule 4: Limit Breach Detection
Identification of credit limit breaches.

## Input Parameters
- `counterparty_id` (string): Counterparty identifier
- `positions` (list): Current positions with counterparty
- `market_data` (dict): Current market prices
- `netting_agreements` (dict): Netting arrangement details
- `collateral` (dict): Posted collateral information
- `credit_limits` (dict): Approved credit limits

## Output
- `current_exposure` (float): Current credit exposure
- `potential_exposure` (float): Potential future exposure
- `collateral_coverage` (dict): Collateral adequacy
- `limit_utilization` (dict): Limit usage analysis
- `breach_alerts` (list): Any limit breaches

## Implementation
The validation logic is implemented in `exposure_validator.py` and references data from `credit_parameters.json`.

## Usage Example
```python
from exposure_validator import validate_exposure

result = validate_exposure(
    counterparty_id="CPTY-001",
    positions=[{"type": "swap", "notional": 10000000, "mtm": 250000}],
    market_data={"rates": {"USD": 0.05}, "fx": {"EURUSD": 1.08}},
    netting_agreements={"type": "ISDA", "enforceable": True},
    collateral={"cash": 100000, "securities": 50000},
    credit_limits={"total": 5000000, "unsecured": 2000000}
)

print(f"Current Exposure: ${result['current_exposure']:,.0f}")
```

## Test Execution
```python
from exposure_validator import validate_exposure

result = validate_exposure(
    counterparty_id=input_data.get('counterparty_id'),
    positions=input_data.get('positions', []),
    market_data=input_data.get('market_data', {}),
    netting_agreements=input_data.get('netting_agreements', {}),
    collateral=input_data.get('collateral', {}),
    credit_limits=input_data.get('credit_limits', {})
)
```
