# Skill: Optimize Shipping Route

## Domain
transportation

## Description
Calculates optimal shipping routes considering distance, transit time, cost, and carbon emissions across multimodal transportation options.

## Tags
transportation, logistics, route-optimization, supply-chain, multimodal

## Use Cases
- Freight route planning
- Mode selection optimization
- Transit time estimation
- Carbon footprint calculation

## Proprietary Business Rules

### Rule 1: Mode Selection Criteria
Optimal mode selection based on shipment characteristics, urgency, and cost targets.

### Rule 2: Hub Network Optimization
Routing through hub network with proprietary transit time and cost matrices.

### Rule 3: Carbon Calculation
Emissions calculation using carrier-specific emission factors.

### Rule 4: Service Level Matching
Route options filtered by service level requirements.

## Input Parameters
- `shipment_id` (string): Shipment identifier
- `origin` (dict): Origin location details
- `destination` (dict): Destination location details
- `cargo_specs` (dict): Weight, volume, type
- `service_level` (string): Express, standard, economy
- `delivery_deadline` (string): Required delivery date
- `preferences` (dict): Cost vs speed vs sustainability weights

## Output
- `recommended_route` (dict): Primary route recommendation
- `alternative_routes` (list): Alternative options
- `transit_time_days` (float): Estimated transit time
- `total_cost` (float): Estimated shipping cost
- `carbon_footprint_kg` (float): CO2 emissions estimate

## Implementation
The routing logic is implemented in `route_optimizer.py` and references transit data from `transit_matrix.csv`.

## Usage Example
```python
from route_optimizer import optimize_route

result = optimize_route(
    shipment_id="SHIP-2024-001",
    origin={"city": "Shanghai", "country": "CN", "port": "CNSHA"},
    destination={"city": "Chicago", "country": "US", "port": "USCHI"},
    cargo_specs={"weight_kg": 5000, "volume_cbm": 25, "type": "general"},
    service_level="standard",
    delivery_deadline="2026-02-15",
    preferences={"cost": 0.5, "speed": 0.3, "sustainability": 0.2}
)

print(f"Route: {result['recommended_route']}")
```

## Test Execution
```python
from route_optimizer import optimize_route

result = optimize_route(
    shipment_id=input_data.get('shipment_id'),
    origin=input_data.get('origin', {}),
    destination=input_data.get('destination', {}),
    cargo_specs=input_data.get('cargo_specs', {}),
    service_level=input_data.get('service_level', 'standard'),
    delivery_deadline=input_data.get('delivery_deadline'),
    preferences=input_data.get('preferences', {})
)
```
