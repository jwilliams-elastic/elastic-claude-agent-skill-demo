"""
Contract Risk Analysis Module

Implements contract risk assessment including
clause analysis, financial risk, and compliance evaluation.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional



def load_csv_as_dict(filename: str, key_column: str = 'id') -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column, row.get('key', ''))
            # Convert numeric values
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
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric values
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


def load_parameters(filename: str = 'parameters.csv') -> Dict[str, Any]:
    """Load parameters CSV as key-value dictionary."""
    csv_path = Path(__file__).parent / filename
    if not csv_path.exists():
        return {}
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('key', '')
            value = row.get('value', '')
            try:
                if '.' in str(value):
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except (ValueError, TypeError):
                if value.lower() == 'true':
                    result[key] = True
                elif value.lower() == 'false':
                    result[key] = False
                else:
                    result[key] = value
    return result

def load_key_value_csv(filename: str) -> Dict[str, Any]:
    """Load a key-value CSV file as a flat dictionary."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('key', row.get('id', ''))
            value = row.get('value', '')
            try:
                if '.' in str(value):
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except (ValueError, TypeError):
                if str(value).lower() == 'true':
                    result[key] = True
                elif str(value).lower() == 'false':
                    result[key] = False
                else:
                    result[key] = value
    return result


def load_risk_matrix() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    risk_categories_data = load_csv_as_dict("risk_categories.csv")
    clause_risk_scores_data = load_key_value_csv("clause_risk_scores.csv")
    payment_term_risk_data = load_csv_as_dict("payment_term_risk.csv")
    liability_cap_standards_data = load_csv_as_dict("liability_cap_standards.csv")
    sla_penalty_thresholds_data = load_key_value_csv("sla_penalty_thresholds.csv")
    contract_value_thresholds_data = load_csv_as_dict("contract_value_thresholds.csv")
    recommended_protections_data = load_key_value_csv("recommended_protections.csv")
    params = load_parameters()
    return {
        "risk_categories": risk_categories_data,
        "clause_risk_scores": clause_risk_scores_data,
        "payment_term_risk": payment_term_risk_data,
        "liability_cap_standards": liability_cap_standards_data,
        "sla_penalty_thresholds": sla_penalty_thresholds_data,
        "contract_value_thresholds": contract_value_thresholds_data,
        "recommended_protections": recommended_protections_data,
        **params
    }


def analyze_financial_risk(
    contract_terms: Dict,
    payment_risk: Dict,
    liability_standards: Dict
) -> Dict[str, Any]:
    """Analyze financial risk elements."""
    risk_score = 0
    findings = []

    # Payment terms
    payment_term = contract_terms.get("payment_terms", "net_30")
    payment_config = payment_risk.get(payment_term, {"risk": "medium", "score": 30})
    risk_score += payment_config.get("score", 30)
    findings.append({
        "element": "payment_terms",
        "value": payment_term,
        "risk_level": payment_config.get("risk", "medium"),
        "score": payment_config.get("score", 30)
    })

    # Liability cap
    liability_cap = contract_terms.get("liability_cap_type", "contract_value_1x")
    liability_config = liability_standards.get(liability_cap, {"acceptable": False, "score": 50})
    risk_score += liability_config.get("score", 50)
    findings.append({
        "element": "liability_cap",
        "value": liability_cap,
        "acceptable": liability_config.get("acceptable", False),
        "score": liability_config.get("score", 50)
    })

    # Contract value risk
    contract_value = contract_terms.get("total_value", 0)
    if contract_value > 2000000:
        value_risk = 40
    elif contract_value > 500000:
        value_risk = 25
    elif contract_value > 100000:
        value_risk = 15
    else:
        value_risk = 5
    risk_score += value_risk
    findings.append({
        "element": "contract_value",
        "value": contract_value,
        "score": value_risk
    })

    return {
        "financial_risk_score": round(risk_score / 3, 1),
        "findings": findings
    }


