"""
Defense Contract Evaluation Module

Implements contract proposal evaluation using FAR/DFARS
compliance checks and cost reasonableness analysis.
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


def load_evaluation_criteria() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    cost_benchmarks_data = load_key_value_csv("cost_benchmarks.csv")
    capability_matrix_data = load_csv_as_dict("capability_matrix.csv")
    clearance_hierarchy_data = load_key_value_csv("clearance_hierarchy.csv")
    evaluation_weights_data = load_key_value_csv("evaluation_weights.csv")
    past_performance_thresholds_data = load_key_value_csv("past_performance_thresholds.csv")
    contract_types_data = load_csv_as_dict("contract_types.csv")
    params = load_parameters()
    return {
        "cost_benchmarks": cost_benchmarks_data,
        "capability_matrix": capability_matrix_data,
        "clearance_hierarchy": clearance_hierarchy_data,
        "evaluation_weights": evaluation_weights_data,
        "past_performance_thresholds": past_performance_thresholds_data,
        "contract_types": contract_types_data,
        **params
    }


def check_far_compliance(
    proposal_details: Dict,
    contractor_info: Dict,
    requirements: Dict
) -> Dict[str, Any]:
    """Check compliance with FAR requirements."""
    issues = []
    compliant_items = []

    # Check required certifications
    required_certs = requirements.get("required_certifications", [])
    contractor_certs = contractor_info.get("certifications", [])

    for cert in required_certs:
        if cert in contractor_certs:
            compliant_items.append(f"Certification {cert} verified")
        else:
            issues.append(f"Missing required certification: {cert}")

    # Check proposal completeness
    required_elements = ["type", "value", "period_months"]
    for element in required_elements:
        if element not in proposal_details:
            issues.append(f"Missing proposal element: {element}")

    # Check small business compliance if applicable
    if contractor_info.get("size") == "small_business":
        if proposal_details.get("value", 0) > 7500000:
            issues.append("Value exceeds small business threshold without justification")

    compliance_score = 100 - (len(issues) * 15)

    return {
        "compliant": len(issues) == 0,
        "score": max(0, compliance_score),
        "issues": issues,
        "verified_items": compliant_items
    }


def analyze_cost_reasonableness(
    cost_elements: List[Dict],
    proposal_details: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Analyze cost reasonableness against benchmarks."""
    findings = []
    total_proposed = sum(e.get("amount", 0) for e in cost_elements)

    labor_costs = sum(e.get("amount", 0) for e in cost_elements
                      if e.get("category") == "labor")
    material_costs = sum(e.get("amount", 0) for e in cost_elements
                         if e.get("category") == "materials")
    overhead_costs = sum(e.get("amount", 0) for e in cost_elements
                         if e.get("category") == "overhead")

    # Check labor rate reasonableness
    labor_benchmark = benchmarks.get("labor_rate_per_month", 15000)
    period = proposal_details.get("period_months", 12)
    expected_labor = labor_benchmark * period

    if labor_costs > expected_labor * 1.2:
        findings.append({
            "category": "labor",
            "finding": "Labor costs exceed benchmark by >20%",
            "severity": "high"
        })

    # Check overhead rate
    if total_proposed > 0:
        overhead_rate = overhead_costs / total_proposed
        max_overhead = benchmarks.get("max_overhead_rate", 0.35)
        if overhead_rate > max_overhead:
            findings.append({
                "category": "overhead",
                "finding": f"Overhead rate {overhead_rate:.1%} exceeds maximum {max_overhead:.1%}",
                "severity": "medium"
            })

    # Calculate reasonableness score
    score = 100
    for finding in findings:
        if finding["severity"] == "high":
            score -= 25
        elif finding["severity"] == "medium":
            score -= 15
        else:
            score -= 5

    return {
        "reasonable": score >= 70,
        "score": max(0, score),
        "total_proposed": total_proposed,
        "findings": findings,
        "cost_breakdown": {
            "labor": labor_costs,
            "materials": material_costs,
            "overhead": overhead_costs
        }
    }


def assess_technical_capability(
    contractor_info: Dict,
    technical_requirements: List[Dict],
    capability_matrix: Dict
) -> Dict[str, Any]:
    """Assess contractor technical capabilities."""
    assessments = []
    met_requirements = 0

    contractor_capabilities = contractor_info.get("capabilities", [])
    past_performance = contractor_info.get("past_performance_rating", 0)

    for req in technical_requirements:
        category = req.get("category", "general")
        req_id = req.get("id", "unknown")

        # Check if contractor has relevant capability
        required_cap = capability_matrix.get(category, {}).get("required_capability", category)
        has_capability = required_cap in contractor_capabilities

        assessment = {
            "requirement_id": req_id,
            "category": category,
            "capable": has_capability,
            "confidence": "high" if has_capability else "low"
        }
        assessments.append(assessment)

        if has_capability:
            met_requirements += 1

    # Calculate technical score
    if technical_requirements:
        capability_score = (met_requirements / len(technical_requirements)) * 70
    else:
        capability_score = 70

    # Factor in past performance
    performance_score = past_performance * 3  # 0-30 points

    total_score = capability_score + performance_score

    return {
        "qualified": total_score >= 70,
        "score": round(total_score, 1),
        "requirements_met": met_requirements,
        "total_requirements": len(technical_requirements),
        "assessments": assessments,
        "past_performance_factor": past_performance
    }


