"""
Claim Subrogation Processing Module

Implements insurance subrogation assessment including
recovery potential analysis and pursuit recommendations.
"""

import csv
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


def load_subrogation_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    subrogation_thresholds_data = load_key_value_csv("subrogation_thresholds.csv")
    recovery_potential_factors_data = load_csv_as_dict("recovery_potential_factors.csv")
    claim_type_multipliers_data = load_key_value_csv("claim_type_multipliers.csv")
    statute_of_limitations_data = load_csv_as_dict("statute_of_limitations.csv")
    cost_thresholds_data = load_key_value_csv("cost_thresholds.csv")
    recovery_rates_data = load_csv_as_dict("recovery_rates.csv")
    pursuit_costs_data = load_key_value_csv("pursuit_costs.csv")
    priority_scoring_data = load_csv_as_dict("priority_scoring.csv")
    params = load_parameters()
    return {
        "subrogation_thresholds": subrogation_thresholds_data,
        "recovery_potential_factors": recovery_potential_factors_data,
        "claim_type_multipliers": claim_type_multipliers_data,
        "statute_of_limitations": statute_of_limitations_data,
        "cost_thresholds": cost_thresholds_data,
        "recovery_rates": recovery_rates_data,
        "pursuit_costs": pursuit_costs_data,
        "priority_scoring": priority_scoring_data,
        **params
    }


def calculate_recovery_potential(
    claim_data: Dict,
    recovery_factors: Dict
) -> Dict[str, Any]:
    """Calculate recovery potential score."""
    total_score = 0
    factor_details = []

    for factor, config in recovery_factors.items():
        factor_value = claim_data.get(factor, "unknown")
        weight = config.get("weight", 0.20)

        # Get score based on factor value
        score_key = f"score_{factor_value}"
        factor_score = config.get(score_key, config.get("score_unknown", 50))

        weighted_score = factor_score * weight
        total_score += weighted_score

        factor_details.append({
            "factor": factor,
            "value": factor_value,
            "raw_score": factor_score,
            "weight": weight,
            "weighted_score": round(weighted_score, 1)
        })

    return {
        "recovery_potential_score": round(total_score, 1),
        "factor_breakdown": factor_details
    }


def apply_claim_type_adjustment(
    base_score: float,
    claim_type: str,
    multipliers: Dict
) -> Dict[str, Any]:
    """Apply claim type adjustment to recovery score."""
    multiplier = multipliers.get(claim_type, 0.8)
    adjusted_score = base_score * multiplier

    return {
        "base_score": base_score,
        "claim_type": claim_type,
        "multiplier": multiplier,
        "adjusted_score": round(adjusted_score, 1)
    }


def check_statute_of_limitations(
    loss_date: str,
    claim_type: str,
    statute_config: Dict
) -> Dict[str, Any]:
    """Check statute of limitations status."""
    loss_datetime = datetime.strptime(loss_date, "%Y-%m-%d")
    current_date = datetime.now()

    claim_category = claim_type.split("_")[0] if "_" in claim_type else claim_type
    statute = statute_config.get(claim_category, statute_config.get("property", {}))
    years = statute.get("years", 3)

    expiration_date = loss_datetime + timedelta(days=years * 365)
    days_remaining = (expiration_date - current_date).days

    if days_remaining < 0:
        status = "EXPIRED"
    elif days_remaining < 180:
        status = "URGENT"
    elif days_remaining < 365:
        status = "WARNING"
    else:
        status = "OK"

    return {
        "loss_date": loss_date,
        "statute_years": years,
        "expiration_date": expiration_date.strftime("%Y-%m-%d"),
        "days_remaining": max(0, days_remaining),
        "status": status
    }


def estimate_recovery_amount(
    paid_amount: float,
    recovery_score: float,
    recovery_rates: Dict
) -> Dict[str, Any]:
    """Estimate expected recovery amount."""
    for potential_level, config in sorted(
        recovery_rates.items(),
        key=lambda x: x[1].get("min", 0),
        reverse=True
    ):
        if recovery_score >= config.get("min", 0):
            expected_rate = config.get("expected_recovery", 0.50)
            potential_level_name = potential_level
            break
    else:
        expected_rate = 0.10
        potential_level_name = "poor_potential"

    expected_recovery = paid_amount * expected_rate
    recovery_range = {
        "low": round(expected_recovery * 0.70, 2),
        "mid": round(expected_recovery, 2),
        "high": round(expected_recovery * 1.30, 2)
    }

    return {
        "paid_amount": paid_amount,
        "potential_level": potential_level_name,
        "expected_recovery_rate": expected_rate,
        "expected_recovery": round(expected_recovery, 2),
        "recovery_range": recovery_range
    }


