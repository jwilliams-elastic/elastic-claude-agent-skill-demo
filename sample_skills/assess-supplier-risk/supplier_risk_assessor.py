"""
Supplier Risk Assessment Module

Implements supplier risk evaluation including
financial, operational, and compliance risk scoring.
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


def load_supplier_risk_factors() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    risk_categories_data = load_csv_as_dict("risk_categories.csv")
    financial_thresholds_data = load_csv_as_dict("financial_thresholds.csv")
    operational_thresholds_data = load_csv_as_dict("operational_thresholds.csv")
    risk_ratings_data = load_csv_as_dict("risk_ratings.csv")
    mitigation_strategies_data = load_csv_as_dict("mitigation_strategies.csv")
    monitoring_frequency_data = load_csv_as_dict("monitoring_frequency.csv")
    params = load_parameters()
    return {
        "risk_categories": risk_categories_data,
        "financial_thresholds": financial_thresholds_data,
        "operational_thresholds": operational_thresholds_data,
        "risk_ratings": risk_ratings_data,
        "mitigation_strategies": mitigation_strategies_data,
        "monitoring_frequency": monitoring_frequency_data,
        **params
    }


def assess_financial_risk(
    financial_data: Dict,
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess supplier financial risk."""
    risk_scores = []
    total_score = 0

    # Credit score assessment
    credit_score = financial_data.get("credit_score", 0)
    credit_thresholds = thresholds.get("credit_score", {})
    if credit_score >= credit_thresholds.get("low_risk", {}).get("min", 80):
        credit_risk = "LOW"
        credit_score_value = 20
    elif credit_score >= credit_thresholds.get("medium_risk", {}).get("min", 60):
        credit_risk = "MEDIUM"
        credit_score_value = 50
    else:
        credit_risk = "HIGH"
        credit_score_value = 80

    risk_scores.append({
        "factor": "credit_score",
        "value": credit_score,
        "risk_level": credit_risk,
        "risk_score": credit_score_value
    })
    total_score += credit_score_value

    # Current ratio assessment
    current_ratio = financial_data.get("current_ratio", 0)
    ratio_thresholds = thresholds.get("current_ratio", {})
    if current_ratio >= ratio_thresholds.get("low_risk", {}).get("min", 1.5):
        ratio_risk = "LOW"
        ratio_score = 20
    elif current_ratio >= ratio_thresholds.get("medium_risk", {}).get("min", 1.0):
        ratio_risk = "MEDIUM"
        ratio_score = 50
    else:
        ratio_risk = "HIGH"
        ratio_score = 80

    risk_scores.append({
        "factor": "current_ratio",
        "value": current_ratio,
        "risk_level": ratio_risk,
        "risk_score": ratio_score
    })
    total_score += ratio_score

    # Debt to equity assessment
    debt_equity = financial_data.get("debt_to_equity", 0)
    de_thresholds = thresholds.get("debt_to_equity", {})
    if debt_equity <= de_thresholds.get("low_risk", {}).get("max", 1.0):
        de_risk = "LOW"
        de_score = 20
    elif debt_equity <= de_thresholds.get("medium_risk", {}).get("max", 2.0):
        de_risk = "MEDIUM"
        de_score = 50
    else:
        de_risk = "HIGH"
        de_score = 80

    risk_scores.append({
        "factor": "debt_to_equity",
        "value": debt_equity,
        "risk_level": de_risk,
        "risk_score": de_score
    })
    total_score += de_score

    # Profit margin assessment
    profit_margin = financial_data.get("profit_margin", 0)
    margin_thresholds = thresholds.get("profit_margin", {})
    if profit_margin >= margin_thresholds.get("low_risk", {}).get("min", 0.10):
        margin_risk = "LOW"
        margin_score = 20
    elif profit_margin >= margin_thresholds.get("medium_risk", {}).get("min", 0.03):
        margin_risk = "MEDIUM"
        margin_score = 50
    else:
        margin_risk = "HIGH"
        margin_score = 80

    risk_scores.append({
        "factor": "profit_margin",
        "value": profit_margin,
        "risk_level": margin_risk,
        "risk_score": margin_score
    })
    total_score += margin_score

    avg_score = total_score / len(risk_scores) if risk_scores else 0

    return {
        "category": "financial_risk",
        "factors": risk_scores,
        "category_score": round(avg_score, 1),
        "high_risk_count": sum(1 for r in risk_scores if r["risk_level"] == "HIGH")
    }


