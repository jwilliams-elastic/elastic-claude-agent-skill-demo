# Skill: Evaluate Defense Contract

## Domain
aerospace_defense

## Description
Evaluates defense contract proposals for compliance, cost reasonableness, and technical feasibility using government acquisition regulations.

## Tags
defense, government, contracts, compliance, FAR, DFARS, acquisition

## Use Cases
- Contract proposal evaluation
- Cost reasonableness assessment
- Compliance verification
- Technical capability review

## Proprietary Business Rules

### Rule 1: FAR Compliance Check
Verification against Federal Acquisition Regulation requirements.

### Rule 2: Cost Reasonableness
Comparison against historical pricing and should-cost models.

### Rule 3: Technical Capability Assessment
Evaluation of contractor's technical capabilities and past performance.

### Rule 4: Security Clearance Verification
Validation of required security clearances and certifications.

## Input Parameters
- `contract_id` (string): Contract identifier
- `proposal_details` (dict): Proposal information
- `contractor_info` (dict): Contractor details
- `cost_elements` (list): Cost breakdown structure
- `technical_requirements` (list): Technical specifications
- `security_requirements` (dict): Security clearance needs

## Output
- `evaluation_score` (float): Overall evaluation score
- `compliance_status` (dict): FAR/DFARS compliance results
- `cost_analysis` (dict): Cost reasonableness findings
- `technical_assessment` (dict): Technical capability evaluation
- `risk_factors` (list): Identified risks
- `recommendation` (string): Award recommendation

## Implementation
The evaluation logic is implemented in `contract_evaluator.py` and references data from CSV files:
- `cost_benchmarks.csv` - Reference data
- `capability_matrix.csv` - Reference data
- `clearance_hierarchy.csv` - Reference data
- `evaluation_weights.csv` - Reference data
- `past_performance_thresholds.csv` - Reference data
- `contract_types.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from contract_evaluator import evaluate_contract

result = evaluate_contract(
    contract_id="W911NF-26-C-0001",
    proposal_details={"type": "FFP", "value": 5000000, "period_months": 24},
    contractor_info={"cage_code": "1ABC2", "size": "small_business"},
    cost_elements=[{"category": "labor", "amount": 3000000}],
    technical_requirements=[{"id": "TR-001", "category": "software"}],
    security_requirements={"clearance_level": "SECRET"}
)

print(f"Evaluation Score: {result['evaluation_score']}")
```

## Test Execution
```python
from contract_evaluator import evaluate_contract

result = evaluate_contract(
    contract_id=input_data.get('contract_id'),
    proposal_details=input_data.get('proposal_details', {}),
    contractor_info=input_data.get('contractor_info', {}),
    cost_elements=input_data.get('cost_elements', []),
    technical_requirements=input_data.get('technical_requirements', []),
    security_requirements=input_data.get('security_requirements', {})
)
```
