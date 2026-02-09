"""
Commission Calculation Module

Implements sales commission calculation including
tiered structures, quotas, and adjustments.
"""

import csv
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta



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


def load_commission_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    commission_structures_data = load_csv_as_dict("commission_structures.csv")
    product_categories_data = load_csv_as_dict("product_categories.csv")
    adjustments_data = load_key_value_csv("adjustments.csv")
    clawback_rules_data = load_key_value_csv("clawback_rules.csv")
    payment_schedules_data = load_csv_as_dict("payment_schedules.csv")
    caps_and_floors_data = load_key_value_csv("caps_and_floors.csv")
    split_rules_data = load_key_value_csv("split_rules.csv")
    params = load_parameters()
    return {
        "commission_structures": commission_structures_data,
        "product_categories": product_categories_data,
        "adjustments": adjustments_data,
        "clawback_rules": clawback_rules_data,
        "payment_schedules": payment_schedules_data,
        "caps_and_floors": caps_and_floors_data,
        "split_rules": split_rules_data,
        **params
    }


def calculate_flat_rate_commission(
    sales_amount: float,
    base_rate: float
) -> Dict[str, Any]:
    """Calculate flat rate commission."""
    commission = sales_amount * base_rate

    return {
        "method": "flat_rate",
        "sales_amount": sales_amount,
        "rate": base_rate,
        "commission": round(commission, 2)
    }


def calculate_tiered_commission(
    sales_amount: float,
    tiers: List[Dict]
) -> Dict[str, Any]:
    """Calculate tiered commission."""
    sorted_tiers = sorted(tiers, key=lambda x: x.get("threshold", 0))
    total_commission = 0
    tier_breakdown = []
    remaining = sales_amount

    for i, tier in enumerate(sorted_tiers):
        threshold = tier.get("threshold", 0)
        rate = tier.get("rate", 0)

        # Get next threshold
        next_threshold = sorted_tiers[i + 1].get("threshold", float('inf')) if i + 1 < len(sorted_tiers) else float('inf')

        # Calculate amount in this tier
        tier_cap = next_threshold - threshold
        tier_amount = min(remaining, tier_cap) if remaining > 0 else 0

        if tier_amount > 0:
            tier_commission = tier_amount * rate
            total_commission += tier_commission
            tier_breakdown.append({
                "tier_threshold": threshold,
                "rate": rate,
                "amount_in_tier": round(tier_amount, 2),
                "tier_commission": round(tier_commission, 2)
            })
            remaining -= tier_amount

        if remaining <= 0:
            break

    return {
        "method": "tiered",
        "sales_amount": sales_amount,
        "tier_breakdown": tier_breakdown,
        "total_commission": round(total_commission, 2),
        "effective_rate": round(total_commission / sales_amount, 4) if sales_amount > 0 else 0
    }


def calculate_quota_commission(
    sales_amount: float,
    quota: float,
    config: Dict
) -> Dict[str, Any]:
    """Calculate quota-based commission with accelerators."""
    base_rate = config.get("base_rate", 0.05)
    quota_rate = config.get("quota_rate", 0.08)
    accelerator_rate = config.get("accelerator_rate", 0.12)
    accelerator_threshold = config.get("accelerator_threshold", 1.2)

    quota_attainment = sales_amount / quota if quota > 0 else 0

    if quota_attainment < 1.0:
        # Below quota - base rate only
        commission = sales_amount * base_rate
        applied_rate = base_rate
        status = "below_quota"
    elif quota_attainment < accelerator_threshold:
        # At quota - quota rate
        commission = sales_amount * quota_rate
        applied_rate = quota_rate
        status = "at_quota"
    else:
        # Above accelerator threshold
        base_commission = quota * accelerator_threshold * quota_rate
        accelerated_amount = sales_amount - (quota * accelerator_threshold)
        accelerated_commission = accelerated_amount * accelerator_rate
        commission = base_commission + accelerated_commission
        applied_rate = commission / sales_amount
        status = "accelerated"

    return {
        "method": "quota_based",
        "sales_amount": sales_amount,
        "quota": quota,
        "quota_attainment_pct": round(quota_attainment * 100, 1),
        "status": status,
        "applied_rate": round(applied_rate, 4),
        "commission": round(commission, 2)
    }


def calculate_margin_commission(
    gross_sales: float,
    cost: float,
    margin_rate: float
) -> Dict[str, Any]:
    """Calculate commission based on gross margin."""
    gross_margin = gross_sales - cost
    margin_pct = gross_margin / gross_sales if gross_sales > 0 else 0
    commission = gross_margin * margin_rate

    return {
        "method": "gross_margin",
        "gross_sales": gross_sales,
        "cost": cost,
        "gross_margin": round(gross_margin, 2),
        "margin_pct": round(margin_pct * 100, 1),
        "margin_rate": margin_rate,
        "commission": round(commission, 2)
    }


