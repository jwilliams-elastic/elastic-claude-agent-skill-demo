# Skill: Process Lease Abstraction

## Domain
real_estate

## Description
Processes commercial lease documents extracting key terms, dates, and financial obligations for lease administration.

## Tags
lease, real-estate, abstraction, contracts, administration, compliance

## Use Cases
- Lease data extraction
- Critical date tracking
- Financial obligation capture
- Portfolio management

## Proprietary Business Rules

### Rule 1: Key Term Extraction
Essential lease term identification.

### Rule 2: Date Calculation
Critical date and deadline computation.

### Rule 3: Financial Obligation Mapping
Rent, CAM, and expense extraction.

### Rule 4: Option Identification
Renewal and termination option capture.

## Input Parameters
- `lease_id` (string): Lease identifier
- `lease_document` (dict): Document content
- `extraction_template` (dict): Fields to extract
- `calculation_rules` (dict): Date calculation rules
- `property_info` (dict): Property details
- `existing_data` (dict): Current lease data

## Output
- `abstracted_terms` (dict): Extracted lease terms
- `critical_dates` (list): Key dates and deadlines
- `financial_summary` (dict): Financial obligations
- `options` (list): Lease options
- `validation_flags` (list): Data quality issues

## Implementation
The processing logic is implemented in `lease_processor.py` and references data from `lease_templates.json`.

## Usage Example
```python
from lease_processor import process_lease

result = process_lease(
    lease_id="LSE-001",
    lease_document={"text": "Lease agreement dated...", "pages": 25},
    extraction_template={"required_fields": ["base_rent", "term", "commencement"]},
    calculation_rules={"notice_period_days": 180},
    property_info={"address": "123 Main St", "sqft": 10000},
    existing_data={}
)

print(f"Base Rent: ${result['financial_summary']['base_rent']:,.0f}")
```

## Test Execution
```python
from lease_processor import process_lease

result = process_lease(
    lease_id=input_data.get('lease_id'),
    lease_document=input_data.get('lease_document', {}),
    extraction_template=input_data.get('extraction_template', {}),
    calculation_rules=input_data.get('calculation_rules', {}),
    property_info=input_data.get('property_info', {}),
    existing_data=input_data.get('existing_data', {})
)
```
