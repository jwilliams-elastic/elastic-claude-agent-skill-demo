"""
Grant Application Evaluation Module

Implements grant application evaluation using eligibility
screening, scoring criteria, and impact assessment.
"""

import csv
import ast
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
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
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
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
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


def load_grant_criteria() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    scoring_rubric_data = load_key_value_csv("scoring_rubric.csv")
    budget_rules_data = load_key_value_csv("budget_rules.csv")
    capacity_criteria_data = load_key_value_csv("capacity_criteria.csv")
    focus_area_weights_data = load_key_value_csv("focus_area_weights.csv")
    geographic_priorities_data = load_key_value_csv("geographic_priorities.csv")
    matching_requirements_data = load_key_value_csv("matching_requirements.csv")
    params = load_parameters()
    return {
        "scoring_rubric": scoring_rubric_data,
        "budget_rules": budget_rules_data,
        "capacity_criteria": capacity_criteria_data,
        "focus_area_weights": focus_area_weights_data,
        "geographic_priorities": geographic_priorities_data,
        "matching_requirements": matching_requirements_data,
        **params
    }


def verify_eligibility(
    applicant_info: Dict,
    project_proposal: Dict,
    program_priorities: Dict,
    eligibility_rules: Dict
) -> Dict[str, Any]:
    """Verify organization and project eligibility."""
    issues = []
    passed_checks = []

    # Organization type check
    org_type = applicant_info.get("org_type", "")
    eligible_types = eligibility_rules.get("eligible_org_types", ["501c3"])

    if org_type in eligible_types:
        passed_checks.append("Organization type eligible")
    else:
        issues.append(f"Organization type '{org_type}' not eligible")

    # Operating history
    years_operating = applicant_info.get("years_operating", 0)
    min_years = eligibility_rules.get("min_years_operating", 2)

    if years_operating >= min_years:
        passed_checks.append(f"Operating history ({years_operating} years) meets minimum")
    else:
        issues.append(f"Insufficient operating history ({years_operating} vs {min_years} required)")

    # Focus area alignment
    focus_area = project_proposal.get("focus_area", "")
    allowed_areas = program_priorities.get("focus_areas", [])

    if focus_area in allowed_areas:
        passed_checks.append(f"Focus area '{focus_area}' aligned with program")
    else:
        issues.append(f"Focus area '{focus_area}' not in program priorities")

    eligible = len(issues) == 0

    return {
        "eligible": eligible,
        "passed_checks": passed_checks,
        "eligibility_issues": issues
    }


def score_program_alignment(
    project_proposal: Dict,
    impact_metrics: Dict,
    program_priorities: Dict,
    scoring_rubric: Dict
) -> Dict[str, Any]:
    """Score project alignment with program priorities."""
    scores = {}

    focus_area = project_proposal.get("focus_area", "")
    primary_focus_areas = program_priorities.get("focus_areas", [])[:2]  # Top priorities

    # Focus area alignment (25 points max)
    if focus_area in primary_focus_areas:
        scores["focus_alignment"] = 25
    elif focus_area in program_priorities.get("focus_areas", []):
        scores["focus_alignment"] = 15
    else:
        scores["focus_alignment"] = 5

    # Target population alignment (20 points max)
    beneficiaries = project_proposal.get("beneficiaries", 0)
    min_beneficiaries = scoring_rubric.get("min_beneficiaries", 100)

    if beneficiaries >= min_beneficiaries * 10:
        scores["reach"] = 20
    elif beneficiaries >= min_beneficiaries * 3:
        scores["reach"] = 15
    elif beneficiaries >= min_beneficiaries:
        scores["reach"] = 10
    else:
        scores["reach"] = 5

    # Outcome measurement (15 points max)
    primary_outcome = impact_metrics.get("primary_outcome", "")
    measurement_plan = impact_metrics.get("measurement_plan", False)

    if primary_outcome and measurement_plan:
        scores["measurement"] = 15
    elif primary_outcome:
        scores["measurement"] = 10
    else:
        scores["measurement"] = 5

    total_alignment = sum(scores.values())
    max_possible = 60

    return {
        "alignment_score": total_alignment,
        "max_possible": max_possible,
        "score_breakdown": scores,
        "percentage": round(total_alignment / max_possible * 100, 1)
    }


def assess_budget_reasonableness(
    budget_request: Dict,
    project_proposal: Dict,
    program_priorities: Dict,
    budget_rules: Dict
) -> Dict[str, Any]:
    """Assess budget request reasonableness."""
    findings = []
    amount_requested = budget_request.get("amount", 0)
    max_award = program_priorities.get("max_award", 500000)

    # Amount check
    if amount_requested > max_award:
        findings.append({
            "issue": "exceeds_max",
            "description": f"Request ${amount_requested:,} exceeds max ${max_award:,}",
            "severity": "error"
        })

    # Category breakdown
    categories = budget_request.get("categories", {})
    total_categories = sum(categories.values())

    if total_categories != amount_requested:
        findings.append({
            "issue": "budget_mismatch",
            "description": "Category totals don't match request amount",
            "severity": "error"
        })

    # Overhead check
    overhead_limit = budget_rules.get("max_overhead_pct", 0.15)
    overhead = categories.get("overhead", 0) + categories.get("admin", 0)
    overhead_pct = overhead / amount_requested if amount_requested > 0 else 0

    if overhead_pct > overhead_limit:
        findings.append({
            "issue": "high_overhead",
            "description": f"Overhead {overhead_pct:.1%} exceeds {overhead_limit:.1%} limit",
            "severity": "warning"
        })

    # Personnel ratio check
    personnel = categories.get("personnel", 0)
    personnel_pct = personnel / amount_requested if amount_requested > 0 else 0
    max_personnel = budget_rules.get("max_personnel_pct", 0.70)

    if personnel_pct > max_personnel:
        findings.append({
            "issue": "high_personnel",
            "description": f"Personnel {personnel_pct:.1%} exceeds {max_personnel:.1%}",
            "severity": "warning"
        })

    # Cost per beneficiary
    beneficiaries = project_proposal.get("beneficiaries", 1)
    cost_per_beneficiary = amount_requested / beneficiaries

    reasonable = len([f for f in findings if f["severity"] == "error"]) == 0
    score = 20 if reasonable and len(findings) == 0 else 15 if reasonable else 5

    return {
        "reasonable": reasonable,
        "budget_score": score,
        "amount_requested": amount_requested,
        "cost_per_beneficiary": round(cost_per_beneficiary, 2),
        "findings": findings,
        "category_breakdown": categories
    }


