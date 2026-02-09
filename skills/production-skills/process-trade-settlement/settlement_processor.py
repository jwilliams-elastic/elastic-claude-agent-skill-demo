"""
Trade Settlement Processing Module

Implements securities trade settlement validation,
obligation calculation, and exception management.
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


def load_settlement_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    settlement_cycles_data = load_key_value_csv("settlement_cycles.csv")
    risk_factors_data = load_csv_as_dict("risk_factors.csv")
    fee_schedules_data = load_key_value_csv("fee_schedules.csv")
    fail_management_data = load_key_value_csv("fail_management.csv")
    netting_rules_data = load_key_value_csv("netting_rules.csv")
    regulatory_reporting_data = load_key_value_csv("regulatory_reporting.csv")
    params = load_parameters()
    return {
        "settlement_cycles": settlement_cycles_data,
        "risk_factors": risk_factors_data,
        "fee_schedules": fee_schedules_data,
        "fail_management": fail_management_data,
        "netting_rules": netting_rules_data,
        "regulatory_reporting": regulatory_reporting_data,
        **params
    }


def calculate_settlement_date(
    trade_date: str,
    security_type: str,
    settlement_cycles: Dict
) -> str:
    """Calculate settlement date based on security type."""
    try:
        trade_dt = datetime.strptime(trade_date, "%Y-%m-%d")
    except ValueError:
        trade_dt = datetime.now()

    cycle_days = settlement_cycles.get(security_type, 2)

    # Add business days (simplified - doesn't account for holidays)
    settlement_dt = trade_dt
    days_added = 0
    while days_added < cycle_days:
        settlement_dt += timedelta(days=1)
        if settlement_dt.weekday() < 5:  # Monday = 0, Friday = 4
            days_added += 1

    return settlement_dt.strftime("%Y-%m-%d")


def validate_trade_matching(
    trade_details: Dict,
    counterparty_info: Dict,
    matching_rules: Dict
) -> Dict[str, Any]:
    """Validate trade details match between parties."""
    match_fields = matching_rules.get("required_fields", [])
    discrepancies = []
    matched_fields = []

    # Simulate counterparty trade details (in production, would query)
    # For this example, assume basic matching
    our_side = trade_details.get("side", "")
    quantity = trade_details.get("quantity", 0)
    price = trade_details.get("price", 0)

    # Validate required fields present
    for field in match_fields:
        if field in trade_details:
            matched_fields.append(field)
        else:
            discrepancies.append({
                "field": field,
                "issue": "Missing required field"
            })

    # Price tolerance check
    price_tolerance = matching_rules.get("price_tolerance", 0.01)
    # In real system, would compare with counterparty price

    match_status = "MATCHED" if len(discrepancies) == 0 else "UNMATCHED"

    return {
        "status": match_status,
        "matched_fields": matched_fields,
        "discrepancies": discrepancies,
        "match_timestamp": datetime.now().isoformat()
    }


def calculate_net_obligation(
    trade_details: Dict,
    security_info: Dict,
    position_data: Dict
) -> Dict[str, Any]:
    """Calculate net settlement obligation."""
    side = trade_details.get("side", "buy")
    quantity = trade_details.get("quantity", 0)
    price = trade_details.get("price", 0)

    gross_amount = quantity * price

    # Fees (simplified)
    sec_fee_rate = 0.0000278  # SEC fee rate
    sec_fee = gross_amount * sec_fee_rate if side == "sell" else 0

    # Net amount
    if side == "buy":
        net_cash = -gross_amount  # Pay cash
        net_securities = quantity  # Receive securities
    else:
        net_cash = gross_amount - sec_fee  # Receive cash minus fees
        net_securities = -quantity  # Deliver securities

    return {
        "gross_amount": round(gross_amount, 2),
        "fees": {
            "sec_fee": round(sec_fee, 2)
        },
        "net_cash_obligation": round(net_cash, 2),
        "net_securities_obligation": net_securities,
        "side": side,
        "currency": "USD"
    }


def assess_fail_risk(
    trade_details: Dict,
    position_data: Dict,
    counterparty_info: Dict,
    risk_factors: Dict
) -> Dict[str, Any]:
    """Assess probability of settlement failure."""
    risk_score = 0
    risk_items = []

    side = trade_details.get("side", "buy")
    quantity = trade_details.get("quantity", 0)

    # For sells, check position availability
    if side == "sell":
        available = position_data.get("available", 0)
        pending_receipts = position_data.get("pending_receipts", 0)

        if available < quantity:
            shortfall = quantity - available
            if available + pending_receipts >= quantity:
                risk_items.append({
                    "factor": "dependent_on_receipts",
                    "detail": f"Need {shortfall} shares from pending receipts",
                    "severity": "medium"
                })
                risk_score += 30
            else:
                risk_items.append({
                    "factor": "insufficient_position",
                    "detail": f"Short {quantity - available - pending_receipts} shares",
                    "severity": "high"
                })
                risk_score += 60

    # Counterparty risk
    cpty_rating = counterparty_info.get("credit_rating", "A")
    cpty_risk = risk_factors.get("counterparty_ratings", {}).get(cpty_rating, 10)
    risk_score += cpty_risk

    # Large trade risk
    if quantity > 100000:
        risk_items.append({
            "factor": "large_trade",
            "detail": f"Large quantity: {quantity}",
            "severity": "low"
        })
        risk_score += 5

    fail_probability = min(100, risk_score)

    return {
        "fail_probability": fail_probability,
        "fail_risk_level": "high" if fail_probability > 50 else "medium" if fail_probability > 20 else "low",
        "risk_items": risk_items
    }


def validate_settlement_instructions(
    settlement_instructions: Dict,
    counterparty_info: Dict,
    instruction_rules: Dict
) -> Dict[str, Any]:
    """Validate settlement instructions."""
    issues = []

    required_fields = instruction_rules.get("required_fields", ["account", "agent"])

    for field in required_fields:
        if field not in settlement_instructions:
            issues.append(f"Missing required field: {field}")

    # Validate agent
    valid_agents = instruction_rules.get("valid_agents", ["DTC", "FED"])
    agent = settlement_instructions.get("agent", "")
    if agent and agent not in valid_agents:
        issues.append(f"Invalid settlement agent: {agent}")

    return {
        "valid": len(issues) == 0,
        "issues": issues,
        "instructions": settlement_instructions
    }


def process_settlement(
    trade_id: str,
    trade_details: Dict,
    counterparty_info: Dict,
    security_info: Dict,
    position_data: Dict,
    settlement_instructions: Dict
) -> Dict[str, Any]:
    """
    Process securities trade settlement.

    Business Rules:
    1. Trade matching validation
    2. Settlement date calculation
    3. Obligation netting
    4. Fail risk assessment

    Args:
        trade_id: Trade identifier
        trade_details: Trade information
        counterparty_info: Counterparty details
        security_info: Security details
        position_data: Current positions
        settlement_instructions: SSI information

    Returns:
        Settlement processing results
    """
    rules = load_settlement_rules()

    # Calculate settlement date
    trade_date = trade_details.get("trade_date", datetime.now().strftime("%Y-%m-%d"))
    security_type = security_info.get("type", "equity")

    settlement_date = calculate_settlement_date(
        trade_date,
        security_type,
        rules.get("settlement_cycles", {})
    )

    # Validate matching
    matching_status = validate_trade_matching(
        trade_details,
        counterparty_info,
        rules.get("matching_rules", {})
    )

    # Calculate obligations
    net_obligation = calculate_net_obligation(
        trade_details,
        security_info,
        position_data
    )

    # Assess fail risk
    fail_risk = assess_fail_risk(
        trade_details,
        position_data,
        counterparty_info,
        rules.get("risk_factors", {})
    )

    # Validate instructions
    instruction_validation = validate_settlement_instructions(
        settlement_instructions,
        counterparty_info,
        rules.get("instruction_rules", {})
    )

    # Determine overall status
    if matching_status["status"] != "MATCHED":
        settlement_status = "UNMATCHED"
    elif not instruction_validation["valid"]:
        settlement_status = "INSTRUCTION_ISSUE"
    elif fail_risk["fail_risk_level"] == "high":
        settlement_status = "AT_RISK"
    else:
        settlement_status = "READY_TO_SETTLE"

    return {
        "trade_id": trade_id,
        "settlement_status": settlement_status,
        "settlement_date": settlement_date,
        "trade_date": trade_date,
        "net_obligation": net_obligation,
        "matching_status": matching_status,
        "fail_risk": fail_risk,
        "instruction_status": instruction_validation,
        "security": {
            "cusip": security_info.get("cusip"),
            "type": security_type
        }
    }


if __name__ == "__main__":
    import json
    result = process_settlement(
        trade_id="TRD-2026-001",
        trade_details={
            "side": "buy",
            "quantity": 1000,
            "price": 150.50,
            "trade_date": "2026-01-20"
        },
        counterparty_info={"id": "CPTY-001", "dtc_number": "0123", "credit_rating": "AA"},
        security_info={"cusip": "037833100", "type": "equity"},
        position_data={"available": 0, "pending_receipts": 1000},
        settlement_instructions={"account": "12345", "agent": "DTC"}
    )
    print(json.dumps(result, indent=2))
