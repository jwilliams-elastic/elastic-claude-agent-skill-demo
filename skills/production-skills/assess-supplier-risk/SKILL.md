# Skill: Assess Supplier Risk

## Domain
supply_chain

## Description
Assesses supplier risk across financial, operational, and compliance dimensions for supply chain risk management.

## Tags
supplier, risk, procurement, supply-chain, due-diligence, vendor

## Use Cases
- Supplier qualification
- Risk monitoring
- Due diligence
- Contingency planning

## Proprietary Business Rules

### Rule 1: Financial Risk Assessment
Supplier financial health evaluation.

### Rule 2: Operational Risk Scoring
Delivery and quality risk analysis.

### Rule 3: Compliance Risk Check
Regulatory and ethical compliance verification.

### Rule 4: Concentration Risk
Single-source dependency assessment.

## Input Parameters
- `supplier_id` (string): Supplier identifier
- `financial_data` (dict): Supplier financials
- `performance_data` (dict): Historical performance
- `compliance_data` (dict): Compliance information
- `relationship_data` (dict): Business relationship details
- `industry_data` (dict): Industry context

## Output
- `risk_score` (float): Overall supplier risk
- `risk_breakdown` (dict): Risk by category
- `financial_health` (dict): Financial assessment
- `alerts` (list): Risk alerts
- `mitigation_actions` (list): Risk mitigation recommendations

## Implementation
The assessment logic is implemented in `supplier_risk_assessor.py` and references data from CSV files:
- `risk_categories.csv` - Reference data
- `financial_thresholds.csv` - Reference data
- `operational_thresholds.csv` - Reference data
- `risk_ratings.csv` - Reference data
- `mitigation_strategies.csv` - Reference data
- `monitoring_frequency.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from supplier_risk_assessor import assess_supplier_risk

result = assess_supplier_risk(
    supplier_id="SUP-001",
    financial_data={"revenue": 50000000, "profit_margin": 0.08, "debt_ratio": 0.45},
    performance_data={"on_time_delivery": 0.94, "defect_rate": 0.02},
    compliance_data={"iso_certified": True, "sustainability_score": 75},
    relationship_data={"years_supplier": 5, "spend_pct": 0.15},
    industry_data={"industry": "manufacturing", "region": "asia_pacific"}
)

print(f"Supplier Risk Score: {result['risk_score']}")
```

## Test Execution
```python
from supplier_risk_assessor import assess_supplier_risk

result = assess_supplier_risk(
    supplier_id=input_data.get('supplier_id'),
    financial_data=input_data.get('financial_data', {}),
    performance_data=input_data.get('performance_data', {}),
    compliance_data=input_data.get('compliance_data', {}),
    relationship_data=input_data.get('relationship_data', {}),
    industry_data=input_data.get('industry_data', {})
)
```
