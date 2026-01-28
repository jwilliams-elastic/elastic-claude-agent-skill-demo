# Skill: Assess Operational Risk

## Domain
financial_services

## Description
Assesses operational risk using Basel framework methodology including loss event analysis, risk control self-assessment, and capital calculation.

## Tags
operational-risk, Basel, banking, compliance, risk-management, RCSA

## Use Cases
- Operational loss analysis
- Risk control assessment
- Capital requirement calculation
- Key risk indicator monitoring

## Proprietary Business Rules

### Rule 1: Loss Event Classification
Basel event type categorization and root cause analysis.

### Rule 2: RCSA Scoring
Risk and control self-assessment methodology.

### Rule 3: Capital Calculation
Operational risk capital requirement using standardized approach.

### Rule 4: KRI Threshold Monitoring
Key risk indicator breach detection.

## Input Parameters
- `assessment_id` (string): Assessment identifier
- `loss_events` (list): Historical loss event data
- `control_assessments` (list): RCSA results
- `business_line_data` (dict): Revenue by business line
- `kri_data` (dict): Key risk indicator values
- `assessment_period` (dict): Assessment time range

## Output
- `risk_score` (float): Overall operational risk score
- `loss_analysis` (dict): Loss event analysis
- `control_effectiveness` (dict): Control assessment results
- `capital_requirement` (float): Required capital
- `kri_breaches` (list): KRI threshold breaches

## Implementation
The assessment logic is implemented in `oprisk_assessor.py` and references data from `oprisk_framework.json`.

## Usage Example
```python
from oprisk_assessor import assess_operational_risk

result = assess_operational_risk(
    assessment_id="ORA-2026-001",
    loss_events=[{"type": "execution", "amount": 50000, "date": "2025-06-15"}],
    control_assessments=[{"control_id": "CTL-001", "effectiveness": 0.85}],
    business_line_data={"trading": 100000000, "retail_banking": 200000000},
    kri_data={"system_downtime_hours": 5, "failed_transactions": 150},
    assessment_period={"start": "2025-01-01", "end": "2025-12-31"}
)

print(f"Risk Score: {result['risk_score']}")
```

## Test Execution
```python
from oprisk_assessor import assess_operational_risk

result = assess_operational_risk(
    assessment_id=input_data.get('assessment_id'),
    loss_events=input_data.get('loss_events', []),
    control_assessments=input_data.get('control_assessments', []),
    business_line_data=input_data.get('business_line_data', {}),
    kri_data=input_data.get('kri_data', {}),
    assessment_period=input_data.get('assessment_period', {})
)
```
