"""
Construction Bid Assessment Module

Implements bid evaluation using cost benchmarks,
contractor qualification, and schedule feasibility analysis.
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


def load_construction_benchmarks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    cost_per_sqft_data = load_csv_as_dict("cost_per_sqft.csv")
    location_factors_data = load_key_value_csv("location_factors.csv")
    contractor_requirements_data = load_key_value_csv("contractor_requirements.csv")
    complexity_factors_data = load_csv_as_dict("complexity_factors.csv")
    evaluation_weights_data = load_key_value_csv("evaluation_weights.csv")
    params = load_parameters()
    return {
        "cost_per_sqft": cost_per_sqft_data,
        "location_factors": location_factors_data,
        "contractor_requirements": contractor_requirements_data,
        "complexity_factors": complexity_factors_data,
        "evaluation_weights": evaluation_weights_data,
        **params
    }


def analyze_cost_reasonableness(
    bid_amounts: Dict,
    project_details: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Analyze bid cost against regional benchmarks."""
    findings = []
    project_type = project_details.get("type", "commercial")
    sqft = project_details.get("sqft", 1)
    location = project_details.get("location", "US")

    # Get benchmark cost per sqft
    type_benchmarks = benchmarks.get("cost_per_sqft", {}).get(project_type, {})
    base_cost = type_benchmarks.get("base", 200)
    location_factor = benchmarks.get("location_factors", {}).get(location, 1.0)

    expected_cost_sqft = base_cost * location_factor

    # Calculate total bid
    total_bid = sum(bid_amounts.values())
    actual_cost_sqft = total_bid / sqft if sqft > 0 else 0

    variance = (actual_cost_sqft - expected_cost_sqft) / expected_cost_sqft if expected_cost_sqft > 0 else 0

    if variance > 0.20:
        findings.append({
            "type": "high_cost",
            "description": f"Bid {variance:.1%} above benchmark",
            "severity": "high"
        })
    elif variance < -0.15:
        findings.append({
            "type": "low_cost",
            "description": f"Bid {abs(variance):.1%} below benchmark - verify scope",
            "severity": "medium"
        })

    # Check category breakdown
    labor_pct = bid_amounts.get("labor", 0) / total_bid if total_bid > 0 else 0
    expected_labor_pct = type_benchmarks.get("labor_pct", 0.45)

    if abs(labor_pct - expected_labor_pct) > 0.10:
        findings.append({
            "type": "labor_variance",
            "description": f"Labor {labor_pct:.1%} vs expected {expected_labor_pct:.1%}",
            "severity": "low"
        })

    score = 100
    for finding in findings:
        if finding["severity"] == "high":
            score -= 25
        elif finding["severity"] == "medium":
            score -= 15
        else:
            score -= 5

    return {
        "score": max(0, score),
        "total_bid": total_bid,
        "cost_per_sqft": round(actual_cost_sqft, 2),
        "benchmark_cost_sqft": round(expected_cost_sqft, 2),
        "variance_pct": round(variance * 100, 1),
        "findings": findings
    }


def evaluate_contractor_qualifications(
    contractor_info: Dict,
    project_details: Dict,
    requirements: Dict
) -> Dict[str, Any]:
    """Evaluate contractor qualifications."""
    issues = []
    project_value = project_details.get("estimated_value", 0)

    # License check
    if contractor_info.get("license") != "valid":
        issues.append("Contractor license not valid")

    # Bonding capacity
    bonding_capacity = contractor_info.get("bonding_capacity", 0)
    if bonding_capacity < project_value:
        issues.append(f"Bonding capacity ${bonding_capacity:,.0f} below project value")

    # Experience check
    similar_projects = contractor_info.get("similar_projects", 0)
    min_experience = requirements.get("min_similar_projects", 3)
    if similar_projects < min_experience:
        issues.append(f"Only {similar_projects} similar projects vs {min_experience} required")

    # Safety record
    emr = contractor_info.get("experience_mod_rate", 1.0)
    if emr > 1.2:
        issues.append(f"High EMR ({emr}) indicates safety concerns")

    qualified = len(issues) == 0
    score = 100 - (len(issues) * 20)

    return {
        "qualified": qualified,
        "score": max(0, score),
        "issues": issues,
        "bonding_adequate": bonding_capacity >= project_value
    }


