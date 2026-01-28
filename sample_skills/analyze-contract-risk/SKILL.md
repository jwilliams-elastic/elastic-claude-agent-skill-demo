# Skill: Analyze Contract Risk

## Domain
legal_operations

## Description
Analyzes legal contracts to identify risk clauses, compliance gaps, and unfavorable terms for contract negotiation and management.

## Tags
contracts, legal, risk, compliance, CLM, procurement

## Use Cases
- Contract risk scoring
- Clause analysis
- Compliance verification
- Negotiation support

## Proprietary Business Rules

### Rule 1: Risk Clause Detection
Identification of high-risk contract provisions.

### Rule 2: Standard Terms Comparison
Deviation from standard contract templates.

### Rule 3: Compliance Verification
Regulatory and policy compliance check.

### Rule 4: Financial Exposure Analysis
Liability cap and indemnification assessment.

## Input Parameters
- `contract_id` (string): Contract identifier
- `contract_metadata` (dict): Contract information
- `extracted_clauses` (list): Key contract clauses
- `standard_template` (dict): Standard terms baseline
- `compliance_requirements` (list): Required provisions
- `financial_thresholds` (dict): Acceptable limits

## Output
- `risk_score` (float): Overall contract risk
- `risk_clauses` (list): High-risk provisions
- `deviations` (list): Template deviations
- `compliance_gaps` (list): Missing requirements
- `recommendations` (list): Negotiation points

## Implementation
The analysis logic is implemented in `contract_analyzer.py` and references data from `contract_standards.json`.

## Usage Example
```python
from contract_analyzer import analyze_contract

result = analyze_contract(
    contract_id="CTR-001",
    contract_metadata={"type": "vendor", "value": 500000, "term_years": 3},
    extracted_clauses=[{"type": "liability", "text": "unlimited liability"}],
    standard_template={"liability_cap": "2x_annual_fees"},
    compliance_requirements=["data_protection", "audit_rights"],
    financial_thresholds={"max_liability_multiple": 2, "min_indemnity_cap": 1000000}
)

print(f"Risk Score: {result['risk_score']}")
```

## Test Execution
```python
from contract_analyzer import analyze_contract

result = analyze_contract(
    contract_id=input_data.get('contract_id'),
    contract_metadata=input_data.get('contract_metadata', {}),
    extracted_clauses=input_data.get('extracted_clauses', []),
    standard_template=input_data.get('standard_template', {}),
    compliance_requirements=input_data.get('compliance_requirements', []),
    financial_thresholds=input_data.get('financial_thresholds', {})
)
```
