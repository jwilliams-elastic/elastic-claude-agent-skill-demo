# Skill: Assess Utility Outage Impact

## Domain
utilities

## Description
Evaluates utility service outage events to estimate customer impact, restoration priorities, and resource allocation requirements.

## Tags
utilities, outage-management, impact-assessment, restoration, infrastructure

## Use Cases
- Outage impact estimation
- Restoration prioritization
- Resource deployment planning
- Regulatory reporting

## Proprietary Business Rules

### Rule 1: Customer Impact Scoring
Weighted impact calculation based on customer class and critical facilities.

### Rule 2: Restoration Priority Matrix
Priority assignment based on impact score, safety concerns, and resource requirements.

### Rule 3: Resource Allocation
Crew and equipment allocation based on damage assessment and restoration complexity.

### Rule 4: ETR Calculation
Estimated time to restoration based on historical performance and conditions.

## Input Parameters
- `outage_id` (string): Outage event identifier
- `affected_area` (dict): Geographic area details
- `customer_counts` (dict): Customers by class
- `damage_reports` (list): Field damage assessments
- `weather_conditions` (dict): Current weather data
- `available_crews` (int): Available restoration crews

## Output
- `impact_score` (float): Overall impact score
- `priority_level` (string): Restoration priority
- `estimated_restoration` (dict): ETR calculation
- `resource_requirements` (dict): Required resources
- `critical_facilities` (list): Affected critical facilities

## Implementation
The assessment logic is implemented in `outage_assessor.py` and references parameters from CSV files:
- `customer_weights.csv` - Reference data
- `damage_complexity.csv` - Reference data
- `critical_facilities_north.csv` - Reference data
- `critical_facilities_south.csv` - Reference data
- `critical_facilities_east.csv` - Reference data
- `critical_facilities_west.csv` - Reference data
- `priority_thresholds.csv` - Reference data
- `restoration_standards.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from outage_assessor import assess_outage

result = assess_outage(
    outage_id="OUT-2024-001",
    affected_area={"zone": "north", "substations": ["SUB-101"]},
    customer_counts={"residential": 5000, "commercial": 200, "industrial": 15},
    damage_reports=[{"type": "downed_wire", "severity": "major"}],
    weather_conditions={"wind_mph": 45, "precipitation": "rain"},
    available_crews=12
)

print(f"Priority: {result['priority_level']}")
```

## Test Execution
```python
from outage_assessor import assess_outage

result = assess_outage(
    outage_id=input_data.get('outage_id'),
    affected_area=input_data.get('affected_area', {}),
    customer_counts=input_data.get('customer_counts', {}),
    damage_reports=input_data.get('damage_reports', []),
    weather_conditions=input_data.get('weather_conditions', {}),
    available_crews=input_data.get('available_crews', 0)
)
```
