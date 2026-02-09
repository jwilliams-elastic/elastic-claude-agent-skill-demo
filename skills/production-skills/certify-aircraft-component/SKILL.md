# Skill: Certify Aircraft Component

## Domain
aerospace_defense

## Description
Validates aircraft components against FAA/EASA certification requirements, performing airworthiness checks based on proprietary compliance matrices and safety criticality classifications.

## Tags
aerospace, certification, faa-compliance, airworthiness, safety-critical

## Use Cases
- Component airworthiness certification
- Maintenance release authorization
- Parts manufacturer approval (PMA) validation
- Supplemental type certificate (STC) compliance

## Proprietary Business Rules

### Rule 1: Design Assurance Level (DAL) Enforcement
Components are classified by DAL (A-E) with corresponding testing and documentation requirements that increase exponentially with criticality.

### Rule 2: Material Traceability Chain
All materials must have complete traceability to original mill certificates with no breaks in chain of custody.

### Rule 3: Non-Destructive Testing (NDT) Requirements
Components in fatigue-critical zones require specific NDT methods based on material and stress classification.

### Rule 4: Life-Limited Part Tracking
Parts with cyclic limits must be tracked against aircraft utilization data.

## Input Parameters
- `part_number` (string): Aircraft part number
- `serial_number` (string): Unique serial identifier
- `dal_level` (string): Design Assurance Level (A, B, C, D, E)
- `material_certs` (list): List of material certificate references
- `ndt_results` (dict): Non-destructive testing results
- `cycles_remaining` (int): Remaining cycles for life-limited parts
- `installation_location` (string): Aircraft zone/station

## Output
- `certification_status` (string): CERTIFIED, REJECTED, CONDITIONAL
- `airworthiness_tag` (string): FAA 8130-3 or equivalent tag number
- `limitations` (list): Any operational limitations
- `next_inspection` (dict): Next required inspection details
- `compliance_matrix` (dict): Detailed compliance status

## Implementation
The certification logic is implemented in `certification_checker.py` and references requirements from CSV files:
- `dal_requirements.csv` - Reference data
- `aircraft_zones.csv` - Reference data
- `ndt_methods.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from certification_checker import certify_component

result = certify_component(
    part_number="737-400-2456",
    serial_number="SN-2024-78901",
    dal_level="B",
    material_certs=["MC-2024-001", "MC-2024-002"],
    ndt_results={"ultrasonic": "PASS", "eddy_current": "PASS"},
    cycles_remaining=15000,
    installation_location="ZONE-41"
)

print(f"Status: {result['certification_status']}")
```

## Test Execution
```python
from certification_checker import certify_component

result = certify_component(
    part_number=input_data.get('part_number'),
    serial_number=input_data.get('serial_number'),
    dal_level=input_data.get('dal_level', 'C'),
    material_certs=input_data.get('material_certs', []),
    ndt_results=input_data.get('ndt_results', {}),
    cycles_remaining=input_data.get('cycles_remaining'),
    installation_location=input_data.get('installation_location')
)
```
