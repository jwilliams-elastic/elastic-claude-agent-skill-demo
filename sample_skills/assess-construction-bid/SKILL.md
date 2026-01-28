# Skill: Assess Construction Bid

## Domain
infrastructure_construction

## Description
Evaluates construction project bids for cost accuracy, contractor qualifications, and project feasibility using industry benchmarks.

## Tags
construction, bidding, estimation, contractors, infrastructure, project-management

## Use Cases
- Bid comparison analysis
- Contractor qualification review
- Cost estimate validation
- Project risk assessment

## Proprietary Business Rules

### Rule 1: Cost Benchmark Comparison
Validation against regional cost indices and historical data.

### Rule 2: Contractor Qualification
Assessment of contractor experience and bonding capacity.

### Rule 3: Schedule Feasibility
Evaluation of proposed timeline against complexity factors.

### Rule 4: Bid Completeness
Verification of required bid components and documentation.

## Input Parameters
- `bid_id` (string): Bid identifier
- `project_details` (dict): Project specifications
- `bid_amounts` (dict): Cost breakdown
- `contractor_info` (dict): Contractor qualifications
- `schedule` (dict): Proposed timeline
- `subcontractors` (list): Subcontractor details

## Output
- `bid_score` (float): Overall bid evaluation score
- `cost_analysis` (dict): Cost reasonableness findings
- `qualification_status` (dict): Contractor qualification results
- `schedule_assessment` (dict): Timeline feasibility analysis
- `recommendation` (string): Award recommendation

## Implementation
The assessment logic is implemented in `bid_assessor.py` and references data from CSV files:
- `cost_per_sqft.csv` - Reference data
- `location_factors.csv` - Reference data
- `contractor_requirements.csv` - Reference data
- `complexity_factors.csv` - Reference data
- `evaluation_weights.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from bid_assessor import assess_bid

result = assess_bid(
    bid_id="BID-2026-001",
    project_details={"type": "commercial", "sqft": 50000, "location": "NY"},
    bid_amounts={"labor": 2000000, "materials": 1500000, "equipment": 500000},
    contractor_info={"license": "valid", "bonding_capacity": 10000000},
    schedule={"duration_months": 18, "start_date": "2026-06-01"},
    subcontractors=[{"trade": "electrical", "qualified": True}]
)

print(f"Bid Score: {result['bid_score']}")
```

## Test Execution
```python
from bid_assessor import assess_bid

result = assess_bid(
    bid_id=input_data.get('bid_id'),
    project_details=input_data.get('project_details', {}),
    bid_amounts=input_data.get('bid_amounts', {}),
    contractor_info=input_data.get('contractor_info', {}),
    schedule=input_data.get('schedule', {}),
    subcontractors=input_data.get('subcontractors', [])
)
```