def analyze_operational_risk(
    operational_terms: Dict
) -> Dict[str, Any]:
    """Analyze operational risk elements."""
    risk_score = 0
    findings = []

    # SLA requirements
    sla_uptime = operational_terms.get("sla_uptime_pct", 99.5)
    if sla_uptime >= 99.99:
        sla_risk = 60  # Very demanding SLA
    elif sla_uptime >= 99.9:
        sla_risk = 40
    elif sla_uptime >= 99.5:
        sla_risk = 20
    else:
        sla_risk = 10
    risk_score += sla_risk
    findings.append({
        "element": "sla_requirements",
        "value": f"{sla_uptime}% uptime",
        "score": sla_risk
    })

    # Response time commitments
    response_time = operational_terms.get("response_time_hours", 24)
    if response_time <= 1:
        response_risk = 50
    elif response_time <= 4:
        response_risk = 30
    elif response_time <= 24:
        response_risk = 15
    else:
        response_risk = 5
    risk_score += response_risk
    findings.append({
        "element": "response_time",
        "value": f"{response_time} hours",
        "score": response_risk
    })

    # Resource commitments
    dedicated_resources = operational_terms.get("dedicated_resources_required", False)
    if dedicated_resources:
        resource_risk = 35
    else:
        resource_risk = 10
    risk_score += resource_risk
    findings.append({
        "element": "resource_commitments",
        "value": "dedicated" if dedicated_resources else "shared",
        "score": resource_risk
    })

    return {
        "operational_risk_score": round(risk_score / 3, 1),
        "findings": findings
    }


def analyze_legal_risk(
    legal_terms: Dict,
    clause_scores: Dict
) -> Dict[str, Any]:
    """Analyze legal risk elements."""
    risk_score = 0
    findings = []

    # Check for high-risk clauses
    clauses_present = legal_terms.get("clauses_present", [])
    for clause in clauses_present:
        clause_risk = clause_scores.get(clause, 30)
        risk_score += clause_risk
        findings.append({
            "element": "clause",
            "clause_type": clause,
            "score": clause_risk
        })

    # Indemnification
    indemnification = legal_terms.get("indemnification_type", "mutual")
    if indemnification == "unlimited":
        indem_risk = 90
    elif indemnification == "one_way":
        indem_risk = 60
    elif indemnification == "mutual":
        indem_risk = 20
    else:
        indem_risk = 30
    risk_score += indem_risk
    findings.append({
        "element": "indemnification",
        "value": indemnification,
        "score": indem_risk
    })

    # Dispute resolution
    dispute_resolution = legal_terms.get("dispute_resolution", "arbitration")
    if dispute_resolution == "litigation":
        dispute_risk = 50
    elif dispute_resolution == "arbitration":
        dispute_risk = 25
    elif dispute_resolution == "mediation_first":
        dispute_risk = 15
    else:
        dispute_risk = 30
    risk_score += dispute_risk
    findings.append({
        "element": "dispute_resolution",
        "value": dispute_resolution,
        "score": dispute_risk
    })

    avg_score = risk_score / (len(findings)) if findings else 0

    return {
        "legal_risk_score": round(avg_score, 1),
        "findings": findings
    }


def analyze_compliance_risk(
    compliance_terms: Dict
) -> Dict[str, Any]:
    """Analyze compliance risk elements."""
    risk_score = 0
    findings = []

    # Data privacy requirements
    has_dpa = compliance_terms.get("data_protection_addendum", False)
    if not has_dpa and compliance_terms.get("handles_personal_data", False):
        privacy_risk = 70
        findings.append({
            "element": "data_privacy",
            "issue": "No DPA for personal data handling",
            "score": privacy_risk
        })
    else:
        privacy_risk = 10
    risk_score += privacy_risk

    # Audit rights
    audit_rights = compliance_terms.get("audit_rights", "none")
    if audit_rights == "none":
        audit_risk = 50
    elif audit_rights == "limited":
        audit_risk = 25
    else:
        audit_risk = 10
    risk_score += audit_risk
    findings.append({
        "element": "audit_rights",
        "value": audit_rights,
        "score": audit_risk
    })

    # Regulatory compliance
    regulatory_reqs = compliance_terms.get("regulatory_requirements", [])
    if not regulatory_reqs:
        reg_risk = 40
    else:
        reg_risk = 15
    risk_score += reg_risk
    findings.append({
        "element": "regulatory_compliance",
        "requirements": regulatory_reqs,
        "score": reg_risk
    })

    return {
        "compliance_risk_score": round(risk_score / 3, 1),
        "findings": findings
    }