def calculate_product_commission(
    line_items: List[Dict],
    product_categories: Dict
) -> Dict[str, Any]:
    """Calculate commission by product category."""
    total_commission = 0
    total_spiffs = 0
    category_breakdown = {}

    for item in line_items:
        category = item.get("category", "hardware")
        amount = item.get("amount", 0)
        quantity = item.get("quantity", 1)

        category_config = product_categories.get(category, {"commission_rate": 0.05, "spiff": 0})
        rate = category_config.get("commission_rate", 0.05)
        spiff = category_config.get("spiff", 0)

        item_commission = amount * rate
        item_spiffs = spiff * quantity

        total_commission += item_commission
        total_spiffs += item_spiffs

        if category not in category_breakdown:
            category_breakdown[category] = {"amount": 0, "commission": 0, "spiffs": 0}

        category_breakdown[category]["amount"] += amount
        category_breakdown[category]["commission"] += item_commission
        category_breakdown[category]["spiffs"] += item_spiffs

    # Round breakdown values
    for cat in category_breakdown:
        category_breakdown[cat] = {
            k: round(v, 2) for k, v in category_breakdown[cat].items()
        }

    return {
        "category_breakdown": category_breakdown,
        "base_commission": round(total_commission, 2),
        "total_spiffs": round(total_spiffs, 2),
        "total": round(total_commission + total_spiffs, 2)
    }


def apply_adjustments(
    base_commission: float,
    deal_attributes: Dict,
    adjustment_rules: Dict
) -> Dict[str, Any]:
    """Apply commission adjustments."""
    adjustments = []
    adjusted_commission = base_commission

    # New customer bonus
    if deal_attributes.get("is_new_customer", False):
        bonus_rate = adjustment_rules.get("new_customer_bonus", 0.02)
        bonus = base_commission * bonus_rate
        adjustments.append({"type": "new_customer_bonus", "amount": round(bonus, 2)})
        adjusted_commission += bonus

    # Strategic account bonus
    if deal_attributes.get("is_strategic_account", False):
        bonus_rate = adjustment_rules.get("strategic_account_bonus", 0.03)
        bonus = base_commission * bonus_rate
        adjustments.append({"type": "strategic_account_bonus", "amount": round(bonus, 2)})
        adjusted_commission += bonus

    # Discount penalty
    discount_given = deal_attributes.get("discount_pct", 0)
    penalty_threshold = adjustment_rules.get("discount_penalty_threshold", 0.25)
    if discount_given > penalty_threshold:
        penalty_rate = adjustment_rules.get("discount_penalty_rate", 0.50)
        excess_discount = discount_given - penalty_threshold
        penalty = base_commission * excess_discount * penalty_rate
        adjustments.append({"type": "discount_penalty", "amount": round(-penalty, 2)})
        adjusted_commission -= penalty

    return {
        "base_commission": base_commission,
        "adjustments": adjustments,
        "total_adjustment": round(adjusted_commission - base_commission, 2),
        "adjusted_commission": round(adjusted_commission, 2)
    }


def calculate_splits(
    total_commission: float,
    team_members: List[Dict],
    split_rules: Dict
) -> Dict[str, Any]:
    """Calculate commission splits."""
    splits = []
    remaining = total_commission

    # Overlay split
    overlay_pct = split_rules.get("overlay_pct", 0.20)
    overlay_members = [m for m in team_members if m.get("role") == "overlay"]

    if overlay_members:
        overlay_amount = total_commission * overlay_pct
        per_overlay = overlay_amount / len(overlay_members)
        for member in overlay_members:
            splits.append({
                "rep_id": member.get("id"),
                "rep_name": member.get("name"),
                "role": "overlay",
                "amount": round(per_overlay, 2)
            })
        remaining -= overlay_amount

    # Primary split
    primary_members = [m for m in team_members if m.get("role") == "primary"]
    if primary_members:
        split_method = split_rules.get("team_split_method", "equal")

        if split_method == "equal":
            per_member = remaining / len(primary_members)
            for member in primary_members:
                splits.append({
                    "rep_id": member.get("id"),
                    "rep_name": member.get("name"),
                    "role": "primary",
                    "amount": round(per_member, 2)
                })
        elif split_method == "weighted":
            total_weight = sum(m.get("weight", 1) for m in primary_members)
            for member in primary_members:
                weight = member.get("weight", 1)
                amount = remaining * (weight / total_weight)
                splits.append({
                    "rep_id": member.get("id"),
                    "rep_name": member.get("name"),
                    "role": "primary",
                    "weight": weight,
                    "amount": round(amount, 2)
                })

    # Manager override
    manager_override_pct = split_rules.get("manager_override_pct", 0.05)
    managers = [m for m in team_members if m.get("role") == "manager"]
    if managers:
        override_amount = total_commission * manager_override_pct
        for manager in managers:
            splits.append({
                "rep_id": manager.get("id"),
                "rep_name": manager.get("name"),
                "role": "manager_override",
                "amount": round(override_amount, 2)
            })

    return {
        "total_commission": total_commission,
        "splits": splits,
        "total_splits": round(sum(s["amount"] for s in splits), 2)
    }


