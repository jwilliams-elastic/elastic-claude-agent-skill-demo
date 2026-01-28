# Skill: Analyze Supply Chain Risk

## Domain
supply_chain

## Description
Evaluates supply chain vulnerabilities across suppliers, logistics, and inventory to identify risks and recommend mitigation strategies.

## Tags
supply-chain, risk-management, procurement, logistics, resilience

## Use Cases
- Supplier risk assessment
- Supply chain mapping
- Disruption scenario planning
- Inventory buffer optimization

## Proprietary Business Rules

### Rule 1: Single Source Dependency
Risk scoring for single-source and critical path dependencies.

### Rule 2: Geographic Concentration
Risk assessment for regional concentration of supply base.

### Rule 3: Financial Health Scoring
Supplier financial stability indicators and credit risk.

### Rule 4: Lead Time Variability
Risk from inconsistent delivery performance.

## Input Parameters
- `product_id` (string): Product identifier
- `suppliers` (list): Supplier details and metrics
- `inventory_levels` (dict): Current inventory data
- `demand_forecast` (dict): Expected demand
- `logistics_routes` (list): Transportation routes
- `historical_disruptions` (list): Past supply issues

## Output
- `overall_risk_score` (float): Composite risk score
- `risk_categories` (dict): Risk by category
- `vulnerable_nodes` (list): Critical vulnerabilities
- `mitigation_recommendations` (list): Risk mitigation actions
- `scenario_impacts` (dict): Disruption scenario analysis

## Implementation
The risk analysis logic is implemented in `risk_analyzer.py` and references parameters from CSV files:
- `thresholds.csv` - Reference data
- `country_risks.csv` - Reference data
- `scenarios.csv` - Reference data
- `category_weights.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from risk_analyzer import analyze_risk

result = analyze_risk(
    product_id="PROD-001",
    suppliers=[{"id": "SUP-A", "location": "CN", "spend_pct": 0.6, "lead_time_days": 45}],
    inventory_levels={"on_hand": 5000, "safety_stock": 2000},
    demand_forecast={"monthly": 3000},
    logistics_routes=[{"mode": "ocean", "origin": "CN", "transit_days": 28}],
    historical_disruptions=[{"date": "2025-03", "duration_days": 14, "cause": "port_congestion"}]
)

print(f"Risk Score: {result['overall_risk_score']}")
```

## Test Execution
```python
from risk_analyzer import analyze_risk

result = analyze_risk(
    product_id=input_data.get('product_id'),
    suppliers=input_data.get('suppliers', []),
    inventory_levels=input_data.get('inventory_levels', {}),
    demand_forecast=input_data.get('demand_forecast', {}),
    logistics_routes=input_data.get('logistics_routes', []),
    historical_disruptions=input_data.get('historical_disruptions', [])
)
```
