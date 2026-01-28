# Skill: Evaluate Clinical Trial Eligibility

## Domain
healthcare

## Description
Screens patient profiles against clinical trial inclusion/exclusion criteria using protocol-specific rules and medical coding standards.

## Tags
healthcare, clinical-trials, patient-screening, eligibility, medical-coding

## Use Cases
- Patient pre-screening for trials
- Site feasibility assessment
- Protocol amendment impact analysis
- Cohort identification

## Proprietary Business Rules

### Rule 1: Inclusion Criteria Matching
Multi-factor matching against protocol-defined inclusion criteria with weighted scoring.

### Rule 2: Exclusion Criteria Enforcement
Hard exclusions that immediately disqualify regardless of inclusion score.

### Rule 3: Lab Value Windows
Time-sensitive lab values must fall within protocol windows relative to screening date.

### Rule 4: Concomitant Medication Check
Prohibited medications with washout period requirements.

## Input Parameters
- `patient_id` (string): Patient identifier
- `protocol_id` (string): Clinical trial protocol
- `demographics` (dict): Age, sex, ethnicity
- `diagnosis_codes` (list): ICD-10 diagnosis codes
- `lab_results` (list): Recent laboratory values
- `medications` (list): Current medications
- `medical_history` (list): Relevant medical history codes

## Output
- `eligibility_status` (string): Eligible, ineligible, pending_review
- `inclusion_score` (float): Weighted inclusion criteria score
- `exclusion_flags` (list): Triggered exclusion criteria
- `missing_data` (list): Required data not provided
- `recommendations` (list): Next steps for enrollment

## Implementation
The eligibility logic is implemented in `eligibility_screener.py` and references protocol criteria from CSV files:
- `protocols.csv` - Reference data
- `lab_time_windows.csv` - Reference data
- `score_thresholds.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from eligibility_screener import evaluate_eligibility

result = evaluate_eligibility(
    patient_id="PT-12345",
    protocol_id="ONCO-2024-001",
    demographics={"age": 58, "sex": "F", "ethnicity": "caucasian"},
    diagnosis_codes=["C50.911", "Z85.3"],
    lab_results=[{"test": "ANC", "value": 1800, "date": "2026-01-10"}],
    medications=["metformin", "lisinopril"],
    medical_history=["Z86.73"]
)

print(f"Status: {result['eligibility_status']}")
```

## Test Execution
```python
from eligibility_screener import evaluate_eligibility

result = evaluate_eligibility(
    patient_id=input_data.get('patient_id'),
    protocol_id=input_data.get('protocol_id'),
    demographics=input_data.get('demographics', {}),
    diagnosis_codes=input_data.get('diagnosis_codes', []),
    lab_results=input_data.get('lab_results', []),
    medications=input_data.get('medications', []),
    medical_history=input_data.get('medical_history', [])
)
```
