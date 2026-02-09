"""
Pricing Anomaly Analysis Module

Implements pricing anomaly detection using
statistical methods and business rule validation.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
import math



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


def load_pricing_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    anomaly_detection_thresholds_data = load_key_value_csv("anomaly_detection_thresholds.csv")
    statistical_parameters_data = load_key_value_csv("statistical_parameters.csv")
    anomaly_categories_data = load_csv_as_dict("anomaly_categories.csv")
    product_category_rules_data = load_csv_as_dict("product_category_rules.csv")
    customer_segment_pricing_data = load_csv_as_dict("customer_segment_pricing.csv")
    approval_thresholds_data = load_key_value_csv("approval_thresholds.csv")
    time_based_patterns_data = load_csv_as_dict("time_based_patterns.csv")
    params = load_parameters()
    return {
        "anomaly_detection_thresholds": anomaly_detection_thresholds_data,
        "statistical_parameters": statistical_parameters_data,
        "anomaly_categories": anomaly_categories_data,
        "product_category_rules": product_category_rules_data,
        "customer_segment_pricing": customer_segment_pricing_data,
        "approval_thresholds": approval_thresholds_data,
        "time_based_patterns": time_based_patterns_data,
        **params
    }


def calculate_statistics(
    prices: List[float]
) -> Dict[str, Any]:
    """Calculate statistical measures for price distribution."""
    if not prices or len(prices) < 2:
        return {"error": "Insufficient data"}

    n = len(prices)
    mean = sum(prices) / n
    variance = sum((x - mean) ** 2 for x in prices) / (n - 1)
    std_dev = math.sqrt(variance)

    sorted_prices = sorted(prices)
    median = sorted_prices[n // 2] if n % 2 == 1 else (sorted_prices[n // 2 - 1] + sorted_prices[n // 2]) / 2

    q1_idx = n // 4
    q3_idx = (3 * n) // 4
    q1 = sorted_prices[q1_idx]
    q3 = sorted_prices[q3_idx]
    iqr = q3 - q1

    return {
        "mean": round(mean, 2),
        "median": round(median, 2),
        "std_dev": round(std_dev, 2),
        "q1": round(q1, 2),
        "q3": round(q3, 2),
        "iqr": round(iqr, 2),
        "sample_size": n
    }


def calculate_z_score(
    value: float,
    mean: float,
    std_dev: float
) -> float:
    """Calculate z-score for a value."""
    if std_dev == 0:
        return 0
    return (value - mean) / std_dev


def detect_statistical_anomalies(
    transaction_price: float,
    historical_stats: Dict,
    thresholds: Dict
) -> Dict[str, Any]:
    """Detect anomalies using statistical methods."""
    anomalies = []

    mean = historical_stats.get("mean", 0)
    std_dev = historical_stats.get("std_dev", 1)
    q1 = historical_stats.get("q1", 0)
    q3 = historical_stats.get("q3", 0)
    iqr = historical_stats.get("iqr", 0)

    # Z-score test
    z_score = calculate_z_score(transaction_price, mean, std_dev)
    z_threshold = thresholds.get("z_score_threshold", 2.5)

    if abs(z_score) > z_threshold:
        anomalies.append({
            "test": "z_score",
            "value": round(z_score, 2),
            "threshold": z_threshold,
            "direction": "high" if z_score > 0 else "low"
        })

    # IQR test
    iqr_multiplier = thresholds.get("iqr_multiplier", 1.5)
    lower_bound = q1 - (iqr_multiplier * iqr)
    upper_bound = q3 + (iqr_multiplier * iqr)

    if transaction_price < lower_bound or transaction_price > upper_bound:
        anomalies.append({
            "test": "iqr",
            "lower_bound": round(lower_bound, 2),
            "upper_bound": round(upper_bound, 2),
            "transaction_price": transaction_price,
            "direction": "high" if transaction_price > upper_bound else "low"
        })

    return {
        "z_score": round(z_score, 2),
        "statistical_anomalies": anomalies,
        "is_anomaly": len(anomalies) > 0
    }


def check_discount_compliance(
    list_price: float,
    transaction_price: float,
    customer_segment: str,
    segment_rules: Dict,
    approval_thresholds: Dict
) -> Dict[str, Any]:
    """Check if discount complies with policies."""
    discount_pct = (list_price - transaction_price) / list_price if list_price > 0 else 0

    segment_config = segment_rules.get(customer_segment, segment_rules.get("smb", {}))
    allowed_discount = segment_config.get("discount_tier", 0.10)

    # Determine approval level needed
    if discount_pct <= approval_thresholds.get("auto_approve_discount_pct", 0.10):
        approval_needed = "auto_approved"
    elif discount_pct <= approval_thresholds.get("manager_approval_discount_pct", 0.20):
        approval_needed = "manager"
    elif discount_pct <= approval_thresholds.get("director_approval_discount_pct", 0.30):
        approval_needed = "director"
    elif discount_pct <= approval_thresholds.get("vp_approval_discount_pct", 0.40):
        approval_needed = "vp"
    else:
        approval_needed = "executive"

    return {
        "list_price": list_price,
        "transaction_price": transaction_price,
        "discount_pct": round(discount_pct * 100, 1),
        "customer_segment": customer_segment,
        "allowed_discount_pct": round(allowed_discount * 100, 1),
        "discount_within_policy": discount_pct <= allowed_discount,
        "approval_level_required": approval_needed
    }


def check_margin_threshold(
    transaction_price: float,
    cost: float,
    min_margin_pct: float = 0.15
) -> Dict[str, Any]:
    """Check if transaction margin is acceptable."""
    if transaction_price <= 0:
        return {"error": "Invalid transaction price"}

    margin = transaction_price - cost
    margin_pct = margin / transaction_price

    return {
        "transaction_price": transaction_price,
        "cost": cost,
        "margin": round(margin, 2),
        "margin_pct": round(margin_pct * 100, 1),
        "min_margin_pct": min_margin_pct * 100,
        "margin_acceptable": margin_pct >= min_margin_pct,
        "margin_gap": round((margin_pct - min_margin_pct) * 100, 1)
    }


def check_volume_discount_alignment(
    quantity: int,
    unit_price: float,
    volume_tiers: List[Dict]
) -> Dict[str, Any]:
    """Check if volume discount is properly applied."""
    expected_price = None
    expected_tier = None

    for tier in sorted(volume_tiers, key=lambda x: x.get("min_qty", 0), reverse=True):
        if quantity >= tier.get("min_qty", 0):
            expected_price = tier.get("unit_price", unit_price)
            expected_tier = tier.get("tier_name", "unknown")
            break

    if expected_price is None:
        return {"volume_discount_check": "no_applicable_tier"}

    price_difference = unit_price - expected_price
    is_aligned = abs(price_difference) < 0.01

    return {
        "quantity": quantity,
        "actual_unit_price": unit_price,
        "expected_unit_price": expected_price,
        "expected_tier": expected_tier,
        "price_difference": round(price_difference, 2),
        "volume_discount_aligned": is_aligned,
        "potential_revenue_impact": round(price_difference * quantity, 2)
    }


def categorize_anomaly(
    anomaly_findings: Dict,
    categories: Dict
) -> List[Dict]:
    """Categorize detected anomalies."""
    detected_categories = []

    if anomaly_findings.get("statistical", {}).get("is_anomaly"):
        detected_categories.append({
            "category": "price_outlier",
            **categories.get("price_outlier", {})
        })

    if not anomaly_findings.get("discount", {}).get("discount_within_policy", True):
        detected_categories.append({
            "category": "unusual_discount",
            **categories.get("unusual_discount", {})
        })

    if not anomaly_findings.get("margin", {}).get("margin_acceptable", True):
        detected_categories.append({
            "category": "margin_erosion",
            **categories.get("margin_erosion", {})
        })

    if not anomaly_findings.get("volume", {}).get("volume_discount_aligned", True):
        detected_categories.append({
            "category": "volume_price_mismatch",
            **categories.get("volume_price_mismatch", {})
        })

    return detected_categories


def analyze_pricing_anomaly(
    transaction_id: str,
    transaction_price: float,
    list_price: float,
    cost: float,
    quantity: int,
    customer_segment: str,
    product_category: str,
    historical_prices: List[float],
    volume_tiers: List[Dict],
    analysis_date: str
) -> Dict[str, Any]:
    """
    Analyze transaction for pricing anomalies.

    Business Rules:
    1. Statistical outlier detection
    2. Discount policy compliance
    3. Margin threshold validation
    4. Volume discount alignment

    Args:
        transaction_id: Transaction identifier
        transaction_price: Actual transaction price
        list_price: List price
        cost: Product cost
        quantity: Transaction quantity
        customer_segment: Customer segment
        product_category: Product category
        historical_prices: Historical price data
        volume_tiers: Volume discount tiers
        analysis_date: Analysis date

    Returns:
        Pricing anomaly analysis results
    """
    rules = load_pricing_rules()

    # Calculate historical statistics
    historical_stats = calculate_statistics(historical_prices)

    # Statistical anomaly detection
    statistical_check = detect_statistical_anomalies(
        transaction_price,
        historical_stats,
        rules.get("statistical_parameters", {})
    )

    # Discount compliance check
    discount_check = check_discount_compliance(
        list_price,
        transaction_price,
        customer_segment,
        rules.get("customer_segment_pricing", {}),
        rules.get("approval_thresholds", {})
    )

    # Margin check
    margin_check = check_margin_threshold(
        transaction_price,
        cost,
        rules.get("anomaly_detection_thresholds", {}).get("margin_deviation_pct", 0.10)
    )

    # Volume discount check
    volume_check = check_volume_discount_alignment(
        quantity,
        transaction_price / quantity if quantity > 0 else transaction_price,
        volume_tiers
    )

    # Aggregate findings
    anomaly_findings = {
        "statistical": statistical_check,
        "discount": discount_check,
        "margin": margin_check,
        "volume": volume_check
    }

    # Categorize anomalies
    anomaly_categories = categorize_anomaly(
        anomaly_findings,
        rules.get("anomaly_categories", {})
    )

    # Determine overall status
    has_anomaly = len(anomaly_categories) > 0
    high_severity = any(a.get("severity") == "high" for a in anomaly_categories)

    return {
        "transaction_id": transaction_id,
        "analysis_date": analysis_date,
        "transaction_details": {
            "price": transaction_price,
            "list_price": list_price,
            "quantity": quantity,
            "customer_segment": customer_segment,
            "product_category": product_category
        },
        "historical_statistics": historical_stats,
        "anomaly_checks": anomaly_findings,
        "detected_anomalies": anomaly_categories,
        "summary": {
            "anomaly_detected": has_anomaly,
            "anomaly_count": len(anomaly_categories),
            "highest_severity": "high" if high_severity else "medium" if anomaly_categories else "none",
            "requires_review": has_anomaly and high_severity,
            "auto_flagged": any(a.get("auto_flag", False) for a in anomaly_categories)
        }
    }


if __name__ == "__main__":
    import json
    result = analyze_pricing_anomaly(
        transaction_id="TXN-001",
        transaction_price=850,
        list_price=1000,
        cost=600,
        quantity=10,
        customer_segment="mid_market",
        product_category="specialty",
        historical_prices=[950, 980, 920, 960, 940, 970, 930, 950, 945, 955],
        volume_tiers=[
            {"tier_name": "standard", "min_qty": 1, "unit_price": 100},
            {"tier_name": "volume_10", "min_qty": 10, "unit_price": 90},
            {"tier_name": "volume_50", "min_qty": 50, "unit_price": 80}
        ],
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
