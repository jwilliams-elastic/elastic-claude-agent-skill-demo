# Skill: Process Trade Settlement

## Domain
financial_services

## Description
Processes securities trade settlements validating matching, calculating obligations, and managing settlement exceptions across T+1/T+2 cycles.

## Tags
securities, settlement, trading, clearing, finance, operations

## Use Cases
- Trade matching validation
- Settlement obligation calculation
- Exception management
- Fail prediction

## Proprietary Business Rules

### Rule 1: Trade Matching
Validation of trade details between counterparties.

### Rule 2: Settlement Date Calculation
T+1/T+2 settlement date determination by security type.

### Rule 3: Obligation Netting
Net settlement obligation calculation across trades.

### Rule 4: Fail Risk Assessment
Prediction of potential settlement failures.

## Input Parameters
- `trade_id` (string): Trade identifier
- `trade_details` (dict): Trade information
- `counterparty_info` (dict): Counterparty details
- `security_info` (dict): Security details
- `position_data` (dict): Current positions
- `settlement_instructions` (dict): SSI information

## Output
- `settlement_status` (string): Processing status
- `settlement_date` (string): Calculated settlement date
- `net_obligation` (dict): Net settlement amounts
- `matching_status` (dict): Match validation results
- `fail_risk` (dict): Fail probability assessment

## Implementation
The processing logic is implemented in `settlement_processor.py` and references data from CSV files:
- `settlement_cycles.csv` - Reference data
- `risk_factors.csv` - Reference data
- `fee_schedules.csv` - Reference data
- `fail_management.csv` - Reference data
- `netting_rules.csv` - Reference data
- `regulatory_reporting.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from settlement_processor import process_settlement

result = process_settlement(
    trade_id="TRD-2026-001",
    trade_details={"side": "buy", "quantity": 1000, "price": 150.50, "trade_date": "2026-01-20"},
    counterparty_info={"id": "CPTY-001", "dtc_number": "0123"},
    security_info={"cusip": "037833100", "type": "equity"},
    position_data={"available": 0, "pending_receipts": 1000},
    settlement_instructions={"account": "12345", "agent": "DTC"}
)

print(f"Settlement Date: {result['settlement_date']}")
```

## Test Execution
```python
from settlement_processor import process_settlement

result = process_settlement(
    trade_id=input_data.get('trade_id'),
    trade_details=input_data.get('trade_details', {}),
    counterparty_info=input_data.get('counterparty_info', {}),
    security_info=input_data.get('security_info', {}),
    position_data=input_data.get('position_data', {}),
    settlement_instructions=input_data.get('settlement_instructions', {})
)
```
