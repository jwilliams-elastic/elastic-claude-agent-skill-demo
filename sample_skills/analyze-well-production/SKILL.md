# Skill: Analyze Well Production

## Domain
energy

## Description
Analyzes oil and gas well production data to predict decline curves, estimate ultimate recovery (EUR), and recommend optimization interventions based on reservoir engineering models.

## Tags
energy, oil-gas, production-analysis, reservoir-engineering, decline-curve

## Use Cases
- Production decline forecasting
- Artificial lift optimization
- Workover candidate identification
- EUR estimation for reserves

## Proprietary Business Rules

### Rule 1: Decline Curve Analysis
Proprietary decline models (exponential, hyperbolic, harmonic) selected based on reservoir and completion characteristics.

### Rule 2: Water Cut Threshold
Economic limit calculations based on water handling costs and oil price assumptions.

### Rule 3: Intervention Triggers
Production anomaly detection triggers workover or optimization recommendations.

### Rule 4: Artificial Lift Selection
Lift method recommendations based on well conditions and production characteristics.

## Input Parameters
- `well_id` (string): Well API number or identifier
- `production_history` (list): Monthly production data (oil, gas, water)
- `completion_type` (string): Conventional, hydraulic fracture, horizontal
- `reservoir_type` (string): Conventional, tight, shale
- `current_lift_method` (string): Natural flow, rod pump, ESP, gas lift
- `wellhead_pressure` (float): Current wellhead pressure (psi)
- `oil_price` (float): Current oil price assumption ($/bbl)

## Output
- `decline_forecast` (dict): Production decline predictions
- `eur_estimate` (float): Estimated ultimate recovery (bbl)
- `economic_limit` (dict): Economic limit calculation
- `optimization_recommendations` (list): Intervention recommendations
- `lift_efficiency` (float): Current lift system efficiency

## Implementation
The analysis logic is implemented in `production_analyzer.py` and references decline parameters from `decline_models.csv`.

## Usage Example
```python
from production_analyzer import analyze_production

result = analyze_production(
    well_id="42-123-45678",
    production_history=[
        {"month": "2025-01", "oil_bbl": 5000, "gas_mcf": 8000, "water_bbl": 2000},
        {"month": "2025-02", "oil_bbl": 4800, "gas_mcf": 7800, "water_bbl": 2200}
    ],
    completion_type="hydraulic_fracture",
    reservoir_type="shale",
    current_lift_method="rod_pump",
    wellhead_pressure=150,
    oil_price=75.00
)

print(f"EUR: {result['eur_estimate']} bbl")
```

## Test Execution
```python
from production_analyzer import analyze_production

result = analyze_production(
    well_id=input_data.get('well_id'),
    production_history=input_data.get('production_history', []),
    completion_type=input_data.get('completion_type'),
    reservoir_type=input_data.get('reservoir_type'),
    current_lift_method=input_data.get('current_lift_method', 'natural_flow'),
    wellhead_pressure=input_data.get('wellhead_pressure', 0),
    oil_price=input_data.get('oil_price', 70)
)
```
