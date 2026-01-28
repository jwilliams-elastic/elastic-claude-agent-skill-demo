"""
Regulatory Filing Validation Module

Implements validation of regulatory filings for completeness,
accuracy, and compliance with SEC/FINRA requirements.
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


def load_regulatory_requirements() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    required_fields_data = load_csv_as_dict("required_fields.csv")
    deadline_rules_data = load_csv_as_dict("deadline_rules.csv")
    accuracy_rules_data = load_key_value_csv("accuracy_rules.csv")
    amendment_triggers_data = load_key_value_csv("amendment_triggers.csv")
    filer_categories_data = load_csv_as_dict("filer_categories.csv")
    xbrl_requirements_data = load_csv_as_dict("xbrl_requirements.csv")
    params = load_parameters()
    return {
        "required_fields": required_fields_data,
        "deadline_rules": deadline_rules_data,
        "accuracy_rules": accuracy_rules_data,
        "amendment_triggers": amendment_triggers_data,
        "filer_categories": filer_categories_data,
        "xbrl_requirements": xbrl_requirements_data,
        **params
    }


def check_completeness(
    filing_data: Dict,
    filing_type: str,
    required_fields: Dict
) -> Dict[str, Any]:
    """Check filing for required fields."""
    missing_fields = []
    completed_fields = []

    type_requirements = required_fields.get(filing_type, required_fields.get("default", {}))

    for field, field_info in type_requirements.items():
        # Skip empty or non-dict field info
        if not field_info or not isinstance(field_info, dict):
            continue
        if field_info.get("required", False):
            if field in filing_data and filing_data[field] is not None:
                completed_fields.append(field)
            else:
                missing_fields.append({
                    "field": field,
                    "description": field_info.get("description", field)
                })

    completeness_pct = len(completed_fields) / (len(completed_fields) + len(missing_fields)) if (len(completed_fields) + len(missing_fields)) > 0 else 1.0

    return {
        "complete": len(missing_fields) == 0,
        "completeness_percentage": round(completeness_pct * 100, 1),
        "missing_fields": missing_fields,
        "completed_fields": completed_fields
    }


def validate_data_accuracy(
    filing_data: Dict,
    prior_filings: List[Dict],
    accuracy_rules: Dict
) -> List[Dict]:
    """Validate data accuracy and consistency."""
    issues = []

    # Cross-check with prior filings
    for prior in prior_filings:
        prior_type = prior.get("type", "")
        prior_period = prior.get("period", "")

        # Check for material changes
        if "total_assets" in filing_data and "total_assets" in prior:
            change = abs(filing_data["total_assets"] - prior["total_assets"]) / prior["total_assets"] if prior["total_assets"] > 0 else 0
            threshold = accuracy_rules.get("material_change_threshold", 0.10)
            if change > threshold:
                issues.append({
                    "type": "material_change",
                    "field": "total_assets",
                    "description": f"Total assets changed {change:.1%} from {prior_type}",
                    "severity": "warning"
                })

    # Validate internal consistency
    total_assets = filing_data.get("total_assets", 0)
    total_liabilities = filing_data.get("total_liabilities", 0)
    equity = filing_data.get("shareholders_equity", 0)

    if total_assets > 0 and total_liabilities > 0 and equity > 0:
        balance_check = abs(total_assets - (total_liabilities + equity))
        if balance_check > 1000:  # Allow small rounding
            issues.append({
                "type": "balance_error",
                "field": "balance_sheet",
                "description": "Assets do not equal Liabilities + Equity",
                "severity": "error"
            })

    return issues


def check_deadline_compliance(
    filing_type: str,
    entity_info: Dict,
    submission_date: str,
    deadline_rules: Dict
) -> Dict[str, Any]:
    """Check filing deadline compliance."""
    try:
        submission_dt = datetime.strptime(submission_date, "%Y-%m-%d")
    except ValueError:
        submission_dt = datetime.now()

    fiscal_year_end = entity_info.get("fiscal_year_end", "12-31")
    filer_status = entity_info.get("filer_status", "non_accelerated")

    # Get deadline rules
    type_rules = deadline_rules.get(filing_type, {})
    days_after = type_rules.get(filer_status, type_rules.get("default", 60))

    # Calculate deadline
    fy_end = datetime.strptime(f"2025-{fiscal_year_end}", "%Y-%m-%d")
    deadline = fy_end + timedelta(days=days_after)

    days_until_deadline = (deadline - submission_dt).days
    on_time = submission_dt <= deadline

    return {
        "deadline": deadline.strftime("%Y-%m-%d"),
        "submission_date": submission_date,
        "on_time": on_time,
        "days_until_deadline": days_until_deadline,
        "filer_status": filer_status
    }


def detect_amendments_needed(
    filing_data: Dict,
    prior_filings: List[Dict],
    amendment_triggers: Dict
) -> List[Dict]:
    """Identify if amendments to prior filings are needed."""
    corrections = []

    for prior in prior_filings:
        # Check for restatements
        if filing_data.get("restatement", False):
            corrections.append({
                "prior_filing": prior.get("type"),
                "period": prior.get("period"),
                "reason": "Restatement disclosed",
                "action": "Amendment may be required"
            })

        # Check for error corrections
        error_threshold = amendment_triggers.get("error_threshold", 0.05)
        # Compare key figures
        for field in ["revenue", "net_income", "total_assets"]:
            if field in filing_data and field in prior:
                if prior[field] > 0:
                    diff = abs(filing_data.get(f"{field}_restated", filing_data[field]) - prior[field]) / prior[field]
                    if diff > error_threshold:
                        corrections.append({
                            "prior_filing": prior.get("type"),
                            "field": field,
                            "reason": f"Material difference ({diff:.1%}) detected",
                            "action": "Review for amendment necessity"
                        })

    return corrections


def validate_filing(
    filing_id: str,
    filing_type: str,
    filing_data: Dict,
    prior_filings: List[Dict],
    entity_info: Dict,
    submission_date: str
) -> Dict[str, Any]:
    """
    Validate regulatory filing.

    Business Rules:
    1. Form completeness verification
    2. Data accuracy validation
    3. Deadline compliance check
    4. Amendment detection

    Args:
        filing_id: Filing identifier
        filing_type: Type of regulatory filing
        filing_data: Filing content
        prior_filings: Previous related filings
        entity_info: Filing entity information
        submission_date: Planned submission date

    Returns:
        Filing validation results
    """
    requirements = load_regulatory_requirements()

    required_corrections = []

    # Completeness check
    completeness_check = check_completeness(
        filing_data,
        filing_type,
        requirements.get("required_fields", {})
    )

    if not completeness_check["complete"]:
        for field in completeness_check["missing_fields"]:
            required_corrections.append({
                "type": "missing_field",
                "item": field["field"],
                "action": f"Provide required field: {field['description']}"
            })

    # Accuracy validation
    accuracy_issues = validate_data_accuracy(
        filing_data,
        prior_filings,
        requirements.get("accuracy_rules", {})
    )

    for issue in accuracy_issues:
        if issue["severity"] == "error":
            required_corrections.append({
                "type": "accuracy_error",
                "item": issue["field"],
                "action": issue["description"]
            })

    # Deadline compliance
    deadline_status = check_deadline_compliance(
        filing_type,
        entity_info,
        submission_date,
        requirements.get("deadline_rules", {})
    )

    # Amendment detection
    amendment_needs = detect_amendments_needed(
        filing_data,
        prior_filings,
        requirements.get("amendment_triggers", {})
    )

    # Determine overall status
    if required_corrections:
        validation_status = "CORRECTIONS_REQUIRED"
    elif not deadline_status["on_time"]:
        validation_status = "LATE_FILING"
    elif accuracy_issues:
        validation_status = "WARNINGS_PRESENT"
    else:
        validation_status = "READY_TO_FILE"

    return {
        "filing_id": filing_id,
        "filing_type": filing_type,
        "validation_status": validation_status,
        "completeness_check": completeness_check,
        "accuracy_issues": accuracy_issues,
        "deadline_status": deadline_status,
        "required_corrections": required_corrections,
        "amendment_review": amendment_needs
    }


if __name__ == "__main__":
    import json
    result = validate_filing(
        filing_id="FIL-2026-001",
        filing_type="10-K",
        filing_data={
            "fiscal_year_end": "2025-12-31",
            "total_assets": 1000000000,
            "total_liabilities": 600000000,
            "shareholders_equity": 400000000,
            "revenue": 500000000,
            "net_income": 50000000
        },
        prior_filings=[
            {"type": "10-Q", "period": "2025-Q3", "total_assets": 980000000}
        ],
        entity_info={"cik": "0001234567", "sic": "6022", "filer_status": "large_accelerated"},
        submission_date="2026-03-01"
    )
    print(json.dumps(result, indent=2))