def evaluate_organizational_capacity(
    applicant_info: Dict,
    capacity_criteria: Dict
) -> Dict[str, Any]:
    """Evaluate organizational capacity to execute."""
    score = 0
    findings = []

    annual_budget = applicant_info.get("annual_budget", 0)
    years_operating = applicant_info.get("years_operating", 0)
    staff_size = applicant_info.get("staff_size", 0)

    # Financial capacity
    budget_threshold = capacity_criteria.get("min_annual_budget", 500000)
    if annual_budget >= budget_threshold * 2:
        score += 10
        findings.append("Strong financial capacity")
    elif annual_budget >= budget_threshold:
        score += 7
        findings.append("Adequate financial capacity")
    else:
        score += 3
        findings.append("Limited financial capacity - may need additional support")

    # Organizational maturity
    if years_operating >= 10:
        score += 5
        findings.append("Established organization")
    elif years_operating >= 5:
        score += 4
    else:
        score += 2

    return {
        "capacity_score": score,
        "max_score": 15,
        "findings": findings
    }


def evaluate_grant(
    application_id: str,
    applicant_info: Dict,
    project_proposal: Dict,
    budget_request: Dict,
    impact_metrics: Dict,
    program_priorities: Dict
) -> Dict[str, Any]:
    """
    Evaluate grant application.

    Business Rules:
    1. Eligibility verification
    2. Program alignment scoring
    3. Budget reasonableness assessment
    4. Impact potential evaluation

    Args:
        application_id: Application ID
        applicant_info: Organization details
        project_proposal: Project description
        budget_request: Funding request
        impact_metrics: Proposed outcomes
        program_priorities: Program criteria

    Returns:
        Grant evaluation results
    """
    criteria = load_grant_criteria()

    # Eligibility check
    eligibility_result = verify_eligibility(
        applicant_info,
        project_proposal,
        program_priorities,
        criteria.get("eligibility_rules", {})
    )

    if not eligibility_result["eligible"]:
        return {
            "application_id": application_id,
            "eligibility_status": "INELIGIBLE",
            "eligibility_check": eligibility_result,
            "total_score": 0,
            "scoring_breakdown": {},
            "budget_assessment": {},
            "recommendation": "DECLINE - Eligibility requirements not met"
        }

    # Program alignment scoring
    alignment_result = score_program_alignment(
        project_proposal,
        impact_metrics,
        program_priorities,
        criteria.get("scoring_rubric", {})
    )

    # Budget assessment
    budget_assessment = assess_budget_reasonableness(
        budget_request,
        project_proposal,
        program_priorities,
        criteria.get("budget_rules", {})
    )

    # Capacity evaluation
    capacity_result = evaluate_organizational_capacity(
        applicant_info,
        criteria.get("capacity_criteria", {})
    )

    # Calculate total score
    total_score = (
        alignment_result["alignment_score"] +
        budget_assessment["budget_score"] +
        capacity_result["capacity_score"]
    )
    max_score = 95

    # Determine recommendation
    score_threshold = criteria.get("funding_threshold", 65)
    score_pct = total_score / max_score * 100

    if score_pct >= score_threshold and budget_assessment["reasonable"]:
        recommendation = "FUND"
    elif score_pct >= score_threshold * 0.85:
        recommendation = "FUND_WITH_CONDITIONS"
    else:
        recommendation = "DECLINE"

    return {
        "application_id": application_id,
        "eligibility_status": "ELIGIBLE",
        "total_score": total_score,
        "max_score": max_score,
        "score_percentage": round(score_pct, 1),
        "scoring_breakdown": {
            "alignment": alignment_result,
            "budget": budget_assessment,
            "capacity": capacity_result
        },
        "eligibility_check": eligibility_result,
        "budget_assessment": budget_assessment,
        "recommendation": recommendation
    }


if __name__ == "__main__":
    import json
    result = evaluate_grant(
        application_id="GRT-2026-001",
        applicant_info={
            "org_type": "501c3",
            "years_operating": 10,
            "annual_budget": 2000000,
            "staff_size": 25
        },
        project_proposal={
            "focus_area": "education",
            "duration_months": 24,
            "beneficiaries": 5000
        },
        budget_request={
            "amount": 250000,
            "categories": {"personnel": 150000, "program": 80000, "overhead": 20000}
        },
        impact_metrics={
            "primary_outcome": "graduation_rate",
            "target_improvement": 0.15,
            "measurement_plan": True
        },
        program_priorities={
            "focus_areas": ["education", "workforce"],
            "max_award": 500000
        }
    )
    print(json.dumps(result, indent=2))