def analyze_termination_risk(
    termination_terms: Dict
) -> Dict[str, Any]:
    """Analyze termination risk elements."""
    risk_score = 0
    findings = []

    # Termination for convenience
    tfc = termination_terms.get("termination_for_convenience", False)
    if not tfc:
        tfc_risk = 60
    else:
        tfc_risk = 15
    risk_score += tfc_risk
    findings.append({
        "element": "termination_for_convenience",
        "available": tfc,
        "score": tfc_risk
    })

    # Notice period
    notice_days = termination_terms.get("notice_period_days", 30)
    if notice_days >= 180:
        notice_risk = 60
    elif notice_days >= 90:
        notice_risk = 35
    elif notice_days >= 30:
        notice_risk = 15
    else:
        notice_risk = 5
    risk_score += notice_risk
    findings.append({
        "element": "notice_period",
        "value": f"{notice_days} days",
        "score": notice_risk
    })

    # Exit costs
    exit_costs = termination_terms.get("exit_costs_pct", 0)
    if exit_costs > 0.50:
        exit_risk = 70
    elif exit_costs > 0.25:
        exit_risk = 45
    elif exit_costs > 0:
        exit_risk = 25
    else:
        exit_risk = 10
    risk_score += exit_risk
    findings.append({
        "element": "exit_costs",
        "value": f"{exit_costs * 100}% of remaining value",
        "score": exit_risk
    })

    return {
        "termination_risk_score": round(risk_score / 3, 1),
        "findings": findings
    }


def check_red_flags(
    contract_text: str,
    red_flags: List[str]
) -> List[Dict]:
    """Check for red flag terms in contract."""
    found_flags = []
    text_lower = contract_text.lower()

    for flag in red_flags:
        if flag.lower() in text_lower:
            found_flags.append({
                "term": flag,
                "severity": "high",
                "recommendation": f"Review and negotiate removal of '{flag}'"
            })

    return found_flags


