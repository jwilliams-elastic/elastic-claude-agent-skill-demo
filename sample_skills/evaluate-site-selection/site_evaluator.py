"""
Site Selection Evaluation Module

Implements facility site selection analysis including
cost comparison, labor market assessment, and infrastructure scoring.
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


def load_site_criteria() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    evaluation_criteria_data = load_csv_as_dict("evaluation_criteria.csv")
    cost_benchmarks_data = load_csv_as_dict("cost_benchmarks.csv")
    infrastructure_scores_data = load_csv_as_dict("infrastructure_scores.csv")
    incentive_types_data = load_csv_as_dict("incentive_types.csv")
    risk_factors_data = load_csv_as_dict("risk_factors.csv")
    facility_requirements_data = load_csv_as_dict("facility_requirements.csv")
    params = load_parameters()
    return {
        "evaluation_criteria": evaluation_criteria_data,
        "cost_benchmarks": cost_benchmarks_data,
        "infrastructure_scores": infrastructure_scores_data,
        "incentive_types": incentive_types_data,
        "risk_factors": risk_factors_data,
        "facility_requirements": facility_requirements_data,
        **params
    }


def score_cost_factors(
    site_data: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Score cost-related factors."""
    scores = {}
    details = []

    # Real estate cost (per sq ft)
    re_cost = site_data.get("real_estate_cost_sqft", 25)
    re_bench = benchmarks.get("real_estate", {})
    if re_cost <= re_bench.get("low", 10):
        scores["real_estate"] = 100
    elif re_cost <= re_bench.get("medium", 25):
        scores["real_estate"] = 70
    else:
        scores["real_estate"] = 40
    details.append({"factor": "real_estate", "value": re_cost, "score": scores["real_estate"]})

    # Labor cost
    labor_cost = site_data.get("avg_hourly_wage", 25)
    labor_bench = benchmarks.get("labor_hourly", {})
    if labor_cost <= labor_bench.get("low", 15):
        scores["labor"] = 100
    elif labor_cost <= labor_bench.get("medium", 25):
        scores["labor"] = 70
    else:
        scores["labor"] = 40
    details.append({"factor": "labor", "value": labor_cost, "score": scores["labor"]})

    # Utility cost
    utility_cost = site_data.get("electricity_rate_kwh", 0.10)
    util_bench = benchmarks.get("electricity_kwh", {})
    if utility_cost <= util_bench.get("low", 0.06):
        scores["utilities"] = 100
    elif utility_cost <= util_bench.get("medium", 0.10):
        scores["utilities"] = 70
    else:
        scores["utilities"] = 40
    details.append({"factor": "utilities", "value": utility_cost, "score": scores["utilities"]})

    # Tax burden
    tax_rate = site_data.get("property_tax_rate", 0.02)
    tax_bench = benchmarks.get("property_tax_rate", {})
    if tax_rate <= tax_bench.get("low", 0.01):
        scores["tax"] = 100
    elif tax_rate <= tax_bench.get("medium", 0.02):
        scores["tax"] = 70
    else:
        scores["tax"] = 40
    details.append({"factor": "tax", "value": tax_rate, "score": scores["tax"]})

    avg_score = sum(scores.values()) / len(scores)

    return {
        "cost_score": round(avg_score, 1),
        "component_scores": scores,
        "details": details
    }


def score_labor_market(
    site_data: Dict
) -> Dict[str, Any]:
    """Score labor market factors."""
    scores = {}

    # Workforce availability
    unemployment_rate = site_data.get("unemployment_rate", 5.0)
    if unemployment_rate >= 5:
        scores["availability"] = 80
    elif unemployment_rate >= 3:
        scores["availability"] = 60
    else:
        scores["availability"] = 40  # Very tight labor market

    # Education level
    college_pct = site_data.get("college_degree_pct", 30)
    if college_pct >= 40:
        scores["education"] = 100
    elif college_pct >= 30:
        scores["education"] = 75
    else:
        scores["education"] = 50

    # Labor force size
    labor_force = site_data.get("labor_force_size", 100000)
    if labor_force >= 500000:
        scores["labor_force_size"] = 100
    elif labor_force >= 200000:
        scores["labor_force_size"] = 75
    elif labor_force >= 100000:
        scores["labor_force_size"] = 60
    else:
        scores["labor_force_size"] = 40

    avg_score = sum(scores.values()) / len(scores)

    return {
        "labor_market_score": round(avg_score, 1),
        "component_scores": scores
    }


