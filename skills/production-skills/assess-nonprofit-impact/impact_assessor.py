"""
Nonprofit Program Impact Assessment Module

Implements outcome measurement and social return on investment
calculations for nonprofit program evaluation.
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


def load_sector_benchmarks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    program_types_data = load_csv_as_dict("program_types.csv")
    sustainability_thresholds_data = load_key_value_csv("sustainability_thresholds.csv")
    impact_score_weights_data = load_key_value_csv("impact_score_weights.csv")
    params = load_parameters()
    return {
        "program_types": program_types_data,
        "sustainability_thresholds": sustainability_thresholds_data,
        "impact_score_weights": impact_score_weights_data,
        **params
    }


def calculate_outcome_achievement(
    outcomes: Dict[str, Any],
    targets: Dict[str, Any],
    weights: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate weighted outcome achievement score."""
    if not outcomes or not targets:
        return {"score": 0, "details": []}

    total_weighted_score = 0
    total_weight = 0
    details = []

    for metric, achieved in outcomes.items():
        target = targets.get(metric)
        weight = weights.get(metric, 1.0)

        if target is not None and target > 0:
            achievement_pct = min(achieved / target, 1.5)  # Cap at 150%
            weighted_contribution = achievement_pct * weight

            total_weighted_score += weighted_contribution
            total_weight += weight

            details.append({
                "metric": metric,
                "achieved": achieved,
                "target": target,
                "achievement_pct": round(achievement_pct * 100, 1),
                "weight": weight
            })

    overall_score = (total_weighted_score / total_weight * 100) if total_weight > 0 else 0

    return {
        "score": round(min(overall_score, 100), 1),
        "details": details
    }


