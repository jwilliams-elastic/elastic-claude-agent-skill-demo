# Skill: Calculate Machinery Maintenance Schedule

## Domain
machinery_equipment

## Description
Predicts optimal maintenance intervals using equipment telemetry, failure history, and reliability models to minimize downtime and maintenance costs.

## Tags
machinery, predictive-maintenance, reliability, equipment-management, industrial

## Use Cases
- Preventive maintenance scheduling
- Spare parts planning
- Equipment lifecycle optimization
- Downtime prediction

## Proprietary Business Rules

### Rule 1: Condition-Based Triggers
Maintenance triggered by sensor threshold exceedances with equipment-specific parameters.

### Rule 2: Failure Probability Modeling
Weibull distribution modeling for remaining useful life estimation.

### Rule 3: Maintenance Optimization
Cost-benefit optimization between preventive and corrective maintenance.

### Rule 4: Parts Lead Time Integration
Maintenance scheduling considers spare parts availability.

## Input Parameters
- `equipment_id` (string): Equipment identifier
- `equipment_type` (string): Equipment classification
- `operating_hours` (float): Current operating hours
- `sensor_data` (dict): Current sensor readings
- `maintenance_history` (list): Past maintenance records
- `parts_inventory` (dict): Available spare parts

## Output
- `next_maintenance` (dict): Recommended next maintenance
- `failure_probability` (float): Probability of failure before maintenance
- `remaining_useful_life` (dict): RUL estimate
- `parts_needed` (list): Required spare parts
- `cost_analysis` (dict): Maintenance cost comparison

## Implementation
The maintenance logic is implemented in `maintenance_scheduler.py` and references parameters from CSV files:
- `equipment_types.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from maintenance_scheduler import calculate_maintenance

result = calculate_maintenance(
    equipment_id="PUMP-001",
    equipment_type="centrifugal_pump",
    operating_hours=8500,
    sensor_data={"vibration_mm_s": 4.2, "temperature_c": 65, "pressure_bar": 8.5},
    maintenance_history=[{"date": "2025-06-15", "type": "bearing_replacement"}],
    parts_inventory={"bearings": 2, "seals": 5}
)

print(f"Next Maintenance: {result['next_maintenance']}")
```

## Test Execution
```python
from maintenance_scheduler import calculate_maintenance

result = calculate_maintenance(
    equipment_id=input_data.get('equipment_id'),
    equipment_type=input_data.get('equipment_type'),
    operating_hours=input_data.get('operating_hours', 0),
    sensor_data=input_data.get('sensor_data', {}),
    maintenance_history=input_data.get('maintenance_history', []),
    parts_inventory=input_data.get('parts_inventory', {})
)
```
