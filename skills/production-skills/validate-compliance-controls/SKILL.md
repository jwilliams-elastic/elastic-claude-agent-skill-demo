# Skill: Validate Compliance Controls

## Domain
financial_services

## Description
Validates internal compliance controls against regulatory requirements testing effectiveness and identifying control gaps.

## Tags
compliance, controls, audit, SOX, regulatory, risk

## Use Cases
- Control testing
- Compliance gap analysis
- Audit preparation
- Control remediation

## Proprietary Business Rules

### Rule 1: Control Effectiveness Testing
Control design and operating effectiveness evaluation.

### Rule 2: Regulatory Mapping
Control to regulatory requirement mapping.

### Rule 3: Gap Identification
Missing or weak control identification.

### Rule 4: Remediation Prioritization
Control improvement prioritization.

## Input Parameters
- `assessment_id` (string): Assessment identifier
- `control_inventory` (list): Controls to assess
- `test_results` (list): Control testing outcomes
- `regulatory_requirements` (list): Applicable requirements
- `prior_assessments` (list): Historical results
- `risk_ratings` (dict): Process risk levels

## Output
- `compliance_score` (float): Overall compliance rating
- `control_effectiveness` (dict): Effectiveness by control
- `gaps_identified` (list): Control gaps
- `regulatory_coverage` (dict): Requirement coverage
- `remediation_plan` (list): Recommended actions

## Implementation
The validation logic is implemented in `compliance_validator.py` and references data from `compliance_framework.json`.

## Usage Example
```python
from compliance_validator import validate_controls

result = validate_controls(
    assessment_id="CMP-001",
    control_inventory=[{"id": "CTL-001", "type": "preventive", "process": "payments"}],
    test_results=[{"control_id": "CTL-001", "result": "effective", "sample_size": 25}],
    regulatory_requirements=[{"id": "SOX-404", "control_ids": ["CTL-001"]}],
    prior_assessments=[{"period": "2024", "score": 85}],
    risk_ratings={"payments": "high"}
)

print(f"Compliance Score: {result['compliance_score']}")
```

## Test Execution
```python
from compliance_validator import validate_controls

result = validate_controls(
    assessment_id=input_data.get('assessment_id'),
    control_inventory=input_data.get('control_inventory', []),
    test_results=input_data.get('test_results', []),
    regulatory_requirements=input_data.get('regulatory_requirements', []),
    prior_assessments=input_data.get('prior_assessments', []),
    risk_ratings=input_data.get('risk_ratings', {})
)
```
