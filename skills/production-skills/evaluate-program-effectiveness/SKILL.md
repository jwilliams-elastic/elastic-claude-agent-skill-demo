# Skill: Evaluate Program Effectiveness

## Domain
social_public_sector

## Description
Evaluates social program effectiveness using outcome measurement, cost-effectiveness analysis, and impact assessment methodologies.

## Tags
program-evaluation, impact, social, outcomes, nonprofit, government

## Use Cases
- Program impact assessment
- Cost-effectiveness analysis
- Outcome tracking
- Funding justification

## Proprietary Business Rules

### Rule 1: Outcome Measurement
Quantification of program outcomes.

### Rule 2: Attribution Analysis
Impact attributable to program intervention.

### Rule 3: Cost-Effectiveness Ratio
Cost per outcome achieved calculation.

### Rule 4: Comparison to Benchmarks
Performance against similar programs.

## Input Parameters
- `program_id` (string): Program identifier
- `program_data` (dict): Program information
- `outcome_data` (list): Measured outcomes
- `cost_data` (dict): Program costs
- `baseline_data` (dict): Pre-intervention baseline
- `comparison_group` (dict): Control group data

## Output
- `effectiveness_score` (float): Program effectiveness rating
- `outcomes_achieved` (dict): Outcome metrics
- `cost_effectiveness` (dict): Cost per outcome
- `attribution_analysis` (dict): Impact attribution
- `recommendations` (list): Program improvements

## Implementation
The evaluation logic is implemented in `program_evaluator.py` and references data from `evaluation_frameworks.json`.

## Usage Example
```python
from program_evaluator import evaluate_program

result = evaluate_program(
    program_id="PRG-001",
    program_data={"name": "Job Training", "type": "workforce", "duration_months": 12},
    outcome_data=[{"metric": "employment_rate", "value": 0.75, "target": 0.70}],
    cost_data={"total_budget": 500000, "participants": 200},
    baseline_data={"employment_rate": 0.40},
    comparison_group={"employment_rate": 0.50}
)

print(f"Effectiveness Score: {result['effectiveness_score']}")
```

## Test Execution
```python
from program_evaluator import evaluate_program

result = evaluate_program(
    program_id=input_data.get('program_id'),
    program_data=input_data.get('program_data', {}),
    outcome_data=input_data.get('outcome_data', []),
    cost_data=input_data.get('cost_data', {}),
    baseline_data=input_data.get('baseline_data', {}),
    comparison_group=input_data.get('comparison_group', {})
)
```
