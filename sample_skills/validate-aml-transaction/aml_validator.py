"""
AML Transaction Validation Module

Implements anti-money laundering transaction screening
using risk scoring, pattern detection, and regulatory thresholds.
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


def load_aml_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    transaction_thresholds_data = load_key_value_csv("transaction_thresholds.csv")
    risk_scoring_data = load_csv_as_dict("risk_scoring.csv")
    red_flags_data = load_csv_as_dict("red_flags.csv")
    alert_thresholds_data = load_csv_as_dict("alert_thresholds.csv")
    velocity_rules_data = load_key_value_csv("velocity_rules.csv")
    params = load_parameters()
    return {
        "transaction_thresholds": transaction_thresholds_data,
        "risk_scoring": risk_scoring_data,
        "red_flags": red_flags_data,
        "alert_thresholds": alert_thresholds_data,
        "velocity_rules": velocity_rules_data,
        **params
    }


def calculate_customer_risk_score(
    customer_data: Dict,
    risk_config: Dict
) -> Dict[str, Any]:
    """Calculate customer risk score."""
    score = 0
    risk_factors = []

    # Check high-risk country
    country = customer_data.get("country", "")
    high_risk_countries = risk_config.get("high_risk_countries", [])
    if country in high_risk_countries:
        factor_score = risk_config.get("customer_risk", {}).get("high_risk_countries", 30)
        score += factor_score
        risk_factors.append({"factor": "high_risk_country", "score": factor_score})

    # Check PEP status
    if customer_data.get("is_pep", False):
        factor_score = risk_config.get("customer_risk", {}).get("pep_status", 25)
        score += factor_score
        risk_factors.append({"factor": "pep_status", "score": factor_score})

    # Check industry
    industry = customer_data.get("industry", "")
    high_risk_industries = risk_config.get("high_risk_industries", [])
    if industry in high_risk_industries:
        factor_score = risk_config.get("customer_risk", {}).get("high_risk_industry", 20)
        score += factor_score
        risk_factors.append({"factor": "high_risk_industry", "score": factor_score})

    # Check adverse media
    if customer_data.get("adverse_media", False):
        factor_score = risk_config.get("customer_risk", {}).get("adverse_media", 15)
        score += factor_score
        risk_factors.append({"factor": "adverse_media", "score": factor_score})

    # Check if new customer
    account_age_days = customer_data.get("account_age_days", 365)
    if account_age_days < 90:
        factor_score = risk_config.get("customer_risk", {}).get("new_customer", 10)
        score += factor_score
        risk_factors.append({"factor": "new_customer", "score": factor_score})

    return {
        "customer_risk_score": min(score, 100),
        "risk_factors": risk_factors
    }


def calculate_transaction_risk_score(
    transaction: Dict,
    risk_config: Dict
) -> Dict[str, Any]:
    """Calculate transaction risk score."""
    score = 0
    risk_factors = []
    transaction_risk = risk_config.get("transaction_risk", {})

    # Cash transaction
    if transaction.get("is_cash", False):
        factor_score = transaction_risk.get("cash_transaction", 15)
        score += factor_score
        risk_factors.append({"factor": "cash_transaction", "score": factor_score})

    # International wire
    if transaction.get("is_international", False):
        factor_score = transaction_risk.get("international_wire", 20)
        score += factor_score
        risk_factors.append({"factor": "international_wire", "score": factor_score})

    # Cryptocurrency
    if transaction.get("is_crypto", False):
        factor_score = transaction_risk.get("cryptocurrency", 25)
        score += factor_score
        risk_factors.append({"factor": "cryptocurrency", "score": factor_score})

    # High value
    thresholds = risk_config.get("transaction_thresholds", {})
    if transaction.get("amount", 0) >= thresholds.get("ctr_threshold", 10000):
        factor_score = transaction_risk.get("high_value", 15)
        score += factor_score
        risk_factors.append({"factor": "high_value", "score": factor_score})

    # Round amount
    amount = transaction.get("amount", 0)
    if amount > 0 and amount % 1000 == 0:
        factor_score = transaction_risk.get("round_amount", 5)
        score += factor_score
        risk_factors.append({"factor": "round_amount", "score": factor_score})

    return {
        "transaction_risk_score": min(score, 100),
        "risk_factors": risk_factors
    }


def calculate_geographic_risk_score(
    countries_involved: List[str],
    risk_config: Dict
) -> Dict[str, Any]:
    """Calculate geographic risk score."""
    score = 0
    risk_factors = []
    geo_risk = risk_config.get("geographic_risk", {})

    high_risk = risk_config.get("high_risk_countries", [])
    greylist = risk_config.get("fatf_greylist", [])

    for country in countries_involved:
        if country in high_risk:
            factor_score = geo_risk.get("fatf_blacklist", 40)
            score += factor_score
            risk_factors.append({"factor": f"blacklist_country_{country}", "score": factor_score})
        elif country in greylist:
            factor_score = geo_risk.get("fatf_greylist", 25)
            score += factor_score
            risk_factors.append({"factor": f"greylist_country_{country}", "score": factor_score})

    return {
        "geographic_risk_score": min(score, 100),
        "risk_factors": risk_factors
    }


def detect_structuring(
    transaction: Dict,
    recent_transactions: List[Dict],
    thresholds: Dict
) -> Dict[str, Any]:
    """Detect potential structuring activity."""
    ctr_threshold = thresholds.get("ctr_threshold", 10000)
    structuring_window = thresholds.get("structuring_window_hours", 24)
    structuring_count = thresholds.get("structuring_count", 3)

    current_amount = transaction.get("amount", 0)
    current_time = datetime.strptime(transaction.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")

    # Check for transactions just below threshold
    suspicious_transactions = []
    window_start = current_time - timedelta(hours=structuring_window)

    for txn in recent_transactions:
        txn_amount = txn.get("amount", 0)
        txn_time = datetime.strptime(txn.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")

        # Transaction within window and just below threshold
        if txn_time >= window_start:
            if ctr_threshold * 0.8 <= txn_amount < ctr_threshold:
                suspicious_transactions.append(txn)

    # Include current transaction if it fits pattern
    if ctr_threshold * 0.8 <= current_amount < ctr_threshold:
        suspicious_transactions.append(transaction)

    is_structuring = len(suspicious_transactions) >= structuring_count

    return {
        "structuring_detected": is_structuring,
        "suspicious_transaction_count": len(suspicious_transactions),
        "window_hours": structuring_window,
        "total_suspicious_amount": sum(t.get("amount", 0) for t in suspicious_transactions)
    }


def check_velocity(
    customer_id: str,
    recent_transactions: List[Dict],
    velocity_rules: Dict
) -> Dict[str, Any]:
    """Check transaction velocity against limits."""
    violations = []

    # Daily checks
    daily_count = len(recent_transactions)
    daily_amount = sum(t.get("amount", 0) for t in recent_transactions)

    if daily_count > velocity_rules.get("daily_transaction_count", 10):
        violations.append({
            "rule": "daily_transaction_count",
            "actual": daily_count,
            "limit": velocity_rules.get("daily_transaction_count", 10)
        })

    if daily_amount > velocity_rules.get("daily_amount_threshold", 50000):
        violations.append({
            "rule": "daily_amount_threshold",
            "actual": daily_amount,
            "limit": velocity_rules.get("daily_amount_threshold", 50000)
        })

    return {
        "velocity_violations": violations,
        "daily_transaction_count": daily_count,
        "daily_transaction_amount": daily_amount
    }


def detect_red_flags(
    transaction: Dict,
    customer_data: Dict,
    recent_transactions: List[Dict],
    red_flag_config: Dict
) -> List[Dict]:
    """Detect red flags in transaction."""
    detected_flags = []

    # Check for unusual volume
    avg_transaction = customer_data.get("avg_transaction_amount", 1000)
    if transaction.get("amount", 0) > avg_transaction * 5:
        detected_flags.append({
            "flag": "unusual_volume",
            "severity": red_flag_config.get("unusual_volume", {}).get("severity", "medium"),
            "description": red_flag_config.get("unusual_volume", {}).get("description", "")
        })

    # Check for rapid movement
    if recent_transactions:
        recent_amounts = sum(t.get("amount", 0) for t in recent_transactions)
        if recent_amounts > customer_data.get("monthly_avg_volume", 10000) * 3:
            detected_flags.append({
                "flag": "rapid_movement",
                "severity": red_flag_config.get("rapid_movement", {}).get("severity", "high"),
                "description": red_flag_config.get("rapid_movement", {}).get("description", "")
            })

    return detected_flags


def determine_alert_action(
    total_score: float,
    alert_thresholds: Dict
) -> Dict[str, Any]:
    """Determine alert action based on score."""
    for level, config in alert_thresholds.items():
        if config["min_score"] <= total_score < config["max_score"]:
            return {
                "alert_level": level.upper(),
                "recommended_action": config["action"],
                "score_range": f"{config['min_score']}-{config['max_score']}"
            }

    return {
        "alert_level": "CRITICAL",
        "recommended_action": "block_and_report"
    }


def validate_aml_transaction(
    transaction_id: str,
    transaction: Dict,
    customer_data: Dict,
    recent_transactions: List[Dict],
    countries_involved: List[str],
    validation_timestamp: str
) -> Dict[str, Any]:
    """
    Validate transaction for AML compliance.

    Business Rules:
    1. Customer risk scoring (PEP, country, industry)
    2. Transaction risk assessment
    3. Structuring detection
    4. Velocity monitoring

    Args:
        transaction_id: Transaction identifier
        transaction: Transaction details
        customer_data: Customer profile data
        recent_transactions: Recent transaction history
        countries_involved: Countries in transaction
        validation_timestamp: Validation timestamp

    Returns:
        AML validation results
    """
    rules = load_aml_rules()

    # Calculate risk scores
    customer_risk = calculate_customer_risk_score(customer_data, rules)
    transaction_risk = calculate_transaction_risk_score(transaction, rules)
    geographic_risk = calculate_geographic_risk_score(countries_involved, rules)

    # Detect structuring
    structuring = detect_structuring(
        transaction,
        recent_transactions,
        rules.get("transaction_thresholds", {})
    )

    # Check velocity
    velocity = check_velocity(
        customer_data.get("customer_id", ""),
        recent_transactions,
        rules.get("velocity_rules", {})
    )

    # Detect red flags
    red_flags = detect_red_flags(
        transaction,
        customer_data,
        recent_transactions,
        rules.get("red_flags", {})
    )

    # Calculate total risk score
    total_score = (
        customer_risk["customer_risk_score"] * 0.30 +
        transaction_risk["transaction_risk_score"] * 0.35 +
        geographic_risk["geographic_risk_score"] * 0.35
    )

    # Add structuring penalty
    if structuring["structuring_detected"]:
        total_score = min(100, total_score + 25)

    # Determine action
    alert_action = determine_alert_action(
        total_score,
        rules.get("alert_thresholds", {})
    )

    # Check CTR requirement
    ctr_required = transaction.get("amount", 0) >= rules.get("transaction_thresholds", {}).get("ctr_threshold", 10000)

    return {
        "transaction_id": transaction_id,
        "validation_timestamp": validation_timestamp,
        "transaction_amount": transaction.get("amount", 0),
        "risk_scores": {
            "customer": customer_risk,
            "transaction": transaction_risk,
            "geographic": geographic_risk,
            "total": round(total_score, 1)
        },
        "structuring_analysis": structuring,
        "velocity_analysis": velocity,
        "red_flags": red_flags,
        "alert": alert_action,
        "regulatory_requirements": {
            "ctr_required": ctr_required,
            "sar_consideration": total_score >= 60
        },
        "decision": "BLOCK" if alert_action["alert_level"] == "CRITICAL" else "REVIEW" if alert_action["alert_level"] == "HIGH" else "APPROVE"
    }


if __name__ == "__main__":
    import json
    result = validate_aml_transaction(
        transaction_id="TXN-001",
        transaction={
            "amount": 9500,
            "is_cash": True,
            "is_international": False,
            "timestamp": "2026-01-20 14:30:00"
        },
        customer_data={
            "customer_id": "CUST-001",
            "country": "US",
            "is_pep": False,
            "industry": "retail",
            "account_age_days": 45,
            "avg_transaction_amount": 2000
        },
        recent_transactions=[
            {"amount": 9200, "timestamp": "2026-01-20 10:00:00"},
            {"amount": 9000, "timestamp": "2026-01-19 16:00:00"}
        ],
        countries_involved=["US"],
        validation_timestamp="2026-01-20 14:30:00"
    )
    print(json.dumps(result, indent=2))
