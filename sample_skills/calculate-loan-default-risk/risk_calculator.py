"""
Loan Default Risk Calculation Module

Implements proprietary credit scoring and probability of default
models for consumer and commercial lending.
"""

import csv
import math
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


def load_scoring_models() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    segments_data = load_csv_as_dict("segments.csv")
    adjustments_data = load_csv_as_dict("adjustments.csv")
    loan_purposes_data = load_csv_as_dict("loan_purposes.csv")
    risk_grades_data = load_csv_as_list("risk_grades.csv")
    pricing_grid_data = load_key_value_csv("pricing_grid.csv")
    decision_thresholds_data = load_key_value_csv("decision_thresholds.csv")
    params = load_parameters()
    return {
        "segments": segments_data,
        "adjustments": adjustments_data,
        "loan_purposes": loan_purposes_data,
        "risk_grades": risk_grades_data,
        "pricing_grid": pricing_grid_data,
        "decision_thresholds": decision_thresholds_data,
        **params
    }


def determine_segment(credit_score: int) -> str:
    """Determine borrower segment based on credit score."""
    if credit_score >= 720:
        return "prime"
    elif credit_score >= 660:
        return "near_prime"
    else:
        return "subprime"


def calculate_base_pd(
    credit_score: int,
    segment_params: Dict
) -> float:
    """Calculate base probability of default from credit score."""
    # Logistic transformation of credit score
    score_normalized = (credit_score - segment_params["score_midpoint"]) / segment_params["score_scale"]
    base_pd = 1 / (1 + math.exp(score_normalized))
    return base_pd


def apply_dti_adjustment(
    base_pd: float,
    dti: float,
    dti_thresholds: Dict
) -> tuple:
    """Apply DTI-based adjustment to PD."""
    if dti > dti_thresholds["high"]:
        adjustment = dti_thresholds["high_factor"]
        factor = "HIGH_DTI"
    elif dti > dti_thresholds["medium"]:
        adjustment = dti_thresholds["medium_factor"]
        factor = "ELEVATED_DTI"
    else:
        adjustment = 1.0
        factor = None

    return base_pd * adjustment, factor


def apply_employment_adjustment(
    base_pd: float,
    employment_months: int,
    thresholds: Dict
) -> tuple:
    """Apply employment stability adjustment."""
    if employment_months < thresholds["minimum_months"]:
        adjustment = thresholds["short_tenure_factor"]
        factor = "SHORT_EMPLOYMENT"
    elif employment_months >= thresholds["stable_months"]:
        adjustment = thresholds["stable_factor"]
        factor = None
    else:
        adjustment = 1.0
        factor = None

    return base_pd * adjustment, factor


def apply_payment_history_adjustment(
    base_pd: float,
    payment_history: Dict,
    thresholds: Dict
) -> tuple:
    """Apply payment behavior adjustment."""
    late_30 = payment_history.get("late_30_count", 0)
    late_60 = payment_history.get("late_60_count", 0)
    late_90 = payment_history.get("late_90_count", 0)

    factors = []

    if late_90 > 0:
        base_pd *= thresholds["late_90_factor"]
        factors.append("SERIOUS_DELINQUENCY")
    elif late_60 > 0:
        base_pd *= thresholds["late_60_factor"]
        factors.append("DELINQUENCY_HISTORY")
    elif late_30 > thresholds["late_30_threshold"]:
        base_pd *= thresholds["late_30_factor"]
        factors.append("PAYMENT_ISSUES")

    return base_pd, factors


def determine_risk_grade(pd: float, grade_thresholds: List) -> str:
    """Determine risk grade from PD."""
    for threshold in grade_thresholds:
        if pd <= threshold["max_pd"]:
            return threshold["grade"]
    return "F"


def calculate_pricing_adjustment(
    risk_grade: str,
    pricing_grid: Dict
) -> int:
    """Calculate pricing adjustment in basis points."""
    return pricing_grid.get(risk_grade, pricing_grid["F"])


