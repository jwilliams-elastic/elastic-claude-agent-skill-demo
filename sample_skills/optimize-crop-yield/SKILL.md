# Skill: Optimize Crop Yield

## Domain
agribusiness

## Description
Analyzes field conditions, soil data, and weather patterns to generate crop-specific yield optimization recommendations based on proprietary agronomic models and regional best practices.

## Tags
agriculture, crop-management, yield-optimization, precision-farming, agronomy

## Use Cases
- Seasonal planting recommendations
- Fertilizer application optimization
- Irrigation scheduling
- Harvest timing decisions

## Proprietary Business Rules

### Rule 1: Soil Nutrient Balance
Optimal NPK ratios vary by crop and growth stage, with proprietary threshold values calibrated to regional soil types.

### Rule 2: Growing Degree Day Accumulation
Crop maturity predictions based on accumulated heat units with cultivar-specific base temperatures.

### Rule 3: Water Stress Index
Irrigation triggers based on soil moisture deficit thresholds adjusted for crop water sensitivity stages.

### Rule 4: Pest Pressure Integration
Yield adjustments based on integrated pest management (IPM) pressure scores.

## Input Parameters
- `field_id` (string): Unique field identifier
- `crop_type` (string): Crop being cultivated
- `soil_analysis` (dict): Recent soil test results (N, P, K, pH, organic matter)
- `weather_forecast` (dict): 14-day weather forecast data
- `growth_stage` (string): Current crop growth stage
- `irrigation_available` (bool): Whether irrigation is available
- `pest_pressure_score` (float): Current IPM pressure score (0-10)

## Output
- `yield_prediction` (float): Predicted yield in bushels/acre
- `optimization_actions` (list): Recommended actions
- `fertilizer_recommendations` (dict): Specific fertilizer applications
- `irrigation_schedule` (list): Recommended irrigation events
- `risk_factors` (list): Identified yield risk factors

## Implementation
The optimization logic is implemented in `yield_optimizer.py` and references agronomic parameters from CSV files:
- `crops.csv` - Reference data
- `fertilizer_conversions.csv` - Reference data
- `nutrient_yield_impacts.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from yield_optimizer import optimize_yield

result = optimize_yield(
    field_id="FIELD-NW-042",
    crop_type="corn",
    soil_analysis={"N": 45, "P": 32, "K": 180, "pH": 6.5, "organic_matter": 3.2},
    weather_forecast={"avg_temp": 78, "precip_chance": 30, "gdd_forecast": 125},
    growth_stage="V8",
    irrigation_available=True,
    pest_pressure_score=3.5
)

print(f"Predicted Yield: {result['yield_prediction']} bu/acre")
```

## Test Execution
```python
from yield_optimizer import optimize_yield

result = optimize_yield(
    field_id=input_data.get('field_id'),
    crop_type=input_data.get('crop_type'),
    soil_analysis=input_data.get('soil_analysis', {}),
    weather_forecast=input_data.get('weather_forecast', {}),
    growth_stage=input_data.get('growth_stage'),
    irrigation_available=input_data.get('irrigation_available', False),
    pest_pressure_score=input_data.get('pest_pressure_score', 0)
)
```