def calculate_pursuit_costs(
    expected_recovery: float,
    recovery_score: float,
    cost_config: Dict,
    threshold_config: Dict
) -> Dict[str, Any]:
    """Calculate estimated pursuit costs."""
    costs = {}
    total_cost = 0

    # Base costs
    costs["demand_letter"] = cost_config.get("demand_letter", 50)
    total_cost += costs["demand_letter"]

    # Investigation if needed
    if recovery_score < 70:
        costs["investigation"] = cost_config.get("investigation", 500)
        total_cost += costs["investigation"]

    # Legal costs based on expected recovery
    if expected_recovery >= threshold_config.get("litigation_threshold", 50000):
        costs["legal"] = cost_config.get("litigation", 10000)
        total_cost += costs["legal"]
    elif expected_recovery >= threshold_config.get("arbitration_threshold", 25000):
        costs["arbitration"] = cost_config.get("arbitration", 2500)
        total_cost += costs["arbitration"]

    # Collection costs
    collection_rate = cost_config.get("collection", 0.15)
    costs["collection_estimate"] = round(expected_recovery * collection_rate, 2)
    total_cost += costs["collection_estimate"]

    net_recovery = expected_recovery - total_cost

    return {
        "cost_breakdown": costs,
        "total_estimated_cost": round(total_cost, 2),
        "expected_recovery": expected_recovery,
        "net_recovery_estimate": round(net_recovery, 2),
        "roi": round(net_recovery / total_cost, 2) if total_cost > 0 else 0
    }


def determine_pursuit_priority(
    recovery_score: float,
    net_recovery: float,
    statute_status: str,
    priority_config: Dict,
    thresholds: Dict
) -> Dict[str, Any]:
    """Determine subrogation pursuit priority."""
    # Check minimum thresholds
    if net_recovery < thresholds.get("auto_close_below", 1000):
        return {
            "priority": "CLOSE",
            "action": "close_uneconomical",
            "reason": "Net recovery below minimum threshold"
        }

    # Check statute urgency
    if statute_status == "EXPIRED":
        return {
            "priority": "CLOSED",
            "action": "close_expired",
            "reason": "Statute of limitations expired"
        }

    if statute_status == "URGENT":
        return {
            "priority": "CRITICAL",
            "action": "immediate_action",
            "reason": "Statute expiring soon"
        }

    # Score-based priority
    for priority, config in priority_config.items():
        if recovery_score >= config.get("min_score", 0):
            return {
                "priority": priority.upper(),
                "action": config.get("action", "evaluate"),
                "reason": f"Recovery score: {recovery_score}"
            }

    return {
        "priority": "LOW",
        "action": "evaluate_close",
        "reason": "Low recovery potential"
    }


def identify_at_fault_party(
    accident_details: Dict
) -> Dict[str, Any]:
    """Identify at-fault party information."""
    at_fault = accident_details.get("at_fault_party", {})

    return {
        "name": at_fault.get("name", "Unknown"),
        "insurance_carrier": at_fault.get("insurance_carrier", "Unknown"),
        "policy_number": at_fault.get("policy_number", "Unknown"),
        "contact_info": at_fault.get("contact_info", {}),
        "is_insured": at_fault.get("is_insured", False),
        "liability_percentage": at_fault.get("liability_pct", 100)
    }