def calculate_default_risk(
    application_id: str,
    credit_score: int,
    debt_to_income: float,
    loan_amount: float,
    loan_purpose: str,
    employment_months: int,
    annual_income: float,
    existing_debt: float,
    payment_history: Dict
) -> Dict[str, Any]:
    """
    Calculate loan default probability and risk grade.

    Business Rules:
    1. Segment-specific scoring models
    2. DTI adjustments based on thresholds
    3. Employment stability considerations
    4. Payment history overlay

    Args:
        application_id: Application identifier
        credit_score: Credit score
        debt_to_income: DTI ratio
        loan_amount: Loan amount
        loan_purpose: Loan purpose
        employment_months: Employment tenure
        annual_income: Annual income
        existing_debt: Existing debt
        payment_history: Payment behavior

    Returns:
        Risk assessment with PD and decision
    """
    models = load_scoring_models()

    risk_factors = []

    # Determine segment and get model parameters
    segment = determine_segment(credit_score)
    segment_params = models["segments"][segment]

    # Calculate base PD
    pd = calculate_base_pd(credit_score, segment_params)

    # Apply DTI adjustment
    pd, dti_factor = apply_dti_adjustment(pd, debt_to_income, models["adjustments"]["dti"])
    if dti_factor:
        risk_factors.append(dti_factor)

    # Apply employment adjustment
    pd, emp_factor = apply_employment_adjustment(
        pd, employment_months, models["adjustments"]["employment"]
    )
    if emp_factor:
        risk_factors.append(emp_factor)

    # Apply payment history adjustment
    pd, payment_factors = apply_payment_history_adjustment(
        pd, payment_history, models["adjustments"]["payment_history"]
    )
    risk_factors.extend(payment_factors)

    # Loan purpose adjustment
    purpose_multiplier = models["loan_purposes"].get(loan_purpose, {}).get("pd_multiplier", 1.0)
    pd *= purpose_multiplier

    # Cap PD between bounds
    pd = max(0.001, min(0.999, pd))

    # Determine risk grade
    risk_grade = determine_risk_grade(pd, models["risk_grades"])

    # Calculate pricing adjustment
    pricing_adjustment = calculate_pricing_adjustment(risk_grade, models["pricing_grid"])

    # Determine decision
    if pd > models["decision_thresholds"]["decline"]:
        decision = "DECLINE"
    elif pd > models["decision_thresholds"]["refer"]:
        decision = "REFER"
    else:
        decision = "APPROVE"

    # Additional risk metrics
    loan_to_income = loan_amount / annual_income if annual_income > 0 else float('inf')
    total_debt_ratio = (existing_debt + loan_amount) / annual_income if annual_income > 0 else float('inf')

    if loan_to_income > 0.5:
        risk_factors.append("HIGH_LOAN_TO_INCOME")
    if total_debt_ratio > 0.6:
        risk_factors.append("HIGH_TOTAL_DEBT")

    return {
        "application_id": application_id,
        "probability_of_default": round(pd, 4),
        "risk_grade": risk_grade,
        "segment": segment,
        "decision": decision,
        "pricing_adjustment_bps": pricing_adjustment,
        "risk_factors": risk_factors,
        "metrics": {
            "credit_score": credit_score,
            "debt_to_income": debt_to_income,
            "loan_to_income": round(loan_to_income, 3),
            "total_debt_ratio": round(total_debt_ratio, 3),
            "employment_months": employment_months
        },
        "loan_details": {
            "amount": loan_amount,
            "purpose": loan_purpose
        }
    }


if __name__ == "__main__":
    import json
    result = calculate_default_risk(
        application_id="APP-2024-12345",
        credit_score=720,
        debt_to_income=0.35,
        loan_amount=25000,
        loan_purpose="debt_consolidation",
        employment_months=36,
        annual_income=85000,
        existing_debt=15000,
        payment_history={"late_30_count": 0, "late_60_count": 0, "late_90_count": 0}
    )
    print(json.dumps(result, indent=2))