def calculate_cost_effectiveness(
    outcomes: Dict[str, Any],
    total_cost: float,
    beneficiaries: int,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Calculate cost-effectiveness metrics."""
    metrics = {}

    # Cost per beneficiary
    cost_per_beneficiary = total_cost / beneficiaries if beneficiaries > 0 else 0
    metrics["cost_per_beneficiary"] = round(cost_per_beneficiary, 2)

    # Cost per primary outcome
    for outcome_name, value in outcomes.items():
        if isinstance(value, (int, float)) and value > 0:
            cost_per = total_cost / value
            metrics[f"cost_per_{outcome_name}"] = round(cost_per, 2)

            # Compare to benchmark if available
            benchmark_key = f"cost_per_{outcome_name}"
            if benchmark_key in benchmarks:
                variance = (cost_per / benchmarks[benchmark_key] - 1) * 100
                metrics[f"{outcome_name}_vs_benchmark_pct"] = round(variance, 1)

    return metrics


def calculate_sroi(
    outcomes: Dict[str, Any],
    total_cost: float,
    value_proxies: Dict
) -> Dict[str, Any]:
    """Calculate social return on investment."""
    total_value = 0
    value_breakdown = []

    for outcome_name, achieved in outcomes.items():
        proxy = value_proxies.get(outcome_name)

        if proxy and isinstance(achieved, (int, float)):
            if isinstance(proxy, dict):
                value = achieved * proxy.get("value_per_unit", 0)
            else:
                value = achieved * proxy

            total_value += value
            value_breakdown.append({
                "outcome": outcome_name,
                "achieved": achieved,
                "value_created": round(value, 2)
            })

    sroi_ratio = total_value / total_cost if total_cost > 0 else 0

    return {
        "total_social_value": round(total_value, 2),
        "total_investment": total_cost,
        "sroi_ratio": round(sroi_ratio, 2),
        "value_breakdown": value_breakdown
    }


def assess_sustainability(
    funding_sources: Dict[str, float],
    program_duration: int,
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess program financial sustainability."""
    score = 100
    factors = []

    # Funding diversity
    num_sources = len([s for s, pct in funding_sources.items() if pct > 0.05])

    if num_sources >= 4:
        factors.append({"factor": "funding_diversity", "status": "strong", "impact": 0})
    elif num_sources >= 2:
        factors.append({"factor": "funding_diversity", "status": "moderate", "impact": -10})
        score -= 10
    else:
        factors.append({"factor": "funding_diversity", "status": "weak", "impact": -25})
        score -= 25

    # Concentration risk
    max_source = max(funding_sources.values()) if funding_sources else 1
    if max_source > 0.6:
        factors.append({"factor": "concentration_risk", "status": "high", "impact": -20})
        score -= 20
    elif max_source > 0.4:
        factors.append({"factor": "concentration_risk", "status": "moderate", "impact": -10})
        score -= 10

    # Earned revenue component
    earned = funding_sources.get("earned_revenue", 0) + funding_sources.get("fee_for_service", 0)
    if earned >= 0.2:
        factors.append({"factor": "earned_revenue", "status": "strong", "impact": 10})
        score += 10
    elif earned >= 0.1:
        factors.append({"factor": "earned_revenue", "status": "developing", "impact": 0})

    return {
        "score": max(0, min(100, score)),
        "factors": factors,
        "funding_sources_count": num_sources,
        "max_source_concentration": round(max_source * 100, 1)
    }


def assess_impact(
    program_id: str,
    program_type: str,
    outcomes: Dict[str, Any],
    targets: Dict[str, Any],
    total_cost: float,
    beneficiaries: int,
    funding_sources: Dict[str, float],
    program_duration_months: int
) -> Dict[str, Any]:
    """
    Assess nonprofit program impact.

    Business Rules:
    1. Weighted outcome achievement scoring
    2. Cost-effectiveness benchmarking
    3. SROI calculation with value proxies
    4. Sustainability assessment

    Args:
        program_id: Program identifier
        program_type: Type of program
        outcomes: Achieved outcomes
        targets: Target outcomes
        total_cost: Total program cost
        beneficiaries: Number served
        funding_sources: Funding by source
        program_duration_months: Duration

    Returns:
        Impact assessment results
    """
    benchmarks = load_sector_benchmarks()

    program_benchmarks = benchmarks["program_types"].get(
        program_type,
        benchmarks["program_types"]["default"]
    )

    recommendations = []

    # Outcome achievement
    outcome_weights = program_benchmarks.get("outcome_weights", {})
    outcome_assessment = calculate_outcome_achievement(outcomes, targets, outcome_weights)

    # Cost effectiveness
    cost_effectiveness = calculate_cost_effectiveness(
        outcomes,
        total_cost,
        beneficiaries,
        program_benchmarks.get("cost_benchmarks", {})
    )

    # SROI calculation
    value_proxies = program_benchmarks.get("value_proxies", {})
    sroi = calculate_sroi(outcomes, total_cost, value_proxies)

    # Sustainability assessment
    sustainability = assess_sustainability(
        funding_sources,
        program_duration_months,
        benchmarks["sustainability_thresholds"]
    )

    # Calculate overall impact score
    weights = benchmarks["impact_score_weights"]
    impact_score = (
        outcome_assessment["score"] * weights["outcomes"] +
        min(100, sroi["sroi_ratio"] * 25) * weights["sroi"] +
        sustainability["score"] * weights["sustainability"] +
        min(100, (beneficiaries / program_benchmarks.get("scale_benchmark", 100)) * 100) * weights["scale"]
    )

    # Generate recommendations
    if outcome_assessment["score"] < 80:
        recommendations.append("Review program design to improve outcome achievement")

    for detail in outcome_assessment["details"]:
        if detail["achievement_pct"] < 70:
            recommendations.append(f"Focus on improving {detail['metric']} performance")

    if sustainability["score"] < 60:
        recommendations.append("Diversify funding sources to improve sustainability")

    if sroi["sroi_ratio"] < 2:
        recommendations.append("Explore opportunities to increase social value creation")

    return {
        "program_id": program_id,
        "program_type": program_type,
        "impact_score": round(min(100, impact_score), 1),
        "outcome_achievement": outcome_assessment,
        "cost_effectiveness": cost_effectiveness,
        "sroi_ratio": sroi["sroi_ratio"],
        "sroi_details": sroi,
        "sustainability_score": sustainability["score"],
        "sustainability_assessment": sustainability,
        "beneficiaries": beneficiaries,
        "cost_per_beneficiary": round(total_cost / beneficiaries, 2) if beneficiaries > 0 else 0,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    import json
    result = assess_impact(
        program_id="PROG-2024-001",
        program_type="workforce_development",
        outcomes={"job_placements": 85, "certifications_earned": 120, "wage_increase_pct": 0.25},
        targets={"job_placements": 100, "certifications_earned": 100, "wage_increase_pct": 0.20},
        total_cost=500000,
        beneficiaries=150,
        funding_sources={"government": 0.4, "foundation": 0.35, "corporate": 0.15, "individual": 0.1},
        program_duration_months=12
    )
    print(json.dumps(result, indent=2))
