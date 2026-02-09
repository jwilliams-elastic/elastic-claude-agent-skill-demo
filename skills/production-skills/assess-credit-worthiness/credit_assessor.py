"""
Credit Worthiness Assessment Module

Implements credit scoring and risk assessment
including payment history, utilization, and DTI analysis.
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
                result[key] = value
    return result


def load_scoring_model() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    # scoring_factors has id,max_points,weight - load as dict of dicts
    scoring_factors_data = load_csv_as_dict("scoring_factors.csv")
    # These are key-value files - load as flat dicts
    payment_history_scoring_data = load_key_value_csv("payment_history_scoring.csv")
    utilization_scoring_data = load_key_value_csv("utilization_scoring.csv")
    history_length_scoring_data = load_key_value_csv("history_length_scoring.csv")
    credit_mix_scoring_data = load_key_value_csv("credit_mix_scoring.csv")
    new_credit_scoring_data = load_key_value_csv("new_credit_scoring.csv")
    # These have more columns - load as dict of dicts
    score_ranges_data = load_csv_as_dict("score_ranges.csv")
    dti_thresholds_data = load_key_value_csv("dti_thresholds.csv")
    lending_criteria_data = load_csv_as_dict("lending_criteria.csv")
    risk_based_pricing_data = load_csv_as_dict("risk_based_pricing.csv")
    params = load_parameters()
    return {
        "scoring_factors": scoring_factors_data,
        "payment_history_scoring": payment_history_scoring_data,
        "utilization_scoring": utilization_scoring_data,
        "history_length_scoring": history_length_scoring_data,
        "credit_mix_scoring": credit_mix_scoring_data,
        "new_credit_scoring": new_credit_scoring_data,
        "score_ranges": score_ranges_data,
        "dti_thresholds": dti_thresholds_data,
        "lending_criteria": lending_criteria_data,
        "risk_based_pricing": risk_based_pricing_data,
        **params
    }


def score_payment_history(
    late_payments: Dict,
    scoring_table: Dict
) -> Dict[str, Any]:
    """Score payment history."""
    # Determine worst delinquency
    if late_payments.get("collections", 0) > 0 or late_payments.get("bankruptcy", False):
        score_pct = scoring_table.get("collection_bankruptcy", 0)
        status = "collection_bankruptcy"
    elif late_payments.get("90_days", 0) > 0:
        score_pct = scoring_table.get("90_days_late", 20)
        status = "90_days_late"
    elif late_payments.get("60_days", 0) > 0:
        score_pct = scoring_table.get("60_days_late", 40)
        status = "60_days_late"
    elif late_payments.get("30_days", 0) > 1:
        score_pct = scoring_table.get("30_days_late_2_plus", 60)
        status = "30_days_late_multiple"
    elif late_payments.get("30_days", 0) == 1:
        score_pct = scoring_table.get("30_days_late_1", 80)
        status = "30_days_late_single"
    else:
        score_pct = scoring_table.get("no_late_payments", 100)
        status = "no_late_payments"

    return {
        "score_percentage": score_pct,
        "status": status,
        "late_payment_details": late_payments
    }


def score_credit_utilization(
    total_credit: float,
    total_balance: float,
    scoring_table: Dict
) -> Dict[str, Any]:
    """Score credit utilization."""
    if total_credit <= 0:
        return {"error": "No credit available"}

    utilization = (total_balance / total_credit) * 100

    if utilization <= 10:
        score_pct = scoring_table.get("0_10", 100)
        rating = "excellent"
    elif utilization <= 30:
        score_pct = scoring_table.get("10_30", 90)
        rating = "good"
    elif utilization <= 50:
        score_pct = scoring_table.get("30_50", 70)
        rating = "fair"
    elif utilization <= 75:
        score_pct = scoring_table.get("50_75", 40)
        rating = "high"
    else:
        score_pct = scoring_table.get("75_plus", 10)
        rating = "very_high"

    return {
        "utilization_pct": round(utilization, 1),
        "score_percentage": score_pct,
        "rating": rating,
        "total_credit": total_credit,
        "total_balance": total_balance
    }


def score_credit_history_length(
    oldest_account_years: float,
    scoring_table: Dict
) -> Dict[str, Any]:
    """Score credit history length."""
    if oldest_account_years >= 10:
        score_pct = scoring_table.get("10_plus_years", 100)
        rating = "excellent"
    elif oldest_account_years >= 7:
        score_pct = scoring_table.get("7_10_years", 85)
        rating = "good"
    elif oldest_account_years >= 5:
        score_pct = scoring_table.get("5_7_years", 70)
        rating = "fair"
    elif oldest_account_years >= 3:
        score_pct = scoring_table.get("3_5_years", 55)
        rating = "limited"
    elif oldest_account_years >= 1:
        score_pct = scoring_table.get("1_3_years", 40)
        rating = "thin"
    else:
        score_pct = scoring_table.get("under_1_year", 20)
        rating = "very_thin"

    return {
        "oldest_account_years": oldest_account_years,
        "score_percentage": score_pct,
        "rating": rating
    }


def score_credit_mix(
    account_types: List[str],
    scoring_table: Dict
) -> Dict[str, Any]:
    """Score credit mix diversity."""
    unique_types = set(account_types)
    type_count = len(unique_types)

    if type_count >= 4:
        score_pct = scoring_table.get("diverse_mix", 100)
        rating = "diverse"
    elif type_count >= 3:
        score_pct = scoring_table.get("moderate_mix", 70)
        rating = "moderate"
    elif type_count >= 2:
        score_pct = scoring_table.get("limited_mix", 40)
        rating = "limited"
    else:
        score_pct = scoring_table.get("single_type", 20)
        rating = "single_type"

    return {
        "account_types": list(unique_types),
        "type_count": type_count,
        "score_percentage": score_pct,
        "rating": rating
    }


def score_new_credit(
    recent_inquiries: int,
    scoring_table: Dict
) -> Dict[str, Any]:
    """Score recent credit inquiries."""
    if recent_inquiries == 0:
        score_pct = scoring_table.get("no_recent_inquiries", 100)
        rating = "excellent"
    elif recent_inquiries <= 2:
        score_pct = scoring_table.get("1_2_inquiries", 80)
        rating = "good"
    elif recent_inquiries <= 4:
        score_pct = scoring_table.get("3_4_inquiries", 60)
        rating = "fair"
    else:
        score_pct = scoring_table.get("5_plus_inquiries", 30)
        rating = "high_activity"

    return {
        "recent_inquiries": recent_inquiries,
        "score_percentage": score_pct,
        "rating": rating
    }


def calculate_credit_score(
    component_scores: Dict,
    weights: Dict
) -> Dict[str, Any]:
    """Calculate overall credit score."""
    weighted_total = 0

    for factor, config in weights.items():
        weight = config.get("weight", 0)
        max_points = config.get("max_points", 100)
        component_pct = component_scores.get(factor, {}).get("score_percentage", 50)

        points = (component_pct / 100) * max_points
        weighted_total += points

    # Normalize to 300-850 range
    base_score = 300
    score_range = 550
    normalized_score = base_score + (weighted_total / 1000) * score_range

    return {
        "raw_score": round(weighted_total, 0),
        "credit_score": round(normalized_score, 0)
    }


def determine_credit_grade(
    score: int,
    score_ranges: Dict
) -> Dict[str, Any]:
    """Determine credit grade from score."""
    for grade, config in score_ranges.items():
        if config["min"] <= score <= config["max"]:
            return {
                "grade": grade.upper(),
                "risk_level": config["risk_level"],
                "score_range": f"{config['min']}-{config['max']}"
            }

    return {"grade": "UNKNOWN", "risk_level": "unknown"}


def calculate_dti(
    monthly_debt_payments: float,
    monthly_income: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Calculate debt-to-income ratio."""
    if monthly_income <= 0:
        return {"error": "Invalid income"}

    dti = monthly_debt_payments / monthly_income

    if dti <= thresholds.get("excellent", 0.20):
        rating = "excellent"
    elif dti <= thresholds.get("good", 0.30):
        rating = "good"
    elif dti <= thresholds.get("acceptable", 0.36):
        rating = "acceptable"
    elif dti <= thresholds.get("concerning", 0.43):
        rating = "concerning"
    else:
        rating = "high_risk"

    return {
        "dti_ratio": round(dti, 3),
        "dti_pct": round(dti * 100, 1),
        "monthly_debt": monthly_debt_payments,
        "monthly_income": monthly_income,
        "rating": rating
    }


