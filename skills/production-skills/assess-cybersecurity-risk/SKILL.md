# Skill: Assess Cybersecurity Risk

## Domain
technology

## Description
Assesses organizational cybersecurity risk using framework-based evaluation, vulnerability analysis, and threat modeling for risk quantification.

## Tags
cybersecurity, risk, NIST, vulnerability, threat, compliance

## Use Cases
- Security posture assessment
- Vulnerability prioritization
- Compliance gap analysis
- Risk quantification

## Proprietary Business Rules

### Rule 1: NIST Framework Mapping
Assessment against NIST Cybersecurity Framework controls.

### Rule 2: Vulnerability Scoring
Risk-adjusted vulnerability prioritization using CVSS.

### Rule 3: Threat Likelihood Estimation
Industry-specific threat probability assessment.

### Rule 4: Business Impact Analysis
Quantification of potential breach impact.

## Input Parameters
- `organization_id` (string): Organization identifier
- `asset_inventory` (list): IT asset details
- `vulnerability_data` (list): Vulnerability scan results
- `control_status` (dict): Security control implementation
- `threat_intel` (dict): Threat intelligence data
- `business_context` (dict): Business criticality info

## Output
- `risk_score` (float): Overall cyber risk score
- `control_gaps` (list): Security control deficiencies
- `critical_vulnerabilities` (list): Priority vulnerabilities
- `threat_assessment` (dict): Threat analysis results
- `recommendations` (list): Risk mitigation actions

## Implementation
The assessment logic is implemented in `cyber_assessor.py` and references data from CSV files:
- `required_controls.csv` - Reference data
- `cvss_thresholds.csv` - Reference data
- `threat_landscape.csv` - Reference data
- `impact_factors.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from cyber_assessor import assess_cyber_risk

result = assess_cyber_risk(
    organization_id="ORG-001",
    asset_inventory=[{"type": "server", "criticality": "high", "exposure": "internet"}],
    vulnerability_data=[{"cve": "CVE-2025-1234", "cvss": 9.8, "affected_assets": 5}],
    control_status={"mfa": True, "encryption": True, "patching": "partial"},
    threat_intel={"industry": "financial", "recent_campaigns": ["ransomware"]},
    business_context={"data_sensitivity": "high", "regulatory": ["PCI", "SOX"]}
)

print(f"Risk Score: {result['risk_score']}")
```

## Test Execution
```python
from cyber_assessor import assess_cyber_risk

result = assess_cyber_risk(
    organization_id=input_data.get('organization_id'),
    asset_inventory=input_data.get('asset_inventory', []),
    vulnerability_data=input_data.get('vulnerability_data', []),
    control_status=input_data.get('control_status', {}),
    threat_intel=input_data.get('threat_intel', {}),
    business_context=input_data.get('business_context', {})
)
```
