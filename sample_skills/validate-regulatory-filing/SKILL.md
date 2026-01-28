# Skill: Validate Regulatory Filing

## Domain
financial_services

## Description
Validates regulatory filings for completeness, accuracy, and compliance with SEC, FINRA, and other regulatory requirements.

## Tags
regulatory, compliance, SEC, FINRA, filing, reporting

## Use Cases
- Filing completeness check
- Data accuracy validation
- Deadline compliance tracking
- Cross-reference verification

## Proprietary Business Rules

### Rule 1: Form Completeness
Validation of all required fields and attachments.

### Rule 2: Data Consistency
Cross-validation of financial data across forms.

### Rule 3: Deadline Compliance
Filing deadline calculation and tracking.

### Rule 4: Amendment Detection
Identification of material changes requiring amendments.

## Input Parameters
- `filing_id` (string): Filing identifier
- `filing_type` (string): Type of regulatory filing
- `filing_data` (dict): Filing content
- `prior_filings` (list): Previous related filings
- `entity_info` (dict): Filing entity information
- `submission_date` (string): Planned submission date

## Output
- `validation_status` (string): Overall validation result
- `completeness_check` (dict): Missing items report
- `accuracy_issues` (list): Data accuracy findings
- `deadline_status` (dict): Filing deadline analysis
- `required_corrections` (list): Required fixes

## Implementation
The validation logic is implemented in `filing_validator.py` and references data from CSV files:
- `required_fields.csv` - Reference data
- `deadline_rules.csv` - Reference data
- `accuracy_rules.csv` - Reference data
- `amendment_triggers.csv` - Reference data
- `filer_categories.csv` - Reference data
- `xbrl_requirements.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from filing_validator import validate_filing

result = validate_filing(
    filing_id="FIL-2026-001",
    filing_type="10-K",
    filing_data={"fiscal_year_end": "2025-12-31", "total_assets": 1000000000},
    prior_filings=[{"type": "10-Q", "period": "2025-Q3"}],
    entity_info={"cik": "0001234567", "sic": "6022"},
    submission_date="2026-03-01"
)

print(f"Status: {result['validation_status']}")
```

## Test Execution
```python
from filing_validator import validate_filing

result = validate_filing(
    filing_id=input_data.get('filing_id'),
    filing_type=input_data.get('filing_type'),
    filing_data=input_data.get('filing_data', {}),
    prior_filings=input_data.get('prior_filings', []),
    entity_info=input_data.get('entity_info', {}),
    submission_date=input_data.get('submission_date')
)
```
