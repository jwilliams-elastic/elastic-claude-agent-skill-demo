# Skill: Assess Vehicle Recall Risk

## Domain
automotive

## Description
Evaluates vehicle components and systems for potential recall risk based on warranty claim patterns, field failure data, and regulatory compliance requirements specific to automotive OEM standards.

## Tags
automotive, recall-management, quality-assurance, risk-assessment, nhtsa-compliance

## Use Cases
- Proactive recall risk identification
- Warranty trend analysis
- Supplier quality monitoring
- NHTSA early warning compliance

## Proprietary Business Rules

### Rule 1: Failure Rate Threshold
Components exceeding proprietary failure rate thresholds (varying by safety criticality) trigger recall evaluation.

### Rule 2: Geographic Clustering
Failures concentrated in specific regions may indicate environmental factors requiring targeted investigation.

### Rule 3: Time-in-Service Correlation
Failure patterns correlated with vehicle age identify potential design life issues.

### Rule 4: Safety System Prioritization
Brake, steering, and restraint system failures have accelerated review timelines.

## Input Parameters
- `component_id` (string): Component part number
- `failure_count` (int): Number of reported failures
- `vehicles_in_field` (int): Total vehicles with component
- `failure_reports` (list): Detailed failure report data
- `component_category` (string): Safety criticality category
- `affected_models` (list): List of affected vehicle models
- `production_date_range` (dict): Start and end production dates

## Output
- `recall_risk_level` (string): LOW, MEDIUM, HIGH, CRITICAL
- `recommended_action` (string): Investigation, monitoring, or recall initiation
- `risk_score` (float): Calculated risk score (0-100)
- `contributing_factors` (list): Identified risk factors
- `regulatory_timeline` (dict): NHTSA reporting requirements

## Implementation
The risk assessment logic is implemented in `recall_assessor.py` and references thresholds from CSV files:
- `categories.csv` - Reference data
- `risk_scoring.csv` - Reference data
- `geographic_regions.csv` - Reference data
- `nhtsa_thresholds.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from recall_assessor import assess_recall_risk

result = assess_recall_risk(
    component_id="BRK-2024-001",
    failure_count=45,
    vehicles_in_field=125000,
    failure_reports=[{"severity": "high", "region": "southwest", "mileage": 35000}],
    component_category="brake_system",
    affected_models=["Sedan-X", "SUV-Y"],
    production_date_range={"start": "2023-01-01", "end": "2024-06-30"}
)

print(f"Risk Level: {result['recall_risk_level']}")
```

## Test Execution
```python
from recall_assessor import assess_recall_risk

result = assess_recall_risk(
    component_id=input_data.get('component_id'),
    failure_count=input_data.get('failure_count', 0),
    vehicles_in_field=input_data.get('vehicles_in_field', 1),
    failure_reports=input_data.get('failure_reports', []),
    component_category=input_data.get('component_category'),
    affected_models=input_data.get('affected_models', []),
    production_date_range=input_data.get('production_date_range', {})
)
```
