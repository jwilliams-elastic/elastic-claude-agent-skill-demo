# Skill: Process Warranty Claim

## Domain
consumer_products

## Description
Processes product warranty claims validating coverage, assessing claim validity, and determining resolution including repair, replacement, or refund.

## Tags
warranty, claims, customer-service, products, returns, support

## Use Cases
- Warranty coverage verification
- Claim validity assessment
- Resolution determination
- Fraud detection

## Proprietary Business Rules

### Rule 1: Coverage Verification
Validation of warranty period and coverage terms.

### Rule 2: Defect Classification
Categorization of reported issues by defect type.

### Rule 3: Resolution Matrix
Determination of appropriate resolution based on defect and coverage.

### Rule 4: Fraud Pattern Detection
Identification of suspicious claim patterns.

## Input Parameters
- `claim_id` (string): Claim identifier
- `product_info` (dict): Product details
- `purchase_info` (dict): Purchase information
- `defect_description` (dict): Reported issue
- `customer_history` (dict): Customer claim history
- `diagnostic_data` (dict): Technical diagnostics if available

## Output
- `claim_status` (string): Approved/Denied/Pending
- `coverage_verification` (dict): Coverage analysis
- `resolution` (dict): Recommended resolution
- `cost_estimate` (float): Estimated claim cost
- `fraud_indicators` (list): Any fraud flags

## Implementation
The processing logic is implemented in `warranty_processor.py` and references data from CSV files:
- `coverage_terms.csv` - Reference data
- `defect_categories.csv` - Reference data
- `resolution_matrix.csv` - Reference data
- `fraud_rules.csv` - Reference data
- `cost_tables.csv` - Reference data
- `sla_targets.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from warranty_processor import process_warranty_claim

result = process_warranty_claim(
    claim_id="WC-2026-001",
    product_info={"sku": "PROD-001", "category": "electronics", "purchase_date": "2025-06-15"},
    purchase_info={"receipt": True, "channel": "retail", "price": 499.99},
    defect_description={"type": "malfunction", "symptom": "won't power on"},
    customer_history={"prior_claims": 0, "customer_since": "2020-01-01"},
    diagnostic_data={"error_code": "E01", "battery_cycles": 150}
)

print(f"Claim Status: {result['claim_status']}")
```

## Test Execution
```python
from warranty_processor import process_warranty_claim

result = process_warranty_claim(
    claim_id=input_data.get('claim_id'),
    product_info=input_data.get('product_info', {}),
    purchase_info=input_data.get('purchase_info', {}),
    defect_description=input_data.get('defect_description', {}),
    customer_history=input_data.get('customer_history', {}),
    diagnostic_data=input_data.get('diagnostic_data', {})
)
```
