# Skill: Evaluate Site Selection

## Domain
real_estate

## Description
Evaluates potential facility sites analyzing demographics, accessibility, competition, and costs for retail and industrial location decisions.

## Tags
real-estate, site-selection, retail, demographics, location, GIS

## Use Cases
- Retail site selection
- Warehouse location analysis
- Market potential assessment
- Competitive analysis

## Proprietary Business Rules

### Rule 1: Trade Area Analysis
Customer catchment area delineation and analysis.

### Rule 2: Demographic Scoring
Population and income criteria evaluation.

### Rule 3: Competitive Assessment
Existing competition density and impact.

### Rule 4: Accessibility Rating
Traffic, visibility, and access evaluation.

## Input Parameters
- `site_id` (string): Site identifier
- `site_details` (dict): Site characteristics
- `demographic_data` (dict): Area demographics
- `competitive_data` (list): Competitor locations
- `cost_factors` (dict): Site costs
- `requirements` (dict): Site requirements

## Output
- `site_score` (float): Overall site rating
- `demographic_analysis` (dict): Population analysis
- `competitive_analysis` (dict): Competition assessment
- `accessibility_score` (dict): Access evaluation
- `financial_projection` (dict): Sales/rent potential
- `recommendation` (string): Site recommendation

## Implementation
The evaluation logic is implemented in `site_evaluator.py` and references data from CSV files:
- `evaluation_criteria.csv` - Reference data
- `cost_benchmarks.csv` - Reference data
- `infrastructure_scores.csv` - Reference data
- `incentive_types.csv` - Reference data
- `risk_factors.csv` - Reference data
- `facility_requirements.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from site_evaluator import evaluate_site

result = evaluate_site(
    site_id="SITE-001",
    site_details={"sqft": 5000, "type": "retail", "visibility": "high"},
    demographic_data={"population_3mi": 150000, "median_income": 75000},
    competitive_data=[{"name": "Competitor A", "distance_mi": 1.5}],
    cost_factors={"rent_sqft": 35, "cam_sqft": 8},
    requirements={"min_population": 100000, "max_competition": 3}
)

print(f"Site Score: {result['site_score']}")
```

## Test Execution
```python
from site_evaluator import evaluate_site

result = evaluate_site(
    site_id=input_data.get('site_id'),
    site_details=input_data.get('site_details', {}),
    demographic_data=input_data.get('demographic_data', {}),
    competitive_data=input_data.get('competitive_data', []),
    cost_factors=input_data.get('cost_factors', {}),
    requirements=input_data.get('requirements', {})
)
```
