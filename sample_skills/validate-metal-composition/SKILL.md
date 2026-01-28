# Skill: Validate Metal Alloy Composition

## Domain
metals

## Description
Analyzes metal alloy composition against specification requirements and industry standards to verify compliance and grade classification.

## Tags
metals, metallurgy, quality-control, composition-analysis, material-certification

## Use Cases
- Incoming material verification
- Grade classification
- Specification compliance
- Customer certification

## Proprietary Business Rules

### Rule 1: Composition Tolerance Bands
Element concentration tolerances vary by alloy grade with proprietary acceptance limits.

### Rule 2: Trace Element Limits
Cumulative trace element limits for premium grades.

### Rule 3: Mechanical Property Correlation
Composition validation against expected mechanical properties.

### Rule 4: Customer-Specific Requirements
Enhanced specifications for specific customer applications.

## Input Parameters
- `sample_id` (string): Sample identifier
- `alloy_family` (string): Steel, aluminum, titanium, etc.
- `target_grade` (string): Target alloy grade
- `composition` (dict): Element percentages from analysis
- `heat_number` (string): Production heat identifier
- `customer_spec` (string): Customer specification if any
- `intended_application` (string): End use application

## Output
- `grade_verified` (bool): Meets grade specification
- `compliance_status` (string): Compliant, non-compliant, marginal
- `element_analysis` (list): Per-element compliance status
- `alternative_grades` (list): Other grades this composition meets
- `recommendations` (list): Actions for non-compliant material

## Implementation
The validation logic is implemented in `composition_validator.py` and references specifications from `alloy_specs.csv`.

## Usage Example
```python
from composition_validator import validate_composition

result = validate_composition(
    sample_id="MET-2024-001",
    alloy_family="stainless_steel",
    target_grade="304",
    composition={"C": 0.05, "Cr": 18.2, "Ni": 8.5, "Mn": 1.5, "Si": 0.5},
    heat_number="H-2024-1234",
    customer_spec="aerospace_standard",
    intended_application="pressure_vessel"
)

print(f"Grade Verified: {result['grade_verified']}")
```

## Test Execution
```python
from composition_validator import validate_composition

result = validate_composition(
    sample_id=input_data.get('sample_id'),
    alloy_family=input_data.get('alloy_family'),
    target_grade=input_data.get('target_grade'),
    composition=input_data.get('composition', {}),
    heat_number=input_data.get('heat_number'),
    customer_spec=input_data.get('customer_spec'),
    intended_application=input_data.get('intended_application')
)
```
