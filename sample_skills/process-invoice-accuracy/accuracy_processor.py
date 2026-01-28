"""
Invoice Accuracy Processing Module

Implements invoice validation and accuracy assessment including
matching, tolerance checks, and exception handling.
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


def load_validation_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    validation_categories_data = load_csv_as_dict("validation_categories.csv")
    tolerance_thresholds_data = load_csv_as_dict("tolerance_thresholds.csv")
    matching_rules_data = load_csv_as_dict("matching_rules.csv")
    exception_types_data = load_csv_as_dict("exception_types.csv")
    accuracy_metrics_data = load_csv_as_dict("accuracy_metrics.csv")
    fraud_indicators_data = load_csv_as_dict("fraud_indicators.csv")
    approval_matrix_data = load_csv_as_dict("approval_matrix.csv")
    params = load_parameters()
    return {
        "validation_categories": validation_categories_data,
        "tolerance_thresholds": tolerance_thresholds_data,
        "matching_rules": matching_rules_data,
        "exception_types": exception_types_data,
        "accuracy_metrics": accuracy_metrics_data,
        "fraud_indicators": fraud_indicators_data,
        "approval_matrix": approval_matrix_data,
        **params
    }


def validate_header(
    invoice_header: Dict,
    validation_checks: List[str]
) -> Dict[str, Any]:
    """Validate invoice header fields."""
    results = []
    all_passed = True

    for check in validation_checks:
        value = invoice_header.get(check)
        passed = value is not None and value != ""

        results.append({
            "field": check,
            "value": value,
            "passed": passed
        })

        if not passed:
            all_passed = False

    return {
        "validation_type": "header",
        "checks_performed": len(results),
        "all_passed": all_passed,
        "results": results
    }


def validate_line_items(
    line_items: List[Dict],
    validation_checks: List[str]
) -> Dict[str, Any]:
    """Validate invoice line items."""
    line_results = []
    total_issues = 0

    for i, line in enumerate(line_items):
        line_issues = []

        for check in validation_checks:
            value = line.get(check)

            if check in ["quantity", "unit_price", "extended_amount"]:
                passed = value is not None and value >= 0
            else:
                passed = value is not None and value != ""

            if not passed:
                line_issues.append({
                    "field": check,
                    "value": value,
                    "issue": f"Invalid or missing {check}"
                })
                total_issues += 1

        line_results.append({
            "line_number": i + 1,
            "issues": line_issues,
            "passed": len(line_issues) == 0
        })

    return {
        "validation_type": "line_items",
        "lines_checked": len(line_items),
        "lines_with_issues": sum(1 for r in line_results if not r["passed"]),
        "total_issues": total_issues,
        "results": line_results
    }


def check_price_tolerance(
    invoice_price: float,
    po_price: float,
    tolerance_config: Dict
) -> Dict[str, Any]:
    """Check price against tolerance thresholds."""
    if po_price <= 0:
        return {"error": "Invalid PO price"}

    variance = invoice_price - po_price
    variance_pct = abs(variance) / po_price

    pct_threshold = tolerance_config.get("percentage", 0.02)
    abs_threshold = tolerance_config.get("absolute_max", 100)

    within_pct = variance_pct <= pct_threshold
    within_abs = abs(variance) <= abs_threshold

    passed = within_pct or within_abs
    action = tolerance_config.get("action_if_exceeded", "flag_for_review") if not passed else "none"

    return {
        "invoice_price": invoice_price,
        "po_price": po_price,
        "variance": round(variance, 2),
        "variance_pct": round(variance_pct * 100, 2),
        "pct_threshold": pct_threshold * 100,
        "abs_threshold": abs_threshold,
        "within_tolerance": passed,
        "action": action
    }


def check_quantity_tolerance(
    invoice_qty: float,
    received_qty: float,
    tolerance_config: Dict
) -> Dict[str, Any]:
    """Check quantity against tolerance thresholds."""
    if received_qty <= 0:
        return {"error": "Invalid received quantity"}

    variance = invoice_qty - received_qty
    variance_pct = abs(variance) / received_qty

    pct_threshold = tolerance_config.get("percentage", 0.05)
    abs_threshold = tolerance_config.get("absolute_max", 10)

    within_pct = variance_pct <= pct_threshold
    within_abs = abs(variance) <= abs_threshold

    passed = within_pct or within_abs
    action = tolerance_config.get("action_if_exceeded", "flag_for_review") if not passed else "none"

    return {
        "invoice_qty": invoice_qty,
        "received_qty": received_qty,
        "variance": round(variance, 2),
        "variance_pct": round(variance_pct * 100, 2),
        "pct_threshold": pct_threshold * 100,
        "abs_threshold": abs_threshold,
        "within_tolerance": passed,
        "action": action
    }


def perform_matching(
    invoice_data: Dict,
    po_data: Dict,
    receipt_data: Optional[Dict],
    matching_rules: Dict
) -> Dict[str, Any]:
    """Perform invoice matching (2-way or 3-way)."""
    match_type = "three_way_match" if receipt_data else "two_way_match"
    match_config = matching_rules.get(match_type, {})

    match_results = {
        "match_type": match_type,
        "description": match_config.get("description", ""),
        "po_match": None,
        "receipt_match": None,
        "overall_match": True
    }

    # PO match
    invoice_total = invoice_data.get("total_amount", 0)
    po_total = po_data.get("total_amount", 0)

    po_variance = abs(invoice_total - po_total)
    po_variance_pct = po_variance / po_total if po_total > 0 else 0

    po_match_passed = po_variance_pct <= 0.02 or po_variance <= 50  # 2% or $50
    match_results["po_match"] = {
        "invoice_total": invoice_total,
        "po_total": po_total,
        "variance": round(po_variance, 2),
        "variance_pct": round(po_variance_pct * 100, 2),
        "matched": po_match_passed
    }

    if not po_match_passed:
        match_results["overall_match"] = False

    # Receipt match (3-way only)
    if receipt_data:
        invoice_qty = sum(item.get("quantity", 0) for item in invoice_data.get("line_items", []))
        received_qty = sum(item.get("quantity", 0) for item in receipt_data.get("line_items", []))

        qty_variance = abs(invoice_qty - received_qty)
        qty_variance_pct = qty_variance / received_qty if received_qty > 0 else 0

        receipt_match_passed = qty_variance_pct <= 0.05 or qty_variance <= 10
        match_results["receipt_match"] = {
            "invoice_qty": invoice_qty,
            "received_qty": received_qty,
            "variance": round(qty_variance, 2),
            "variance_pct": round(qty_variance_pct * 100, 2),
            "matched": receipt_match_passed
        }

        if not receipt_match_passed:
            match_results["overall_match"] = False

    return match_results


def check_for_duplicates(
    invoice_data: Dict,
    historical_invoices: List[Dict]
) -> Dict[str, Any]:
    """Check for duplicate invoices."""
    invoice_number = invoice_data.get("invoice_number", "")
    vendor_id = invoice_data.get("vendor_id", "")
    invoice_date = invoice_data.get("invoice_date", "")
    invoice_amount = invoice_data.get("total_amount", 0)

    potential_duplicates = []

    for hist in historical_invoices:
        # Same invoice number from same vendor
        if hist.get("invoice_number") == invoice_number and hist.get("vendor_id") == vendor_id:
            potential_duplicates.append({
                "match_type": "exact_invoice_number",
                "historical_invoice_id": hist.get("invoice_id", ""),
                "confidence": 1.0
            })
            continue

        # Same amount, same vendor, same date
        if (hist.get("total_amount") == invoice_amount and
            hist.get("vendor_id") == vendor_id and
            hist.get("invoice_date") == invoice_date):
            potential_duplicates.append({
                "match_type": "amount_vendor_date",
                "historical_invoice_id": hist.get("invoice_id", ""),
                "confidence": 0.9
            })

    is_duplicate = len(potential_duplicates) > 0

    return {
        "is_potential_duplicate": is_duplicate,
        "duplicate_count": len(potential_duplicates),
        "potential_duplicates": potential_duplicates
    }


def check_fraud_indicators(
    invoice_data: Dict,
    fraud_config: Dict
) -> List[Dict]:
    """Check for potential fraud indicators."""
    indicators = []

    amount = invoice_data.get("total_amount", 0)

    # Round amounts
    if amount > 0 and amount == int(amount) and amount >= 1000:
        indicators.append({
            "indicator": "ROUND_AMOUNT",
            "description": "Invoice amount is a round number",
            "value": amount,
            "risk_level": "LOW"
        })

    # Just under approval threshold (assuming $10,000 threshold)
    approval_threshold = 10000
    if 9500 <= amount < approval_threshold:
        indicators.append({
            "indicator": "JUST_UNDER_APPROVAL",
            "description": f"Amount just under ${approval_threshold} approval threshold",
            "value": amount,
            "risk_level": "MEDIUM"
        })

    # Unusual vendor (new vendor check would need more data)
    vendor_id = invoice_data.get("vendor_id", "")
    is_new_vendor = invoice_data.get("is_new_vendor", False)
    if is_new_vendor and amount >= fraud_config.get("unusual_vendor", {}).get("new_vendor_high_amount", 10000):
        indicators.append({
            "indicator": "NEW_VENDOR_HIGH_AMOUNT",
            "description": "High amount invoice from new vendor",
            "value": amount,
            "risk_level": "HIGH"
        })

    # Rush payment
    payment_terms = invoice_data.get("payment_terms_days", 30)
    if payment_terms <= fraud_config.get("rush_payment", {}).get("days_before_normal", 10):
        indicators.append({
            "indicator": "RUSH_PAYMENT",
            "description": f"Payment terms of {payment_terms} days is unusually short",
            "value": payment_terms,
            "risk_level": "MEDIUM"
        })

    return indicators


def calculate_accuracy_metrics(
    validation_results: Dict
) -> Dict[str, Any]:
    """Calculate overall accuracy metrics."""
    header_passed = validation_results.get("header_validation", {}).get("all_passed", False)
    line_issues = validation_results.get("line_validation", {}).get("total_issues", 0)
    match_passed = validation_results.get("matching", {}).get("overall_match", False)
    is_duplicate = validation_results.get("duplicate_check", {}).get("is_potential_duplicate", False)
    fraud_indicators = len(validation_results.get("fraud_indicators", []))

    # Calculate score
    score = 100
    if not header_passed:
        score -= 15
    score -= min(line_issues * 5, 25)
    if not match_passed:
        score -= 30
    if is_duplicate:
        score -= 20
    score -= min(fraud_indicators * 5, 15)

    score = max(0, score)

    # Determine status
    if score >= 95 and not is_duplicate and match_passed:
        status = "AUTO_APPROVE"
    elif score >= 70 and not is_duplicate:
        status = "REVIEW_REQUIRED"
    elif is_duplicate:
        status = "DUPLICATE_HOLD"
    else:
        status = "REJECT"

    return {
        "accuracy_score": score,
        "status": status,
        "header_valid": header_passed,
        "lines_valid": line_issues == 0,
        "matching_passed": match_passed,
        "duplicate_flag": is_duplicate,
        "fraud_indicator_count": fraud_indicators
    }


def process_invoice_accuracy(
    invoice_id: str,
    invoice_data: Dict,
    po_data: Dict,
    receipt_data: Optional[Dict],
    historical_invoices: List[Dict],
    processing_date: str
) -> Dict[str, Any]:
    """
    Process invoice accuracy validation.

    Business Rules:
    1. Header and line item validation
    2. PO and receipt matching
    3. Duplicate detection
    4. Fraud indicator checking

    Args:
        invoice_id: Invoice identifier
        invoice_data: Invoice details
        po_data: Purchase order data
        receipt_data: Optional receipt data for 3-way match
        historical_invoices: Historical invoices for duplicate check
        processing_date: Processing date

    Returns:
        Invoice accuracy processing results
    """
    config = load_validation_rules()
    validation_categories = config.get("validation_categories", {})
    tolerance_thresholds = config.get("tolerance_thresholds", {})
    matching_rules = config.get("matching_rules", {})
    fraud_indicators_config = config.get("fraud_indicators", {})
    approval_matrix = config.get("approval_matrix", {})

    # Header validation
    header_checks = validation_categories.get("header_validation", {}).get("checks", [])
    header_validation = validate_header(invoice_data, header_checks)

    # Line item validation
    line_checks = validation_categories.get("line_item_validation", {}).get("checks", [])
    line_validation = validate_line_items(
        invoice_data.get("line_items", []),
        line_checks
    )

    # Matching
    matching = perform_matching(invoice_data, po_data, receipt_data, matching_rules)

    # Duplicate check
    duplicate_check = check_for_duplicates(invoice_data, historical_invoices)

    # Fraud indicators
    fraud_indicators = check_fraud_indicators(invoice_data, fraud_indicators_config)

    # Compile validation results
    validation_results = {
        "header_validation": header_validation,
        "line_validation": line_validation,
        "matching": matching,
        "duplicate_check": duplicate_check,
        "fraud_indicators": fraud_indicators
    }

    # Calculate accuracy metrics
    accuracy_metrics = calculate_accuracy_metrics(validation_results)

    # Determine approval level needed
    amount = invoice_data.get("total_amount", 0)
    required_approver = "auto_approve"
    # Sort by max_amount, treating empty/None as infinity
    def get_max_amount(x):
        val = x[1].get("max_amount")
        if val is None or val == "":
            return float('inf')
        return val
    for tier, tier_config in sorted(approval_matrix.items(), key=get_max_amount):
        max_amount = tier_config.get("max_amount")
        if max_amount is None or max_amount == "" or amount <= max_amount:
            required_approver = tier_config.get("approver", "vp_finance")
            break

    return {
        "invoice_id": invoice_id,
        "vendor_id": invoice_data.get("vendor_id", ""),
        "invoice_number": invoice_data.get("invoice_number", ""),
        "invoice_amount": invoice_data.get("total_amount", 0),
        "processing_date": processing_date,
        "validation_results": validation_results,
        "accuracy_metrics": accuracy_metrics,
        "approval": {
            "status": accuracy_metrics["status"],
            "required_approver": required_approver if accuracy_metrics["status"] != "AUTO_APPROVE" else "none",
            "auto_approved": accuracy_metrics["status"] == "AUTO_APPROVE"
        },
        "processing_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = process_invoice_accuracy(
        invoice_id="INV-2026-001234",
        invoice_data={
            "invoice_number": "VND-12345",
            "vendor_id": "V-001",
            "invoice_date": "2026-01-15",
            "due_date": "2026-02-15",
            "payment_terms": "Net 30",
            "currency": "USD",
            "total_amount": 15750.00,
            "payment_terms_days": 30,
            "is_new_vendor": False,
            "line_items": [
                {"item_description": "Widget A", "quantity": 100, "unit_price": 75.00, "extended_amount": 7500.00, "tax": 600.00},
                {"item_description": "Widget B", "quantity": 50, "unit_price": 150.00, "extended_amount": 7500.00, "tax": 600.00}
            ]
        },
        po_data={
            "po_number": "PO-2026-0500",
            "total_amount": 15600.00,
            "line_items": [
                {"quantity": 100, "unit_price": 74.00},
                {"quantity": 50, "unit_price": 148.00}
            ]
        },
        receipt_data={
            "receipt_number": "RCV-2026-0800",
            "line_items": [
                {"quantity": 100},
                {"quantity": 50}
            ]
        },
        historical_invoices=[
            {"invoice_id": "INV-2025-009000", "invoice_number": "VND-12340", "vendor_id": "V-001", "invoice_date": "2025-12-15", "total_amount": 12000.00}
        ],
        processing_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
