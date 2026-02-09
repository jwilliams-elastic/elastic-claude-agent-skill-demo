"""
Warranty Claim Processing Module

Implements warranty claim validation, coverage verification,
and resolution determination.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime



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


def load_warranty_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    coverage_terms_data = load_csv_as_dict("coverage_terms.csv")
    defect_categories_data = load_csv_as_dict("defect_categories.csv")
    resolution_matrix_data = load_csv_as_dict("resolution_matrix.csv")
    fraud_rules_data = load_key_value_csv("fraud_rules.csv")
    cost_tables_data = load_csv_as_dict("cost_tables.csv")
    sla_targets_data = load_key_value_csv("sla_targets.csv")
    params = load_parameters()
    return {
        "coverage_terms": coverage_terms_data,
        "defect_categories": defect_categories_data,
        "resolution_matrix": resolution_matrix_data,
        "fraud_rules": fraud_rules_data,
        "cost_tables": cost_tables_data,
        "sla_targets": sla_targets_data,
        **params
    }


def verify_coverage(
    product_info: Dict,
    purchase_info: Dict,
    coverage_terms: Dict
) -> Dict[str, Any]:
    """Verify warranty coverage is valid."""
    issues = []

    category = product_info.get("category", "general")
    purchase_date_str = product_info.get("purchase_date", "")

    # Get warranty period for category
    warranty_months = coverage_terms.get(category, {}).get("warranty_months", 12)

    try:
        purchase_date = datetime.strptime(purchase_date_str, "%Y-%m-%d")
        days_since_purchase = (datetime.now() - purchase_date).days
        months_since_purchase = days_since_purchase / 30.44
        within_warranty = months_since_purchase <= warranty_months
    except ValueError:
        within_warranty = False
        months_since_purchase = 0
        issues.append("Invalid or missing purchase date")

    # Verify proof of purchase
    has_receipt = purchase_info.get("receipt", False)
    if not has_receipt:
        issues.append("No proof of purchase provided")

    # Check for extended warranty
    has_extended = purchase_info.get("extended_warranty", False)
    if has_extended:
        warranty_months += coverage_terms.get("extended_months", 12)
        within_warranty = months_since_purchase <= warranty_months

    covered = within_warranty and has_receipt

    return {
        "covered": covered,
        "within_warranty_period": within_warranty,
        "warranty_months": warranty_months,
        "months_since_purchase": round(months_since_purchase, 1),
        "proof_of_purchase": has_receipt,
        "extended_warranty": has_extended,
        "issues": issues
    }


def classify_defect(
    defect_description: Dict,
    diagnostic_data: Dict,
    defect_categories: Dict
) -> Dict[str, Any]:
    """Classify the reported defect."""
    defect_type = defect_description.get("type", "unknown")
    symptom = defect_description.get("symptom", "")

    category_info = defect_categories.get(defect_type, defect_categories.get("unknown", {}))

    # Check if covered under warranty
    covered_defect = category_info.get("warranty_covered", True)

    # Determine severity
    severity = "low"
    if defect_type in ["malfunction", "safety"]:
        severity = "high"
    elif defect_type in ["performance", "intermittent"]:
        severity = "medium"

    # Check diagnostic data for additional classification
    classification_confidence = "medium"
    if diagnostic_data:
        error_code = diagnostic_data.get("error_code", "")
        if error_code:
            classification_confidence = "high"

    # Check for user-caused damage
    user_caused_indicators = ["dropped", "water", "physical", "misuse"]
    user_caused = any(ind in symptom.lower() for ind in user_caused_indicators)

    if user_caused:
        covered_defect = False

    return {
        "defect_type": defect_type,
        "symptom": symptom,
        "severity": severity,
        "covered_defect": covered_defect,
        "classification_confidence": classification_confidence,
        "user_caused": user_caused
    }


def determine_resolution(
    defect_classification: Dict,
    product_info: Dict,
    coverage_verification: Dict,
    resolution_matrix: Dict
) -> Dict[str, Any]:
    """Determine appropriate resolution for claim."""
    if not coverage_verification.get("covered"):
        return {
            "resolution_type": "DENIED",
            "reason": "Not covered under warranty",
            "customer_options": ["Out-of-warranty repair", "Trade-in program"]
        }

    if not defect_classification.get("covered_defect"):
        return {
            "resolution_type": "DENIED",
            "reason": "Defect type not covered",
            "customer_options": ["Paid repair service"]
        }

    defect_type = defect_classification.get("defect_type", "unknown")
    severity = defect_classification.get("severity", "low")
    category = product_info.get("category", "general")

    # Get resolution from matrix
    category_resolutions = resolution_matrix.get(category, resolution_matrix.get("default", {}))
    resolution_type = category_resolutions.get(severity, "repair")

    # Age-based adjustment
    months_owned = coverage_verification.get("months_since_purchase", 0)
    if months_owned < 3 and severity == "high":
        resolution_type = "replacement"

    # Build resolution details
    if resolution_type == "replacement":
        resolution = {
            "resolution_type": "REPLACEMENT",
            "action": "Replace with new or refurbished unit",
            "customer_options": ["Same model replacement", "Store credit"],
            "estimated_timeline_days": 5
        }
    elif resolution_type == "refund":
        resolution = {
            "resolution_type": "REFUND",
            "action": "Full or prorated refund",
            "customer_options": ["Refund to original payment", "Store credit"],
            "estimated_timeline_days": 7
        }
    else:
        resolution = {
            "resolution_type": "REPAIR",
            "action": "Repair under warranty",
            "customer_options": ["Mail-in repair", "Service center"],
            "estimated_timeline_days": 10
        }

    return resolution


def detect_fraud_patterns(
    customer_history: Dict,
    claim_details: Dict,
    fraud_rules: Dict
) -> List[Dict]:
    """Check for potential fraud indicators."""
    indicators = []

    prior_claims = customer_history.get("prior_claims", 0)
    max_claims_threshold = fraud_rules.get("max_claims_per_year", 3)

    if prior_claims >= max_claims_threshold:
        indicators.append({
            "indicator": "high_claim_frequency",
            "detail": f"{prior_claims} prior claims",
            "risk_level": "high"
        })

    # Check for pattern of same defect type
    # In production, would analyze historical claim data

    # Check for claims shortly after purchase
    months_since_purchase = claim_details.get("months_since_purchase", 0)
    if months_since_purchase < 0.5:  # Within 2 weeks
        indicators.append({
            "indicator": "very_early_claim",
            "detail": "Claim within first 2 weeks",
            "risk_level": "low"
        })

    return indicators


def estimate_claim_cost(
    resolution: Dict,
    product_info: Dict,
    cost_tables: Dict
) -> float:
    """Estimate cost of processing claim."""
    resolution_type = resolution.get("resolution_type", "REPAIR")
    category = product_info.get("category", "general")
    purchase_price = product_info.get("price", 0) or 500  # Default

    category_costs = cost_tables.get(category, cost_tables.get("default", {}))

    if resolution_type == "REPLACEMENT":
        cost = purchase_price * category_costs.get("replacement_cost_pct", 0.8)
    elif resolution_type == "REFUND":
        cost = purchase_price * category_costs.get("refund_cost_pct", 1.0)
    elif resolution_type == "REPAIR":
        cost = category_costs.get("avg_repair_cost", 75)
    else:
        cost = 0

    # Add processing cost
    cost += cost_tables.get("processing_cost", 15)

    return round(cost, 2)


def process_warranty_claim(
    claim_id: str,
    product_info: Dict,
    purchase_info: Dict,
    defect_description: Dict,
    customer_history: Dict,
    diagnostic_data: Dict
) -> Dict[str, Any]:
    """
    Process warranty claim.

    Business Rules:
    1. Coverage verification
    2. Defect classification
    3. Resolution determination
    4. Fraud pattern detection

    Args:
        claim_id: Claim identifier
        product_info: Product details
        purchase_info: Purchase information
        defect_description: Reported issue
        customer_history: Customer claim history
        diagnostic_data: Technical diagnostics

    Returns:
        Warranty claim processing results
    """
    rules = load_warranty_rules()

    # Verify coverage
    coverage_verification = verify_coverage(
        product_info,
        purchase_info,
        rules.get("coverage_terms", {})
    )

    # Classify defect
    defect_classification = classify_defect(
        defect_description,
        diagnostic_data,
        rules.get("defect_categories", {})
    )

    # Determine resolution
    resolution = determine_resolution(
        defect_classification,
        product_info,
        coverage_verification,
        rules.get("resolution_matrix", {})
    )

    # Check for fraud
    fraud_indicators = detect_fraud_patterns(
        customer_history,
        {"months_since_purchase": coverage_verification.get("months_since_purchase", 0)},
        rules.get("fraud_rules", {})
    )

    # Estimate cost
    cost_estimate = 0
    if resolution.get("resolution_type") != "DENIED":
        cost_estimate = estimate_claim_cost(
            resolution,
            {"category": product_info.get("category"), "price": purchase_info.get("price")},
            rules.get("cost_tables", {})
        )

    # Determine final status
    if fraud_indicators and any(f["risk_level"] == "high" for f in fraud_indicators):
        claim_status = "PENDING_REVIEW"
    elif resolution.get("resolution_type") == "DENIED":
        claim_status = "DENIED"
    else:
        claim_status = "APPROVED"

    return {
        "claim_id": claim_id,
        "claim_status": claim_status,
        "coverage_verification": coverage_verification,
        "defect_classification": defect_classification,
        "resolution": resolution,
        "cost_estimate": cost_estimate,
        "fraud_indicators": fraud_indicators
    }


if __name__ == "__main__":
    import json
    result = process_warranty_claim(
        claim_id="WC-2026-001",
        product_info={"sku": "PROD-001", "category": "electronics", "purchase_date": "2025-06-15"},
        purchase_info={"receipt": True, "channel": "retail", "price": 499.99},
        defect_description={"type": "malfunction", "symptom": "won't power on"},
        customer_history={"prior_claims": 0, "customer_since": "2020-01-01"},
        diagnostic_data={"error_code": "E01", "battery_cycles": 150}
    )
    print(json.dumps(result, indent=2))
