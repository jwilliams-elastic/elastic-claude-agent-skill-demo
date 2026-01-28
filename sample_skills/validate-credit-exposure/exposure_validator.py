"""
Credit Exposure Validation Module

Implements credit exposure validation against
counterparty limits, concentration thresholds, and regulatory requirements.
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


def load_credit_limits() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    exposure_categories_data = load_csv_as_dict("exposure_categories.csv")
    counterparty_limits_data = load_csv_as_dict("counterparty_limits.csv")
    concentration_thresholds_data = load_key_value_csv("concentration_thresholds.csv")
    risk_weights_data = load_key_value_csv("risk_weights.csv")
    netting_agreements_data = load_csv_as_dict("netting_agreements.csv")
    collateral_haircuts_data = load_key_value_csv("collateral_haircuts.csv")
    regulatory_requirements_data = load_key_value_csv("regulatory_requirements.csv")
    params = load_parameters()
    return {
        "exposure_categories": exposure_categories_data,
        "counterparty_limits": counterparty_limits_data,
        "concentration_thresholds": concentration_thresholds_data,
        "risk_weights": risk_weights_data,
        "netting_agreements": netting_agreements_data,
        "collateral_haircuts": collateral_haircuts_data,
        "regulatory_requirements": regulatory_requirements_data,
        **params
    }


def calculate_gross_exposure(
    positions: List[Dict]
) -> Dict[str, float]:
    """Calculate gross exposure by category."""
    exposure_by_category = {}

    for position in positions:
        category = position.get("category", "other")
        amount = position.get("notional", 0)

        exposure_by_category[category] = exposure_by_category.get(category, 0) + amount

    return exposure_by_category


def apply_netting(
    gross_exposure: float,
    netting_agreement: str,
    netting_config: Dict
) -> Dict[str, Any]:
    """Apply netting benefit to exposure."""
    agreement_config = netting_config.get(netting_agreement, netting_config.get("none", {}))
    netting_benefit = agreement_config.get("netting_benefit", 0)

    net_exposure = gross_exposure * (1 - netting_benefit)

    return {
        "gross_exposure": gross_exposure,
        "netting_agreement": netting_agreement,
        "netting_benefit_pct": netting_benefit * 100,
        "net_exposure": round(net_exposure, 2)
    }


def apply_collateral_haircut(
    collateral: List[Dict],
    haircuts: Dict
) -> Dict[str, Any]:
    """Calculate collateral value after haircuts."""
    total_collateral = 0
    haircut_details = []

    for item in collateral:
        coll_type = item.get("type", "other")
        value = item.get("value", 0)
        haircut_rate = haircuts.get(coll_type, haircuts.get("other", 0.25))

        adjusted_value = value * (1 - haircut_rate)
        total_collateral += adjusted_value

        haircut_details.append({
            "type": coll_type,
            "original_value": value,
            "haircut_rate": haircut_rate,
            "adjusted_value": round(adjusted_value, 2)
        })

    return {
        "total_adjusted_collateral": round(total_collateral, 2),
        "collateral_details": haircut_details
    }


def validate_single_name_limit(
    exposure: float,
    capital: float,
    rating: str,
    limits: Dict
) -> Dict[str, Any]:
    """Validate single counterparty exposure limit."""
    rating_limits = limits.get(rating, limits.get("B", {}))
    limit_pct = rating_limits.get("single_name_pct", 0.05)
    limit_amount = capital * limit_pct

    utilization = (exposure / limit_amount * 100) if limit_amount > 0 else 100

    return {
        "limit_type": "single_name",
        "exposure": round(exposure, 2),
        "limit": round(limit_amount, 2),
        "utilization_pct": round(utilization, 1),
        "status": "BREACH" if exposure > limit_amount else "WARNING" if utilization > 80 else "OK"
    }


def validate_concentration(
    exposures: Dict[str, float],
    total_portfolio: float,
    thresholds: Dict,
    concentration_type: str
) -> List[Dict]:
    """Validate concentration limits."""
    results = []
    warning_threshold = thresholds.get(f"{concentration_type}_warning", 0.20)
    limit_threshold = thresholds.get(f"{concentration_type}_limit", 0.25)

    for name, exposure in exposures.items():
        concentration = exposure / total_portfolio if total_portfolio > 0 else 0

        if concentration > limit_threshold:
            status = "BREACH"
        elif concentration > warning_threshold:
            status = "WARNING"
        else:
            status = "OK"

        results.append({
            "name": name,
            "exposure": round(exposure, 2),
            "concentration_pct": round(concentration * 100, 1),
            "limit_pct": round(limit_threshold * 100, 1),
            "status": status
        })

    return sorted(results, key=lambda x: x["concentration_pct"], reverse=True)


def calculate_risk_weighted_exposure(
    exposure: float,
    asset_class: str,
    risk_weights: Dict
) -> Dict[str, Any]:
    """Calculate risk-weighted exposure."""
    risk_weight = risk_weights.get(asset_class, 1.0)
    rwa = exposure * risk_weight

    return {
        "exposure": round(exposure, 2),
        "asset_class": asset_class,
        "risk_weight": risk_weight,
        "risk_weighted_exposure": round(rwa, 2)
    }


def check_regulatory_thresholds(
    net_exposure: float,
    capital: float,
    regulatory_config: Dict
) -> Dict[str, Any]:
    """Check regulatory reporting and limit thresholds."""
    large_exposure_threshold = regulatory_config.get("large_exposure_threshold", 0.10)
    reporting_threshold = regulatory_config.get("reporting_threshold", 0.05)

    exposure_ratio = net_exposure / capital if capital > 0 else 0

    flags = []
    if exposure_ratio >= large_exposure_threshold:
        flags.append("LARGE_EXPOSURE_LIMIT")
    if exposure_ratio >= reporting_threshold:
        flags.append("REPORTING_REQUIRED")

    return {
        "exposure_to_capital_ratio": round(exposure_ratio * 100, 2),
        "large_exposure_threshold_pct": large_exposure_threshold * 100,
        "reporting_threshold_pct": reporting_threshold * 100,
        "regulatory_flags": flags,
        "capital_charge": round(net_exposure * regulatory_config.get("capital_charge_rate", 0.08), 2)
    }


def validate_credit_exposure(
    counterparty_id: str,
    positions: List[Dict],
    collateral: List[Dict],
    counterparty_rating: str,
    netting_agreement: str,
    sector: str,
    country: str,
    institution_capital: float,
    total_portfolio_exposure: float,
    sector_exposures: Dict[str, float],
    country_exposures: Dict[str, float],
    validation_date: str
) -> Dict[str, Any]:
    """
    Validate credit exposure against limits.

    Business Rules:
    1. Single-name exposure limit validation
    2. Concentration risk assessment
    3. Netting and collateral adjustments
    4. Regulatory threshold monitoring

    Args:
        counterparty_id: Counterparty identifier
        positions: List of positions with counterparty
        collateral: Collateral held
        counterparty_rating: Credit rating
        netting_agreement: Type of netting agreement
        sector: Counterparty sector
        country: Counterparty country
        institution_capital: Institution's capital base
        total_portfolio_exposure: Total portfolio exposure
        sector_exposures: Exposure by sector
        country_exposures: Exposure by country
        validation_date: Validation date

    Returns:
        Credit exposure validation results
    """
    limits = load_credit_limits()

    # Calculate gross exposure
    gross_by_category = calculate_gross_exposure(positions)
    total_gross = sum(gross_by_category.values())

    # Apply netting
    netting_result = apply_netting(
        total_gross,
        netting_agreement,
        limits.get("netting_agreements", {})
    )

    # Apply collateral
    collateral_result = apply_collateral_haircut(
        collateral,
        limits.get("collateral_haircuts", {})
    )

    # Net exposure after collateral
    net_exposure = max(0, netting_result["net_exposure"] - collateral_result["total_adjusted_collateral"])

    # Validate single name limit
    single_name_check = validate_single_name_limit(
        net_exposure,
        institution_capital,
        counterparty_rating,
        limits.get("counterparty_limits", {})
    )

    # Validate sector concentration
    sector_concentration = validate_concentration(
        sector_exposures,
        total_portfolio_exposure,
        limits.get("concentration_thresholds", {}),
        "sector"
    )

    # Validate geographic concentration
    country_concentration = validate_concentration(
        country_exposures,
        total_portfolio_exposure,
        limits.get("concentration_thresholds", {}),
        "geographic"
    )

    # Check regulatory thresholds
    regulatory_check = check_regulatory_thresholds(
        net_exposure,
        institution_capital,
        limits.get("regulatory_requirements", {})
    )

    # Determine overall status
    breaches = []
    if single_name_check["status"] == "BREACH":
        breaches.append("single_name_limit")
    if any(s["status"] == "BREACH" for s in sector_concentration):
        breaches.append("sector_concentration")
    if any(c["status"] == "BREACH" for c in country_concentration):
        breaches.append("country_concentration")

    overall_status = "BREACH" if breaches else "APPROVED"

    return {
        "counterparty_id": counterparty_id,
        "validation_date": validation_date,
        "counterparty_rating": counterparty_rating,
        "exposure_summary": {
            "gross_exposure": round(total_gross, 2),
            "net_exposure_after_netting": netting_result["net_exposure"],
            "collateral_value": collateral_result["total_adjusted_collateral"],
            "final_net_exposure": round(net_exposure, 2)
        },
        "netting_details": netting_result,
        "collateral_details": collateral_result,
        "limit_checks": {
            "single_name": single_name_check,
            "sector_concentration": sector_concentration[:5],
            "country_concentration": country_concentration[:5]
        },
        "regulatory_assessment": regulatory_check,
        "overall_status": overall_status,
        "breaches": breaches
    }


if __name__ == "__main__":
    import json
    result = validate_credit_exposure(
        counterparty_id="CP-001",
        positions=[
            {"category": "trading", "notional": 5000000},
            {"category": "lending", "notional": 10000000},
            {"category": "derivatives", "notional": 3000000}
        ],
        collateral=[
            {"type": "cash", "value": 2000000},
            {"type": "government_bonds", "value": 1000000}
        ],
        counterparty_rating="A",
        netting_agreement="isda_master",
        sector="financial",
        country="US",
        institution_capital=100000000,
        total_portfolio_exposure=500000000,
        sector_exposures={"financial": 100000000, "technology": 80000000},
        country_exposures={"US": 200000000, "UK": 100000000},
        validation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
