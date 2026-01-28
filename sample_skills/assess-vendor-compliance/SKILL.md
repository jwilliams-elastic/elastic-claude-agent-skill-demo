# Skill: Assess Vendor Compliance

## Domain
supply_chain

## Description
Assesses vendor compliance with contractual requirements, quality standards, and regulatory obligations for supplier management.

## Tags
vendor, compliance, procurement, supplier, audit, quality

## Use Cases
- Vendor qualification review
- Compliance monitoring
- Performance assessment
- Risk identification

## Proprietary Business Rules

### Rule 1: Certification Verification
Validation of required vendor certifications.

### Rule 2: Performance Metrics
Assessment against SLA and KPI requirements.

### Rule 3: Regulatory Compliance
Verification of regulatory obligation adherence.

### Rule 4: Risk Scoring
Vendor risk assessment based on compliance status.

## Input Parameters
- `vendor_id` (string): Vendor identifier
- `contract_requirements` (dict): Contractual obligations
- `vendor_certifications` (list): Current certifications
- `performance_data` (dict): Performance metrics
- `audit_history` (list): Previous audit results
- `regulatory_requirements` (list): Applicable regulations

## Output
- `compliance_score` (float): Overall compliance rating
- `certification_status` (dict): Certification verification
- `performance_assessment` (dict): SLA/KPI analysis
- `compliance_gaps` (list): Identified deficiencies
- `risk_rating` (string): Vendor risk level

## Implementation
The assessment logic is implemented in `compliance_assessor.py` and references data from CSV files:
- `compliance_categories.csv` - Reference data
- `certification_requirements.csv` - Reference data
- `risk_thresholds.csv` - Reference data
- `audit_criteria.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from compliance_assessor import assess_vendor

result = assess_vendor(
    vendor_id="VND-001",
    contract_requirements={"certifications": ["ISO9001"], "on_time_delivery": 0.95},
    vendor_certifications=[{"type": "ISO9001", "expiry": "2026-12-31"}],
    performance_data={"on_time_delivery": 0.92, "defect_rate": 0.02},
    audit_history=[{"date": "2025-06-01", "score": 85, "findings": 2}],
    regulatory_requirements=["SOC2", "GDPR"]
)

print(f"Compliance Score: {result['compliance_score']}")
```

## Test Execution
```python
from compliance_assessor import assess_vendor

result = assess_vendor(
    vendor_id=input_data.get('vendor_id'),
    contract_requirements=input_data.get('contract_requirements', {}),
    vendor_certifications=input_data.get('vendor_certifications', []),
    performance_data=input_data.get('performance_data', {}),
    audit_history=input_data.get('audit_history', []),
    regulatory_requirements=input_data.get('regulatory_requirements', [])
)
```
