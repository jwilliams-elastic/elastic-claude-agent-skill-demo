"""
Acquisition Target Evaluation Module

Implements M&A target evaluation including
valuation, synergy analysis, and risk assessment.
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


def load_valuation_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    valuation_multiples_data = load_csv_as_dict("valuation_multiples.csv")
    growth_adjustments_data = load_csv_as_dict("growth_adjustments.csv")
    quality_factors_data = load_csv_as_dict("quality_factors.csv")
    risk_factors_data = load_csv_as_dict("risk_factors.csv")
    dcf_parameters_data = load_key_value_csv("dcf_parameters.csv")
    params = load_parameters()
    return {
        "valuation_multiples": valuation_multiples_data,
        "growth_adjustments": growth_adjustments_data,
        "quality_factors": quality_factors_data,
        "risk_factors": risk_factors_data,
        "dcf_parameters": dcf_parameters_data,
        **params
    }


def calculate_comparable_valuation(
    financials: Dict,
    industry: str,
    multiples: Dict
) -> Dict[str, Any]:
    """Calculate valuation using comparable multiples."""
    industry_multiples = multiples.get(industry, multiples.get("default", {}))

    revenue = financials.get("revenue", 0)
    ebitda = financials.get("ebitda", 0)
    net_income = financials.get("net_income", 0)

    ev_revenue = revenue * industry_multiples.get("ev_revenue", 2.0)
    ev_ebitda = ebitda * industry_multiples.get("ev_ebitda", 8.0) if ebitda > 0 else 0
    pe_value = net_income * industry_multiples.get("pe_ratio", 15.0) if net_income > 0 else 0

    valuations = [v for v in [ev_revenue, ev_ebitda, pe_value] if v > 0]
    avg_valuation = sum(valuations) / len(valuations) if valuations else 0

    return {
        "ev_revenue_valuation": round(ev_revenue, 0),
        "ev_ebitda_valuation": round(ev_ebitda, 0),
        "pe_valuation": round(pe_value, 0),
        "average_valuation": round(avg_valuation, 0),
        "multiples_used": industry_multiples
    }


def apply_growth_premium(
    base_valuation: float,
    revenue_growth: float,
    growth_adjustments: Dict
) -> Dict[str, Any]:
    """Apply premium/discount based on growth rate."""
    premium = 0

    for level, config in sorted(growth_adjustments.items(), key=lambda x: -x[1]["threshold"]):
        if revenue_growth >= config["threshold"]:
            premium = config["premium"]
            growth_category = level
            break
    else:
        premium = -0.20
        growth_category = "declining"

    adjusted_valuation = base_valuation * (1 + premium)

    return {
        "base_valuation": base_valuation,
        "revenue_growth_rate": revenue_growth,
        "growth_category": growth_category,
        "premium_applied": premium,
        "growth_adjusted_valuation": round(adjusted_valuation, 0)
    }


def assess_quality_score(
    target_profile: Dict,
    quality_factors: Dict
) -> Dict[str, Any]:
    """Assess target quality score."""
    total_score = 0
    factor_scores = []

    # Market position
    market_position = target_profile.get("market_position", "follower")
    position_config = quality_factors.get("market_position", {})
    position_score = position_config.get("scores", {}).get(market_position, 50)
    weighted_score = position_score * position_config.get("weight", 0.20)
    total_score += weighted_score
    factor_scores.append({"factor": "market_position", "score": position_score, "weighted": weighted_score})

    # Customer concentration
    top_customer_pct = target_profile.get("top_customer_pct", 0.20)
    concentration_config = quality_factors.get("customer_concentration", {})
    if top_customer_pct <= concentration_config.get("thresholds", {}).get("low", 0.10):
        conc_score = 100
    elif top_customer_pct <= concentration_config.get("thresholds", {}).get("medium", 0.25):
        conc_score = 70
    else:
        conc_score = 40
    weighted_score = conc_score * concentration_config.get("weight", 0.15)
    total_score += weighted_score
    factor_scores.append({"factor": "customer_concentration", "score": conc_score, "weighted": weighted_score})

    # Management quality
    management = target_profile.get("management_quality", "average")
    mgmt_config = quality_factors.get("management_quality", {})
    mgmt_score = mgmt_config.get("scores", {}).get(management, 50)
    weighted_score = mgmt_score * mgmt_config.get("weight", 0.15)
    total_score += weighted_score
    factor_scores.append({"factor": "management_quality", "score": mgmt_score, "weighted": weighted_score})

    # Technology moat
    tech_moat = target_profile.get("technology_moat", "moderate")
    tech_config = quality_factors.get("technology_moat", {})
    tech_score = tech_config.get("scores", {}).get(tech_moat, 50)
    weighted_score = tech_score * tech_config.get("weight", 0.15)
    total_score += weighted_score
    factor_scores.append({"factor": "technology_moat", "score": tech_score, "weighted": weighted_score})

    # Recurring revenue
    recurring_pct = target_profile.get("recurring_revenue_pct", 0.30)
    recurring_config = quality_factors.get("recurring_revenue", {})
    if recurring_pct >= recurring_config.get("thresholds", {}).get("high", 0.70):
        recurring_score = 100
    elif recurring_pct >= recurring_config.get("thresholds", {}).get("medium", 0.40):
        recurring_score = 70
    else:
        recurring_score = 40
    weighted_score = recurring_score * recurring_config.get("weight", 0.20)
    total_score += weighted_score
    factor_scores.append({"factor": "recurring_revenue", "score": recurring_score, "weighted": weighted_score})

    return {
        "quality_score": round(total_score, 1),
        "factor_scores": factor_scores,
        "quality_rating": "EXCELLENT" if total_score >= 80 else "GOOD" if total_score >= 65 else "AVERAGE" if total_score >= 50 else "BELOW_AVERAGE"
    }


def calculate_risk_adjustment(
    risk_profile: Dict,
    risk_factors: Dict
) -> Dict[str, Any]:
    """Calculate risk-adjusted valuation factor."""
    adjustment_factor = 1.0
    risk_details = []

    for risk_type, levels in risk_factors.items():
        risk_level = risk_profile.get(risk_type, "medium")
        factor = levels.get(risk_level, 0.90)
        adjustment_factor *= factor
        risk_details.append({
            "risk_type": risk_type,
            "level": risk_level,
            "factor": factor
        })

    return {
        "risk_adjustment_factor": round(adjustment_factor, 3),
        "risk_details": risk_details
    }


def estimate_synergies(
    acquirer_revenue: float,
    target_revenue: float,
    acquirer_costs: float,
    target_costs: float,
    synergy_assumptions: Dict
) -> Dict[str, Any]:
    """Estimate potential synergies."""
    combined_revenue = acquirer_revenue + target_revenue
    combined_costs = acquirer_costs + target_costs

    # Revenue synergies (cross-selling, market expansion)
    rev_synergy_rate = (synergy_assumptions.get("revenue_synergy_range", [0.02, 0.10])[0] +
                        synergy_assumptions.get("revenue_synergy_range", [0.02, 0.10])[1]) / 2
    revenue_synergies = target_revenue * rev_synergy_rate

    # Cost synergies (consolidation, economies of scale)
    cost_synergy_rate = (synergy_assumptions.get("cost_synergy_range", [0.05, 0.20])[0] +
                         synergy_assumptions.get("cost_synergy_range", [0.05, 0.20])[1]) / 2
    cost_synergies = target_costs * cost_synergy_rate

    # Integration costs
    integration_costs = target_revenue * synergy_assumptions.get("integration_cost_pct", 0.05)

    # Net synergy value (PV)
    realization_years = synergy_assumptions.get("synergy_realization_years", 3)
    annual_synergies = (revenue_synergies + cost_synergies) / realization_years
    pv_synergies = annual_synergies * realization_years * 0.85  # Simplified PV

    return {
        "revenue_synergies": round(revenue_synergies, 0),
        "cost_synergies": round(cost_synergies, 0),
        "total_gross_synergies": round(revenue_synergies + cost_synergies, 0),
        "integration_costs": round(integration_costs, 0),
        "net_synergy_value": round(pv_synergies - integration_costs, 0),
        "realization_timeline_years": realization_years
    }


def calculate_dcf_valuation(
    financials: Dict,
    dcf_params: Dict,
    beta: float = 1.0
) -> Dict[str, Any]:
    """Calculate DCF-based valuation."""
    fcf = financials.get("free_cash_flow", 0)
    growth_rate = financials.get("revenue_growth", 0.05)

    risk_free = dcf_params.get("risk_free_rate", 0.04)
    market_premium = dcf_params.get("market_risk_premium", 0.05)
    terminal_growth = dcf_params.get("terminal_growth_rate", 0.025)

    # WACC calculation (simplified)
    cost_of_equity = risk_free + beta * market_premium
    wacc = cost_of_equity * 0.7 + 0.05 * 0.3  # Assume 70% equity, 30% debt at 5%

    # Project FCF
    projection_years = dcf_params.get("projection_years", 5)
    projected_fcf = []
    pv_fcf = 0
    current_fcf = fcf

    for year in range(1, projection_years + 1):
        current_fcf *= (1 + growth_rate)
        discount_factor = (1 + wacc) ** year
        pv = current_fcf / discount_factor
        pv_fcf += pv
        projected_fcf.append({"year": year, "fcf": round(current_fcf, 0), "pv": round(pv, 0)})

    # Terminal value
    terminal_fcf = current_fcf * (1 + terminal_growth)
    terminal_value = terminal_fcf / (wacc - terminal_growth)
    pv_terminal = terminal_value / ((1 + wacc) ** projection_years)

    dcf_value = pv_fcf + pv_terminal

    return {
        "wacc": round(wacc * 100, 2),
        "pv_projection_period": round(pv_fcf, 0),
        "terminal_value": round(terminal_value, 0),
        "pv_terminal_value": round(pv_terminal, 0),
        "dcf_valuation": round(dcf_value, 0)
    }


def evaluate_acquisition_target(
    target_id: str,
    target_name: str,
    financials: Dict,
    target_profile: Dict,
    risk_profile: Dict,
    acquirer_financials: Dict,
    industry: str,
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate acquisition target.

    Business Rules:
    1. Comparable company valuation
    2. Growth premium adjustment
    3. Quality and risk assessment
    4. Synergy estimation

    Args:
        target_id: Target identifier
        target_name: Target company name
        financials: Target financial data
        target_profile: Target quality profile
        risk_profile: Risk assessment data
        acquirer_financials: Acquirer financial data
        industry: Industry classification
        evaluation_date: Evaluation date

    Returns:
        Acquisition target evaluation results
    """
    params = load_valuation_parameters()

    # Comparable valuation
    comp_valuation = calculate_comparable_valuation(
        financials,
        industry,
        params.get("valuation_multiples", {})
    )

    # Growth adjustment
    revenue_growth = financials.get("revenue_growth", 0.05)
    growth_adjusted = apply_growth_premium(
        comp_valuation["average_valuation"],
        revenue_growth,
        params.get("growth_adjustments", {})
    )

    # Quality assessment
    quality = assess_quality_score(
        target_profile,
        params.get("quality_factors", {})
    )

    # Risk adjustment
    risk = calculate_risk_adjustment(
        risk_profile,
        params.get("risk_factors", {})
    )

    # Apply risk adjustment to valuation
    risk_adjusted_value = growth_adjusted["growth_adjusted_valuation"] * risk["risk_adjustment_factor"]

    # Synergy estimation
    synergies = estimate_synergies(
        acquirer_financials.get("revenue", 0),
        financials.get("revenue", 0),
        acquirer_financials.get("operating_costs", 0),
        financials.get("operating_costs", 0),
        params.get("synergy_assumptions", {})
    )

    # DCF valuation
    dcf = calculate_dcf_valuation(
        financials,
        params.get("dcf_parameters", {}),
        target_profile.get("beta", 1.0)
    )

    # Final valuation range
    low_value = min(risk_adjusted_value, dcf["dcf_valuation"]) * 0.90
    high_value = max(risk_adjusted_value, dcf["dcf_valuation"]) * 1.10 + synergies["net_synergy_value"]
    mid_value = (low_value + high_value) / 2

    return {
        "target_id": target_id,
        "target_name": target_name,
        "evaluation_date": evaluation_date,
        "industry": industry,
        "comparable_valuation": comp_valuation,
        "growth_adjusted_valuation": growth_adjusted,
        "quality_assessment": quality,
        "risk_assessment": risk,
        "synergy_analysis": synergies,
        "dcf_valuation": dcf,
        "valuation_summary": {
            "standalone_value": round(risk_adjusted_value, 0),
            "with_synergies": round(risk_adjusted_value + synergies["net_synergy_value"], 0),
            "valuation_range": {
                "low": round(low_value, 0),
                "mid": round(mid_value, 0),
                "high": round(high_value, 0)
            }
        },
        "recommendation": "ATTRACTIVE" if quality["quality_score"] >= 70 and risk["risk_adjustment_factor"] >= 0.85 else "NEUTRAL" if quality["quality_score"] >= 50 else "CAUTIOUS"
    }


if __name__ == "__main__":
    import json
    result = evaluate_acquisition_target(
        target_id="TGT-001",
        target_name="TechCorp Inc.",
        financials={
            "revenue": 50000000,
            "ebitda": 8000000,
            "net_income": 4000000,
            "free_cash_flow": 5000000,
            "revenue_growth": 0.15,
            "operating_costs": 42000000
        },
        target_profile={
            "market_position": "challenger",
            "top_customer_pct": 0.15,
            "management_quality": "good",
            "technology_moat": "moderate",
            "recurring_revenue_pct": 0.60,
            "beta": 1.2
        },
        risk_profile={
            "integration_complexity": "medium",
            "regulatory_risk": "low",
            "key_person_dependency": "medium",
            "technology_obsolescence": "low"
        },
        acquirer_financials={
            "revenue": 200000000,
            "operating_costs": 170000000
        },
        industry="technology",
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