def score_infrastructure(
    site_data: Dict,
    infra_config: Dict
) -> Dict[str, Any]:
    """Score infrastructure factors."""
    scores = {}

    # Highway access
    highway_miles = site_data.get("highway_distance_miles", 10)
    highway_config = infra_config.get("transportation", {}).get("major_highway_miles", {})
    if highway_miles <= highway_config.get("excellent", 5):
        scores["highway"] = 100
    elif highway_miles <= highway_config.get("good", 15):
        scores["highway"] = 75
    else:
        scores["highway"] = 50

    # Airport access
    airport_miles = site_data.get("airport_distance_miles", 30)
    airport_config = infra_config.get("transportation", {}).get("airport_miles", {})
    if airport_miles <= airport_config.get("excellent", 20):
        scores["airport"] = 100
    elif airport_miles <= airport_config.get("good", 40):
        scores["airport"] = 75
    else:
        scores["airport"] = 50

    # Power reliability
    power_reliability = site_data.get("power_reliability_pct", 99.5)
    if power_reliability >= 99.9:
        scores["power"] = 100
    elif power_reliability >= 99.0:
        scores["power"] = 75
    else:
        scores["power"] = 50

    # Telecom/broadband
    broadband_speed = site_data.get("broadband_mbps", 100)
    if broadband_speed >= 1000:
        scores["telecom"] = 100
    elif broadband_speed >= 500:
        scores["telecom"] = 80
    elif broadband_speed >= 100:
        scores["telecom"] = 60
    else:
        scores["telecom"] = 40

    avg_score = sum(scores.values()) / len(scores)

    return {
        "infrastructure_score": round(avg_score, 1),
        "component_scores": scores
    }


def score_market_access(
    site_data: Dict
) -> Dict[str, Any]:
    """Score market access factors."""
    scores = {}

    # Customer proximity (% of customers within 500 miles)
    customer_proximity = site_data.get("customers_within_500mi_pct", 50)
    if customer_proximity >= 70:
        scores["customer_proximity"] = 100
    elif customer_proximity >= 50:
        scores["customer_proximity"] = 75
    else:
        scores["customer_proximity"] = 50

    # Market size (population within 100 miles)
    market_pop = site_data.get("population_100mi", 1000000)
    if market_pop >= 5000000:
        scores["market_size"] = 100
    elif market_pop >= 2000000:
        scores["market_size"] = 75
    elif market_pop >= 1000000:
        scores["market_size"] = 60
    else:
        scores["market_size"] = 40

    # GDP growth
    gdp_growth = site_data.get("regional_gdp_growth_pct", 2.0)
    if gdp_growth >= 4:
        scores["growth"] = 100
    elif gdp_growth >= 2:
        scores["growth"] = 70
    else:
        scores["growth"] = 50

    avg_score = sum(scores.values()) / len(scores)

    return {
        "market_access_score": round(avg_score, 1),
        "component_scores": scores
    }


