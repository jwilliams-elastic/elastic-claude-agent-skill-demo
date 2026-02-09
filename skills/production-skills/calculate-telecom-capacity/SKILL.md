# Skill: Calculate Telecom Network Capacity

## Domain
telecommunications

## Description
Analyzes network traffic patterns and infrastructure capacity to plan upgrades, predict congestion, and optimize resource allocation.

## Tags
telecommunications, network-planning, capacity-analysis, traffic-engineering, infrastructure

## Use Cases
- Network capacity planning
- Congestion prediction
- Infrastructure investment planning
- Quality of service optimization

## Proprietary Business Rules

### Rule 1: Traffic Growth Modeling
Compound annual growth rate projections with peak hour multipliers.

### Rule 2: Utilization Thresholds
Capacity upgrade triggers based on sustained utilization levels.

### Rule 3: Redundancy Requirements
N+1 or N+2 redundancy calculations by service tier.

### Rule 4: Technology Migration Impact
Capacity gains from technology upgrades (4G to 5G, fiber deployment).

## Input Parameters
- `network_element` (string): Element identifier
- `element_type` (string): Router, switch, cell tower, fiber link
- `current_capacity` (float): Current capacity in Gbps
- `traffic_history` (list): Historical traffic data
- `service_tier` (string): Critical, standard, best-effort
- `technology` (string): Current technology type
- `forecast_years` (int): Planning horizon

## Output
- `upgrade_required` (bool): Whether upgrade is needed
- `upgrade_timeline` (dict): Recommended upgrade schedule
- `capacity_forecast` (list): Projected capacity needs
- `congestion_risk` (dict): Congestion probability by timeframe
- `investment_estimate` (dict): CAPEX estimates

## Implementation
The capacity logic is implemented in `capacity_planner.py` and references parameters from CSV files:
- `element_types.csv` - Reference data
- `service_tiers.csv` - Reference data
- `upgrade_paths.csv` - Reference data
- `cost_factors.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from capacity_planner import calculate_capacity

result = calculate_capacity(
    network_element="ROUTER-NYC-01",
    element_type="core_router",
    current_capacity=100.0,
    traffic_history=[45.2, 48.5, 52.1, 55.8, 60.3, 65.0],
    service_tier="critical",
    technology="100G",
    forecast_years=5
)

print(f"Upgrade Required: {result['upgrade_required']}")
```

## Test Execution
```python
from capacity_planner import calculate_capacity

result = calculate_capacity(
    network_element=input_data.get('network_element'),
    element_type=input_data.get('element_type'),
    current_capacity=input_data.get('current_capacity', 0),
    traffic_history=input_data.get('traffic_history', []),
    service_tier=input_data.get('service_tier', 'standard'),
    technology=input_data.get('technology'),
    forecast_years=input_data.get('forecast_years', 3)
)
```
