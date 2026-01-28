# Skill: Assess Nonprofit Program Impact

## Domain
social_sector

## Description
Evaluates nonprofit program effectiveness using outcome metrics, cost-effectiveness analysis, and social return on investment (SROI) calculations.

## Tags
nonprofit, impact-measurement, sroi, program-evaluation, social-sector

## Use Cases
- Grant application support
- Program performance review
- Donor reporting
- Strategic planning

## Proprietary Business Rules

### Rule 1: Outcome Achievement Scoring
Weighted scoring of program outcomes against targets with population-adjusted metrics.

### Rule 2: Cost-Effectiveness Benchmarking
Cost per outcome compared to sector benchmarks and similar programs.

### Rule 3: SROI Calculation
Social return on investment using standardized value proxies.

### Rule 4: Sustainability Assessment
Program sustainability scoring based on funding diversity and scalability.

## Input Parameters
- `program_id` (string): Program identifier
- `program_type` (string): Education, health, workforce, etc.
- `outcomes` (dict): Achieved outcome metrics
- `targets` (dict): Target outcome metrics
- `total_cost` (float): Total program cost
- `beneficiaries` (int): Number served
- `funding_sources` (dict): Funding by source type
- `program_duration_months` (int): Program duration

## Output
- `impact_score` (float): Overall impact score 0-100
- `cost_effectiveness` (dict): Cost per outcome metrics
- `sroi_ratio` (float): Social return on investment ratio
- `sustainability_score` (int): Sustainability rating
- `recommendations` (list): Program improvement recommendations

## Implementation
The assessment logic is implemented in `impact_assessor.py` and references benchmarks from CSV files:
- `program_types.csv` - Reference data
- `sustainability_thresholds.csv` - Reference data
- `impact_score_weights.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from impact_assessor import assess_impact

result = assess_impact(
    program_id="PROG-2024-001",
    program_type="workforce_development",
    outcomes={"job_placements": 85, "certifications_earned": 120, "wage_increase_pct": 0.25},
    targets={"job_placements": 100, "certifications_earned": 100, "wage_increase_pct": 0.20},
    total_cost=500000,
    beneficiaries=150,
    funding_sources={"government": 0.4, "foundation": 0.35, "corporate": 0.15, "individual": 0.1},
    program_duration_months=12
)

print(f"Impact Score: {result['impact_score']}")
print(f"SROI: {result['sroi_ratio']}:1")
```

## Test Execution
```python
from impact_assessor import assess_impact

result = assess_impact(
    program_id=input_data.get('program_id'),
    program_type=input_data.get('program_type'),
    outcomes=input_data.get('outcomes', {}),
    targets=input_data.get('targets', {}),
    total_cost=input_data.get('total_cost', 0),
    beneficiaries=input_data.get('beneficiaries', 0),
    funding_sources=input_data.get('funding_sources', {}),
    program_duration_months=input_data.get('program_duration_months', 12)
)
```