def calculate_incentives_value(
    incentives: Dict,
    incentive_types: Dict,
    investment_amount: float,
    jobs_created: int
) -> Dict[str, Any]:
    """Calculate total value of available incentives."""
    total_value = 0
    incentive_details = []

    # Tax abatement
    if incentives.get("tax_abatement", False):
        years = incentives.get("tax_abatement_years", incentive_types.get("tax_abatement", {}).get("typical_years", 10))
        pct = incentives.get("tax_abatement_pct", incentive_types.get("tax_abatement", {}).get("typical_pct", 0.50))
        annual_tax = investment_amount * 0.02  # Assume 2% property tax
        value = annual_tax * pct * years
        total_value += value
        incentive_details.append({"type": "tax_abatement", "value": round(value, 0)})

    # Job creation credits
    if incentives.get("job_creation_credit", False):
        per_job = incentives.get("credit_per_job", incentive_types.get("job_creation_credit", {}).get("typical_per_job", 5000))
        value = per_job * jobs_created
        total_value += value
        incentive_details.append({"type": "job_creation_credit", "value": round(value, 0)})

    # Training assistance
    if incentives.get("training_assistance", False):
        per_emp = incentives.get("training_per_employee", incentive_types.get("training_assistance", {}).get("typical_per_employee", 2000))
        value = per_emp * jobs_created
        total_value += value
        incentive_details.append({"type": "training_assistance", "value": round(value, 0)})

    # Infrastructure grant
    if incentives.get("infrastructure_grant", False):
        grant_pct = incentives.get("grant_pct", incentive_types.get("infrastructure_grant", {}).get("typical_pct_of_cost", 0.25))
        infra_cost = incentives.get("infrastructure_cost", investment_amount * 0.10)
        value = infra_cost * grant_pct
        total_value += value
        incentive_details.append({"type": "infrastructure_grant", "value": round(value, 0)})

    return {
        "total_incentive_value": round(total_value, 0),
        "incentive_details": incentive_details,
        "incentives_pct_of_investment": round(total_value / investment_amount * 100, 1) if investment_amount > 0 else 0
    }


def assess_risk_factors(
    site_data: Dict,
    risk_config: Dict
) -> Dict[str, Any]:
    """Assess site risk factors."""
    risks = []
    risk_score = 100

    # Natural disaster risk
    region_type = site_data.get("region_type", "")
    high_risk_regions = risk_config.get("natural_disaster", {}).get("high_risk_regions", [])
    if region_type in high_risk_regions:
        risks.append({"risk": "natural_disaster", "level": "high", "impact": -20})
        risk_score -= 20

    # Political/regulatory stability
    stability = site_data.get("political_stability", "stable")
    stability_score = risk_config.get("political_stability", {}).get("scores", {}).get(stability, 70)
    if stability_score < 70:
        risks.append({"risk": "political_instability", "level": "medium", "impact": -15})
        risk_score -= 15

    # Labor relations
    union_density = site_data.get("union_density", 0.10)
    union_threshold = risk_config.get("labor_relations", {}).get("union_density_high", 0.20)
    if union_density > union_threshold:
        risks.append({"risk": "labor_relations", "level": "medium", "impact": -10})
        risk_score -= 10

    return {
        "risk_adjusted_score": max(0, risk_score),
        "identified_risks": risks
    }