def check_clawback(
    original_commission: float,
    deal_status: str,
    days_since_close: int,
    clawback_rules: Dict
) -> Dict[str, Any]:
    """Check for commission clawback."""
    window_days = clawback_rules.get("cancellation_window_days", 90)
    clawback_pct = clawback_rules.get("churn_clawback_pct", 1.0)

    clawback_amount = 0
    clawback_applies = False

    if deal_status == "cancelled" and days_since_close <= window_days:
        clawback_applies = True
        clawback_amount = original_commission * clawback_pct

    return {
        "deal_status": deal_status,
        "days_since_close": days_since_close,
        "within_clawback_window": days_since_close <= window_days,
        "clawback_applies": clawback_applies,
        "clawback_amount": round(clawback_amount, 2)
    }


def process_commission_calculation(
    deal_id: str,
    rep_id: str,
    commission_structure: str,
    gross_sales: float,
    cost: float,
    line_items: List[Dict],
    quota: float,
    deal_attributes: Dict,
    team_members: List[Dict],
    deal_status: str,
    days_since_close: int,
    calculation_date: str
) -> Dict[str, Any]:
    """
    Process commission calculation.

    Business Rules:
    1. Multiple commission structure support
    2. Product category rates
    3. Adjustments and bonuses
    4. Split calculations

    Args:
        deal_id: Deal identifier
        rep_id: Primary rep identifier
        commission_structure: Commission structure type
        gross_sales: Gross sales amount
        cost: Cost of goods
        line_items: Product line items
        quota: Sales quota
        deal_attributes: Deal characteristics
        team_members: Team members for splits
        deal_status: Current deal status
        days_since_close: Days since deal closed
        calculation_date: Calculation date

    Returns:
        Commission calculation results
    """
    rules = load_commission_rules()
    structures = rules.get("commission_structures", {})

    # Calculate base commission based on structure
    if commission_structure == "flat_rate":
        config = structures.get("flat_rate", {})
        base_calc = calculate_flat_rate_commission(gross_sales, config.get("base_rate", 0.05))
        base_commission = base_calc["commission"]

    elif commission_structure == "tiered":
        config = structures.get("tiered", {})
        base_calc = calculate_tiered_commission(gross_sales, config.get("tiers", []))
        base_commission = base_calc["total_commission"]

    elif commission_structure == "quota_based":
        config = structures.get("quota_based", {})
        base_calc = calculate_quota_commission(gross_sales, quota, config)
        base_commission = base_calc["commission"]

    elif commission_structure == "gross_margin":
        config = structures.get("gross_margin", {})
        base_calc = calculate_margin_commission(gross_sales, cost, config.get("margin_rate", 0.15))
        base_commission = base_calc["commission"]

    else:
        base_calc = calculate_flat_rate_commission(gross_sales, 0.05)
        base_commission = base_calc["commission"]

    # Calculate product-based commission
    product_calc = calculate_product_commission(
        line_items,
        rules.get("product_categories", {})
    )

    # Apply adjustments
    adjustment_calc = apply_adjustments(
        base_commission,
        deal_attributes,
        rules.get("adjustments", {})
    )

    # Calculate splits
    total_commission = adjustment_calc["adjusted_commission"] + product_calc["total_spiffs"]
    split_calc = calculate_splits(
        total_commission,
        team_members,
        rules.get("split_rules", {})
    )

    # Check clawback
    clawback_calc = check_clawback(
        total_commission,
        deal_status,
        days_since_close,
        rules.get("clawback_rules", {})
    )

    # Final commission
    final_commission = total_commission - clawback_calc["clawback_amount"]

    return {
        "deal_id": deal_id,
        "rep_id": rep_id,
        "calculation_date": calculation_date,
        "deal_value": gross_sales,
        "commission_structure": commission_structure,
        "base_calculation": base_calc,
        "product_commission": product_calc,
        "adjustments": adjustment_calc,
        "splits": split_calc,
        "clawback": clawback_calc,
        "summary": {
            "base_commission": round(base_commission, 2),
            "spiffs": product_calc["total_spiffs"],
            "adjustments": adjustment_calc["total_adjustment"],
            "clawback": -clawback_calc["clawback_amount"],
            "final_commission": round(final_commission, 2)
        }
    }


if __name__ == "__main__":
    import json
    result = process_commission_calculation(
        deal_id="DEAL-001",
        rep_id="REP-001",
        commission_structure="quota_based",
        gross_sales=125000,
        cost=75000,
        line_items=[
            {"category": "software", "amount": 75000, "quantity": 5},
            {"category": "services", "amount": 50000, "quantity": 1}
        ],
        quota=100000,
        deal_attributes={
            "is_new_customer": True,
            "is_strategic_account": False,
            "discount_pct": 0.15
        },
        team_members=[
            {"id": "REP-001", "name": "John Sales", "role": "primary", "weight": 0.7},
            {"id": "REP-002", "name": "Jane Support", "role": "primary", "weight": 0.3},
            {"id": "MGR-001", "name": "Bob Manager", "role": "manager"}
        ],
        deal_status="closed_won",
        days_since_close=15,
        calculation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