def check_lending_eligibility(
    credit_score: int,
    dti: float,
    loan_type: str,
    criteria: Dict
) -> Dict[str, Any]:
    """Check eligibility for specific loan types."""
    loan_criteria = criteria.get(loan_type, {})

    min_score = loan_criteria.get("min_score", 600)
    max_dti = loan_criteria.get("max_dti", 0.43)

    score_eligible = credit_score >= min_score
    dti_eligible = dti <= max_dti

    return {
        "loan_type": loan_type,
        "eligible": score_eligible and dti_eligible,
        "score_requirement": {
            "minimum": min_score,
            "actual": credit_score,
            "meets_requirement": score_eligible
        },
        "dti_requirement": {
            "maximum": max_dti,
            "actual": round(dti, 3),
            "meets_requirement": dti_eligible
        }
    }


def calculate_risk_pricing(
    credit_grade: str,
    base_rate: float,
    pricing_adjustments: Dict
) -> Dict[str, Any]:
    """Calculate risk-based pricing adjustment."""
    adjustment = pricing_adjustments.get(credit_grade.lower(), {}).get("rate_adjustment", 0)
    adjusted_rate = base_rate + adjustment

    return {
        "base_rate": base_rate,
        "credit_grade": credit_grade,
        "rate_adjustment": adjustment,
        "adjusted_rate": round(adjusted_rate, 2)
    }