def verify_security_clearances(
    contractor_info: Dict,
    security_requirements: Dict,
    clearance_hierarchy: Dict
) -> Dict[str, Any]:
    """Verify security clearance requirements."""
    issues = []

    required_level = security_requirements.get("clearance_level", "UNCLASSIFIED")
    contractor_level = contractor_info.get("facility_clearance", "UNCLASSIFIED")

    # Get clearance rankings
    required_rank = clearance_hierarchy.get(required_level, 0)
    contractor_rank = clearance_hierarchy.get(contractor_level, 0)

    clearance_met = contractor_rank >= required_rank

    if not clearance_met:
        issues.append(f"Contractor clearance ({contractor_level}) insufficient for requirement ({required_level})")

    # Check specific program requirements
    if security_requirements.get("sap_required", False):
        if not contractor_info.get("sap_eligible", False):
            issues.append("SAP eligibility required but not verified")

    return {
        "verified": len(issues) == 0,
        "required_clearance": required_level,
        "contractor_clearance": contractor_level,
        "issues": issues
    }


def evaluate_contract(
    contract_id: str,
    proposal_details: Dict,
    contractor_info: Dict,
    cost_elements: List[Dict],
    technical_requirements: List[Dict],
    security_requirements: Dict
) -> Dict[str, Any]:
    """
    Evaluate defense contract proposal.

    Business Rules:
    1. FAR/DFARS compliance verification
    2. Cost reasonableness against benchmarks
    3. Technical capability assessment
    4. Security clearance verification

    Args:
        contract_id: Contract identifier
        proposal_details: Proposal information
        contractor_info: Contractor details
        cost_elements: Cost breakdown
        technical_requirements: Technical specs
        security_requirements: Security needs

    Returns:
        Contract evaluation results
    """
    criteria = load_evaluation_criteria()

    risk_factors = []

    # FAR compliance check
    compliance_status = check_far_compliance(
        proposal_details,
        contractor_info,
        criteria.get("far_requirements", {})
    )

    if not compliance_status["compliant"]:
        risk_factors.append({
            "category": "compliance",
            "description": "FAR compliance issues identified",
            "severity": "high"
        })

    # Cost reasonableness analysis
    cost_analysis = analyze_cost_reasonableness(
        cost_elements,
        proposal_details,
        criteria.get("cost_benchmarks", {})
    )

    if not cost_analysis["reasonable"]:
        risk_factors.append({
            "category": "cost",
            "description": "Cost reasonableness concerns",
            "severity": "medium"
        })

    # Technical assessment
    technical_assessment = assess_technical_capability(
        contractor_info,
        technical_requirements,
        criteria.get("capability_matrix", {})
    )

    if not technical_assessment["qualified"]:
        risk_factors.append({
            "category": "technical",
            "description": "Technical capability gaps identified",
            "severity": "high"
        })

    # Security verification
    security_status = verify_security_clearances(
        contractor_info,
        security_requirements,
        criteria.get("clearance_hierarchy", {})
    )

    if not security_status["verified"]:
        risk_factors.append({
            "category": "security",
            "description": "Security clearance deficiencies",
            "severity": "critical"
        })

    # Calculate overall evaluation score
    weights = criteria.get("evaluation_weights", {})
    evaluation_score = (
        compliance_status["score"] * weights.get("compliance", 0.25) +
        cost_analysis["score"] * weights.get("cost", 0.30) +
        technical_assessment["score"] * weights.get("technical", 0.35) +
        (100 if security_status["verified"] else 0) * weights.get("security", 0.10)
    )

    # Determine recommendation
    if evaluation_score >= 85 and security_status["verified"]:
        recommendation = "AWARD_RECOMMENDED"
    elif evaluation_score >= 70 and security_status["verified"]:
        recommendation = "CONDITIONAL_AWARD"
    elif evaluation_score >= 60:
        recommendation = "REQUIRES_NEGOTIATION"
    else:
        recommendation = "NOT_RECOMMENDED"

    return {
        "contract_id": contract_id,
        "evaluation_score": round(evaluation_score, 1),
        "compliance_status": compliance_status,
        "cost_analysis": cost_analysis,
        "technical_assessment": technical_assessment,
        "security_verification": security_status,
        "risk_factors": risk_factors,
        "recommendation": recommendation
    }


if __name__ == "__main__":
    import json
    result = evaluate_contract(
        contract_id="W911NF-26-C-0001",
        proposal_details={"type": "FFP", "value": 5000000, "period_months": 24},
        contractor_info={
            "cage_code": "1ABC2",
            "size": "small_business",
            "certifications": ["ISO9001", "CMMI_L3"],
            "capabilities": ["software", "systems_engineering"],
            "past_performance_rating": 8,
            "facility_clearance": "SECRET"
        },
        cost_elements=[
            {"category": "labor", "amount": 3000000},
            {"category": "materials", "amount": 1000000},
            {"category": "overhead", "amount": 1000000}
        ],
        technical_requirements=[
            {"id": "TR-001", "category": "software"},
            {"id": "TR-002", "category": "systems_engineering"}
        ],
        security_requirements={"clearance_level": "SECRET", "sap_required": False}
    )
    print(json.dumps(result, indent=2))
