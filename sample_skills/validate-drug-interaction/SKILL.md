# Skill: Validate Drug Interaction

## Domain
healthcare

## Description
Screens medication combinations for potential drug-drug interactions, contraindications, and dosage adjustments based on patient profile.

## Tags
healthcare, pharmacy, drug-interactions, clinical-decision-support, patient-safety

## Use Cases
- Prescription validation
- Medication reconciliation
- Clinical decision support
- Pharmacy dispensing checks

## Proprietary Business Rules

### Rule 1: Interaction Severity Classification
Multi-level severity scoring based on clinical significance and evidence quality.

### Rule 2: Patient Factor Adjustments
Interaction risk modified by age, renal function, hepatic function.

### Rule 3: Therapeutic Duplication
Detection of overlapping therapeutic classes.

### Rule 4: Timing Recommendations
Administration timing to minimize interactions.

## Input Parameters
- `patient_id` (string): Patient identifier
- `medications` (list): List of medications with doses
- `patient_factors` (dict): Age, weight, renal/hepatic function
- `allergies` (list): Known allergies
- `diagnosis_codes` (list): Active diagnoses

## Output
- `interactions_found` (list): Identified interactions
- `severity_score` (int): Overall risk score
- `recommendations` (list): Clinical recommendations
- `therapeutic_duplications` (list): Duplicate therapy alerts
- `dose_adjustments` (list): Recommended dose changes

## Implementation
The validation logic is implemented in `interaction_checker.py` and references the drug database in CSV files:
- `interactions.csv` - Reference data
- `drug_classes.csv` - Reference data
- `severity_definitions.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from interaction_checker import validate_interactions

result = validate_interactions(
    patient_id="PT-12345",
    medications=[
        {"name": "warfarin", "dose": "5mg", "frequency": "daily"},
        {"name": "aspirin", "dose": "81mg", "frequency": "daily"}
    ],
    patient_factors={"age": 72, "egfr": 45, "weight_kg": 70},
    allergies=["penicillin"],
    diagnosis_codes=["I48.0", "Z79.01"]
)

print(f"Interactions: {len(result['interactions_found'])}")
```

## Test Execution
```python
from interaction_checker import validate_interactions

result = validate_interactions(
    patient_id=input_data.get('patient_id'),
    medications=input_data.get('medications', []),
    patient_factors=input_data.get('patient_factors', {}),
    allergies=input_data.get('allergies', []),
    diagnosis_codes=input_data.get('diagnosis_codes', [])
)
```
