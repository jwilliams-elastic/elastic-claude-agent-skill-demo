# Skill: Evaluate AI Model Governance

## Domain
technology

## Description
Assesses AI/ML model deployments against enterprise governance frameworks, regulatory requirements, and responsible AI principles. Evaluates model risk, explainability, bias, data lineage, and operational controls to ensure compliant and trustworthy AI systems.

## Business Rules
This skill implements comprehensive AI governance evaluation based on industry standards (NIST AI RMF, EU AI Act, SR 11-7):

1. **Model Risk Classification**: Tier 1 (Critical), Tier 2 (High), Tier 3 (Medium), Tier 4 (Low) based on business impact and autonomy level
2. **Explainability Requirement**: Tier 1-2 models require full explainability; black-box models prohibited for high-stakes decisions
3. **Bias Testing Mandate**: All customer-facing models must pass demographic parity and equalized odds tests
4. **Data Lineage**: Complete data provenance required for regulated industries (financial services, healthcare)
5. **Model Monitoring**: Real-time drift detection required for Tier 1 models; monthly for Tier 2
6. **Human Override**: Tier 1-2 models must have human-in-the-loop controls with <5 minute escalation SLA

## Input Parameters
- `model_name` (string): Name/ID of the AI model
- `model_type` (string): "classification", "regression", "nlp", "computer_vision", "generative"
- `use_case` (string): Business use case description
- `decision_autonomy` (string): "fully_autonomous", "human_assisted", "human_final_decision"
- `customer_facing` (bool): Whether model outputs directly affect customers
- `regulated_industry` (bool): Whether deployed in regulated industry
- `explainability_method` (string): "none", "shap", "lime", "attention", "inherent"
- `bias_testing_performed` (bool): Whether bias testing was conducted
- `bias_metrics` (dict, optional): Results of bias testing if performed
- `data_lineage_documented` (bool): Whether data lineage is fully documented
- `drift_monitoring_enabled` (bool): Whether model drift monitoring is active
- `human_override_available` (bool): Whether human override mechanism exists
- `last_validation_date` (string): Date of last model validation (ISO format)

## Output
Returns a governance assessment with:
- `compliant` (bool): Overall compliance status
- `risk_tier` (string): Model risk classification (Tier 1-4)
- `governance_score` (float): Composite governance score (0-100)
- `violations` (list): List of governance violations with severity
- `required_controls` (list): Controls that must be implemented
- `regulatory_flags` (list): Specific regulatory concerns (EU AI Act, SR 11-7, etc.)
- `remediation_priority` (string): "critical", "high", "medium", "low"
- `next_validation_due` (string): Required next validation date

## Usage Example
```python
from ai_governance import evaluate_model_governance

result = evaluate_model_governance(
    model_name="credit-decision-v2",
    model_type="classification",
    use_case="Automated credit approval decisions",
    decision_autonomy="fully_autonomous",
    customer_facing=True,
    regulated_industry=True,
    explainability_method="shap",
    bias_testing_performed=True,
    bias_metrics={"demographic_parity": 0.92, "equalized_odds": 0.88},
    data_lineage_documented=True,
    drift_monitoring_enabled=True,
    human_override_available=False,
    last_validation_date="2025-06-15"
)
```

## Tags
technology, ai-governance, mlops, risk-management, compliance, responsible-ai, financial-services

## Implementation
The governance logic is implemented in `ai_governance.py` and references:
- `risk_tier_matrix.csv` - Risk classification criteria
- `regulatory_requirements.csv` - Regulatory framework requirements
- `control_catalog.csv` - Required controls by risk tier
- `bias_thresholds.csv` - Acceptable bias metric thresholds
