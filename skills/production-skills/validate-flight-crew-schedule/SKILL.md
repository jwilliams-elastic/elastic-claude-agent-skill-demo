# Skill: Validate Flight Crew Schedule

## Domain
aviation

## Description
Validates flight crew schedules against FAA Part 117 flight duty time limitations, rest requirements, and company-specific scheduling policies to ensure regulatory compliance and crew fatigue management.

## Tags
aviation, crew-scheduling, faa-compliance, fatigue-management, flight-operations

## Use Cases
- Crew pairing validation
- Rest requirement verification
- Duty time limit checking
- Fatigue risk assessment

## Proprietary Business Rules

### Rule 1: Flight Duty Period (FDP) Limits
Maximum FDP varies by report time, number of segments, and time zone crossings with company-specific buffers below regulatory limits.

### Rule 2: Cumulative Duty Limits
Rolling window limits for 7-day, 28-day, and 365-day periods with automatic tracking.

### Rule 3: Rest Period Requirements
Minimum rest between FDPs based on prior duty length and whether rest is at home base or outstation.

### Rule 4: Augmented Crew Extensions
Extended FDP limits for augmented crew operations with specific bunk facility requirements.

## Input Parameters
- `crew_member_id` (string): Unique crew member identifier
- `proposed_schedule` (list): List of flight segments with times
- `duty_history` (dict): Recent duty time history
- `home_base` (string): Crew member's home base airport
- `crew_position` (string): Captain, First Officer, or Relief Pilot
- `augmentation_type` (string): None, Class 1, Class 2, or Class 3

## Output
- `schedule_valid` (bool): Whether schedule meets all requirements
- `violations` (list): List of regulatory violations
- `warnings` (list): Items approaching limits
- `fatigue_risk_score` (float): Calculated fatigue risk (0-100)
- `recommendations` (list): Schedule optimization suggestions

## Implementation
The validation logic is implemented in `schedule_validator.py` and references duty limits from `duty_limits.csv`.

## Usage Example
```python
from schedule_validator import validate_schedule

result = validate_schedule(
    crew_member_id="CPT-12345",
    proposed_schedule=[
        {"flight": "AA100", "departure": "2026-01-20T06:00", "arrival": "2026-01-20T10:30"},
        {"flight": "AA101", "departure": "2026-01-20T11:30", "arrival": "2026-01-20T15:00"}
    ],
    duty_history={"7_day_hours": 42, "28_day_hours": 95, "365_day_hours": 850},
    home_base="DFW",
    crew_position="captain",
    augmentation_type="none"
)

print(f"Valid: {result['schedule_valid']}")
```

## Test Execution
```python
from schedule_validator import validate_schedule

result = validate_schedule(
    crew_member_id=input_data.get('crew_member_id'),
    proposed_schedule=input_data.get('proposed_schedule', []),
    duty_history=input_data.get('duty_history', {}),
    home_base=input_data.get('home_base'),
    crew_position=input_data.get('crew_position', 'first_officer'),
    augmentation_type=input_data.get('augmentation_type', 'none')
)
```
