"""
AI Model Governance Evaluation Module

Assesses AI/ML model deployments against enterprise governance frameworks,
regulatory requirements (NIST AI RMF, EU AI Act, SR 11-7), and responsible AI principles.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def load_csv_as_dict(filename: str, key_column: str) -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column, row.get('id', ''))
            for k, v in list(row.items()):
                if v == '':
                    continue
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result[key] = row
    return result


def load_csv_as_list(filename: str) -> List[Dict[str, Any]]:
    """Load a CSV file and return as list of dictionaries."""
    csv_path = Path(__file__).parent / filename
    result = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            for k, v in list(row.items()):
                if v == '':
                    continue
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result.append(row)
    return result


def determine_risk_tier(
    decision_autonomy: str,
    customer_facing: bool,
    regulated_industry: bool,
    model_type: str
) -> str:
    """Determine model risk tier based on classification criteria."""
    risk_score = 0

    # Decision autonomy impact
    autonomy_scores = {
        "fully_autonomous": 40,
        "human_assisted": 20,
        "human_final_decision": 10
    }
    risk_score += autonomy_scores.get(decision_autonomy, 20)

    # Customer-facing impact
    if customer_facing:
        risk_score += 25

    # Regulated industry impact
    if regulated_industry:
        risk_score += 25

    # Model type complexity
    type_scores = {
        "generative": 15,
        "nlp": 12,
        "computer_vision": 10,
        "classification": 8,
        "regression": 5
    }
    risk_score += type_scores.get(model_type, 8)

    # Determine tier
    if risk_score >= 80:
        return "Tier 1"
    elif risk_score >= 60:
        return "Tier 2"
    elif risk_score >= 40:
        return "Tier 3"
    else:
        return "Tier 4"


def validate_explainability(
    risk_tier: str,
    explainability_method: str
) -> Dict[str, Any]:
    """Validate explainability requirements based on risk tier."""
    tier_requirements = {
        "Tier 1": ["shap", "lime", "inherent"],
        "Tier 2": ["shap", "lime", "attention", "inherent"],
        "Tier 3": ["shap", "lime", "attention", "inherent", "none"],
        "Tier 4": ["shap", "lime", "attention", "inherent", "none"]
    }

    required_methods = tier_requirements.get(risk_tier, [])
    compliant = explainability_method in required_methods

    return {
        "compliant": compliant,
        "method_used": explainability_method,
        "required_for_tier": risk_tier in ["Tier 1", "Tier 2"] and explainability_method == "none",
        "violation": None if compliant else f"{risk_tier} models require explainability - 'none' not permitted"
    }


def validate_bias_testing(
    customer_facing: bool,
    bias_testing_performed: bool,
    bias_metrics: Optional[Dict[str, float]]
) -> Dict[str, Any]:
    """Validate bias testing requirements."""
    thresholds = {
        "demographic_parity": 0.80,
        "equalized_odds": 0.80,
        "predictive_parity": 0.80
    }

    violations = []

    if customer_facing and not bias_testing_performed:
        violations.append("Customer-facing models require bias testing")

    if bias_metrics:
        for metric, value in bias_metrics.items():
            threshold = thresholds.get(metric, 0.80)
            if value < threshold:
                violations.append(f"{metric} ({value:.2f}) below threshold ({threshold})")

    return {
        "compliant": len(violations) == 0,
        "testing_performed": bias_testing_performed,
        "metrics": bias_metrics or {},
        "thresholds": thresholds,
        "violations": violations
    }


def validate_monitoring(
    risk_tier: str,
    drift_monitoring_enabled: bool
) -> Dict[str, Any]:
    """Validate drift monitoring requirements."""
    tier_requirements = {
        "Tier 1": {"required": True, "frequency": "real-time"},
        "Tier 2": {"required": True, "frequency": "monthly"},
        "Tier 3": {"required": False, "frequency": "quarterly"},
        "Tier 4": {"required": False, "frequency": "annual"}
    }

    requirement = tier_requirements.get(risk_tier, {"required": False, "frequency": "annual"})
    compliant = not requirement["required"] or drift_monitoring_enabled

    return {
        "compliant": compliant,
        "monitoring_enabled": drift_monitoring_enabled,
        "required_frequency": requirement["frequency"],
        "violation": None if compliant else f"{risk_tier} models require drift monitoring"
    }


def validate_human_override(
    risk_tier: str,
    human_override_available: bool
) -> Dict[str, Any]:
    """Validate human override requirements."""
    requires_override = risk_tier in ["Tier 1", "Tier 2"]
    compliant = not requires_override or human_override_available

    return {
        "compliant": compliant,
        "override_available": human_override_available,
        "required": requires_override,
        "violation": None if compliant else f"{risk_tier} models require human-in-the-loop controls"
    }


def get_required_controls(risk_tier: str) -> List[Dict[str, Any]]:
    """Get required controls for the model risk tier."""
    controls_by_tier = {
        "Tier 1": [
            {"control": "Real-time drift monitoring", "criticality": "mandatory"},
            {"control": "Full explainability (SHAP/LIME)", "criticality": "mandatory"},
            {"control": "Human-in-the-loop with <5min SLA", "criticality": "mandatory"},
            {"control": "Quarterly validation", "criticality": "mandatory"},
            {"control": "Bias testing with demographic parity", "criticality": "mandatory"},
            {"control": "Complete data lineage documentation", "criticality": "mandatory"},
            {"control": "Model risk committee approval", "criticality": "mandatory"}
        ],
        "Tier 2": [
            {"control": "Monthly drift monitoring", "criticality": "mandatory"},
            {"control": "Explainability documentation", "criticality": "mandatory"},
            {"control": "Human override capability", "criticality": "mandatory"},
            {"control": "Semi-annual validation", "criticality": "mandatory"},
            {"control": "Bias testing for customer-facing", "criticality": "conditional"},
            {"control": "Data lineage documentation", "criticality": "mandatory"}
        ],
        "Tier 3": [
            {"control": "Quarterly drift review", "criticality": "recommended"},
            {"control": "Annual validation", "criticality": "mandatory"},
            {"control": "Basic monitoring", "criticality": "mandatory"},
            {"control": "Documentation", "criticality": "mandatory"}
        ],
        "Tier 4": [
            {"control": "Annual review", "criticality": "mandatory"},
            {"control": "Basic documentation", "criticality": "mandatory"}
        ]
    }

    return controls_by_tier.get(risk_tier, [])


def get_regulatory_flags(
    regulated_industry: bool,
    customer_facing: bool,
    decision_autonomy: str,
    risk_tier: str
) -> List[Dict[str, str]]:
    """Identify applicable regulatory requirements."""
    flags = []

    if regulated_industry:
        flags.append({
            "regulation": "SR 11-7",
            "description": "Model Risk Management guidance for banking",
            "requirement": "Comprehensive model documentation and validation"
        })

    if customer_facing and decision_autonomy == "fully_autonomous":
        flags.append({
            "regulation": "EU AI Act - High Risk",
            "description": "EU AI Act high-risk AI system requirements",
            "requirement": "Conformity assessment, CE marking, post-market monitoring"
        })

    if risk_tier in ["Tier 1", "Tier 2"]:
        flags.append({
            "regulation": "NIST AI RMF",
            "description": "NIST AI Risk Management Framework",
            "requirement": "MAP, MEASURE, MANAGE, GOVERN functions"
        })

    if customer_facing:
        flags.append({
            "regulation": "FTC Act Section 5",
            "description": "Unfair or deceptive practices",
            "requirement": "Algorithmic fairness and transparency"
        })

    return flags


def calculate_governance_score(validations: Dict[str, Dict]) -> float:
    """Calculate composite governance score."""
    weights = {
        "explainability": 0.20,
        "bias": 0.25,
        "monitoring": 0.20,
        "human_override": 0.15,
        "data_lineage": 0.10,
        "validation_currency": 0.10
    }

    score = 0
    for key, weight in weights.items():
        if key in validations and validations[key].get("compliant", False):
            score += weight * 100
        elif key in validations:
            # Partial credit for some compliance
            partial = validations[key].get("partial_score", 0)
            score += weight * partial

    return round(score, 1)


def determine_remediation_priority(violations: List[Dict], risk_tier: str) -> str:
    """Determine remediation priority based on violations and risk tier."""
    critical_violations = [v for v in violations if v.get("severity") == "critical"]
    high_violations = [v for v in violations if v.get("severity") == "high"]

    if critical_violations or (risk_tier == "Tier 1" and len(violations) > 0):
        return "critical"
    elif high_violations or (risk_tier == "Tier 2" and len(violations) > 0):
        return "high"
    elif violations:
        return "medium"
    else:
        return "low"


def calculate_next_validation_date(risk_tier: str, last_validation_date: str) -> str:
    """Calculate next required validation date based on risk tier."""
    validation_intervals = {
        "Tier 1": 90,   # Quarterly
        "Tier 2": 180,  # Semi-annual
        "Tier 3": 365,  # Annual
        "Tier 4": 365   # Annual
    }

    interval = validation_intervals.get(risk_tier, 365)

    try:
        last_date = datetime.fromisoformat(last_validation_date)
        next_date = last_date + timedelta(days=interval)
        return next_date.strftime("%Y-%m-%d")
    except (ValueError, TypeError):
        return datetime.now().strftime("%Y-%m-%d")


def evaluate_model_governance(
    model_name: str,
    model_type: str,
    use_case: str,
    decision_autonomy: str,
    customer_facing: bool,
    regulated_industry: bool,
    explainability_method: str,
    bias_testing_performed: bool,
    bias_metrics: Optional[Dict[str, float]],
    data_lineage_documented: bool,
    drift_monitoring_enabled: bool,
    human_override_available: bool,
    last_validation_date: str
) -> Dict[str, Any]:
    """
    Evaluate AI/ML model against governance requirements.

    Returns comprehensive governance assessment with compliance status,
    risk tier, violations, required controls, and remediation guidance.
    """
    # Determine risk tier
    risk_tier = determine_risk_tier(
        decision_autonomy, customer_facing, regulated_industry, model_type
    )

    # Run validations
    explainability_result = validate_explainability(risk_tier, explainability_method)
    bias_result = validate_bias_testing(customer_facing, bias_testing_performed, bias_metrics)
    monitoring_result = validate_monitoring(risk_tier, drift_monitoring_enabled)
    override_result = validate_human_override(risk_tier, human_override_available)

    # Data lineage validation
    lineage_compliant = not regulated_industry or data_lineage_documented
    lineage_result = {
        "compliant": lineage_compliant,
        "documented": data_lineage_documented,
        "violation": None if lineage_compliant else "Regulated industries require complete data lineage"
    }

    # Validation currency check
    try:
        last_date = datetime.fromisoformat(last_validation_date)
        days_since = (datetime.now() - last_date).days
        validation_intervals = {"Tier 1": 90, "Tier 2": 180, "Tier 3": 365, "Tier 4": 365}
        max_interval = validation_intervals.get(risk_tier, 365)
        validation_current = days_since <= max_interval
    except (ValueError, TypeError):
        validation_current = False
        days_since = 999

    validation_result = {
        "compliant": validation_current,
        "days_since_validation": days_since,
        "violation": None if validation_current else f"Model validation overdue ({days_since} days since last validation)"
    }

    # Compile validations
    validations = {
        "explainability": explainability_result,
        "bias": bias_result,
        "monitoring": monitoring_result,
        "human_override": override_result,
        "data_lineage": lineage_result,
        "validation_currency": validation_result
    }

    # Compile violations
    violations = []
    severity_map = {
        "Tier 1": "critical",
        "Tier 2": "high",
        "Tier 3": "medium",
        "Tier 4": "low"
    }
    base_severity = severity_map.get(risk_tier, "medium")

    for key, result in validations.items():
        if not result.get("compliant", True):
            violation = result.get("violation") or result.get("violations", [])
            if isinstance(violation, list):
                for v in violation:
                    violations.append({"area": key, "description": v, "severity": base_severity})
            elif violation:
                violations.append({"area": key, "description": violation, "severity": base_severity})

    # Calculate governance score
    governance_score = calculate_governance_score(validations)

    # Overall compliance
    overall_compliant = all(v.get("compliant", True) for v in validations.values())

    # Get required controls
    required_controls = get_required_controls(risk_tier)

    # Get regulatory flags
    regulatory_flags = get_regulatory_flags(
        regulated_industry, customer_facing, decision_autonomy, risk_tier
    )

    # Determine remediation priority
    remediation_priority = determine_remediation_priority(violations, risk_tier)

    # Calculate next validation date
    next_validation = calculate_next_validation_date(risk_tier, last_validation_date)

    return {
        "model_name": model_name,
        "use_case": use_case,
        "compliant": overall_compliant,
        "risk_tier": risk_tier,
        "governance_score": governance_score,
        "violations": violations,
        "required_controls": required_controls,
        "regulatory_flags": regulatory_flags,
        "remediation_priority": remediation_priority,
        "next_validation_due": next_validation,
        "validation_details": validations
    }


def main():
    """Example usage."""
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

    print(f"Model: {result['model_name']}")
    print(f"Compliant: {result['compliant']}")
    print(f"Risk Tier: {result['risk_tier']}")
    print(f"Governance Score: {result['governance_score']}")
    print(f"Violations: {len(result['violations'])}")
    print(f"Remediation Priority: {result['remediation_priority']}")


if __name__ == "__main__":
    main()
