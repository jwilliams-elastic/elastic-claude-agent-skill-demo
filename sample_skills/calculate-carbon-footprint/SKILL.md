# Skill: Calculate Carbon Footprint

## Domain
energy_sustainability

## Description
Calculates organizational carbon footprint across Scope 1, 2, and 3 emissions using GHG Protocol methodology for ESG reporting.

## Tags
carbon, emissions, GHG, sustainability, ESG, climate, environmental

## Use Cases
- Annual emissions reporting
- Carbon reduction planning
- Scope 3 supply chain analysis
- Offset requirement calculation

## Proprietary Business Rules

### Rule 1: Scope Classification
Categorization of emissions by GHG Protocol scopes.

### Rule 2: Emission Factor Application
Activity-specific emission factor selection and calculation.

### Rule 3: Data Quality Scoring
Assessment of calculation certainty based on data sources.

### Rule 4: Reduction Opportunity Identification
Analysis of high-impact reduction opportunities.

## Input Parameters
- `organization_id` (string): Organization identifier
- `reporting_period` (dict): Start and end dates
- `scope1_activities` (list): Direct emission activities
- `scope2_data` (dict): Purchased energy data
- `scope3_categories` (list): Value chain emissions
- `baseline_year` (dict): Baseline comparison data

## Output
- `total_emissions` (float): Total CO2e in metric tons
- `emissions_by_scope` (dict): Breakdown by scope
- `intensity_metrics` (dict): Normalized metrics
- `reduction_opportunities` (list): Identified reductions
- `data_quality_score` (float): Calculation confidence

## Implementation
The calculation logic is implemented in `carbon_calculator.py` and references data from CSV files:
- `scope1.csv` - Reference data
- `scope2.csv` - Reference data
- `scope3.csv` - Reference data
- `thresholds.csv` - Reference data
- `gwp_values.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from carbon_calculator import calculate_footprint

result = calculate_footprint(
    organization_id="ORG-001",
    reporting_period={"start": "2025-01-01", "end": "2025-12-31"},
    scope1_activities=[{"type": "natural_gas", "quantity": 50000, "unit": "therms"}],
    scope2_data={"electricity_kwh": 1000000, "grid_region": "US-WECC"},
    scope3_categories=[{"category": "business_travel", "data": {"air_miles": 500000}}],
    baseline_year={"year": 2020, "total_emissions": 5000}
)

print(f"Total Emissions: {result['total_emissions']} tCO2e")
```

## Test Execution
```python
from carbon_calculator import calculate_footprint

result = calculate_footprint(
    organization_id=input_data.get('organization_id'),
    reporting_period=input_data.get('reporting_period', {}),
    scope1_activities=input_data.get('scope1_activities', []),
    scope2_data=input_data.get('scope2_data', {}),
    scope3_categories=input_data.get('scope3_categories', []),
    baseline_year=input_data.get('baseline_year', {})
)
```
