"""
Insurance Premium Calculation Module

Implements actuarial rating algorithms for insurance premium
determination across various product lines.
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


def load_rating_tables() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    products_data = load_csv_as_dict("products.csv")
    tier_rules_data = load_csv_as_dict("tier_rules.csv")
    params = load_parameters()
    return {
        "products": products_data,
        "tier_rules": tier_rules_data,
        **params
    }


def get_base_rate(
    policy_type: str,
    territory: str,
    rates: Dict
) -> float:
    """Get base rate for policy type and territory."""
    product_rates = rates.get(policy_type, {})
    territory_rates = product_rates.get("territory_rates", {})
    return territory_rates.get(territory, product_rates.get("default_rate", 0.01))


def apply_rating_factors(
    base_premium: float,
    risk_characteristics: Dict,
    factors: Dict
) -> Dict[str, Any]:
    """Apply rating factors to base premium."""
    current_premium = base_premium
    applied_factors = {}

    for char_name, char_value in risk_characteristics.items():
        factor_table = factors.get(char_name, {})
        factor = factor_table.get(str(char_value), factor_table.get(char_value, 1.0))

        if isinstance(factor, (int, float)):
            applied_factors[char_name] = {
                "value": char_value,
                "factor": factor,
                "premium_impact": current_premium * (factor - 1)
            }
            current_premium *= factor

    return {
        "adjusted_premium": round(current_premium, 2),
        "applied_factors": applied_factors
    }


def calculate_experience_mod(
    loss_history: List[Dict],
    expected_losses: float,
    credibility: float = 0.5
) -> float:
    """Calculate experience modification factor."""
    if not loss_history:
        return 1.0

    actual_losses = sum(l.get("losses", 0) for l in loss_history)
    years = len(loss_history)

    if years == 0 or expected_losses <= 0:
        return 1.0

    annual_actual = actual_losses / years
    annual_expected = expected_losses

    # Credibility-weighted experience mod
    actual_ratio = annual_actual / annual_expected
    exp_mod = credibility * actual_ratio + (1 - credibility) * 1.0

    # Cap at reasonable bounds
    exp_mod = max(0.7, min(1.5, exp_mod))

    return round(exp_mod, 3)


def determine_tier(
    risk_characteristics: Dict,
    exp_mod: float,
    tier_rules: Dict
) -> str:
    """Determine risk tier placement."""
    score = 100

    # Adjust for characteristics
    if risk_characteristics.get("construction") == "frame":
        score -= 20
    if risk_characteristics.get("protection_class", 10) > 7:
        score -= 15

    # Adjust for experience
    if exp_mod > 1.2:
        score -= 25
    elif exp_mod > 1.0:
        score -= 10
    elif exp_mod < 0.9:
        score += 10

    if score >= 85:
        return "preferred"
    elif score >= 70:
        return "standard"
    elif score >= 50:
        return "substandard"
    else:
        return "high_risk"


def calculate_premium(
    policy_type: str,
    coverage_limits: Dict,
    risk_characteristics: Dict,
    territory: str,
    effective_date: str,
    loss_history: List[Dict]
) -> Dict[str, Any]:
    """
    Calculate insurance premium.

    Business Rules:
    1. Base rate by territory and class
    2. Multiplicative rating factors
    3. Experience modification
    4. Minimum premium enforcement

    Args:
        policy_type: Insurance product
        coverage_limits: Coverage amounts
        risk_characteristics: Risk profile
        territory: Rating territory
        effective_date: Policy effective date
        loss_history: Loss experience

    Returns:
        Premium calculation results
    """
    tables = load_rating_tables()

    product_config = tables["products"].get(policy_type, tables["products"]["default"])

    # Get base rate
    base_rate = get_base_rate(policy_type, territory, tables["products"])

    # Calculate exposure base
    primary_coverage = coverage_limits.get(
        product_config.get("primary_coverage", "building"),
        coverage_limits.get("limit", 100000)
    )
    exposure_base = primary_coverage / 1000

    # Calculate base premium
    base_premium = exposure_base * base_rate

    # Apply rating factors
    factor_result = apply_rating_factors(
        base_premium,
        risk_characteristics,
        product_config.get("rating_factors", {})
    )

    # Calculate experience modification
    expected_losses = base_premium * product_config.get("expected_loss_ratio", 0.6)
    exp_mod = calculate_experience_mod(
        loss_history,
        expected_losses,
        product_config.get("credibility", 0.5)
    )

    # Apply experience mod
    rated_premium = factor_result["adjusted_premium"] * exp_mod

    # Determine tier
    tier = determine_tier(
        risk_characteristics,
        exp_mod,
        tables.get("tier_rules", {})
    )

    # Apply tier adjustment
    tier_factors = {"preferred": 0.9, "standard": 1.0, "substandard": 1.15, "high_risk": 1.35}
    tier_factor = tier_factors.get(tier, 1.0)
    tier_adjusted_premium = rated_premium * tier_factor

    # Apply deductible credit
    deductible = coverage_limits.get("deductible", 1000)
    deductible_credits = product_config.get("deductible_credits", {})
    deductible_factor = 1.0
    for threshold, credit in sorted(deductible_credits.items(), key=lambda x: int(x[0])):
        if deductible >= int(threshold):
            deductible_factor = credit

    final_premium = tier_adjusted_premium * deductible_factor

    # Enforce minimum premium
    minimum_premium = product_config.get("minimum_premium", 250)
    total_premium = max(final_premium, minimum_premium)

    # Premium breakdown
    premium_breakdown = {
        "base_premium": round(base_premium, 2),
        "factor_adjusted": factor_result["adjusted_premium"],
        "experience_adjusted": round(rated_premium, 2),
        "tier_adjusted": round(tier_adjusted_premium, 2),
        "deductible_adjusted": round(final_premium, 2),
        "total_premium": round(total_premium, 2)
    }

    return {
        "total_premium": round(total_premium, 2),
        "premium_breakdown": premium_breakdown,
        "rating_factors": factor_result["applied_factors"],
        "experience_mod": exp_mod,
        "tier_placement": tier,
        "tier_factor": tier_factor,
        "deductible_factor": deductible_factor,
        "policy_type": policy_type,
        "territory": territory,
        "effective_date": effective_date
    }


if __name__ == "__main__":
    import json
    result = calculate_premium(
        policy_type="commercial_property",
        coverage_limits={"building": 1000000, "contents": 500000, "deductible": 5000},
        risk_characteristics={"construction": "fire_resistive", "occupancy": "office", "protection_class": 3},
        territory="NY-001",
        effective_date="2026-03-01",
        loss_history=[{"year": 2024, "losses": 15000}, {"year": 2025, "losses": 0}]
    )
    print(json.dumps(result, indent=2))