def assess_operational_risk(
    operational_data: Dict,
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess supplier operational risk."""
    risk_scores = []
    total_score = 0

    # On-time delivery
    otd = operational_data.get("on_time_delivery", 0)
    otd_thresholds = thresholds.get("on_time_delivery", {})
    if otd >= otd_thresholds.get("low_risk", {}).get("min", 0.95):
        otd_risk = "LOW"
        otd_score = 20
    elif otd >= otd_thresholds.get("medium_risk", {}).get("min", 0.85):
        otd_risk = "MEDIUM"
        otd_score = 50
    else:
        otd_risk = "HIGH"
        otd_score = 80

    risk_scores.append({
        "factor": "on_time_delivery",
        "value": round(otd * 100, 1),
        "risk_level": otd_risk,
        "risk_score": otd_score
    })
    total_score += otd_score

    # Quality acceptance rate
    quality = operational_data.get("quality_acceptance", 0)
    quality_thresholds = thresholds.get("quality_acceptance", {})
    if quality >= quality_thresholds.get("low_risk", {}).get("min", 0.98):
        quality_risk = "LOW"
        quality_score = 20
    elif quality >= quality_thresholds.get("medium_risk", {}).get("min", 0.95):
        quality_risk = "MEDIUM"
        quality_score = 50
    else:
        quality_risk = "HIGH"
        quality_score = 80

    risk_scores.append({
        "factor": "quality_acceptance",
        "value": round(quality * 100, 1),
        "risk_level": quality_risk,
        "risk_score": quality_score
    })
    total_score += quality_score

    # Capacity headroom
    capacity = operational_data.get("capacity_headroom", 0)
    capacity_thresholds = thresholds.get("capacity_headroom", {})
    if capacity >= capacity_thresholds.get("low_risk", {}).get("min", 0.20):
        capacity_risk = "LOW"
        capacity_score = 20
    elif capacity >= capacity_thresholds.get("medium_risk", {}).get("min", 0.10):
        capacity_risk = "MEDIUM"
        capacity_score = 50
    else:
        capacity_risk = "HIGH"
        capacity_score = 80

    risk_scores.append({
        "factor": "capacity_headroom",
        "value": round(capacity * 100, 1),
        "risk_level": capacity_risk,
        "risk_score": capacity_score
    })
    total_score += capacity_score

    avg_score = total_score / len(risk_scores) if risk_scores else 0

    return {
        "category": "operational_risk",
        "factors": risk_scores,
        "category_score": round(avg_score, 1),
        "high_risk_count": sum(1 for r in risk_scores if r["risk_level"] == "HIGH")
    }


def calculate_overall_risk(
    category_scores: List[Dict],
    category_weights: Dict
) -> Dict[str, Any]:
    """Calculate overall weighted risk score."""
    total_weighted = 0
    total_weight = 0

    for cat_score in category_scores:
        category = cat_score.get("category", "")
        score = cat_score.get("category_score", 0)
        weight = category_weights.get(category, {}).get("weight", 0)

        total_weighted += score * weight
        total_weight += weight

    overall_score = total_weighted / total_weight if total_weight > 0 else 0

    return {
        "overall_risk_score": round(overall_score, 1),
        "total_weight_applied": total_weight,
        "category_contributions": [
            {
                "category": c.get("category"),
                "score": c.get("category_score"),
                "weight": category_weights.get(c.get("category"), {}).get("weight", 0),
                "contribution": round(c.get("category_score", 0) * category_weights.get(c.get("category"), {}).get("weight", 0), 2)
            }
            for c in category_scores
        ]
    }


def rate_risk_level(
    score: float,
    ratings: Dict
) -> Dict[str, Any]:
    """Rate overall risk level."""
    for rating_name, config in sorted(
        ratings.items(),
        key=lambda x: x[1].get("score_range", {}).get("min", 0),
        reverse=True
    ):
        score_range = config.get("score_range", {})
        if score >= score_range.get("min", 0):
            return {
                "risk_rating": rating_name.upper(),
                "score": score,
                "recommended_action": config.get("action", "")
            }

    return {
        "risk_rating": "MINIMAL",
        "score": score,
        "recommended_action": "routine_oversight"
    }


def recommend_mitigation(
    risk_rating: str,
    category_scores: List[Dict],
    mitigation_strategies: Dict
) -> List[Dict]:
    """Recommend risk mitigation strategies."""
    recommendations = []

    # Get high risk categories
    high_risk_categories = [
        c for c in category_scores
        if c.get("category_score", 0) >= 60
    ]

    for strategy_name, config in mitigation_strategies.items():
        applicable_level = config.get("applicable_risk_level", "")

        if (applicable_level == "critical" and risk_rating in ["CRITICAL"]) or \
           (applicable_level == "high" and risk_rating in ["CRITICAL", "HIGH"]) or \
           (applicable_level == "medium" and risk_rating in ["CRITICAL", "HIGH", "MEDIUM"]):

            recommendations.append({
                "strategy": strategy_name.replace("_", " ").title(),
                "risk_reduction_pct": round(config.get("risk_reduction_pct", 0) * 100, 0),
                "implementation_cost": config.get("implementation_cost", "medium"),
                "priority": "HIGH" if risk_rating in ["CRITICAL", "HIGH"] else "MEDIUM"
            })

    # Sort by risk reduction potential
    recommendations.sort(key=lambda x: x["risk_reduction_pct"], reverse=True)

    return recommendations


def determine_monitoring_frequency(
    risk_rating: str,
    monitoring_config: Dict
) -> Dict[str, Any]:
    """Determine appropriate monitoring frequency."""
    if risk_rating in ["CRITICAL", "HIGH"]:
        frequency = monitoring_config.get("critical_suppliers", {})
    elif risk_rating == "MEDIUM":
        frequency = monitoring_config.get("strategic_suppliers", {})
    else:
        frequency = monitoring_config.get("standard_suppliers", {})

    return {
        "risk_rating": risk_rating,
        "financial_review": frequency.get("financial", "annual"),
        "operational_review": frequency.get("operational", "quarterly"),
        "compliance_review": frequency.get("compliance", "annual")
    }


def assess_supplier_risk(
    assessment_id: str,
    supplier_id: str,
    supplier_name: str,
    financial_data: Dict,
    operational_data: Dict,
    compliance_data: Dict,
    geopolitical_data: Dict,
    spend_data: Dict,
    assessment_date: str
) -> Dict[str, Any]:
    """
    Assess supplier risk.

    Business Rules:
    1. Multi-category risk scoring
    2. Weighted risk aggregation
    3. Risk rating determination
    4. Mitigation recommendations

    Args:
        assessment_id: Assessment identifier
        supplier_id: Supplier identifier
        supplier_name: Supplier name
        financial_data: Financial risk indicators
        operational_data: Operational risk indicators
        compliance_data: Compliance risk indicators
        geopolitical_data: Geopolitical risk indicators
        spend_data: Spend and dependency data
        assessment_date: Assessment date

    Returns:
        Supplier risk assessment results
    """
    config = load_supplier_risk_factors()
    risk_categories = config.get("risk_categories", {})
    financial_thresholds = config.get("financial_thresholds", {})
    operational_thresholds = config.get("operational_thresholds", {})
    risk_ratings = config.get("risk_ratings", {})
    mitigation_strategies = config.get("mitigation_strategies", {})
    monitoring_frequency = config.get("monitoring_frequency", {})

    # Assess each risk category
    category_scores = []

    # Financial risk
    financial_assessment = assess_financial_risk(financial_data, financial_thresholds)
    category_scores.append(financial_assessment)

    # Operational risk
    operational_assessment = assess_operational_risk(operational_data, operational_thresholds)
    category_scores.append(operational_assessment)

    # Calculate overall risk
    overall_risk = calculate_overall_risk(category_scores, risk_categories)

    # Rate risk level
    risk_rating = rate_risk_level(overall_risk["overall_risk_score"], risk_ratings)

    # Recommend mitigation strategies
    mitigation_recs = recommend_mitigation(
        risk_rating["risk_rating"],
        category_scores,
        mitigation_strategies
    )

    # Determine monitoring frequency
    monitoring = determine_monitoring_frequency(
        risk_rating["risk_rating"],
        monitoring_frequency
    )

    # Calculate criticality based on spend
    annual_spend = spend_data.get("annual_spend", 0)
    total_category_spend = spend_data.get("total_category_spend", 1)
    spend_concentration = annual_spend / total_category_spend if total_category_spend > 0 else 0

    if spend_concentration >= 0.30:
        criticality = "CRITICAL"
    elif spend_concentration >= 0.15:
        criticality = "STRATEGIC"
    elif spend_concentration >= 0.05:
        criticality = "IMPORTANT"
    else:
        criticality = "STANDARD"

    return {
        "assessment_id": assessment_id,
        "supplier_id": supplier_id,
        "supplier_name": supplier_name,
        "assessment_date": assessment_date,
        "risk_summary": {
            "overall_risk_score": overall_risk["overall_risk_score"],
            "risk_rating": risk_rating["risk_rating"],
            "recommended_action": risk_rating["recommended_action"]
        },
        "category_assessments": category_scores,
        "overall_calculation": overall_risk,
        "supplier_criticality": {
            "criticality_level": criticality,
            "annual_spend": annual_spend,
            "spend_concentration_pct": round(spend_concentration * 100, 1)
        },
        "mitigation_recommendations": mitigation_recs,
        "monitoring_schedule": monitoring,
        "assessment_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = assess_supplier_risk(
        assessment_id="SRISK-2026-001",
        supplier_id="SUP-12345",
        supplier_name="Premier Components Inc",
        financial_data={
            "credit_score": 72,
            "current_ratio": 1.35,
            "debt_to_equity": 1.8,
            "profit_margin": 0.06
        },
        operational_data={
            "on_time_delivery": 0.91,
            "quality_acceptance": 0.97,
            "capacity_headroom": 0.15
        },
        compliance_data={
            "certifications_current": True,
            "audit_findings": 2,
            "regulatory_status": "compliant"
        },
        geopolitical_data={
            "country": "United States",
            "country_risk_score": 15,
            "trade_restrictions": False
        },
        spend_data={
            "annual_spend": 2500000,
            "total_category_spend": 12000000
        },
        assessment_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
