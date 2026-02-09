"""
Rebate Calculation Processing Module

Implements rebate calculation including
volume tiers, growth incentives, and settlement processing.
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


def load_rebate_programs() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    rebate_types_data = load_csv_as_dict("rebate_types.csv")
    volume_tiers_data = load_csv_as_dict("volume_tiers.csv")
    growth_tiers_data = load_csv_as_dict("growth_tiers.csv")
    calculation_rules_data = load_csv_as_dict("calculation_rules.csv")
    eligibility_requirements_data = load_key_value_csv("eligibility_requirements.csv")
    accrual_methods_data = load_csv_as_dict("accrual_methods.csv")
    settlement_options_data = load_csv_as_dict("settlement_options.csv")
    audit_requirements_data = load_key_value_csv("audit_requirements.csv")
    params = load_parameters()
    return {
        "rebate_types": rebate_types_data,
        "volume_tiers": volume_tiers_data,
        "growth_tiers": growth_tiers_data,
        "calculation_rules": calculation_rules_data,
        "eligibility_requirements": eligibility_requirements_data,
        "accrual_methods": accrual_methods_data,
        "settlement_options": settlement_options_data,
        "audit_requirements": audit_requirements_data,
        **params
    }


def check_eligibility(
    customer_data: Dict,
    requirements: Dict
) -> Dict[str, Any]:
    """Check customer rebate eligibility."""
    checks = []
    all_passed = True

    # Minimum spend check
    min_spend = requirements.get("minimum_spend", 0)
    actual_spend = customer_data.get("total_spend", 0)
    spend_check = actual_spend >= min_spend
    checks.append({
        "requirement": "minimum_spend",
        "required": min_spend,
        "actual": actual_spend,
        "passed": spend_check
    })
    if not spend_check:
        all_passed = False

    # Agreement status
    required_status = requirements.get("agreement_status", "active")
    actual_status = customer_data.get("agreement_status", "")
    status_check = actual_status == required_status
    checks.append({
        "requirement": "agreement_status",
        "required": required_status,
        "actual": actual_status,
        "passed": status_check
    })
    if not status_check:
        all_passed = False

    # Payment status
    required_payment = requirements.get("payment_status", "current")
    actual_payment = customer_data.get("payment_status", "")
    payment_check = actual_payment == required_payment
    checks.append({
        "requirement": "payment_status",
        "required": required_payment,
        "actual": actual_payment,
        "passed": payment_check
    })
    if not payment_check:
        all_passed = False

    # Compliance score
    min_compliance = requirements.get("compliance_score_min", 0)
    actual_compliance = customer_data.get("compliance_score", 0)
    compliance_check = actual_compliance >= min_compliance
    checks.append({
        "requirement": "compliance_score",
        "required": min_compliance,
        "actual": actual_compliance,
        "passed": compliance_check
    })
    if not compliance_check:
        all_passed = False

    return {
        "eligible": all_passed,
        "checks": checks,
        "failed_count": sum(1 for c in checks if not c["passed"])
    }


def calculate_volume_rebate(
    total_volume: float,
    volume_tiers: Dict,
    calculation_method: str = "retroactive"
) -> Dict[str, Any]:
    """Calculate volume-based rebate."""
    tier_calculations = []
    total_rebate = 0

    # Sort tiers by min volume
    sorted_tiers = sorted(
        volume_tiers.items(),
        key=lambda x: x[1].get("min_volume", 0)
    )

    if calculation_method == "retroactive":
        # Find highest applicable tier
        applicable_tier = None
        for tier_name, tier_config in sorted_tiers:
            min_vol = tier_config.get("min_volume", 0)
            max_vol = tier_config.get("max_volume")

            if total_volume >= min_vol:
                if max_vol is None or total_volume <= max_vol:
                    applicable_tier = (tier_name, tier_config)
                elif total_volume > max_vol:
                    continue

        if applicable_tier:
            tier_name, tier_config = applicable_tier
            rebate_pct = tier_config.get("rebate_pct", 0)
            rebate_amount = total_volume * rebate_pct
            total_rebate = rebate_amount

            tier_calculations.append({
                "tier": tier_name,
                "volume": total_volume,
                "rate": rebate_pct,
                "rebate": round(rebate_amount, 2)
            })

    else:  # incremental
        remaining_volume = total_volume

        for tier_name, tier_config in sorted_tiers:
            min_vol = tier_config.get("min_volume", 0)
            max_vol = tier_config.get("max_volume")
            rebate_pct = tier_config.get("rebate_pct", 0)

            if remaining_volume <= 0:
                break

            tier_volume = 0
            if max_vol is None:
                tier_volume = max(0, remaining_volume - min_vol)
            else:
                tier_range = max_vol - min_vol
                tier_volume = min(tier_range, max(0, remaining_volume - min_vol))

            if tier_volume > 0:
                tier_rebate = tier_volume * rebate_pct
                total_rebate += tier_rebate

                tier_calculations.append({
                    "tier": tier_name,
                    "volume_in_tier": round(tier_volume, 2),
                    "rate": rebate_pct,
                    "rebate": round(tier_rebate, 2)
                })

            remaining_volume = min_vol

    return {
        "rebate_type": "volume_based",
        "calculation_method": calculation_method,
        "total_volume": total_volume,
        "tier_breakdown": tier_calculations,
        "total_rebate": round(total_rebate, 2),
        "effective_rate": round(total_rebate / total_volume, 4) if total_volume > 0 else 0
    }


def calculate_growth_rebate(
    current_period_volume: float,
    prior_period_volume: float,
    growth_tiers: Dict
) -> Dict[str, Any]:
    """Calculate growth-based rebate."""
    if prior_period_volume <= 0:
        return {
            "rebate_type": "growth_based",
            "error": "No prior period volume for comparison"
        }

    growth_pct = (current_period_volume - prior_period_volume) / prior_period_volume

    # Find applicable tier
    applicable_tier = None
    sorted_tiers = sorted(
        growth_tiers.items(),
        key=lambda x: x[1].get("min_growth_pct", 0),
        reverse=True
    )

    for tier_name, tier_config in sorted_tiers:
        min_growth = tier_config.get("min_growth_pct", 0)
        max_growth = tier_config.get("max_growth_pct")

        if growth_pct >= min_growth:
            if max_growth is None or growth_pct < max_growth:
                applicable_tier = (tier_name, tier_config)
                break

    if applicable_tier:
        tier_name, tier_config = applicable_tier
        rebate_pct = tier_config.get("rebate_pct", 0)
        rebate_amount = current_period_volume * rebate_pct

        return {
            "rebate_type": "growth_based",
            "current_volume": current_period_volume,
            "prior_volume": prior_period_volume,
            "growth_pct": round(growth_pct * 100, 1),
            "applicable_tier": tier_name,
            "rebate_rate": rebate_pct,
            "rebate_amount": round(rebate_amount, 2)
        }

    return {
        "rebate_type": "growth_based",
        "current_volume": current_period_volume,
        "prior_volume": prior_period_volume,
        "growth_pct": round(growth_pct * 100, 1),
        "applicable_tier": None,
        "rebate_rate": 0,
        "rebate_amount": 0
    }


def apply_exclusions(
    gross_volume: float,
    exclusion_data: Dict,
    exclusion_rules: Dict
) -> Dict[str, Any]:
    """Apply exclusions to volume."""
    exclusions = []
    total_excluded = 0

    # Product type exclusions
    for product_type in exclusion_rules.get("product_types", []):
        excluded_amount = exclusion_data.get(f"excluded_{product_type}", 0)
        if excluded_amount > 0:
            exclusions.append({
                "type": "product",
                "category": product_type,
                "amount": excluded_amount
            })
            total_excluded += excluded_amount

    # Transaction type exclusions
    for txn_type in exclusion_rules.get("transaction_types", []):
        excluded_amount = exclusion_data.get(f"excluded_{txn_type}", 0)
        if excluded_amount > 0:
            exclusions.append({
                "type": "transaction",
                "category": txn_type,
                "amount": excluded_amount
            })
            total_excluded += excluded_amount

    eligible_volume = gross_volume - total_excluded

    return {
        "gross_volume": gross_volume,
        "exclusions": exclusions,
        "total_excluded": round(total_excluded, 2),
        "eligible_volume": round(eligible_volume, 2),
        "exclusion_rate": round(total_excluded / gross_volume * 100, 1) if gross_volume > 0 else 0
    }


def calculate_accrual(
    estimated_volume: float,
    rebate_rate: float,
    accrual_method: str,
    prior_accrual: float
) -> Dict[str, Any]:
    """Calculate rebate accrual."""
    if accrual_method == "estimated":
        current_accrual = estimated_volume * rebate_rate
        adjustment = 0
    elif accrual_method == "actual":
        current_accrual = estimated_volume * rebate_rate
        adjustment = 0
    else:  # hybrid
        current_accrual = estimated_volume * rebate_rate
        adjustment = current_accrual - prior_accrual

    return {
        "accrual_method": accrual_method,
        "estimated_volume": estimated_volume,
        "rebate_rate": rebate_rate,
        "current_period_accrual": round(current_accrual, 2),
        "prior_accrual": prior_accrual,
        "adjustment": round(adjustment, 2),
        "cumulative_accrual": round(prior_accrual + adjustment, 2)
    }


def process_settlement(
    calculated_rebate: float,
    settlement_option: str,
    customer_balance: float
) -> Dict[str, Any]:
    """Process rebate settlement."""
    settlement_details = {
        "rebate_amount": calculated_rebate,
        "settlement_method": settlement_option
    }

    if settlement_option == "credit_memo":
        settlement_details["action"] = "Apply as credit to customer account"
        settlement_details["account_impact"] = -calculated_rebate

    elif settlement_option == "offset":
        offset_amount = min(calculated_rebate, customer_balance)
        remaining = calculated_rebate - offset_amount
        settlement_details["offset_amount"] = round(offset_amount, 2)
        settlement_details["remaining_rebate"] = round(remaining, 2)
        settlement_details["action"] = "Offset against outstanding balance"

    else:  # check or ach
        settlement_details["action"] = f"Issue payment via {settlement_option.upper()}"
        settlement_details["payment_amount"] = calculated_rebate

    return settlement_details


def process_rebate_calculation(
    calculation_id: str,
    customer_id: str,
    customer_name: str,
    customer_data: Dict,
    gross_volume: float,
    prior_period_volume: float,
    exclusion_data: Dict,
    rebate_program: str,
    settlement_option: str,
    prior_accrual: float,
    calculation_period: str,
    calculation_date: str
) -> Dict[str, Any]:
    """
    Process rebate calculation.

    Business Rules:
    1. Eligibility verification
    2. Volume and growth rebate calculation
    3. Exclusion application
    4. Settlement processing

    Args:
        calculation_id: Calculation identifier
        customer_id: Customer identifier
        customer_name: Customer name
        customer_data: Customer eligibility data
        gross_volume: Gross purchase volume
        prior_period_volume: Prior period volume for growth
        exclusion_data: Excluded volume data
        rebate_program: Rebate program type
        settlement_option: Settlement method
        prior_accrual: Prior accrual amount
        calculation_period: Period being calculated
        calculation_date: Calculation date

    Returns:
        Rebate calculation results
    """
    config = load_rebate_programs()
    rebate_types = config.get("rebate_types", {})
    volume_tiers = config.get("volume_tiers", {})
    growth_tiers = config.get("growth_tiers", {})
    eligibility_requirements = config.get("eligibility_requirements", {})
    exclusions = config.get("exclusions", {})
    accrual_methods = config.get("accrual_methods", {})

    # Check eligibility
    eligibility = check_eligibility(customer_data, eligibility_requirements)

    if not eligibility["eligible"]:
        return {
            "calculation_id": calculation_id,
            "customer_id": customer_id,
            "customer_name": customer_name,
            "calculation_date": calculation_date,
            "calculation_period": calculation_period,
            "eligibility": eligibility,
            "rebate_amount": 0,
            "status": "INELIGIBLE"
        }

    # Apply exclusions
    exclusion_result = apply_exclusions(gross_volume, exclusion_data, exclusions)
    eligible_volume = exclusion_result["eligible_volume"]

    # Calculate rebates
    rebates = []
    total_rebate = 0

    # Volume rebate
    if rebate_program in ["volume_based", "combined"]:
        volume_rebate = calculate_volume_rebate(
            eligible_volume,
            volume_tiers,
            config.get("calculation_rules", {}).get("retroactive", {}).get("applicable_types", ["volume_based"])[0] if "volume_based" in str(config.get("calculation_rules", {})) else "retroactive"
        )
        rebates.append(volume_rebate)
        total_rebate += volume_rebate["total_rebate"]

    # Growth rebate
    if rebate_program in ["growth_based", "combined"]:
        growth_rebate = calculate_growth_rebate(
            eligible_volume,
            prior_period_volume,
            growth_tiers
        )
        rebates.append(growth_rebate)
        total_rebate += growth_rebate.get("rebate_amount", 0)

    # Calculate accrual
    effective_rate = total_rebate / eligible_volume if eligible_volume > 0 else 0
    accrual = calculate_accrual(
        eligible_volume,
        effective_rate,
        "hybrid",
        prior_accrual
    )

    # Process settlement
    customer_balance = customer_data.get("outstanding_balance", 0)
    settlement = process_settlement(total_rebate, settlement_option, customer_balance)

    return {
        "calculation_id": calculation_id,
        "customer_id": customer_id,
        "customer_name": customer_name,
        "calculation_date": calculation_date,
        "calculation_period": calculation_period,
        "eligibility": eligibility,
        "volume_analysis": exclusion_result,
        "rebate_calculations": rebates,
        "total_rebate": round(total_rebate, 2),
        "effective_rebate_rate": round(effective_rate * 100, 2),
        "accrual": accrual,
        "settlement": settlement,
        "status": "CALCULATED"
    }


if __name__ == "__main__":
    import json
    result = process_rebate_calculation(
        calculation_id="REB-2026-001",
        customer_id="CUST-12345",
        customer_name="ABC Distribution Co",
        customer_data={
            "total_spend": 350000,
            "agreement_status": "active",
            "payment_status": "current",
            "compliance_score": 0.92,
            "outstanding_balance": 25000
        },
        gross_volume=350000,
        prior_period_volume=300000,
        exclusion_data={
            "excluded_samples": 5000,
            "excluded_returns": 8000,
            "excluded_credit_memo": 2000
        },
        rebate_program="combined",
        settlement_option="offset",
        prior_accrual=8500,
        calculation_period="2025-Q4",
        calculation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