def evaluate_site_selection(
    project_id: str,
    sites: List[Dict],
    facility_type: str,
    investment_amount: float,
    jobs_to_create: int,
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate site selection options.

    Business Rules:
    1. Multi-criteria scoring (cost, labor, infrastructure)
    2. Incentive value calculation
    3. Risk factor assessment
    4. Weighted comparison

    Args:
        project_id: Project identifier
        sites: List of site candidates
        facility_type: Type of facility
        investment_amount: Planned investment
        jobs_to_create: Expected job creation
        evaluation_date: Evaluation date

    Returns:
        Site selection evaluation results
    """
    criteria = load_site_criteria()
    evaluation_weights = criteria.get("evaluation_criteria", {})
    benchmarks = criteria.get("cost_benchmarks", {})
    infra_config = criteria.get("infrastructure_scores", {})
    incentive_types = criteria.get("incentive_types", {})
    risk_config = criteria.get("risk_factors", {})

    site_evaluations = []

    for site in sites:
        # Score each category
        cost_result = score_cost_factors(site, benchmarks)
        labor_result = score_labor_market(site)
        infra_result = score_infrastructure(site, infra_config)
        market_result = score_market_access(site)

        # Calculate incentives
        incentives = calculate_incentives_value(
            site.get("incentives", {}),
            incentive_types,
            investment_amount,
            jobs_to_create
        )

        # Assess risks
        risks = assess_risk_factors(site, risk_config)

        # Calculate weighted score
        weighted_score = (
            cost_result["cost_score"] * evaluation_weights.get("cost_factors", {}).get("weight", 0.25) +
            labor_result["labor_market_score"] * evaluation_weights.get("labor_market", {}).get("weight", 0.20) +
            infra_result["infrastructure_score"] * evaluation_weights.get("infrastructure", {}).get("weight", 0.20) +
            market_result["market_access_score"] * evaluation_weights.get("market_access", {}).get("weight", 0.15)
        )

        # Apply risk adjustment
        risk_multiplier = risks["risk_adjusted_score"] / 100
        final_score = weighted_score * risk_multiplier

        # Add incentive bonus (up to 10 points)
        incentive_bonus = min(10, incentives["incentives_pct_of_investment"])
        final_score += incentive_bonus

        site_evaluations.append({
            "site_name": site.get("name", "Unknown"),
            "location": site.get("location", ""),
            "scores": {
                "cost": cost_result,
                "labor_market": labor_result,
                "infrastructure": infra_result,
                "market_access": market_result
            },
            "incentives": incentives,
            "risk_assessment": risks,
            "weighted_score": round(weighted_score, 1),
            "final_score": round(final_score, 1)
        })

    # Rank sites
    ranked_sites = sorted(site_evaluations, key=lambda x: x["final_score"], reverse=True)
    for rank, site in enumerate(ranked_sites, 1):
        site["rank"] = rank

    return {
        "project_id": project_id,
        "evaluation_date": evaluation_date,
        "facility_type": facility_type,
        "investment_amount": investment_amount,
        "jobs_to_create": jobs_to_create,
        "sites_evaluated": len(sites),
        "site_rankings": ranked_sites,
        "recommended_site": ranked_sites[0]["site_name"] if ranked_sites else None,
        "recommendation_confidence": "HIGH" if ranked_sites and (ranked_sites[0]["final_score"] - ranked_sites[1]["final_score"] if len(ranked_sites) > 1 else 100) > 10 else "MEDIUM"
    }


if __name__ == "__main__":
    import json
    result = evaluate_site_selection(
        project_id="SITE-001",
        sites=[
            {
                "name": "Austin, TX",
                "location": "Austin, Texas",
                "real_estate_cost_sqft": 20,
                "avg_hourly_wage": 28,
                "electricity_rate_kwh": 0.08,
                "property_tax_rate": 0.025,
                "unemployment_rate": 3.5,
                "college_degree_pct": 45,
                "labor_force_size": 1200000,
                "highway_distance_miles": 5,
                "airport_distance_miles": 15,
                "power_reliability_pct": 99.5,
                "broadband_mbps": 1000,
                "customers_within_500mi_pct": 40,
                "population_100mi": 3000000,
                "regional_gdp_growth_pct": 4.5,
                "region_type": "inland",
                "political_stability": "stable",
                "union_density": 0.05,
                "incentives": {
                    "tax_abatement": True,
                    "job_creation_credit": True,
                    "training_assistance": True
                }
            },
            {
                "name": "Columbus, OH",
                "location": "Columbus, Ohio",
                "real_estate_cost_sqft": 12,
                "avg_hourly_wage": 22,
                "electricity_rate_kwh": 0.09,
                "property_tax_rate": 0.018,
                "unemployment_rate": 4.0,
                "college_degree_pct": 35,
                "labor_force_size": 900000,
                "highway_distance_miles": 3,
                "airport_distance_miles": 10,
                "power_reliability_pct": 99.7,
                "broadband_mbps": 500,
                "customers_within_500mi_pct": 60,
                "population_100mi": 2500000,
                "regional_gdp_growth_pct": 2.5,
                "region_type": "inland",
                "political_stability": "stable",
                "union_density": 0.12,
                "incentives": {
                    "tax_abatement": True,
                    "job_creation_credit": True
                }
            }
        ],
        facility_type="manufacturing",
        investment_amount=50000000,
        jobs_to_create=200,
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