def determine_approval_level(
    contract_value: float,
    overall_risk_score: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Determine required approval level."""
    # Base on contract value
    for level, config in thresholds.items():
        max_val = config.get("max_value")
        if max_val is None or contract_value <= max_val:
            base_approval = config.get("approval_level", "manager")
            break
    else:
        base_approval = "executive"

    # Escalate if high risk
    approval_hierarchy = ["manager", "director", "vp", "executive"]
    base_idx = approval_hierarchy.index(base_approval)

    if overall_risk_score > 70:
        final_idx = min(base_idx + 2, len(approval_hierarchy) - 1)
    elif overall_risk_score > 50:
        final_idx = min(base_idx + 1, len(approval_hierarchy) - 1)
    else:
        final_idx = base_idx

    return {
        "value_based_approval": base_approval,
        "risk_adjusted_approval": approval_hierarchy[final_idx],
        "escalation_reason": "high_risk_score" if final_idx > base_idx else "none"
    }


def analyze_contract_risk(
    contract_id: str,
    contract_terms: Dict,
    operational_terms: Dict,
    legal_terms: Dict,
    compliance_terms: Dict,
    termination_terms: Dict,
    contract_text: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Analyze contract risk.

    Business Rules:
    1. Multi-category risk assessment
    2. Red flag identification
    3. Weighted risk scoring
    4. Approval level determination

    Args:
        contract_id: Contract identifier
        contract_terms: Financial/commercial terms
        operational_terms: Operational requirements
        legal_terms: Legal provisions
        compliance_terms: Compliance requirements
        termination_terms: Termination provisions
        contract_text: Full contract text for red flag scan
        analysis_date: Analysis date

    Returns:
        Contract risk analysis results
    """
    matrix = load_risk_matrix()
    categories = matrix.get("risk_categories", {})

    # Analyze each risk category
    financial = analyze_financial_risk(
        contract_terms,
        matrix.get("payment_term_risk", {}),
        matrix.get("liability_cap_standards", {})
    )

    operational = analyze_operational_risk(operational_terms)

    legal = analyze_legal_risk(
        legal_terms,
        matrix.get("clause_risk_scores", {})
    )

    compliance = analyze_compliance_risk(compliance_terms)

    termination = analyze_termination_risk(termination_terms)

    # Calculate weighted overall score
    risk_scores = {
        "financial": financial["financial_risk_score"],
        "operational": operational["operational_risk_score"],
        "legal": legal["legal_risk_score"],
        "compliance": compliance["compliance_risk_score"],
        "termination": termination["termination_risk_score"]
    }

    weighted_score = sum(
        risk_scores[cat] * categories.get(cat, {}).get("weight", 0.2)
        for cat in risk_scores
    )

    # Check red flags
    red_flags = check_red_flags(
        contract_text,
        matrix.get("red_flag_terms", [])
    )

    # Determine approval level
    approval = determine_approval_level(
        contract_terms.get("total_value", 0),
        weighted_score,
        matrix.get("contract_value_thresholds", {})
    )

    # Determine overall risk level
    if weighted_score >= 70:
        risk_level = "HIGH"
    elif weighted_score >= 50:
        risk_level = "MEDIUM"
    elif weighted_score >= 30:
        risk_level = "LOW"
    else:
        risk_level = "MINIMAL"

    return {
        "contract_id": contract_id,
        "analysis_date": analysis_date,
        "contract_value": contract_terms.get("total_value", 0),
        "risk_analysis": {
            "financial": financial,
            "operational": operational,
            "legal": legal,
            "compliance": compliance,
            "termination": termination
        },
        "category_scores": risk_scores,
        "overall_risk_score": round(weighted_score, 1),
        "risk_level": risk_level,
        "red_flags": red_flags,
        "approval_requirement": approval,
        "recommendations": generate_recommendations(risk_scores, red_flags)
    }


def generate_recommendations(
    risk_scores: Dict,
    red_flags: List
) -> List[str]:
    """Generate risk mitigation recommendations."""
    recommendations = []

    if risk_scores.get("financial", 0) > 50:
        recommendations.append("Negotiate improved payment terms or liability caps")

    if risk_scores.get("legal", 0) > 50:
        recommendations.append("Engage legal counsel for clause review")

    if risk_scores.get("compliance", 0) > 50:
        recommendations.append("Ensure data protection addendum is included")

    if risk_scores.get("termination", 0) > 50:
        recommendations.append("Negotiate termination for convenience rights")

    if red_flags:
        recommendations.append(f"Address {len(red_flags)} red flag terms before execution")

    return recommendations


if __name__ == "__main__":
    import json
    result = analyze_contract_risk(
        contract_id="CTR-001",
        contract_terms={
            "total_value": 750000,
            "payment_terms": "net_45",
            "liability_cap_type": "annual_fees_12_months"
        },
        operational_terms={
            "sla_uptime_pct": 99.9,
            "response_time_hours": 4,
            "dedicated_resources_required": False
        },
        legal_terms={
            "clauses_present": ["auto_renewal", "non_compete"],
            "indemnification_type": "mutual",
            "dispute_resolution": "arbitration"
        },
        compliance_terms={
            "data_protection_addendum": True,
            "handles_personal_data": True,
            "audit_rights": "limited",
            "regulatory_requirements": ["SOC2", "GDPR"]
        },
        termination_terms={
            "termination_for_convenience": True,
            "notice_period_days": 90,
            "exit_costs_pct": 0.15
        },
        contract_text="This agreement includes standard commercial terms. Automatic price increases apply annually.",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
