# Skill: Process Invoice Accuracy

## Domain
financial_services

## Description
Processes and validates invoice accuracy by matching against purchase orders, contracts, and receiving records.

## Tags
invoicing, AP, procurement, matching, accuracy, finance

## Use Cases
- 3-way matching
- Invoice validation
- Duplicate detection
- Payment authorization

## Proprietary Business Rules

### Rule 1: Three-Way Matching
Invoice to PO to receipt matching.

### Rule 2: Price Variance Detection
Unit price discrepancy identification.

### Rule 3: Quantity Verification
Quantity accuracy validation.

### Rule 4: Duplicate Prevention
Duplicate invoice detection.

## Input Parameters
- `invoice_id` (string): Invoice identifier
- `invoice_data` (dict): Invoice details
- `purchase_order` (dict): Related PO data
- `receiving_records` (list): Receipt documentation
- `contract_terms` (dict): Applicable contract
- `tolerance_rules` (dict): Matching tolerances

## Output
- `match_result` (string): Match status
- `variances` (list): Identified discrepancies
- `duplicate_check` (dict): Duplicate detection
- `approval_status` (string): Payment authorization
- `exceptions` (list): Required actions

## Implementation
The processing logic is implemented in `invoice_processor.py` and references data from `invoice_rules.json`.

## Usage Example
```python
from invoice_processor import process_invoice

result = process_invoice(
    invoice_id="INV-001",
    invoice_data={"amount": 10500, "vendor": "VND-001", "line_items": [{"qty": 100, "price": 105}]},
    purchase_order={"po_number": "PO-001", "line_items": [{"qty": 100, "price": 100}]},
    receiving_records=[{"po": "PO-001", "qty_received": 100}],
    contract_terms={"price_per_unit": 100, "effective_date": "2025-01-01"},
    tolerance_rules={"price_variance_pct": 0.05, "quantity_variance_units": 2}
)

print(f"Match Result: {result['match_result']}")
```

## Test Execution
```python
from invoice_processor import process_invoice

result = process_invoice(
    invoice_id=input_data.get('invoice_id'),
    invoice_data=input_data.get('invoice_data', {}),
    purchase_order=input_data.get('purchase_order', {}),
    receiving_records=input_data.get('receiving_records', []),
    contract_terms=input_data.get('contract_terms', {}),
    tolerance_rules=input_data.get('tolerance_rules', {})
)
```
