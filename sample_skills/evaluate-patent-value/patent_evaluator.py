"""
Patent Value Evaluation Module

Implements patent valuation including
income and market approaches, strength assessment, and strategic value.
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


def load_patent_valuation() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    valuation_methods_data = load_csv_as_dict("valuation_methods.csv")
    royalty_rates_by_industry_data = load_csv_as_dict("royalty_rates_by_industry.csv")
    strength_factors_data = load_csv_as_dict("strength_factors.csv")
    life_cycle_factors_data = load_csv_as_dict("life_cycle_factors.csv")
    discount_rates_data = load_csv_as_dict("discount_rates.csv")
    quality_scores_data = load_csv_as_dict("quality_scores.csv")
    jurisdiction_factors_data = load_csv_as_dict("jurisdiction_factors.csv")
    cost_components_data = load_csv_as_dict("cost_components.csv")
    params = load_parameters()
    return {
        "valuation_methods": valuation_methods_data,
        "royalty_rates_by_industry": royalty_rates_by_industry_data,
        "strength_factors": strength_factors_data,
        "life_cycle_factors": life_cycle_factors_data,
        "discount_rates": discount_rates_data,
        "quality_scores": quality_scores_data,
        "jurisdiction_factors": jurisdiction_factors_data,
        "cost_components": cost_components_data,
        **params
    }


def calculate_relief_from_royalty(
    projected_revenues: List[float],
    royalty_rate: float,
    discount_rate: float,
    years_remaining: int
) -> Dict[str, Any]:
    """Calculate patent value using relief from royalty method."""
    if not projected_revenues:
        return {"error": "No revenue projections provided"}

    yearly_royalties = []
    total_npv = 0

    for i, revenue in enumerate(projected_revenues[:years_remaining]):
        royalty = revenue * royalty_rate
        discount_factor = 1 / ((1 + discount_rate) ** (i + 1))
        pv = royalty * discount_factor

        yearly_royalties.append({
            "year": i + 1,
            "projected_revenue": revenue,
            "royalty_amount": round(royalty, 2),
            "discount_factor": round(discount_factor, 4),
            "present_value": round(pv, 2)
        })

        total_npv += pv

    return {
        "method": "relief_from_royalty",
        "royalty_rate": royalty_rate,
        "discount_rate": discount_rate,
        "years_valued": len(yearly_royalties),
        "yearly_breakdown": yearly_royalties,
        "total_npv": round(total_npv, 2)
    }


def calculate_market_value(
    annual_revenue: float,
    annual_profit: float,
    industry: str,
    royalty_rates: Dict
) -> Dict[str, Any]:
    """Calculate patent value using market approach."""
    industry_rates = royalty_rates.get(industry, royalty_rates.get("software", {}))
    median_rate = industry_rates.get("median", 0.05)
    rate_range = industry_rates.get("range", {"min": 0.02, "max": 0.10})

    # Calculate implied values at different rates
    low_value = annual_revenue * rate_range.get("min", 0.02) * 10  # 10x multiplier
    median_value = annual_revenue * median_rate * 10
    high_value = annual_revenue * rate_range.get("max", 0.10) * 10

    return {
        "method": "market_approach",
        "industry": industry,
        "annual_revenue_base": annual_revenue,
        "royalty_rate_range": {
            "low": rate_range.get("min", 0),
            "median": median_rate,
            "high": rate_range.get("max", 0)
        },
        "implied_value_range": {
            "low": round(low_value, 2),
            "median": round(median_value, 2),
            "high": round(high_value, 2)
        }
    }


def assess_legal_strength(
    legal_factors: Dict,
    strength_config: Dict
) -> Dict[str, Any]:
    """Assess patent legal strength."""
    components = strength_config.get("components", {})
    total_weighted = 0
    total_weight = 0

    factor_scores = []
    for factor, config in components.items():
        weight = config.get("weight", 0.25)
        value = legal_factors.get(factor, 0.5)

        weighted = value * weight
        total_weighted += weighted
        total_weight += weight

        factor_scores.append({
            "factor": factor,
            "score": value,
            "weight": weight,
            "weighted_score": round(weighted, 3)
        })

    overall_score = total_weighted / total_weight if total_weight > 0 else 0

    return {
        "dimension": "legal_strength",
        "factors": factor_scores,
        "overall_score": round(overall_score, 3)
    }


def assess_technical_strength(
    technical_factors: Dict,
    strength_config: Dict
) -> Dict[str, Any]:
    """Assess patent technical strength."""
    components = strength_config.get("components", {})
    total_weighted = 0
    total_weight = 0

    factor_scores = []
    for factor, config in components.items():
        weight = config.get("weight", 0.25)
        value = technical_factors.get(factor, 0.5)

        weighted = value * weight
        total_weighted += weighted
        total_weight += weight

        factor_scores.append({
            "factor": factor,
            "score": value,
            "weight": weight,
            "weighted_score": round(weighted, 3)
        })

    overall_score = total_weighted / total_weight if total_weight > 0 else 0

    return {
        "dimension": "technical_strength",
        "factors": factor_scores,
        "overall_score": round(overall_score, 3)
    }


def assess_market_strength(
    market_factors: Dict,
    strength_config: Dict
) -> Dict[str, Any]:
    """Assess patent market strength."""
    components = strength_config.get("components", {})
    total_weighted = 0
    total_weight = 0

    factor_scores = []
    for factor, config in components.items():
        weight = config.get("weight", 0.25)
        value = market_factors.get(factor, 0.5)

        weighted = value * weight
        total_weighted += weighted
        total_weight += weight

        factor_scores.append({
            "factor": factor,
            "score": value,
            "weight": weight,
            "weighted_score": round(weighted, 3)
        })

    overall_score = total_weighted / total_weight if total_weight > 0 else 0

    return {
        "dimension": "market_strength",
        "factors": factor_scores,
        "overall_score": round(overall_score, 3)
    }


def calculate_overall_strength(
    strength_assessments: List[Dict],
    strength_factors: Dict
) -> Dict[str, Any]:
    """Calculate overall patent strength score."""
    total_weighted = 0

    for assessment in strength_assessments:
        dimension = assessment.get("dimension", "")
        score = assessment.get("overall_score", 0)
        weight = strength_factors.get(dimension, {}).get("weight", 0.25)

        total_weighted += score * weight

    return {
        "overall_strength_score": round(total_weighted, 3),
        "strength_pct": round(total_weighted * 100, 1)
    }


def apply_quality_premium(
    base_value: float,
    strength_score: float,
    quality_scores: Dict
) -> Dict[str, Any]:
    """Apply quality premium/discount to base value."""
    strength_pct = strength_score * 100

    for quality_level, config in sorted(
        quality_scores.items(),
        key=lambda x: x[1].get("min_score", 0),
        reverse=True
    ):
        if strength_pct >= config.get("min_score", 0):
            multiplier = config.get("premium_multiplier", 1.0)
            adjusted_value = base_value * multiplier

            return {
                "quality_level": quality_level.upper(),
                "strength_score_pct": round(strength_pct, 1),
                "base_value": base_value,
                "premium_multiplier": multiplier,
                "adjusted_value": round(adjusted_value, 2)
            }

    return {
        "quality_level": "POOR",
        "strength_score_pct": round(strength_pct, 1),
        "base_value": base_value,
        "premium_multiplier": 0.40,
        "adjusted_value": round(base_value * 0.40, 2)
    }


def apply_lifecycle_adjustment(
    value: float,
    years_remaining: int,
    lifecycle_factors: Dict
) -> Dict[str, Any]:
    """Apply lifecycle stage adjustment to value."""
    for stage, config in lifecycle_factors.items():
        years_threshold = config.get("years_remaining_min", 0)
        if years_remaining >= years_threshold:
            multiplier = config.get("value_multiplier", 1.0)
            adjusted_value = value * multiplier

            return {
                "lifecycle_stage": stage.upper().replace("_", " "),
                "years_remaining": years_remaining,
                "value_multiplier": multiplier,
                "adjusted_value": round(adjusted_value, 2)
            }

    return {
        "lifecycle_stage": "EXPIRED",
        "years_remaining": years_remaining,
        "value_multiplier": 0,
        "adjusted_value": 0
    }


def calculate_jurisdiction_value(
    base_value: float,
    jurisdictions: List[str],
    jurisdiction_factors: Dict
) -> Dict[str, Any]:
    """Calculate value contribution by jurisdiction."""
    jurisdiction_values = []
    total_weighted_value = 0

    for jurisdiction in jurisdictions:
        config = jurisdiction_factors.get(jurisdiction.lower(), jurisdiction_factors.get("other", {}))
        importance = config.get("importance", 0.30)
        enforcement = config.get("enforcement_score", 0.50)

        jurisdiction_weight = importance * enforcement
        jurisdiction_value = base_value * jurisdiction_weight

        jurisdiction_values.append({
            "jurisdiction": jurisdiction.upper(),
            "importance_factor": importance,
            "enforcement_score": enforcement,
            "combined_weight": round(jurisdiction_weight, 3),
            "value_contribution": round(jurisdiction_value, 2)
        })

        total_weighted_value += jurisdiction_value

    return {
        "jurisdictions_analyzed": len(jurisdictions),
        "jurisdiction_breakdown": jurisdiction_values,
        "total_jurisdiction_weighted_value": round(total_weighted_value, 2)
    }


def evaluate_patent_value(
    evaluation_id: str,
    patent_id: str,
    patent_title: str,
    industry: str,
    years_remaining: int,
    projected_revenues: List[float],
    annual_revenue: float,
    annual_profit: float,
    legal_factors: Dict,
    technical_factors: Dict,
    market_factors: Dict,
    jurisdictions: List[str],
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate patent value.

    Business Rules:
    1. Income and market valuation approaches
    2. Multi-factor strength assessment
    3. Quality and lifecycle adjustments
    4. Jurisdiction-weighted value

    Args:
        evaluation_id: Evaluation identifier
        patent_id: Patent identifier
        patent_title: Patent title
        industry: Industry classification
        years_remaining: Years until expiration
        projected_revenues: Yearly revenue projections
        annual_revenue: Current annual revenue
        annual_profit: Current annual profit
        legal_factors: Legal strength factors
        technical_factors: Technical strength factors
        market_factors: Market strength factors
        jurisdictions: Patent jurisdictions
        evaluation_date: Evaluation date

    Returns:
        Patent valuation results
    """
    config = load_patent_valuation()
    valuation_methods = config.get("valuation_methods", {})
    royalty_rates = config.get("royalty_rates_by_industry", {})
    strength_factors = config.get("strength_factors", {})
    lifecycle_factors = config.get("life_cycle_factors", {})
    discount_rates = config.get("discount_rates", {})
    quality_scores = config.get("quality_scores", {})
    jurisdiction_config = config.get("jurisdiction_factors", {})

    # Get industry royalty rate
    industry_rates = royalty_rates.get(industry, royalty_rates.get("software", {}))
    royalty_rate = industry_rates.get("median", 0.05)

    # Determine discount rate based on risk level
    discount_rate = discount_rates.get("medium_risk", {}).get("rate", 0.15)

    # Income approach valuation
    income_valuation = calculate_relief_from_royalty(
        projected_revenues,
        royalty_rate,
        discount_rate,
        years_remaining
    )

    # Market approach valuation
    market_valuation = calculate_market_value(
        annual_revenue,
        annual_profit,
        industry,
        royalty_rates
    )

    # Strength assessments
    legal_strength = assess_legal_strength(
        legal_factors,
        strength_factors.get("legal_strength", {})
    )

    technical_strength = assess_technical_strength(
        technical_factors,
        strength_factors.get("technical_strength", {})
    )

    market_strength = assess_market_strength(
        market_factors,
        strength_factors.get("market_strength", {})
    )

    strength_assessments = [legal_strength, technical_strength, market_strength]
    overall_strength = calculate_overall_strength(strength_assessments, strength_factors)

    # Calculate blended base value
    income_weight = valuation_methods.get("income_approach", {}).get("weight", 0.50)
    market_weight = valuation_methods.get("market_approach", {}).get("weight", 0.30)

    income_value = income_valuation.get("total_npv", 0)
    market_value = market_valuation.get("implied_value_range", {}).get("median", 0)

    blended_value = (income_value * income_weight + market_value * market_weight) / (income_weight + market_weight)

    # Apply quality premium
    quality_adjusted = apply_quality_premium(
        blended_value,
        overall_strength["overall_strength_score"],
        quality_scores
    )

    # Apply lifecycle adjustment
    lifecycle_adjusted = apply_lifecycle_adjustment(
        quality_adjusted["adjusted_value"],
        years_remaining,
        lifecycle_factors
    )

    # Calculate jurisdiction-weighted value
    jurisdiction_analysis = calculate_jurisdiction_value(
        lifecycle_adjusted["adjusted_value"],
        jurisdictions,
        jurisdiction_config
    )

    # Final value
    final_value = lifecycle_adjusted["adjusted_value"]

    return {
        "evaluation_id": evaluation_id,
        "patent_id": patent_id,
        "patent_title": patent_title,
        "industry": industry,
        "evaluation_date": evaluation_date,
        "patent_details": {
            "years_remaining": years_remaining,
            "jurisdictions": jurisdictions
        },
        "valuation_approaches": {
            "income_approach": income_valuation,
            "market_approach": market_valuation,
            "blended_base_value": round(blended_value, 2)
        },
        "strength_analysis": {
            "legal": legal_strength,
            "technical": technical_strength,
            "market": market_strength,
            "overall": overall_strength
        },
        "value_adjustments": {
            "quality_adjustment": quality_adjusted,
            "lifecycle_adjustment": lifecycle_adjusted
        },
        "jurisdiction_analysis": jurisdiction_analysis,
        "final_valuation": {
            "estimated_value": round(final_value, 2),
            "value_range": {
                "low": round(final_value * 0.7, 2),
                "mid": round(final_value, 2),
                "high": round(final_value * 1.3, 2)
            },
            "confidence_level": "MEDIUM" if overall_strength["overall_strength_score"] >= 0.5 else "LOW"
        },
        "evaluation_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = evaluate_patent_value(
        evaluation_id="PAT-2026-001",
        patent_id="US-10234567",
        patent_title="Advanced Machine Learning Algorithm for Predictive Analytics",
        industry="software",
        years_remaining=12,
        projected_revenues=[10000000, 12000000, 14000000, 16000000, 18000000],
        annual_revenue=10000000,
        annual_profit=2500000,
        legal_factors={
            "claim_breadth": 0.75,
            "prosecution_history": 0.80,
            "validity_challenges": 0.90,
            "enforceability_history": 0.85
        },
        technical_factors={
            "innovation_level": 0.85,
            "technical_scope": 0.70,
            "design_around_difficulty": 0.75,
            "citation_metrics": 0.80
        },
        market_factors={
            "market_size": 0.80,
            "market_growth": 0.85,
            "competitive_advantage": 0.75,
            "licensing_potential": 0.70
        },
        jurisdictions=["US", "EU", "Japan", "China"],
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
