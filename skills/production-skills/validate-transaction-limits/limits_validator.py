"""
Transaction Limits Validation Module

Implements transaction limit validation including
tier-based limits, velocity checks, and exception handling.
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


def load_transaction_limits() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    limit_types_data = load_csv_as_dict("limit_types.csv")
    customer_tiers_data = load_csv_as_dict("customer_tiers.csv")
    channel_limits_data = load_csv_as_dict("channel_limits.csv")
    transaction_types_data = load_csv_as_dict("transaction_types.csv")
    validation_actions_data = load_csv_as_dict("validation_actions.csv")
    exception_rules_data = load_csv_as_dict("exception_rules.csv")
    override_authorities_data = load_csv_as_dict("override_authorities.csv")
    params = load_parameters()
    return {
        "limit_types": limit_types_data,
        "customer_tiers": customer_tiers_data,
        "channel_limits": channel_limits_data,
        "transaction_types": transaction_types_data,
        "validation_actions": validation_actions_data,
        "exception_rules": exception_rules_data,
        "override_authorities": override_authorities_data,
        **params
    }


def get_customer_limits(
    customer_tier: str,
    customer_tiers: Dict
) -> Dict[str, Any]:
    """Get limits for customer tier."""
    return customer_tiers.get(customer_tier, customer_tiers.get("basic", {}))


def apply_channel_adjustment(
    base_limits: Dict,
    channel: str,
    channel_limits: Dict
) -> Dict[str, Any]:
    """Apply channel-specific limit adjustments."""
    channel_config = channel_limits.get(channel, {"multiplier": 1.0})
    multiplier = channel_config.get("multiplier", 1.0)
    verification_threshold = channel_config.get("additional_verification_threshold", 0.80)

    adjusted_limits = {
        "single_transaction": base_limits.get("single_transaction", 0) * multiplier,
        "daily_cumulative": base_limits.get("daily_cumulative", 0) * multiplier,
        "weekly_cumulative": base_limits.get("weekly_cumulative", 0) * multiplier,
        "monthly_cumulative": base_limits.get("monthly_cumulative", 0) * multiplier,
        "velocity_limit": base_limits.get("velocity_limit", {}),
        "verification_threshold": verification_threshold
    }

    return adjusted_limits


def apply_transaction_type_adjustment(
    limits: Dict,
    transaction_type: str,
    transaction_types: Dict
) -> Dict[str, Any]:
    """Apply transaction type specific adjustments."""
    type_config = transaction_types.get(transaction_type, {"risk_weight": 1.0, "limit_multiplier": 1.0})
    multiplier = type_config.get("limit_multiplier", 1.0)
    risk_weight = type_config.get("risk_weight", 1.0)

    adjusted_limits = {
        "single_transaction": limits.get("single_transaction", 0) * multiplier,
        "daily_cumulative": limits.get("daily_cumulative", 0) * multiplier,
        "weekly_cumulative": limits.get("weekly_cumulative", 0) * multiplier,
        "monthly_cumulative": limits.get("monthly_cumulative", 0) * multiplier,
        "velocity_limit": limits.get("velocity_limit", {}),
        "verification_threshold": limits.get("verification_threshold", 0.80),
        "risk_weight": risk_weight
    }

    return adjusted_limits


def check_single_transaction_limit(
    amount: float,
    limit: float
) -> Dict[str, Any]:
    """Check single transaction limit."""
    utilization = amount / limit if limit > 0 else 1.0
    exceeded = amount > limit

    return {
        "limit_type": "single_transaction",
        "amount": amount,
        "limit": limit,
        "utilization_pct": round(utilization * 100, 1),
        "exceeded": exceeded,
        "excess_amount": round(amount - limit, 2) if exceeded else 0
    }


def check_cumulative_limit(
    amount: float,
    prior_amount: float,
    limit: float,
    period: str
) -> Dict[str, Any]:
    """Check cumulative period limit."""
    total = prior_amount + amount
    utilization = total / limit if limit > 0 else 1.0
    exceeded = total > limit

    return {
        "limit_type": f"{period}_cumulative",
        "transaction_amount": amount,
        "prior_amount": prior_amount,
        "total_amount": round(total, 2),
        "limit": limit,
        "utilization_pct": round(utilization * 100, 1),
        "exceeded": exceeded,
        "remaining": round(limit - total, 2) if not exceeded else 0
    }


def check_velocity_limit(
    transaction_count: int,
    velocity_config: Dict
) -> Dict[str, Any]:
    """Check transaction velocity limit."""
    limit_count = velocity_config.get("count", 100)
    window_hours = velocity_config.get("window_hours", 24)

    utilization = transaction_count / limit_count if limit_count > 0 else 1.0
    exceeded = transaction_count >= limit_count

    return {
        "limit_type": "velocity",
        "transaction_count": transaction_count,
        "limit_count": limit_count,
        "window_hours": window_hours,
        "utilization_pct": round(utilization * 100, 1),
        "exceeded": exceeded,
        "remaining_transactions": limit_count - transaction_count if not exceeded else 0
    }


def apply_exception_rules(
    transaction_data: Dict,
    exception_rules: Dict
) -> Dict[str, Any]:
    """Apply exception rules that may reduce limits."""
    applied_rules = []
    combined_reduction = 1.0
    verification_required = False

    for rule_name, rule_config in exception_rules.items():
        if transaction_data.get(rule_name, False):
            reduction = rule_config.get("limit_reduction", 1.0)
            verification = rule_config.get("verification", "optional")

            applied_rules.append({
                "rule": rule_name,
                "limit_reduction": reduction,
                "verification": verification
            })

            combined_reduction = min(combined_reduction, reduction)
            if verification == "required" or verification == "enhanced":
                verification_required = True

    return {
        "rules_applied": len(applied_rules),
        "applied_rules": applied_rules,
        "combined_reduction_factor": combined_reduction,
        "verification_required": verification_required
    }


def determine_action(
    limit_checks: List[Dict],
    verification_threshold: float,
    exception_result: Dict,
    validation_actions: Dict
) -> Dict[str, Any]:
    """Determine transaction action based on all checks."""
    # Check for hard limit exceeded
    hard_exceeded = any(c["exceeded"] for c in limit_checks)

    if hard_exceeded:
        action_config = validation_actions.get("hard_decline", {})
        return {
            "action": "HARD_DECLINE",
            "code": action_config.get("code", "HARD_DECLINE"),
            "description": action_config.get("description", ""),
            "reason": "Transaction exceeds hard limits"
        }

    # Check for high utilization requiring verification
    max_utilization = max(c["utilization_pct"] for c in limit_checks) / 100

    if exception_result.get("verification_required", False):
        action_config = validation_actions.get("soft_decline", {})
        return {
            "action": "SOFT_DECLINE",
            "code": action_config.get("code", "SOFT_DECLINE"),
            "description": action_config.get("description", ""),
            "reason": "Additional verification required due to exception rules"
        }

    if max_utilization >= verification_threshold:
        action_config = validation_actions.get("soft_decline", {})
        return {
            "action": "SOFT_DECLINE",
            "code": action_config.get("code", "SOFT_DECLINE"),
            "description": action_config.get("description", ""),
            "reason": f"High limit utilization ({max_utilization * 100:.1f}%)"
        }

    # Transaction approved
    action_config = validation_actions.get("approved", {})
    return {
        "action": "APPROVED",
        "code": action_config.get("code", "APPROVED"),
        "description": action_config.get("description", ""),
        "reason": "Transaction within all limits"
    }


def check_override_authority(
    excess_amount: float,
    limit: float,
    requested_authority: str,
    override_authorities: Dict
) -> Dict[str, Any]:
    """Check if override authority is sufficient."""
    if limit <= 0:
        return {"override_allowed": False, "reason": "Invalid limit"}

    excess_pct = excess_amount / limit

    authority_config = override_authorities.get(requested_authority, {})
    max_override_pct = authority_config.get("max_override_pct", 0)

    override_allowed = excess_pct <= max_override_pct

    return {
        "requested_authority": requested_authority,
        "excess_amount": excess_amount,
        "excess_pct": round(excess_pct * 100, 1),
        "max_override_pct": round(max_override_pct * 100, 1),
        "override_allowed": override_allowed,
        "required_authority": next(
            (auth for auth, config in override_authorities.items()
             if config.get("max_override_pct", 0) >= excess_pct),
            "director"
        ) if not override_allowed else requested_authority
    }


def validate_transaction_limits(
    transaction_id: str,
    customer_id: str,
    customer_tier: str,
    channel: str,
    transaction_type: str,
    amount: float,
    daily_prior_amount: float,
    weekly_prior_amount: float,
    monthly_prior_amount: float,
    transactions_in_window: int,
    exception_flags: Dict,
    validation_timestamp: str
) -> Dict[str, Any]:
    """
    Validate transaction against limits.

    Business Rules:
    1. Tier-based limit application
    2. Channel and type adjustments
    3. Velocity checking
    4. Exception rule application

    Args:
        transaction_id: Transaction identifier
        customer_id: Customer identifier
        customer_tier: Customer tier level
        channel: Transaction channel
        transaction_type: Type of transaction
        amount: Transaction amount
        daily_prior_amount: Prior daily cumulative amount
        weekly_prior_amount: Prior weekly cumulative amount
        monthly_prior_amount: Prior monthly cumulative amount
        transactions_in_window: Number of transactions in velocity window
        exception_flags: Exception condition flags
        validation_timestamp: Validation timestamp

    Returns:
        Transaction limit validation results
    """
    config = load_transaction_limits()
    customer_tiers = config.get("customer_tiers", {})
    channel_limits = config.get("channel_limits", {})
    transaction_types = config.get("transaction_types", {})
    validation_actions = config.get("validation_actions", {})
    exception_rules = config.get("exception_rules", {})
    override_authorities = config.get("override_authorities", {})

    # Get base limits for customer tier
    base_limits = get_customer_limits(customer_tier, customer_tiers)

    # Apply channel adjustment
    channel_adjusted = apply_channel_adjustment(base_limits, channel, channel_limits)

    # Apply transaction type adjustment
    final_limits = apply_transaction_type_adjustment(
        channel_adjusted,
        transaction_type,
        transaction_types
    )

    # Apply exception rules
    exception_result = apply_exception_rules(exception_flags, exception_rules)

    # Apply exception reduction to limits
    reduction_factor = exception_result.get("combined_reduction_factor", 1.0)
    adjusted_single = final_limits["single_transaction"] * reduction_factor
    adjusted_daily = final_limits["daily_cumulative"] * reduction_factor

    # Perform limit checks
    limit_checks = []

    # Single transaction check
    single_check = check_single_transaction_limit(amount, adjusted_single)
    limit_checks.append(single_check)

    # Daily cumulative check
    daily_check = check_cumulative_limit(
        amount, daily_prior_amount, adjusted_daily, "daily"
    )
    limit_checks.append(daily_check)

    # Weekly cumulative check
    weekly_check = check_cumulative_limit(
        amount, weekly_prior_amount,
        final_limits["weekly_cumulative"] * reduction_factor, "weekly"
    )
    limit_checks.append(weekly_check)

    # Monthly cumulative check
    monthly_check = check_cumulative_limit(
        amount, monthly_prior_amount,
        final_limits["monthly_cumulative"] * reduction_factor, "monthly"
    )
    limit_checks.append(monthly_check)

    # Velocity check
    velocity_check = check_velocity_limit(
        transactions_in_window + 1,  # Include current transaction
        final_limits["velocity_limit"]
    )
    limit_checks.append(velocity_check)

    # Determine action
    action = determine_action(
        limit_checks,
        final_limits["verification_threshold"],
        exception_result,
        validation_actions
    )

    # Check override if declined
    override_info = None
    if action["action"] in ["HARD_DECLINE", "SOFT_DECLINE"]:
        exceeded_check = next((c for c in limit_checks if c["exceeded"]), None)
        if exceeded_check:
            override_info = check_override_authority(
                exceeded_check.get("excess_amount", 0),
                exceeded_check.get("limit", 1),
                "supervisor",
                override_authorities
            )

    return {
        "transaction_id": transaction_id,
        "customer_id": customer_id,
        "validation_timestamp": validation_timestamp,
        "transaction_details": {
            "amount": amount,
            "channel": channel,
            "transaction_type": transaction_type,
            "customer_tier": customer_tier
        },
        "applied_limits": {
            "single_transaction": round(adjusted_single, 2),
            "daily_cumulative": round(adjusted_daily, 2),
            "weekly_cumulative": round(final_limits["weekly_cumulative"] * reduction_factor, 2),
            "monthly_cumulative": round(final_limits["monthly_cumulative"] * reduction_factor, 2),
            "velocity": final_limits["velocity_limit"]
        },
        "limit_checks": limit_checks,
        "exception_evaluation": exception_result,
        "validation_result": action,
        "override_information": override_info,
        "risk_weight": final_limits.get("risk_weight", 1.0)
    }


if __name__ == "__main__":
    import json
    result = validate_transaction_limits(
        transaction_id="TXN-20260120-001",
        customer_id="CUST-12345",
        customer_tier="standard",
        channel="online",
        transaction_type="transfer_external",
        amount=3500,
        daily_prior_amount=8500,
        weekly_prior_amount=25000,
        monthly_prior_amount=45000,
        transactions_in_window=12,
        exception_flags={
            "first_time_recipient": True,
            "new_device": False,
            "high_risk_country": False
        },
        validation_timestamp="2026-01-20T14:30:00Z"
    )
    print(json.dumps(result, indent=2))