def assess_schedule_feasibility(
    schedule: Dict,
    project_details: Dict,
    complexity_factors: Dict
) -> Dict[str, Any]:
    """Assess proposed schedule feasibility."""
    issues = []

    proposed_months = schedule.get("duration_months", 12)
    sqft = project_details.get("sqft", 1)
    project_type = project_details.get("type", "commercial")

    # Calculate expected duration
    base_months_per_10k_sqft = complexity_factors.get("base_months_per_10k_sqft", {}).get(project_type, 3)
    expected_months = (sqft / 10000) * base_months_per_10k_sqft

    # Apply minimum
    expected_months = max(expected_months, complexity_factors.get("minimum_months", 6))

    variance = (proposed_months - expected_months) / expected_months if expected_months > 0 else 0

    if variance < -0.20:
        issues.append({
            "type": "aggressive_schedule",
            "description": f"Schedule {abs(variance):.1%} shorter than typical",
            "risk": "high"
        })
    elif variance > 0.30:
        issues.append({
            "type": "extended_schedule",
            "description": f"Schedule {variance:.1%} longer than typical",
            "risk": "low"
        })

    feasible = len([i for i in issues if i.get("risk") == "high"]) == 0
    score = 100 if feasible else 70

    return {
        "feasible": feasible,
        "score": score,
        "proposed_months": proposed_months,
        "expected_months": round(expected_months, 1),
        "issues": issues
    }


def verify_bid_completeness(
    bid_amounts: Dict,
    subcontractors: List[Dict],
    requirements: Dict
) -> Dict[str, Any]:
    """Verify bid contains all required components."""
    missing = []

    required_categories = requirements.get("required_cost_categories", [])
    for category in required_categories:
        if category not in bid_amounts or bid_amounts[category] == 0:
            missing.append(f"Missing or zero: {category}")

    required_trades = requirements.get("required_trades", [])
    provided_trades = [s.get("trade") for s in subcontractors]
    for trade in required_trades:
        if trade not in provided_trades:
            missing.append(f"Missing subcontractor for: {trade}")

    complete = len(missing) == 0

    return {
        "complete": complete,
        "missing_items": missing,
        "categories_provided": list(bid_amounts.keys()),
        "trades_provided": provided_trades
    }


def assess_bid(
    bid_id: str,
    project_details: Dict,
    bid_amounts: Dict,
    contractor_info: Dict,
    schedule: Dict,
    subcontractors: List[Dict]
) -> Dict[str, Any]:
    """
    Assess construction project bid.

    Business Rules:
    1. Cost benchmark comparison
    2. Contractor qualification verification
    3. Schedule feasibility analysis
    4. Bid completeness check

    Args:
        bid_id: Bid identifier
        project_details: Project specifications
        bid_amounts: Cost breakdown
        contractor_info: Contractor qualifications
        schedule: Proposed timeline
        subcontractors: Subcontractor details

    Returns:
        Bid assessment results
    """
    benchmarks = load_construction_benchmarks()

    # Cost analysis
    cost_analysis = analyze_cost_reasonableness(
        bid_amounts,
        project_details,
        benchmarks
    )

    # Contractor qualifications
    qualification_status = evaluate_contractor_qualifications(
        contractor_info,
        project_details,
        benchmarks.get("contractor_requirements", {})
    )

    # Schedule assessment
    schedule_assessment = assess_schedule_feasibility(
        schedule,
        project_details,
        benchmarks.get("complexity_factors", {})
    )

    # Completeness check
    completeness = verify_bid_completeness(
        bid_amounts,
        subcontractors,
        benchmarks.get("bid_requirements", {})
    )

    # Calculate overall score
    weights = benchmarks.get("evaluation_weights", {})
    bid_score = (
        cost_analysis["score"] * weights.get("cost", 0.35) +
        qualification_status["score"] * weights.get("qualification", 0.30) +
        schedule_assessment["score"] * weights.get("schedule", 0.20) +
        (100 if completeness["complete"] else 60) * weights.get("completeness", 0.15)
    )

    # Determine recommendation
    if bid_score >= 85 and qualification_status["qualified"]:
        recommendation = "AWARD_RECOMMENDED"
    elif bid_score >= 70 and qualification_status["qualified"]:
        recommendation = "ACCEPTABLE"
    elif bid_score >= 60:
        recommendation = "CONDITIONAL"
    else:
        recommendation = "NOT_RECOMMENDED"

    return {
        "bid_id": bid_id,
        "bid_score": round(bid_score, 1),
        "cost_analysis": cost_analysis,
        "qualification_status": qualification_status,
        "schedule_assessment": schedule_assessment,
        "completeness": completeness,
        "recommendation": recommendation
    }


if __name__ == "__main__":
    import json
    result = assess_bid(
        bid_id="BID-2026-001",
        project_details={"type": "commercial", "sqft": 50000, "location": "NY", "estimated_value": 4000000},
        bid_amounts={"labor": 2000000, "materials": 1500000, "equipment": 500000},
        contractor_info={
            "license": "valid",
            "bonding_capacity": 10000000,
            "similar_projects": 5,
            "experience_mod_rate": 0.95
        },
        schedule={"duration_months": 18, "start_date": "2026-06-01"},
        subcontractors=[
            {"trade": "electrical", "qualified": True},
            {"trade": "plumbing", "qualified": True},
            {"trade": "hvac", "qualified": True}
        ]
    )
    print(json.dumps(result, indent=2))
