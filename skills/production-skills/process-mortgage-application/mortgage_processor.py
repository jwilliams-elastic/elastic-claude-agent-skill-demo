"""
Mortgage Application Processing Module

Implements mortgage underwriting logic using standard
lending guidelines and risk assessment criteria.
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


def load_lending_guidelines() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    credit_tiers_data = load_csv_as_dict("credit_tiers.csv")
    ltv_limits_data = load_csv_as_dict("ltv_limits.csv")
    loan_programs_data = load_csv_as_dict("loan_programs.csv")
    pmi_rates_data = load_key_value_csv("pmi_rates.csv")
    params = load_parameters()
    return {
        "credit_tiers": credit_tiers_data,
        "ltv_limits": ltv_limits_data,
        "loan_programs": loan_programs_data,
        "pmi_rates": pmi_rates_data,
        **params
    }


def evaluate_credit_score(
    fico_score: int,
    credit_tiers: Dict
) -> Dict[str, Any]:
    """Evaluate credit score against tier thresholds."""
    tier = "subprime"
    rate_adjustment = 0.0

    for tier_name, tier_info in sorted(
        credit_tiers.items(),
        key=lambda x: x[1].get("min_score", 0),
        reverse=True
    ):
        if fico_score >= tier_info.get("min_score", 0):
            tier = tier_name
            rate_adjustment = tier_info.get("rate_adjustment", 0)
            break

    return {
        "score": fico_score,
        "tier": tier,
        "rate_adjustment": rate_adjustment,
        "meets_minimum": fico_score >= 620
    }


def calculate_dti_ratio(
    borrower_info: Dict,
    loan_request: Dict,
    guidelines: Dict
) -> Dict[str, Any]:
    """Calculate debt-to-income ratios."""
    annual_income = borrower_info.get("annual_income", 0)
    monthly_income = annual_income / 12

    existing_debt = borrower_info.get("monthly_debt", 0)
    loan_amount = loan_request.get("amount", 0)
    term_years = loan_request.get("term_years", 30)
    estimated_rate = guidelines.get("base_rate", 0.065)

    # Estimate monthly payment (simple calculation)
    monthly_rate = estimated_rate / 12
    num_payments = term_years * 12
    if monthly_rate > 0:
        monthly_payment = loan_amount * (monthly_rate * (1 + monthly_rate)**num_payments) / ((1 + monthly_rate)**num_payments - 1)
    else:
        monthly_payment = loan_amount / num_payments

    # Add estimated taxes and insurance
    estimated_piti = monthly_payment * 1.25

    front_end_dti = estimated_piti / monthly_income if monthly_income > 0 else 1.0
    back_end_dti = (estimated_piti + existing_debt) / monthly_income if monthly_income > 0 else 1.0

    max_front = guidelines.get("max_front_end_dti", 0.28)
    max_back = guidelines.get("max_back_end_dti", 0.43)

    return {
        "front_end_dti": round(front_end_dti, 3),
        "back_end_dti": round(back_end_dti, 3),
        "meets_front_end": front_end_dti <= max_front,
        "meets_back_end": back_end_dti <= max_back,
        "estimated_payment": round(monthly_payment, 2),
        "estimated_piti": round(estimated_piti, 2)
    }


def calculate_ltv_ratio(
    loan_request: Dict,
    property_info: Dict,
    ltv_limits: Dict
) -> Dict[str, Any]:
    """Calculate loan-to-value ratio."""
    loan_amount = loan_request.get("amount", 0)
    property_value = property_info.get("value", 1)
    property_type = property_info.get("type", "single_family")

    ltv = loan_amount / property_value if property_value > 0 else 1.0

    max_ltv = ltv_limits.get(property_type, {}).get("max_ltv", 0.80)
    pmi_threshold = ltv_limits.get(property_type, {}).get("pmi_threshold", 0.80)

    requires_pmi = ltv > pmi_threshold

    return {
        "ltv_ratio": round(ltv, 3),
        "max_allowed": max_ltv,
        "meets_requirement": ltv <= max_ltv,
        "requires_pmi": requires_pmi,
        "property_type": property_type
    }


def verify_income(
    income_documents: List[Dict],
    borrower_info: Dict,
    requirements: Dict
) -> Dict[str, Any]:
    """Verify income documentation."""
    issues = []
    verified_income = 0

    required_docs = requirements.get("required_documents", ["w2", "paystubs"])
    provided_docs = [d.get("type") for d in income_documents if d.get("verified")]

    for req_doc in required_docs:
        if req_doc not in provided_docs:
            issues.append(f"Missing required document: {req_doc}")

    # Calculate verified income
    for doc in income_documents:
        if doc.get("verified"):
            verified_income += doc.get("annual_amount", 0)

    if verified_income == 0:
        verified_income = borrower_info.get("annual_income", 0)

    stated_income = borrower_info.get("annual_income", 0)
    income_variance = abs(verified_income - stated_income) / stated_income if stated_income > 0 else 0

    if income_variance > 0.1:
        issues.append(f"Income variance {income_variance:.1%} exceeds tolerance")

    return {
        "verified": len(issues) == 0,
        "verified_income": verified_income,
        "stated_income": stated_income,
        "variance": round(income_variance, 3),
        "issues": issues
    }


def determine_interest_rate(
    credit_evaluation: Dict,
    ltv_result: Dict,
    guidelines: Dict
) -> float:
    """Determine offered interest rate."""
    base_rate = guidelines.get("base_rate", 0.065)

    # Credit adjustment
    rate = base_rate + credit_evaluation.get("rate_adjustment", 0)

    # LTV adjustment
    ltv = ltv_result.get("ltv_ratio", 0.8)
    if ltv > 0.90:
        rate += 0.005
    elif ltv > 0.80:
        rate += 0.0025

    # PMI adjustment if applicable
    if ltv_result.get("requires_pmi"):
        rate += 0.001

    return round(rate, 4)


def process_application(
    application_id: str,
    borrower_info: Dict,
    property_info: Dict,
    loan_request: Dict,
    credit_report: Dict,
    income_documents: List[Dict]
) -> Dict[str, Any]:
    """
    Process mortgage loan application.

    Business Rules:
    1. Credit score tier evaluation
    2. DTI ratio calculation and limits
    3. LTV requirements and PMI
    4. Income verification

    Args:
        application_id: Application ID
        borrower_info: Borrower financial profile
        property_info: Property details
        loan_request: Loan terms requested
        credit_report: Credit information
        income_documents: Income verification

    Returns:
        Mortgage application decision
    """
    guidelines = load_lending_guidelines()
    conditions = []

    # Credit evaluation
    credit_eval = evaluate_credit_score(
        credit_report.get("fico_score", 0),
        guidelines.get("credit_tiers", {})
    )

    if not credit_eval["meets_minimum"]:
        return {
            "application_id": application_id,
            "decision": "DENIED",
            "denial_reason": "Credit score below minimum requirement",
            "approved_amount": 0,
            "interest_rate": None,
            "conditions": [],
            "risk_assessment": {"credit": credit_eval}
        }

    # DTI calculation
    dti_result = calculate_dti_ratio(
        borrower_info,
        loan_request,
        guidelines
    )

    if not dti_result["meets_back_end"]:
        # Try reduced loan amount
        max_payment = borrower_info.get("annual_income", 0) / 12 * guidelines.get("max_back_end_dti", 0.43)
        max_payment -= borrower_info.get("monthly_debt", 0)
        conditions.append("Loan amount may be reduced to meet DTI requirements")

    # LTV calculation
    ltv_result = calculate_ltv_ratio(
        loan_request,
        property_info,
        guidelines.get("ltv_limits", {})
    )

    if not ltv_result["meets_requirement"]:
        conditions.append("Additional down payment required to meet LTV limits")

    if ltv_result["requires_pmi"]:
        conditions.append("Private mortgage insurance (PMI) required")

    # Income verification
    income_result = verify_income(
        income_documents,
        borrower_info,
        guidelines.get("income_requirements", {})
    )

    if not income_result["verified"]:
        conditions.extend([f"Required: {issue}" for issue in income_result["issues"]])

    # Determine interest rate
    interest_rate = determine_interest_rate(
        credit_eval,
        ltv_result,
        guidelines
    )

    # Make decision
    if credit_eval["meets_minimum"] and dti_result["meets_back_end"] and ltv_result["meets_requirement"]:
        if income_result["verified"]:
            decision = "APPROVED"
        else:
            decision = "APPROVED_WITH_CONDITIONS"
    elif credit_eval["meets_minimum"]:
        decision = "APPROVED_WITH_CONDITIONS"
    else:
        decision = "DENIED"

    approved_amount = loan_request.get("amount", 0) if decision != "DENIED" else 0

    return {
        "application_id": application_id,
        "decision": decision,
        "approved_amount": approved_amount,
        "interest_rate": interest_rate,
        "conditions": conditions,
        "risk_assessment": {
            "credit": credit_eval,
            "dti": dti_result,
            "ltv": ltv_result,
            "income": income_result
        }
    }


if __name__ == "__main__":
    import json
    result = process_application(
        application_id="MTG-2026-001",
        borrower_info={
            "annual_income": 120000,
            "employment_years": 5,
            "monthly_debt": 500
        },
        property_info={"value": 450000, "type": "single_family"},
        loan_request={"amount": 360000, "term_years": 30},
        credit_report={"fico_score": 740, "derogatory_marks": 0},
        income_documents=[
            {"type": "w2", "verified": True, "annual_amount": 120000},
            {"type": "paystubs", "verified": True}
        ]
    )
    print(json.dumps(result, indent=2))
