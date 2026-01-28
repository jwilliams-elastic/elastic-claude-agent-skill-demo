"""
Private Equity Deal Screening Module

Implements investment criteria matching and preliminary due diligence
scoring for deal flow management.
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


def load_fund_criteria() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    funds_data = load_csv_as_dict("funds.csv")
    params = load_parameters()
    return {
        "funds": funds_data,
        **params
    }


def check_size_fit(
    deal_size: float,
    min_size: float,
    max_size: float,
    sweet_spot: Dict
) -> Dict[str, Any]:
    """Check deal size against fund parameters."""
    if deal_size < min_size:
        return {"fits": False, "reason": "Below minimum", "score": 0}
    elif deal_size > max_size:
        return {"fits": False, "reason": "Above maximum", "score": 0}

    sweet_min = sweet_spot.get("min", min_size)
    sweet_max = sweet_spot.get("max", max_size)

    if sweet_min <= deal_size <= sweet_max:
        return {"fits": True, "reason": "In sweet spot", "score": 100}
    else:
        return {"fits": True, "reason": "In range but outside sweet spot", "score": 70}


def evaluate_financials(
    financials: Dict,
    criteria: Dict
) -> Dict[str, Any]:
    """Evaluate financial metrics against criteria."""
    score = 0
    findings = []

    revenue = financials.get("revenue", 0)
    ebitda = financials.get("ebitda", 0)
    growth_rate = financials.get("growth_rate", 0)

    # Revenue check
    min_revenue = criteria.get("min_revenue", 0)
    if revenue >= min_revenue:
        score += 25
        findings.append({"metric": "revenue", "status": "meets_criteria"})
    else:
        findings.append({"metric": "revenue", "status": "below_minimum", "gap": min_revenue - revenue})

    # EBITDA margin check
    if revenue > 0:
        ebitda_margin = ebitda / revenue
        min_margin = criteria.get("min_ebitda_margin", 0)
        if ebitda_margin >= min_margin:
            score += 25
            findings.append({"metric": "ebitda_margin", "status": "meets_criteria", "value": ebitda_margin})
        else:
            findings.append({"metric": "ebitda_margin", "status": "below_minimum", "value": ebitda_margin})

    # Growth rate check
    min_growth = criteria.get("min_growth_rate", 0)
    if growth_rate >= min_growth:
        score += 25
        findings.append({"metric": "growth_rate", "status": "meets_criteria"})
    elif growth_rate >= min_growth * 0.7:
        score += 15
        findings.append({"metric": "growth_rate", "status": "marginally_below"})
    else:
        findings.append({"metric": "growth_rate", "status": "significantly_below"})

    return {
        "score": score,
        "findings": findings,
        "metrics_analyzed": {
            "revenue": revenue,
            "ebitda": ebitda,
            "ebitda_margin": ebitda / revenue if revenue > 0 else 0,
            "growth_rate": growth_rate
        }
    }


def assess_value_creation(
    company_profile: Dict,
    financials: Dict,
    management_quality: int
) -> Dict[str, Any]:
    """Assess value creation potential."""
    opportunities = []
    total_potential = 0

    # Operational improvement
    ebitda_margin = financials.get("ebitda", 0) / financials.get("revenue", 1)
    if ebitda_margin < 0.20:
        margin_uplift = (0.20 - ebitda_margin) * financials.get("revenue", 0)
        opportunities.append({
            "type": "margin_expansion",
            "potential_value": margin_uplift,
            "confidence": "medium"
        })
        total_potential += margin_uplift

    # Growth acceleration
    current_growth = financials.get("growth_rate", 0)
    if current_growth < 0.30:
        opportunities.append({
            "type": "growth_acceleration",
            "description": "Potential to increase organic growth",
            "confidence": "medium"
        })

    # Management upgrade potential
    if management_quality < 7:
        opportunities.append({
            "type": "management_upgrade",
            "description": "Opportunity to strengthen management team",
            "confidence": "high" if management_quality < 5 else "medium"
        })

    # Technology/digital
    employees = company_profile.get("employees", 0)
    if employees > 100:
        opportunities.append({
            "type": "digital_transformation",
            "description": "Potential for technology-enabled efficiency",
            "confidence": "medium"
        })

    return {
        "opportunities": opportunities,
        "total_identified_potential": total_potential,
        "value_creation_score": min(100, len(opportunities) * 25)
    }


def assess_risks(
    company_profile: Dict,
    financials: Dict,
    sector: str,
    geography: str
) -> Dict[str, Any]:
    """Assess investment risks."""
    risks = []
    risk_score = 100  # Start with perfect, deduct for risks

    # Customer concentration
    # Simplified - would need actual data
    risks.append({
        "type": "customer_concentration",
        "severity": "medium",
        "mitigation": "Verify top 10 customer concentration"
    })
    risk_score -= 10

    # Market risk by sector
    high_risk_sectors = ["retail", "media", "energy"]
    if sector in high_risk_sectors:
        risks.append({
            "type": "sector_risk",
            "severity": "high",
            "description": f"Elevated risk in {sector} sector"
        })
        risk_score -= 20

    # Geographic risk
    high_risk_geo = ["emerging_markets", "latam"]
    if geography in high_risk_geo:
        risks.append({
            "type": "geographic_risk",
            "severity": "medium",
            "description": "Emerging market operational risks"
        })
        risk_score -= 15

    # Financial leverage
    # Would need actual debt data
    risks.append({
        "type": "leverage_capacity",
        "severity": "low",
        "description": "Assess debt capacity and refinancing risk"
    })

    return {
        "identified_risks": risks,
        "risk_score": max(0, risk_score),
        "overall_risk_level": "high" if risk_score < 50 else "medium" if risk_score < 75 else "low"
    }


def screen_deal(
    deal_id: str,
    company_profile: Dict,
    financials: Dict,
    sector: str,
    geography: str,
    deal_size: float,
    fund_id: str,
    management_quality: int
) -> Dict[str, Any]:
    """
    Screen private equity deal opportunity.

    Business Rules:
    1. Investment criteria matching
    2. Value creation assessment
    3. Risk factor evaluation
    4. Portfolio concentration limits

    Args:
        deal_id: Deal identifier
        company_profile: Target company details
        financials: Financial metrics
        sector: Industry sector
        geography: Geography
        deal_size: Enterprise value
        fund_id: Target fund
        management_quality: Management score

    Returns:
        Deal screening results
    """
    criteria = load_fund_criteria()

    fund = criteria["funds"].get(fund_id, criteria["funds"]["default"])

    # Check size fit
    size_fit = check_size_fit(
        deal_size,
        fund["size_range"]["min"],
        fund["size_range"]["max"],
        fund["size_range"]["sweet_spot"]
    )

    # Check sector fit
    sector_fit = sector in fund["target_sectors"]
    sector_score = 100 if sector_fit else 0

    # Check geography fit
    geo_fit = geography in fund["target_geographies"]
    geo_score = 100 if geo_fit else 0

    # Evaluate financials
    financial_eval = evaluate_financials(financials, fund["financial_criteria"])

    # Assess value creation
    value_creation = assess_value_creation(company_profile, financials, management_quality)

    # Assess risks
    risk_assessment = assess_risks(company_profile, financials, sector, geography)

    # Calculate overall criteria match score
    weights = {
        "size": 0.20,
        "sector": 0.20,
        "geography": 0.15,
        "financials": 0.25,
        "value_creation": 0.20
    }

    criteria_match_score = (
        size_fit["score"] * weights["size"] +
        sector_score * weights["sector"] +
        geo_score * weights["geography"] +
        financial_eval["score"] * weights["financials"] +
        value_creation["value_creation_score"] * weights["value_creation"]
    )

    # Determine screening status
    if not size_fit["fits"] or not sector_fit or not geo_fit:
        screening_status = "PASS"
        recommendation = "Does not meet fund investment criteria"
    elif criteria_match_score >= 75 and risk_assessment["risk_score"] >= 50:
        screening_status = "PURSUE"
        recommendation = "Strong fit - recommend detailed due diligence"
    elif criteria_match_score >= 50:
        screening_status = "REVIEW"
        recommendation = "Potential fit - requires further analysis"
    else:
        screening_status = "PASS"
        recommendation = "Limited strategic fit"

    return {
        "deal_id": deal_id,
        "company_name": company_profile.get("name"),
        "screening_status": screening_status,
        "criteria_match_score": round(criteria_match_score, 1),
        "recommendation": recommendation,
        "criteria_analysis": {
            "size_fit": size_fit,
            "sector_fit": sector_fit,
            "geography_fit": geo_fit,
            "financial_evaluation": financial_eval
        },
        "value_creation_potential": value_creation,
        "risk_assessment": risk_assessment,
        "deal_size": deal_size,
        "sector": sector,
        "geography": geography,
        "fund_id": fund_id
    }


if __name__ == "__main__":
    import json
    result = screen_deal(
        deal_id="DEAL-2024-001",
        company_profile={"name": "TechCo Inc", "employees": 500, "founded": 2015},
        financials={"revenue": 50000000, "ebitda": 8000000, "growth_rate": 0.25},
        sector="technology",
        geography="north_america",
        deal_size=100000000,
        fund_id="FUND-GROWTH-I",
        management_quality=8
    )
    print(json.dumps(result, indent=2))
