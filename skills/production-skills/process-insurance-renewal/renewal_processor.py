"""
Insurance Renewal Processing Module

Implements policy renewal processing including
premium adjustments, risk reassessment, and renewal offer generation.
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


def load_renewal_config() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    policy_types_data = load_csv_as_dict("policy_types.csv")
    experience_rating_data = load_csv_as_dict("experience_rating.csv")
    loyalty_discounts_data = load_csv_as_dict("loyalty_discounts.csv")
    risk_change_factors_data = load_csv_as_dict("risk_change_factors.csv")
    market_conditions_data = load_csv_as_dict("market_conditions.csv")
    retention_risk_data = load_csv_as_dict("retention_risk.csv")
    underwriter_referral_data = load_key_value_csv("underwriter_referral.csv")
    coverage_recommendations_data = load_csv_as_dict("coverage_recommendations.csv")
    params = load_parameters()
    return {
        "policy_types": policy_types_data,
        "experience_rating": experience_rating_data,
        "loyalty_discounts": loyalty_discounts_data,
        "risk_change_factors": risk_change_factors_data,
        "market_conditions": market_conditions_data,
        "retention_risk": retention_risk_data,
        "underwriter_referral": underwriter_referral_data,
        "coverage_recommendations": coverage_recommendations_data,
        **params
    }


def calculate_loss_ratio(
    claims_history: List[Dict],
    earned_premium: float
) -> Dict[str, Any]:
    """Calculate loss ratio from claims history."""
    if earned_premium <= 0:
        return {"error": "Invalid earned premium"}

    total_incurred = sum(
        claim.get("incurred_amount", 0) for claim in claims_history
    )

    loss_ratio = total_incurred / earned_premium

    return {
        "total_claims": len(claims_history),
        "total_incurred": round(total_incurred, 2),
        "earned_premium": earned_premium,
        "loss_ratio": round(loss_ratio, 3)
    }


def determine_experience_rating(
    loss_ratio: float,
    claims_count: int,
    experience_config: Dict
) -> Dict[str, Any]:
    """Determine experience rating adjustment."""
    if claims_count == 0:
        rating = experience_config.get("no_claims", {})
        return {
            "rating_class": "NO_CLAIMS",
            "adjustment": rating.get("adjustment", -0.10),
            "description": rating.get("description", "No claims discount")
        }

    # Find applicable rating class
    for rating_class, config in experience_config.items():
        if rating_class == "no_claims":
            continue

        if "loss_ratio_max" in config:
            if loss_ratio <= config["loss_ratio_max"]:
                return {
                    "rating_class": rating_class.upper(),
                    "adjustment": config.get("adjustment", 0),
                    "loss_ratio": loss_ratio
                }
        elif "loss_ratio_min" in config:
            if loss_ratio >= config["loss_ratio_min"]:
                return {
                    "rating_class": rating_class.upper(),
                    "adjustment": config.get("adjustment", 0),
                    "loss_ratio": loss_ratio
                }

    return {
        "rating_class": "AVERAGE",
        "adjustment": 0,
        "loss_ratio": loss_ratio
    }


def calculate_loyalty_discount(
    policy_tenure_years: int,
    loyalty_config: Dict
) -> Dict[str, Any]:
    """Calculate loyalty discount based on tenure."""
    if policy_tenure_years >= 10:
        tier_config = loyalty_config.get("years_10_plus", {})
    elif policy_tenure_years >= 6:
        tier_config = loyalty_config.get("years_6_10", {})
    elif policy_tenure_years >= 3:
        tier_config = loyalty_config.get("years_3_5", {})
    else:
        tier_config = loyalty_config.get("years_1_2", {})

    return {
        "tenure_years": policy_tenure_years,
        "loyalty_tier": tier_config.get("tier", "new").upper(),
        "discount": tier_config.get("discount", 0)
    }


def evaluate_risk_changes(
    risk_changes: Dict,
    risk_factors: Dict
) -> Dict[str, Any]:
    """Evaluate risk changes and calculate adjustment."""
    adjustments = []
    total_adjustment = 0

    # Exposure increases
    exposure_increases = risk_factors.get("exposure_increase", {})
    if risk_changes.get("revenue_change_pct", 0) >= exposure_increases.get("revenue_increase", {}).get("threshold", 0.10):
        factor = exposure_increases.get("revenue_increase", {}).get("rate_factor", 0.05)
        adjustments.append({
            "factor": "revenue_increase",
            "adjustment": factor
        })
        total_adjustment += factor

    if risk_changes.get("employee_change_pct", 0) >= exposure_increases.get("employee_increase", {}).get("threshold", 0.15):
        factor = exposure_increases.get("employee_increase", {}).get("rate_factor", 0.04)
        adjustments.append({
            "factor": "employee_increase",
            "adjustment": factor
        })
        total_adjustment += factor

    if risk_changes.get("locations_added", 0) > 0:
        factor = exposure_increases.get("location_addition", {}).get("rate_factor", 0.08)
        adjustments.append({
            "factor": "location_addition",
            "adjustment": factor
        })
        total_adjustment += factor

    # Exposure decreases
    exposure_decreases = risk_factors.get("exposure_decrease", {})
    if risk_changes.get("revenue_change_pct", 0) <= -exposure_decreases.get("revenue_decrease", {}).get("threshold", 0.10):
        factor = exposure_decreases.get("revenue_decrease", {}).get("rate_factor", -0.03)
        adjustments.append({
            "factor": "revenue_decrease",
            "adjustment": factor
        })
        total_adjustment += factor

    # Risk improvements
    improvements = risk_factors.get("risk_improvements", {})
    if risk_changes.get("safety_program_implemented", False):
        credit = improvements.get("safety_program", {}).get("credit", -0.03)
        adjustments.append({
            "factor": "safety_program",
            "adjustment": credit
        })
        total_adjustment += credit

    if risk_changes.get("security_upgrade", False):
        credit = improvements.get("security_upgrade", {}).get("credit", -0.02)
        adjustments.append({
            "factor": "security_upgrade",
            "adjustment": credit
        })
        total_adjustment += credit

    return {
        "risk_adjustments": adjustments,
        "total_risk_adjustment": round(total_adjustment, 3)
    }


def apply_market_conditions(
    market_condition: str,
    market_config: Dict
) -> Dict[str, Any]:
    """Apply market condition adjustment."""
    condition = market_config.get(market_condition, market_config.get("stable", {}))

    return {
        "market_condition": market_condition.upper().replace("_", " "),
        "adjustment": condition.get("base_adjustment", 0),
        "description": condition.get("description", "")
    }


def calculate_renewal_premium(
    current_premium: float,
    base_rate_change: float,
    experience_adjustment: float,
    loyalty_discount: float,
    risk_adjustment: float,
    market_adjustment: float,
    rate_caps: Dict
) -> Dict[str, Any]:
    """Calculate renewal premium with all adjustments."""
    # Sum all adjustments
    total_adjustment = (
        base_rate_change +
        experience_adjustment +
        (-loyalty_discount) +  # Discount is negative
        risk_adjustment +
        market_adjustment
    )

    # Apply caps
    max_increase = rate_caps.get("max_rate_increase", 0.25)
    max_decrease = rate_caps.get("max_rate_decrease", 0.15)

    if total_adjustment > max_increase:
        capped_adjustment = max_increase
        cap_applied = "INCREASE_CAP"
    elif total_adjustment < -max_decrease:
        capped_adjustment = -max_decrease
        cap_applied = "DECREASE_CAP"
    else:
        capped_adjustment = total_adjustment
        cap_applied = "NONE"

    renewal_premium = current_premium * (1 + capped_adjustment)

    return {
        "current_premium": current_premium,
        "adjustments": {
            "base_rate": round(base_rate_change * 100, 1),
            "experience": round(experience_adjustment * 100, 1),
            "loyalty": round(-loyalty_discount * 100, 1),
            "risk_changes": round(risk_adjustment * 100, 1),
            "market": round(market_adjustment * 100, 1)
        },
        "total_adjustment_pct": round(total_adjustment * 100, 1),
        "capped_adjustment_pct": round(capped_adjustment * 100, 1),
        "cap_applied": cap_applied,
        "renewal_premium": round(renewal_premium, 2),
        "premium_change": round(renewal_premium - current_premium, 2)
    }


def assess_retention_risk(
    rate_change_pct: float,
    loss_ratio: float,
    policy_tenure: int,
    retention_config: Dict
) -> Dict[str, Any]:
    """Assess risk of policy non-renewal."""
    # Determine risk level based on rate increase
    if rate_change_pct >= retention_config.get("critical", {}).get("increase_threshold", 0.20):
        risk_level = "CRITICAL"
        action = retention_config.get("critical", {}).get("action", "executive_review")
    elif rate_change_pct >= retention_config.get("high", {}).get("increase_threshold", 0.15):
        risk_level = "HIGH"
        action = retention_config.get("high", {}).get("action", "retention_offer")
    elif rate_change_pct >= retention_config.get("moderate", {}).get("increase_threshold", 0.10):
        risk_level = "MODERATE"
        action = retention_config.get("moderate", {}).get("action", "review_pricing")
    else:
        risk_level = "LOW"
        action = retention_config.get("low", {}).get("action", "standard_renewal")

    # Adjust for tenure (longer tenure = lower risk)
    if policy_tenure >= 10:
        risk_adjustment = "Reduced risk due to long tenure"
    elif policy_tenure >= 5:
        risk_adjustment = "Moderate tenure mitigates some risk"
    else:
        risk_adjustment = "Short tenure increases sensitivity"

    return {
        "risk_level": risk_level,
        "recommended_action": action.replace("_", " ").title(),
        "tenure_factor": risk_adjustment,
        "rate_increase_pct": round(rate_change_pct * 100, 1)
    }


def check_underwriter_referral(
    premium_data: Dict,
    loss_data: Dict,
    claims_history: List[Dict],
    referral_config: Dict
) -> Dict[str, Any]:
    """Check if renewal requires underwriter referral."""
    referral_reasons = []

    rate_increase = premium_data.get("capped_adjustment_pct", 0) / 100
    if rate_increase >= referral_config.get("rate_increase_threshold", 0.20):
        referral_reasons.append("Rate increase exceeds threshold")

    loss_ratio = loss_data.get("loss_ratio", 0)
    if loss_ratio >= referral_config.get("loss_ratio_threshold", 0.80):
        referral_reasons.append("Loss ratio exceeds threshold")

    large_claim_threshold = referral_config.get("large_claim_threshold", 100000)
    large_claims = [c for c in claims_history if c.get("incurred_amount", 0) >= large_claim_threshold]
    if large_claims:
        referral_reasons.append(f"{len(large_claims)} large claim(s) in period")

    return {
        "referral_required": len(referral_reasons) > 0,
        "referral_reasons": referral_reasons,
        "auto_renew_eligible": len(referral_reasons) == 0
    }


def process_insurance_renewal(
    renewal_id: str,
    policy_id: str,
    policy_type: str,
    current_premium: float,
    policy_tenure_years: int,
    claims_history: List[Dict],
    risk_changes: Dict,
    market_condition: str,
    renewal_date: str
) -> Dict[str, Any]:
    """
    Process insurance renewal.

    Business Rules:
    1. Calculate loss ratio and experience rating
    2. Apply loyalty discounts
    3. Evaluate risk changes
    4. Apply market conditions
    5. Assess retention risk

    Args:
        renewal_id: Renewal identifier
        policy_id: Policy identifier
        policy_type: Type of insurance
        current_premium: Current policy premium
        policy_tenure_years: Years as policyholder
        claims_history: Claims in current period
        risk_changes: Changes to risk profile
        market_condition: Current market conditions
        renewal_date: Effective renewal date

    Returns:
        Renewal processing results
    """
    config = load_renewal_config()
    policy_config = config.get("policy_types", {}).get(policy_type, {})
    experience_config = config.get("experience_rating", {})
    loyalty_config = config.get("loyalty_discounts", {})
    risk_factors = config.get("risk_change_factors", {})
    market_config = config.get("market_conditions", {})
    retention_config = config.get("retention_risk", {})
    referral_config = config.get("underwriter_referral", {})

    # Calculate loss ratio
    loss_data = calculate_loss_ratio(claims_history, current_premium)

    # Determine experience rating
    experience = determine_experience_rating(
        loss_data.get("loss_ratio", 0),
        loss_data.get("total_claims", 0),
        experience_config
    )

    # Calculate loyalty discount
    loyalty = calculate_loyalty_discount(policy_tenure_years, loyalty_config)

    # Evaluate risk changes
    risk_eval = evaluate_risk_changes(risk_changes, risk_factors)

    # Apply market conditions
    market = apply_market_conditions(market_condition, market_config)

    # Calculate renewal premium
    rate_caps = {
        "max_rate_increase": policy_config.get("max_rate_increase", 0.25),
        "max_rate_decrease": policy_config.get("max_rate_decrease", 0.15)
    }

    premium = calculate_renewal_premium(
        current_premium,
        policy_config.get("base_rate_change", 0.03),
        experience["adjustment"],
        loyalty["discount"],
        risk_eval["total_risk_adjustment"],
        market["adjustment"],
        rate_caps
    )

    # Assess retention risk
    retention = assess_retention_risk(
        premium["capped_adjustment_pct"] / 100,
        loss_data.get("loss_ratio", 0),
        policy_tenure_years,
        retention_config
    )

    # Check underwriter referral
    referral = check_underwriter_referral(
        premium,
        loss_data,
        claims_history,
        referral_config
    )

    return {
        "renewal_id": renewal_id,
        "policy_id": policy_id,
        "policy_type": policy_type,
        "renewal_date": renewal_date,
        "loss_analysis": loss_data,
        "experience_rating": experience,
        "loyalty_assessment": loyalty,
        "risk_evaluation": risk_eval,
        "market_adjustment": market,
        "premium_calculation": premium,
        "retention_assessment": retention,
        "underwriter_referral": referral,
        "renewal_status": "PENDING_REVIEW" if referral["referral_required"] else "AUTO_APPROVED"
    }


if __name__ == "__main__":
    import json
    result = process_insurance_renewal(
        renewal_id="REN-2026-001234",
        policy_id="POL-2020-005678",
        policy_type="commercial_property",
        current_premium=125000,
        policy_tenure_years=6,
        claims_history=[
            {"claim_id": "CLM-001", "incurred_amount": 35000, "status": "closed"},
            {"claim_id": "CLM-002", "incurred_amount": 12000, "status": "closed"}
        ],
        risk_changes={
            "revenue_change_pct": 0.15,
            "employee_change_pct": 0.08,
            "locations_added": 0,
            "safety_program_implemented": True,
            "security_upgrade": False
        },
        market_condition="firming",
        renewal_date="2026-04-01"
    )
    print(json.dumps(result, indent=2))
