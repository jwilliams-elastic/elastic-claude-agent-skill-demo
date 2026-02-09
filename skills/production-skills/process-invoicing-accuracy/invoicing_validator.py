"""
Invoicing Accuracy Validation Module

Implements outbound invoice validation including
pricing verification, contract compliance, and tax calculation checks.
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


def load_invoicing_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    billing_types_data = load_csv_as_dict("billing_types.csv")
    validation_checks_data = load_csv_as_dict("validation_checks.csv")
    tax_rules_data = load_csv_as_dict("tax_rules.csv")
    accuracy_thresholds_data = load_csv_as_dict("accuracy_thresholds.csv")
    error_severity_data = load_csv_as_dict("error_severity.csv")
    audit_requirements_data = load_key_value_csv("audit_requirements.csv")
    params = load_parameters()
    return {
        "billing_types": billing_types_data,
        "validation_checks": validation_checks_data,
        "tax_rules": tax_rules_data,
        "accuracy_thresholds": accuracy_thresholds_data,
        "error_severity": error_severity_data,
        "audit_requirements": audit_requirements_data,
        **params
    }


def validate_line_item_fields(
    line_items: List[Dict],
    required_fields: List[str]
) -> Dict[str, Any]:
    """Validate required fields in line items."""
    errors = []
    valid_count = 0

    for i, item in enumerate(line_items):
        item_errors = []
        for field in required_fields:
            if field not in item or item[field] is None or item[field] == "":
                item_errors.append({
                    "field": field,
                    "error": "Missing required field"
                })

        if item_errors:
            errors.append({
                "line_number": i + 1,
                "errors": item_errors
            })
        else:
            valid_count += 1

    return {
        "check": "required_fields",
        "total_lines": len(line_items),
        "valid_lines": valid_count,
        "lines_with_errors": len(errors),
        "errors": errors
    }


def validate_line_calculations(
    line_items: List[Dict],
    tolerance: float
) -> Dict[str, Any]:
    """Validate line item calculations."""
    errors = []

    for i, item in enumerate(line_items):
        quantity = item.get("quantity", 0)
        unit_price = item.get("unit_price", 0)
        stated_amount = item.get("amount", 0)

        calculated_amount = quantity * unit_price
        variance = abs(calculated_amount - stated_amount)

        if variance > tolerance:
            errors.append({
                "line_number": i + 1,
                "quantity": quantity,
                "unit_price": unit_price,
                "calculated_amount": round(calculated_amount, 2),
                "stated_amount": stated_amount,
                "variance": round(variance, 2),
                "error": "Calculation mismatch"
            })

    return {
        "check": "line_calculations",
        "lines_checked": len(line_items),
        "calculation_errors": len(errors),
        "errors": errors
    }


def validate_contract_pricing(
    line_items: List[Dict],
    contract_terms: Dict,
    pricing_data: Dict,
    compliance_rules: Dict
) -> Dict[str, Any]:
    """Validate pricing against contract terms."""
    pricing_results = []

    contract_rates = contract_terms.get("contracted_rates", {})
    special_pricing = contract_terms.get("special_pricing", {})

    for i, item in enumerate(line_items):
        product_id = item.get("product_id", "")
        invoiced_price = item.get("unit_price", 0)

        # Determine expected price based on priority
        expected_price = None
        price_source = None

        if product_id in special_pricing:
            expected_price = special_pricing[product_id]
            price_source = "special_pricing"
        elif product_id in contract_rates:
            expected_price = contract_rates[product_id]
            price_source = "contract_rate"
        else:
            list_price = pricing_data.get(product_id, {}).get("list_price", 0)
            expected_price = list_price
            price_source = "list_price"

        if expected_price and expected_price > 0:
            variance_pct = abs(invoiced_price - expected_price) / expected_price
        else:
            variance_pct = 0

        is_compliant = invoiced_price <= expected_price if expected_price else True

        pricing_results.append({
            "line_number": i + 1,
            "product_id": product_id,
            "invoiced_price": invoiced_price,
            "expected_price": expected_price,
            "price_source": price_source,
            "variance_pct": round(variance_pct * 100, 2),
            "compliant": is_compliant
        })

    non_compliant = [r for r in pricing_results if not r["compliant"]]

    return {
        "check": "contract_pricing",
        "items_checked": len(pricing_results),
        "compliant_items": len(pricing_results) - len(non_compliant),
        "non_compliant_items": len(non_compliant),
        "pricing_details": pricing_results,
        "pricing_errors": non_compliant
    }


def validate_tax_calculations(
    line_items: List[Dict],
    tax_info: Dict,
    tax_rules: Dict
) -> Dict[str, Any]:
    """Validate tax calculations."""
    errors = []

    customer_exemptions = tax_info.get("exemptions", [])
    tax_jurisdiction = tax_info.get("jurisdiction", "")
    expected_tax_rate = tax_info.get("tax_rate", 0)

    subtotal = sum(item.get("amount", 0) for item in line_items)
    taxable_amount = subtotal

    # Apply exemptions
    for item in line_items:
        if item.get("tax_exempt", False):
            taxable_amount -= item.get("amount", 0)

    expected_tax = taxable_amount * expected_tax_rate
    stated_tax = tax_info.get("stated_tax_amount", 0)

    tolerance = tax_rules.get("rate_variance_tolerance", 0.001)
    variance = abs(expected_tax - stated_tax)
    variance_pct = variance / expected_tax if expected_tax > 0 else 0

    is_valid = variance_pct <= tolerance

    if not is_valid:
        errors.append({
            "error": "Tax calculation mismatch",
            "expected_tax": round(expected_tax, 2),
            "stated_tax": stated_tax,
            "variance": round(variance, 2)
        })

    # Check exemption documentation if required
    if tax_rules.get("exemption_documentation_required") and customer_exemptions:
        for exemption in customer_exemptions:
            if not exemption.get("certificate_on_file", False):
                errors.append({
                    "error": "Missing exemption certificate",
                    "exemption_type": exemption.get("type", "unknown")
                })

    return {
        "check": "tax_calculations",
        "jurisdiction": tax_jurisdiction,
        "subtotal": round(subtotal, 2),
        "taxable_amount": round(taxable_amount, 2),
        "expected_tax": round(expected_tax, 2),
        "stated_tax": stated_tax,
        "tax_rate": expected_tax_rate,
        "variance": round(variance, 2),
        "is_valid": is_valid and len(errors) == 0,
        "errors": errors
    }


def validate_invoice_totals(
    line_items: List[Dict],
    header_totals: Dict,
    tolerance: float
) -> Dict[str, Any]:
    """Validate invoice totals reconciliation."""
    errors = []

    calculated_subtotal = sum(item.get("amount", 0) for item in line_items)
    stated_subtotal = header_totals.get("subtotal", 0)

    subtotal_variance = abs(calculated_subtotal - stated_subtotal)
    if subtotal_variance > tolerance:
        errors.append({
            "field": "subtotal",
            "calculated": round(calculated_subtotal, 2),
            "stated": stated_subtotal,
            "variance": round(subtotal_variance, 2)
        })

    # Check total (subtotal + tax)
    stated_tax = header_totals.get("tax", 0)
    expected_total = stated_subtotal + stated_tax
    stated_total = header_totals.get("total", 0)

    total_variance = abs(expected_total - stated_total)
    if total_variance > tolerance:
        errors.append({
            "field": "total",
            "calculated": round(expected_total, 2),
            "stated": stated_total,
            "variance": round(total_variance, 2)
        })

    return {
        "check": "invoice_totals",
        "calculated_subtotal": round(calculated_subtotal, 2),
        "stated_subtotal": stated_subtotal,
        "calculated_total": round(calculated_subtotal + stated_tax, 2),
        "stated_total": stated_total,
        "is_valid": len(errors) == 0,
        "errors": errors
    }


def calculate_accuracy_score(
    validation_results: Dict,
    error_severity: Dict
) -> Dict[str, Any]:
    """Calculate overall invoice accuracy score."""
    score = 100
    blocking_errors = []
    warnings = []

    # Field validation errors
    field_errors = validation_results.get("field_validation", {}).get("lines_with_errors", 0)
    if field_errors > 0:
        score -= field_errors * 2
        severity = error_severity.get("missing_field", {})
        if severity.get("blocks_approval"):
            blocking_errors.append("Missing required fields")

    # Calculation errors
    calc_errors = validation_results.get("calculation_validation", {}).get("calculation_errors", 0)
    if calc_errors > 0:
        score -= calc_errors * 5
        severity = error_severity.get("calculation_error", {})
        if severity.get("blocks_approval"):
            blocking_errors.append("Calculation errors")

    # Pricing errors
    pricing_errors = len(validation_results.get("pricing_validation", {}).get("pricing_errors", []))
    if pricing_errors > 0:
        score -= pricing_errors * 5
        severity = error_severity.get("pricing_mismatch", {})
        if severity.get("blocks_approval"):
            blocking_errors.append("Pricing compliance errors")

    # Tax errors
    if not validation_results.get("tax_validation", {}).get("is_valid", True):
        score -= 10
        severity = error_severity.get("tax_rate_error", {})
        if severity.get("blocks_approval"):
            blocking_errors.append("Tax calculation error")

    # Totals errors
    if not validation_results.get("totals_validation", {}).get("is_valid", True):
        score -= 5
        warnings.append("Total reconciliation error")

    score = max(0, score)

    return {
        "accuracy_score": score,
        "blocking_errors": blocking_errors,
        "warnings": warnings,
        "has_blocking_errors": len(blocking_errors) > 0
    }


def determine_approval_status(
    accuracy_score: float,
    has_blocking_errors: bool,
    thresholds: Dict
) -> Dict[str, Any]:
    """Determine invoice approval status."""
    if has_blocking_errors:
        return {
            "status": "REJECTED",
            "action": "return_for_correction",
            "reason": "Contains blocking errors"
        }

    auto_approve = thresholds.get("auto_approve", {})
    if accuracy_score >= auto_approve.get("min_score", 98):
        return {
            "status": "AUTO_APPROVED",
            "action": "proceed_to_issue",
            "reason": "Meets auto-approval criteria"
        }

    review_required = thresholds.get("review_required", {})
    if accuracy_score >= review_required.get("min_score", 90):
        return {
            "status": "REVIEW_REQUIRED",
            "action": "route_for_approval",
            "reason": "Requires manual review"
        }

    return {
        "status": "REJECTED",
        "action": thresholds.get("reject", {}).get("action", "return_for_correction"),
        "reason": "Below minimum accuracy threshold"
    }


def process_invoicing_accuracy(
    invoice_id: str,
    customer_id: str,
    contract_id: str,
    line_items: List[Dict],
    header_totals: Dict,
    contract_terms: Dict,
    pricing_data: Dict,
    tax_info: Dict,
    billing_period: str,
    generation_date: str
) -> Dict[str, Any]:
    """
    Process invoicing accuracy validation.

    Business Rules:
    1. Validate all required fields
    2. Verify calculations
    3. Check contract pricing compliance
    4. Validate tax calculations
    5. Reconcile totals

    Args:
        invoice_id: Draft invoice identifier
        customer_id: Customer identifier
        contract_id: Contract identifier
        line_items: Invoice line items
        header_totals: Invoice header totals
        contract_terms: Contract pricing terms
        pricing_data: Current pricing data
        tax_info: Tax calculation info
        billing_period: Billing period
        generation_date: Invoice generation date

    Returns:
        Invoicing accuracy validation results
    """
    config = load_invoicing_rules()
    validation_checks = config.get("validation_checks", {})
    compliance_rules = config.get("contract_compliance", {})
    tax_rules = config.get("tax_rules", {}).get("us_sales_tax", {})
    accuracy_thresholds = config.get("accuracy_thresholds", {})
    error_severity = config.get("error_severity", {})

    # Validate required fields
    field_validation = validate_line_item_fields(
        line_items,
        validation_checks.get("line_item", {}).get("required_fields", [])
    )

    # Validate calculations
    calculation_validation = validate_line_calculations(
        line_items,
        validation_checks.get("line_item", {}).get("calculation_tolerance", 0.01)
    )

    # Validate pricing
    pricing_validation = validate_contract_pricing(
        line_items,
        contract_terms,
        pricing_data,
        compliance_rules
    )

    # Validate tax
    tax_validation = validate_tax_calculations(
        line_items,
        tax_info,
        tax_rules
    )

    # Validate totals
    totals_validation = validate_invoice_totals(
        line_items,
        header_totals,
        validation_checks.get("totals", {}).get("line_total_vs_header_tolerance", 0.01)
    )

    # Compile validation results
    validation_results = {
        "field_validation": field_validation,
        "calculation_validation": calculation_validation,
        "pricing_validation": pricing_validation,
        "tax_validation": tax_validation,
        "totals_validation": totals_validation
    }

    # Calculate accuracy score
    accuracy = calculate_accuracy_score(validation_results, error_severity)

    # Determine approval status
    approval = determine_approval_status(
        accuracy["accuracy_score"],
        accuracy["has_blocking_errors"],
        accuracy_thresholds
    )

    return {
        "invoice_id": invoice_id,
        "customer_id": customer_id,
        "contract_id": contract_id,
        "billing_period": billing_period,
        "generation_date": generation_date,
        "invoice_summary": {
            "line_count": len(line_items),
            "subtotal": header_totals.get("subtotal", 0),
            "tax": header_totals.get("tax", 0),
            "total": header_totals.get("total", 0)
        },
        "validation_results": validation_results,
        "accuracy_assessment": accuracy,
        "approval_status": approval,
        "processing_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = process_invoicing_accuracy(
        invoice_id="INV-DRAFT-2026-001",
        customer_id="CUST-12345",
        contract_id="CTR-2024-001",
        line_items=[
            {"product_id": "PROD-001", "description": "Software License - Annual", "quantity": 10, "unit_price": 500.00, "amount": 5000.00},
            {"product_id": "PROD-002", "description": "Support Services", "quantity": 1, "unit_price": 2500.00, "amount": 2500.00},
            {"product_id": "PROD-003", "description": "Implementation Hours", "quantity": 40, "unit_price": 150.00, "amount": 6000.00}
        ],
        header_totals={
            "subtotal": 13500.00,
            "tax": 1080.00,
            "total": 14580.00
        },
        contract_terms={
            "contracted_rates": {
                "PROD-001": 500.00,
                "PROD-002": 2500.00
            },
            "special_pricing": {},
            "discount_pct": 0.0
        },
        pricing_data={
            "PROD-001": {"list_price": 600.00},
            "PROD-002": {"list_price": 3000.00},
            "PROD-003": {"list_price": 175.00}
        },
        tax_info={
            "jurisdiction": "CA",
            "tax_rate": 0.08,
            "stated_tax_amount": 1080.00,
            "exemptions": []
        },
        billing_period="2026-Q1",
        generation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
