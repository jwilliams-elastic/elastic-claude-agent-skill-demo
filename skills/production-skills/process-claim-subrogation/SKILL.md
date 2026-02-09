# Skill: Process Claim Subrogation

## Domain
insurance

## Description
Processes insurance claim subrogation opportunities identifying recovery potential, liable parties, and prioritizing collection efforts.

## Tags
insurance, subrogation, claims, recovery, legal, collections

## Use Cases
- Subrogation opportunity identification
- Recovery amount estimation
- Liable party identification
- Collection prioritization

## Proprietary Business Rules

### Rule 1: Recovery Potential Assessment
Likelihood and amount of potential recovery.

### Rule 2: Liability Determination
Identification of at-fault parties.

### Rule 3: Cost-Benefit Analysis
Recovery effort ROI calculation.

### Rule 4: Statute of Limitations Tracking
Recovery deadline management.

## Input Parameters
- `claim_id` (string): Claim identifier
- `claim_details` (dict): Claim information
- `involved_parties` (list): Parties in incident
- `liability_assessment` (dict): Fault determination
- `recovery_history` (list): Past recovery attempts
- `jurisdiction_info` (dict): Legal jurisdiction

## Output
- `subrogation_potential` (dict): Recovery opportunity
- `liable_parties` (list): Identified liable parties
- `estimated_recovery` (float): Expected recovery amount
- `priority_score` (float): Collection priority
- `recommended_actions` (list): Next steps

## Implementation
The processing logic is implemented in `subrogation_processor.py` and references data from CSV files:
- `subrogation_thresholds.csv` - Reference data
- `recovery_potential_factors.csv` - Reference data
- `claim_type_multipliers.csv` - Reference data
- `statute_of_limitations.csv` - Reference data
- `cost_thresholds.csv` - Reference data
- `recovery_rates.csv` - Reference data
- `pursuit_costs.csv` - Reference data
- `priority_scoring.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from subrogation_processor import process_subrogation

result = process_subrogation(
    claim_id="CLM-001",
    claim_details={"type": "auto", "paid_amount": 25000, "loss_date": "2025-06-15"},
    involved_parties=[{"name": "Party A", "role": "insured"}, {"name": "Party B", "role": "third_party"}],
    liability_assessment={"party_b_fault_pct": 0.80},
    recovery_history=[],
    jurisdiction_info={"state": "CA", "sol_years": 3}
)

print(f"Estimated Recovery: ${result['estimated_recovery']:,.0f}")
```

## Test Execution
```python
from subrogation_processor import process_subrogation

result = process_subrogation(
    claim_id=input_data.get('claim_id'),
    claim_details=input_data.get('claim_details', {}),
    involved_parties=input_data.get('involved_parties', []),
    liability_assessment=input_data.get('liability_assessment', {}),
    recovery_history=input_data.get('recovery_history', []),
    jurisdiction_info=input_data.get('jurisdiction_info', {})
)
```
