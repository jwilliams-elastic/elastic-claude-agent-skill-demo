# Skill: Calculate Fleet Efficiency

## Domain
transportation

## Description
Calculates fleet operational efficiency metrics including utilization, fuel economy, and maintenance optimization for fleet management decisions.

## Tags
fleet, transportation, logistics, efficiency, fuel, maintenance

## Use Cases
- Fleet utilization analysis
- Fuel efficiency optimization
- Maintenance scheduling
- Route efficiency assessment

## Proprietary Business Rules

### Rule 1: Utilization Calculation
Asset utilization measurement against capacity.

### Rule 2: Fuel Economy Analysis
MPG analysis and fuel cost optimization.

### Rule 3: Maintenance Interval Optimization
Predictive maintenance scheduling based on usage.

### Rule 4: Driver Performance Scoring
Driver efficiency and safety metrics.

## Input Parameters
- `fleet_id` (string): Fleet identifier
- `vehicle_data` (list): Vehicle details and specs
- `trip_history` (list): Recent trip records
- `fuel_records` (list): Fuel consumption data
- `maintenance_logs` (list): Maintenance history
- `driver_metrics` (dict): Driver performance data

## Output
- `fleet_efficiency_score` (float): Overall efficiency rating
- `utilization_metrics` (dict): Utilization analysis
- `fuel_analysis` (dict): Fuel efficiency findings
- `maintenance_forecast` (list): Upcoming maintenance needs
- `optimization_recommendations` (list): Efficiency improvements

## Implementation
The calculation logic is implemented in `fleet_calculator.py` and references data from CSV files:
- `utilization.csv` - Reference data
- `fuel.csv` - Reference data
- `maintenance_intervals.csv` - Reference data
- `driver_benchmarks.csv` - Reference data
- `score_weights.csv` - Reference data
- `cost_factors.csv` - Reference data
- `compliance.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from fleet_calculator import calculate_fleet_efficiency

result = calculate_fleet_efficiency(
    fleet_id="FLT-001",
    vehicle_data=[{"id": "VH-001", "type": "semi", "capacity_tons": 20}],
    trip_history=[{"vehicle_id": "VH-001", "miles": 500, "load_pct": 0.85}],
    fuel_records=[{"vehicle_id": "VH-001", "gallons": 80, "miles": 500}],
    maintenance_logs=[{"vehicle_id": "VH-001", "type": "oil_change", "odometer": 45000}],
    driver_metrics={"avg_speed": 58, "idle_time_pct": 0.12}
)

print(f"Fleet Efficiency Score: {result['fleet_efficiency_score']}")
```

## Test Execution
```python
from fleet_calculator import calculate_fleet_efficiency

result = calculate_fleet_efficiency(
    fleet_id=input_data.get('fleet_id'),
    vehicle_data=input_data.get('vehicle_data', []),
    trip_history=input_data.get('trip_history', []),
    fuel_records=input_data.get('fuel_records', []),
    maintenance_logs=input_data.get('maintenance_logs', []),
    driver_metrics=input_data.get('driver_metrics', {})
)
```