def assess_credit_worthiness(
    applicant_id: str,
    payment_history: Dict,
    credit_accounts: List[Dict],
    oldest_account_years: float,
    recent_inquiries: int,
    monthly_income: float,
    monthly_debt_payments: float,
    loan_type: str,
    base_interest_rate: float,
    assessment_date: str
) -> Dict[str, Any]:
    """
    Assess credit worthiness.

    Business Rules:
    1. Five-factor credit scoring
    2. DTI ratio analysis
    3. Lending eligibility check
    4. Risk-based pricing

    Args:
        applicant_id: Applicant identifier
        payment_history: Late payment history
        credit_accounts: List of credit accounts
        oldest_account_years: Age of oldest account
        recent_inquiries: Recent credit inquiries
        monthly_income: Monthly gross income
        monthly_debt_payments: Monthly debt obligations
        loan_type: Type of loan requested
        base_interest_rate: Base interest rate
        assessment_date: Assessment date

    Returns:
        Credit worthiness assessment results
    """
    model = load_scoring_model()

    # Calculate utilization
    total_credit = sum(a.get("credit_limit", 0) for a in credit_accounts)
    total_balance = sum(a.get("balance", 0) for a in credit_accounts)
    account_types = [a.get("type", "unknown") for a in credit_accounts]

    # Score each factor
    payment_score = score_payment_history(
        payment_history,
        model.get("payment_history_scoring", {})
    )

    utilization_score = score_credit_utilization(
        total_credit,
        total_balance,
        model.get("utilization_scoring", {})
    )

    history_score = score_credit_history_length(
        oldest_account_years,
        model.get("history_length_scoring", {})
    )

    mix_score = score_credit_mix(
        account_types,
        model.get("credit_mix_scoring", {})
    )

    inquiry_score = score_new_credit(
        recent_inquiries,
        model.get("new_credit_scoring", {})
    )

    # Aggregate component scores
    component_scores = {
        "payment_history": payment_score,
        "credit_utilization": utilization_score,
        "credit_history_length": history_score,
        "credit_mix": mix_score,
        "new_credit": inquiry_score
    }

    # Calculate overall score
    credit_score = calculate_credit_score(
        component_scores,
        model.get("scoring_factors", {})
    )

    # Determine grade
    credit_grade = determine_credit_grade(
        credit_score["credit_score"],
        model.get("score_ranges", {})
    )

    # Calculate DTI
    dti_result = calculate_dti(
        monthly_debt_payments,
        monthly_income,
        model.get("dti_thresholds", {})
    )

    # Check lending eligibility
    eligibility = check_lending_eligibility(
        credit_score["credit_score"],
        dti_result.get("dti_ratio", 1.0),
        loan_type,
        model.get("lending_criteria", {})
    )

    # Calculate risk-based pricing
    pricing = calculate_risk_pricing(
        credit_grade["grade"],
        base_interest_rate,
        model.get("risk_based_pricing", {})
    )

    return {
        "applicant_id": applicant_id,
        "assessment_date": assessment_date,
        "credit_profile": {
            "total_accounts": len(credit_accounts),
            "total_credit_limit": total_credit,
            "total_balance": total_balance,
            "oldest_account_years": oldest_account_years
        },
        "component_scores": component_scores,
        "credit_score": credit_score["credit_score"],
        "credit_grade": credit_grade,
        "dti_analysis": dti_result,
        "lending_eligibility": eligibility,
        "risk_based_pricing": pricing,
        "decision": "APPROVE" if eligibility["eligible"] else "DECLINE",
        "conditions": generate_conditions(eligibility, dti_result, credit_grade)
    }


def generate_conditions(
    eligibility: Dict,
    dti: Dict,
    grade: Dict
) -> List[str]:
    """Generate approval conditions if applicable."""
    conditions = []

    if not eligibility["score_requirement"]["meets_requirement"]:
        conditions.append("Credit score below minimum requirement")

    if not eligibility["dti_requirement"]["meets_requirement"]:
        conditions.append("DTI ratio exceeds maximum threshold")

    if grade["risk_level"] in ["high", "very_high"]:
        conditions.append("Consider requiring collateral or co-signer")

    if dti.get("rating") == "concerning":
        conditions.append("Verify income documentation thoroughly")

    return conditions


if __name__ == "__main__":
    import json
    result = assess_credit_worthiness(
        applicant_id="APP-001",
        payment_history={
            "30_days": 1,
            "60_days": 0,
            "90_days": 0,
            "collections": 0,
            "bankruptcy": False
        },
        credit_accounts=[
            {"type": "credit_card", "credit_limit": 10000, "balance": 2500},
            {"type": "credit_card", "credit_limit": 5000, "balance": 1000},
            {"type": "auto_loan", "credit_limit": 25000, "balance": 15000},
            {"type": "mortgage", "credit_limit": 300000, "balance": 250000}
        ],
        oldest_account_years=8.5,
        recent_inquiries=2,
        monthly_income=8000,
        monthly_debt_payments=2400,
        loan_type="personal_loan",
        base_interest_rate=8.5,
        assessment_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
