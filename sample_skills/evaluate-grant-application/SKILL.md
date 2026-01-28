# Skill: Evaluate Grant Application

## Domain
social_public_sector

## Description
Evaluates grant applications for eligibility, program alignment, and impact potential using structured scoring criteria for funding decisions.

## Tags
grants, nonprofit, funding, evaluation, social-impact, philanthropy

## Use Cases
- Grant eligibility screening
- Application scoring
- Impact assessment
- Budget reasonableness review

## Proprietary Business Rules

### Rule 1: Eligibility Verification
Organization and project eligibility criteria check.

### Rule 2: Program Alignment Scoring
Assessment of fit with funding priorities.

### Rule 3: Budget Reasonableness
Evaluation of proposed budget against norms.

### Rule 4: Impact Potential Assessment
Projected outcomes and measurement capacity.

## Input Parameters
- `application_id` (string): Application identifier
- `applicant_info` (dict): Organization details
- `project_proposal` (dict): Project description
- `budget_request` (dict): Funding request details
- `impact_metrics` (dict): Proposed outcomes
- `program_priorities` (dict): Funding program criteria

## Output
- `eligibility_status` (string): Eligibility determination
- `total_score` (float): Application score
- `scoring_breakdown` (dict): Score by category
- `budget_assessment` (dict): Budget analysis
- `recommendation` (string): Funding recommendation

## Implementation
The evaluation logic is implemented in `grant_evaluator.py` and references data from CSV files:
- `scoring_rubric.csv` - Reference data
- `budget_rules.csv` - Reference data
- `capacity_criteria.csv` - Reference data
- `focus_area_weights.csv` - Reference data
- `geographic_priorities.csv` - Reference data
- `matching_requirements.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from grant_evaluator import evaluate_grant

result = evaluate_grant(
    application_id="GRT-2026-001",
    applicant_info={"org_type": "501c3", "years_operating": 10, "annual_budget": 2000000},
    project_proposal={"focus_area": "education", "duration_months": 24, "beneficiaries": 5000},
    budget_request={"amount": 250000, "categories": {"personnel": 150000, "program": 80000}},
    impact_metrics={"primary_outcome": "graduation_rate", "target_improvement": 0.15},
    program_priorities={"focus_areas": ["education", "workforce"], "max_award": 500000}
)

print(f"Total Score: {result['total_score']}")
```

## Test Execution
```python
from grant_evaluator import evaluate_grant

result = evaluate_grant(
    application_id=input_data.get('application_id'),
    applicant_info=input_data.get('applicant_info', {}),
    project_proposal=input_data.get('project_proposal', {}),
    budget_request=input_data.get('budget_request', {}),
    impact_metrics=input_data.get('impact_metrics', {}),
    program_priorities=input_data.get('program_priorities', {})
)
```