def generate_next_steps(
    priority: str,
    statute_status: str,
    at_fault_insured: bool,
    expected_recovery: float
) -> List[Dict]:
    """Generate recommended next steps."""
    steps = []

    if statute_status == "URGENT":
        steps.append({
            "step": 1,
            "action": "File demand immediately",
            "deadline": "5 business days",
            "priority": "critical"
        })

    if priority in ["HIGH", "CRITICAL"]:
        steps.append({
            "step": len(steps) + 1,
            "action": "Send demand letter to at-fault carrier",
            "deadline": "10 business days",
            "priority": "high"
        })

    if at_fault_insured:
        steps.append({
            "step": len(steps) + 1,
            "action": "Contact at-fault insurance carrier",
            "deadline": "15 business days",
            "priority": "medium"
        })
    else:
        steps.append({
            "step": len(steps) + 1,
            "action": "Evaluate direct pursuit options",
            "deadline": "30 business days",
            "priority": "medium"
        })

    if expected_recovery >= 25000:
        steps.append({
            "step": len(steps) + 1,
            "action": "Engage subrogation counsel",
            "deadline": "30 business days",
            "priority": "medium"
        })

    return steps


def process_claim_subrogation(
    claim_id: str,
    claim_type: str,
    loss_date: str,
    paid_amount: float,
    claim_data: Dict,
    accident_details: Dict,
    processing_date: str
) -> Dict[str, Any]:
    """
    Process claim for subrogation.

    Business Rules:
    1. Recovery potential scoring
    2. Statute of limitations tracking
    3. Cost-benefit analysis
    4. Pursuit priority determination

    Args:
        claim_id: Claim identifier
        claim_type: Type of claim
        loss_date: Date of loss
        paid_amount: Amount paid on claim
        claim_data: Claim recovery factors
        accident_details: Accident/loss details
        processing_date: Processing date

    Returns:
        Subrogation processing results
    """
    rules = load_subrogation_rules()

    # Calculate recovery potential
    recovery_potential = calculate_recovery_potential(
        claim_data,
        rules.get("recovery_potential_factors", {})
    )

    # Apply claim type adjustment
    adjusted_score = apply_claim_type_adjustment(
        recovery_potential["recovery_potential_score"],
        claim_type,
        rules.get("claim_type_multipliers", {})
    )

    # Check statute of limitations
    statute = check_statute_of_limitations(
        loss_date,
        claim_type,
        rules.get("statute_of_limitations", {})
    )

    # Estimate recovery amount
    recovery_estimate = estimate_recovery_amount(
        paid_amount,
        adjusted_score["adjusted_score"],
        rules.get("recovery_rates", {})
    )

    # Calculate pursuit costs
    pursuit_costs = calculate_pursuit_costs(
        recovery_estimate["expected_recovery"],
        adjusted_score["adjusted_score"],
        rules.get("pursuit_costs", {}),
        rules.get("cost_thresholds", {})
    )

    # Determine priority
    priority = determine_pursuit_priority(
        adjusted_score["adjusted_score"],
        pursuit_costs["net_recovery_estimate"],
        statute["status"],
        rules.get("priority_scoring", {}),
        rules.get("subrogation_thresholds", {})
    )

    # Identify at-fault party
    at_fault = identify_at_fault_party(accident_details)

    # Generate next steps
    next_steps = generate_next_steps(
        priority["priority"],
        statute["status"],
        at_fault["is_insured"],
        recovery_estimate["expected_recovery"]
    )

    return {
        "claim_id": claim_id,
        "processing_date": processing_date,
        "claim_type": claim_type,
        "paid_amount": paid_amount,
        "recovery_potential": recovery_potential,
        "adjusted_recovery_score": adjusted_score,
        "statute_of_limitations": statute,
        "recovery_estimate": recovery_estimate,
        "pursuit_cost_analysis": pursuit_costs,
        "at_fault_party": at_fault,
        "pursuit_priority": priority,
        "next_steps": next_steps,
        "recommendation": "PURSUE" if priority["priority"] in ["HIGH", "CRITICAL", "MEDIUM"] else "EVALUATE" if priority["priority"] == "LOW" else "CLOSE"
    }


if __name__ == "__main__":
    import json
    result = process_claim_subrogation(
        claim_id="CLM-SUB-001",
        claim_type="auto_collision",
        loss_date="2025-06-15",
        paid_amount=15000,
        claim_data={
            "liability_clear": "clear",
            "at_fault_party_insured": "yes",
            "evidence_quality": "strong",
            "damages_documented": "complete",
            "cooperation_level": "full"
        },
        accident_details={
            "at_fault_party": {
                "name": "John Doe",
                "insurance_carrier": "ABC Insurance",
                "policy_number": "POL-123456",
                "is_insured": True,
                "liability_pct": 100
            }
        },
        processing_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
