"""
Talent Retention Assessment Module

Implements talent retention risk assessment including
flight risk scoring, engagement analysis, and intervention recommendations.
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


def load_retention_factors() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    retention_risk_factors_data = load_csv_as_dict("retention_risk_factors.csv")
    engagement_indicators_data = load_csv_as_dict("engagement_indicators.csv")
    turnover_benchmarks_data = load_csv_as_dict("turnover_benchmarks.csv")
    replacement_cost_multipliers_data = load_key_value_csv("replacement_cost_multipliers.csv")
    intervention_strategies_data = load_csv_as_dict("intervention_strategies.csv")
    flight_risk_thresholds_data = load_csv_as_dict("flight_risk_thresholds.csv")
    tenure_risk_curve_data = load_key_value_csv("tenure_risk_curve.csv")
    params = load_parameters()
    return {
        "retention_risk_factors": retention_risk_factors_data,
        "engagement_indicators": engagement_indicators_data,
        "turnover_benchmarks": turnover_benchmarks_data,
        "replacement_cost_multipliers": replacement_cost_multipliers_data,
        "intervention_strategies": intervention_strategies_data,
        "flight_risk_thresholds": flight_risk_thresholds_data,
        "tenure_risk_curve": tenure_risk_curve_data,
        **params
    }


def calculate_compensation_risk(
    current_salary: float,
    market_salary: float,
    factor_config: Dict
) -> Dict[str, Any]:
    """Calculate compensation-based retention risk."""
    if market_salary <= 0:
        return {"error": "Invalid market salary"}

    comp_ratio = current_salary / market_salary
    below_market = comp_ratio - 1

    threshold = factor_config.get("threshold_below_market", -0.10)

    if below_market < threshold:
        risk_score = min(100, abs(below_market) * 500)  # Scale to 100
    elif below_market < 0:
        risk_score = abs(below_market) * 200
    else:
        risk_score = 0

    return {
        "current_salary": current_salary,
        "market_salary": market_salary,
        "comp_ratio": round(comp_ratio, 2),
        "below_market_pct": round(below_market * 100, 1),
        "risk_score": round(min(risk_score, 100), 1)
    }


def calculate_career_growth_risk(
    years_since_promotion: int,
    has_development_plan: bool,
    factor_config: Dict
) -> Dict[str, Any]:
    """Calculate career growth retention risk."""
    threshold = factor_config.get("no_promotion_years", 3)

    risk_score = 0
    if years_since_promotion >= threshold:
        risk_score = min(100, (years_since_promotion - threshold + 1) * 25)

    if not has_development_plan:
        risk_score += 20

    return {
        "years_since_promotion": years_since_promotion,
        "has_development_plan": has_development_plan,
        "promotion_threshold_years": threshold,
        "risk_score": round(min(risk_score, 100), 1)
    }


def calculate_engagement_risk(
    engagement_data: Dict,
    indicators: Dict
) -> Dict[str, Any]:
    """Calculate engagement-based retention risk."""
    total_score = 0
    indicator_results = []

    for indicator, config in indicators.items():
        actual_value = engagement_data.get(indicator, config.get("benchmark", 0))
        benchmark = config.get("benchmark", 0)
        weight = config.get("weight", 0.25)

        if benchmark > 0:
            performance_ratio = actual_value / benchmark
        else:
            performance_ratio = 1

        # Lower performance = higher risk
        if performance_ratio < 1:
            indicator_risk = (1 - performance_ratio) * 100
        else:
            indicator_risk = 0

        weighted_risk = indicator_risk * weight
        total_score += weighted_risk

        indicator_results.append({
            "indicator": indicator,
            "actual": actual_value,
            "benchmark": benchmark,
            "risk_contribution": round(weighted_risk, 1)
        })

    return {
        "engagement_risk_score": round(total_score, 1),
        "indicator_analysis": indicator_results
    }


def calculate_tenure_risk(
    tenure_years: float,
    tenure_curve: Dict
) -> Dict[str, Any]:
    """Calculate tenure-based retention risk."""
    risk_rate = 0.10  # Default

    if tenure_years < 1:
        risk_rate = tenure_curve.get("0-1", 0.25)
        bucket = "0-1 years"
    elif tenure_years < 2:
        risk_rate = tenure_curve.get("1-2", 0.20)
        bucket = "1-2 years"
    elif tenure_years < 3:
        risk_rate = tenure_curve.get("2-3", 0.10)
        bucket = "2-3 years"
    elif tenure_years < 5:
        risk_rate = tenure_curve.get("3-5", 0.08)
        bucket = "3-5 years"
    elif tenure_years < 7:
        risk_rate = tenure_curve.get("5-7", 0.12)
        bucket = "5-7 years"
    elif tenure_years < 10:
        risk_rate = tenure_curve.get("7-10", 0.10)
        bucket = "7-10 years"
    else:
        risk_rate = tenure_curve.get("10+", 0.06)
        bucket = "10+ years"

    return {
        "tenure_years": tenure_years,
        "tenure_bucket": bucket,
        "base_turnover_risk": round(risk_rate * 100, 1),
        "risk_score": round(risk_rate * 100, 1)
    }


def calculate_overall_flight_risk(
    risk_components: Dict,
    weights: Dict
) -> Dict[str, Any]:
    """Calculate overall flight risk score."""
    weighted_score = 0

    for component, config in weights.items():
        component_score = risk_components.get(component, {}).get("risk_score", 0)
        weight = config.get("weight", 0.15)
        weighted_score += component_score * weight

    return {
        "flight_risk_score": round(weighted_score, 1),
        "component_contributions": {
            component: round(risk_components.get(component, {}).get("risk_score", 0) * config.get("weight", 0), 1)
            for component, config in weights.items()
        }
    }


def determine_risk_level(
    score: float,
    thresholds: Dict
) -> str:
    """Determine risk level from score."""
    for level in ["low", "moderate", "high", "critical"]:
        if score <= thresholds.get(level, {}).get("max_score", 100):
            return level.upper()
    return "CRITICAL"


def calculate_replacement_cost(
    annual_salary: float,
    job_level: str,
    multipliers: Dict
) -> Dict[str, Any]:
    """Calculate estimated replacement cost."""
    multiplier = multipliers.get(job_level, multipliers.get("professional", 1.0))
    replacement_cost = annual_salary * multiplier

    return {
        "annual_salary": annual_salary,
        "job_level": job_level,
        "cost_multiplier": multiplier,
        "estimated_replacement_cost": round(replacement_cost, 2)
    }


def recommend_interventions(
    risk_components: Dict,
    flight_risk_score: float,
    strategies: Dict
) -> List[Dict]:
    """Recommend retention interventions."""
    recommendations = []

    # Compensation intervention
    if risk_components.get("compensation", {}).get("risk_score", 0) > 40:
        recommendations.append({
            "intervention": "compensation_adjustment",
            "priority": "high",
            **strategies.get("compensation_adjustment", {})
        })

    # Career development intervention
    if risk_components.get("career_growth", {}).get("risk_score", 0) > 30:
        recommendations.append({
            "intervention": "career_development_plan",
            "priority": "high",
            **strategies.get("career_development_plan", {})
        })

    # Engagement intervention
    if risk_components.get("engagement", {}).get("engagement_risk_score", 0) > 40:
        recommendations.append({
            "intervention": "role_enrichment",
            "priority": "medium",
            **strategies.get("role_enrichment", {})
        })

    # Critical risk intervention
    if flight_risk_score > 70:
        recommendations.append({
            "intervention": "retention_bonus",
            "priority": "critical",
            **strategies.get("retention_bonus", {})
        })

    return sorted(recommendations, key=lambda x: {"critical": 0, "high": 1, "medium": 2, "low": 3}.get(x["priority"], 4))


def assess_talent_retention(
    employee_id: str,
    employee_data: Dict,
    compensation_data: Dict,
    engagement_data: Dict,
    performance_data: Dict,
    industry: str,
    assessment_date: str
) -> Dict[str, Any]:
    """
    Assess talent retention risk.

    Business Rules:
    1. Multi-factor flight risk scoring
    2. Tenure-based risk assessment
    3. Engagement indicator analysis
    4. Intervention recommendations

    Args:
        employee_id: Employee identifier
        employee_data: Employee profile data
        compensation_data: Compensation information
        engagement_data: Engagement survey data
        performance_data: Performance data
        industry: Industry for benchmarks
        assessment_date: Assessment date

    Returns:
        Talent retention assessment results
    """
    factors = load_retention_factors()
    risk_factors = factors.get("retention_risk_factors", {})

    # Calculate risk components
    compensation_risk = calculate_compensation_risk(
        compensation_data.get("current_salary", 0),
        compensation_data.get("market_salary", 0),
        risk_factors.get("compensation", {})
    )

    career_risk = calculate_career_growth_risk(
        performance_data.get("years_since_promotion", 0),
        performance_data.get("has_development_plan", False),
        risk_factors.get("career_growth", {})
    )

    engagement_risk = calculate_engagement_risk(
        engagement_data,
        factors.get("engagement_indicators", {})
    )

    tenure_risk = calculate_tenure_risk(
        employee_data.get("tenure_years", 0),
        factors.get("tenure_risk_curve", {})
    )

    # Aggregate risk components
    risk_components = {
        "compensation": compensation_risk,
        "career_growth": career_risk,
        "engagement": engagement_risk,
        "tenure": tenure_risk
    }

    # Calculate overall flight risk
    flight_risk = calculate_overall_flight_risk(
        risk_components,
        risk_factors
    )

    # Determine risk level
    risk_level = determine_risk_level(
        flight_risk["flight_risk_score"],
        factors.get("flight_risk_thresholds", {})
    )

    # Calculate replacement cost
    replacement_cost = calculate_replacement_cost(
        compensation_data.get("current_salary", 0),
        employee_data.get("job_level", "professional"),
        factors.get("replacement_cost_multipliers", {})
    )

    # Get industry turnover benchmark
    turnover_benchmark = factors.get("turnover_benchmarks", {}).get(
        industry,
        factors.get("turnover_benchmarks", {}).get("default", {})
    )

    # Recommend interventions
    interventions = recommend_interventions(
        risk_components,
        flight_risk["flight_risk_score"],
        factors.get("intervention_strategies", {})
    )

    return {
        "employee_id": employee_id,
        "assessment_date": assessment_date,
        "employee_profile": {
            "name": employee_data.get("name", ""),
            "job_level": employee_data.get("job_level", ""),
            "tenure_years": employee_data.get("tenure_years", 0),
            "department": employee_data.get("department", "")
        },
        "risk_components": risk_components,
        "flight_risk": flight_risk,
        "risk_level": risk_level,
        "replacement_cost": replacement_cost,
        "industry_turnover_benchmark": turnover_benchmark,
        "recommended_interventions": interventions,
        "summary": {
            "overall_risk_score": flight_risk["flight_risk_score"],
            "risk_level": risk_level,
            "primary_risk_driver": max(
                risk_components.keys(),
                key=lambda k: risk_components[k].get("risk_score", 0)
            ),
            "intervention_count": len(interventions)
        }
    }


if __name__ == "__main__":
    import json
    result = assess_talent_retention(
        employee_id="EMP-001",
        employee_data={
            "name": "John Smith",
            "job_level": "senior_manager",
            "tenure_years": 5.5,
            "department": "Engineering"
        },
        compensation_data={
            "current_salary": 150000,
            "market_salary": 165000
        },
        engagement_data={
            "participation_rate": 0.75,
            "nps_score": 25,
            "pulse_survey_score": 3.5,
            "voluntary_initiative_count": 1
        },
        performance_data={
            "years_since_promotion": 4,
            "has_development_plan": False,
            "performance_rating": 4
        },
        industry="technology",
        assessment_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
