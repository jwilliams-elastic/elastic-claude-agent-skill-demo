# Skill: Assess Building Permit Application

## Domain
infrastructure

## Description
Evaluates building permit applications against zoning codes, building codes, and municipal requirements to determine approval status and required modifications.

## Tags
infrastructure, construction, building-codes, zoning, permit-review

## Use Cases
- Permit application pre-screening
- Zoning compliance verification
- Building code review
- Variance identification

## Proprietary Business Rules

### Rule 1: Zoning District Compliance
Building use, height, and density must comply with zoning district regulations.

### Rule 2: Setback Requirements
Structure placement must meet front, side, and rear setback minimums.

### Rule 3: Floor Area Ratio (FAR)
Total floor area cannot exceed FAR limits for the zoning district.

### Rule 4: Parking Requirements
Off-street parking must meet minimums based on use type and square footage.

## Input Parameters
- `permit_id` (string): Permit application identifier
- `parcel_id` (string): Property parcel number
- `zoning_district` (string): Zoning classification
- `project_type` (string): New construction, addition, renovation
- `proposed_use` (string): Building use classification
- `building_specs` (dict): Height, stories, square footage
- `setbacks` (dict): Proposed setbacks from property lines
- `parking_spaces` (int): Proposed parking spaces

## Output
- `permit_status` (string): Approved, denied, conditional
- `compliance_score` (float): Overall compliance percentage
- `violations` (list): Code violations found
- `variances_needed` (list): Required variance applications
- `conditions` (list): Approval conditions

## Implementation
The permit review logic is implemented in `permit_reviewer.py` and references codes from CSV files:
- `zoning_districts.csv` - Reference data
- `parking_requirements.csv` - Reference data
- `ada_requirements.csv` - Reference data
- `fire_code.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from permit_reviewer import assess_permit

result = assess_permit(
    permit_id="BP-2024-001",
    parcel_id="123-456-789",
    zoning_district="C-2",
    project_type="new_construction",
    proposed_use="retail",
    building_specs={"height_ft": 45, "stories": 3, "sqft": 15000},
    setbacks={"front": 20, "side": 10, "rear": 15},
    parking_spaces=45
)

print(f"Status: {result['permit_status']}")
```

## Test Execution
```python
from permit_reviewer import assess_permit

result = assess_permit(
    permit_id=input_data.get('permit_id'),
    parcel_id=input_data.get('parcel_id'),
    zoning_district=input_data.get('zoning_district'),
    project_type=input_data.get('project_type'),
    proposed_use=input_data.get('proposed_use'),
    building_specs=input_data.get('building_specs', {}),
    setbacks=input_data.get('setbacks', {}),
    parking_spaces=input_data.get('parking_spaces', 0)
)
```
