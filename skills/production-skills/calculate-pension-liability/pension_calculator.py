"""
Pension Liability Calculation Module

Implements defined benefit pension liability calculation
using actuarial methods including PBO and ABO.
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


def load_pension_assumptions() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    default_assumptions_data = load_key_value_csv("default_assumptions.csv")
    discount_rate_guidance_data = load_key_value_csv("discount_rate_guidance.csv")
    mortality_tables_data = load_csv_as_dict("mortality_tables.csv")
    benefit_formulas_data = load_csv_as_dict("benefit_formulas.csv")
    erisa_requirements_data = load_csv_as_dict("erisa_requirements.csv")
    accounting_standards_data = load_csv_as_dict("accounting_standards.csv")
    asset_allocation_benchmarks_data = load_csv_as_dict("asset_allocation_benchmarks.csv")
    params = load_parameters()
    return {
        "default_assumptions": default_assumptions_data,
        "discount_rate_guidance": discount_rate_guidance_data,
        "mortality_tables": mortality_tables_data,
        "benefit_formulas": benefit_formulas_data,
        "erisa_requirements": erisa_requirements_data,
        "accounting_standards": accounting_standards_data,
        "asset_allocation_benchmarks": asset_allocation_benchmarks_data,
        **params
    }


def calculate_pbo(
    participant_data: List[Dict],
    plan_provisions: Dict,
    assumptions: Dict
) -> Dict[str, Any]:
    """Calculate Projected Benefit Obligation."""
    discount_rate = assumptions.get("discount_rate", 0.055)
    salary_growth = assumptions.get("salary_growth", 0.03)
    formula = plan_provisions.get("formula", "final_average")
    benefit_pct = plan_provisions.get("benefit_pct", 0.015)

    total_pbo = 0
    participant_details = []

    for participant in participant_data:
        age = participant.get("age", 55)
        service_years = participant.get("service_years", 0)
        current_salary = participant.get("salary", 0)

        # Project salary to retirement (assume age 65)
        years_to_retirement = max(0, 65 - age)
        projected_salary = current_salary * ((1 + salary_growth) ** years_to_retirement)

        # Calculate annual benefit
        if formula == "final_average":
            annual_benefit = projected_salary * benefit_pct * (service_years + years_to_retirement)
        else:
            annual_benefit = current_salary * benefit_pct * service_years

        # Calculate PV of benefits
        # Simplified: assume 20-year payout at retirement
        annuity_factor = (1 - (1 + discount_rate) ** -20) / discount_rate
        pv_at_retirement = annual_benefit * annuity_factor

        # Discount to current date
        pbo_participant = pv_at_retirement / ((1 + discount_rate) ** years_to_retirement)

        participant_details.append({
            "participant_id": participant.get("id", "unknown"),
            "projected_salary": round(projected_salary, 2),
            "annual_benefit": round(annual_benefit, 2),
            "pbo": round(pbo_participant, 2)
        })

        total_pbo += pbo_participant

    return {
        "total_pbo": round(total_pbo, 2),
        "participant_count": len(participant_data),
        "participant_details": participant_details[:5]  # First 5 for sample
    }


def calculate_abo(
    participant_data: List[Dict],
    plan_provisions: Dict,
    assumptions: Dict
) -> Dict[str, Any]:
    """Calculate Accumulated Benefit Obligation."""
    discount_rate = assumptions.get("discount_rate", 0.055)
    benefit_pct = plan_provisions.get("benefit_pct", 0.015)

    total_abo = 0

    for participant in participant_data:
        age = participant.get("age", 55)
        service_years = participant.get("service_years", 0)
        current_salary = participant.get("salary", 0)

        # ABO uses current salary and current service
        annual_benefit = current_salary * benefit_pct * service_years

        # Calculate PV
        years_to_retirement = max(0, 65 - age)
        annuity_factor = (1 - (1 + discount_rate) ** -20) / discount_rate
        pv_at_retirement = annual_benefit * annuity_factor
        abo_participant = pv_at_retirement / ((1 + discount_rate) ** years_to_retirement)

        total_abo += abo_participant

    return {
        "total_abo": round(total_abo, 2)
    }


def calculate_funding_status(
    pbo: float,
    asset_values: Dict
) -> Dict[str, Any]:
    """Calculate plan funding status."""
    plan_assets = asset_values.get("market_value", 0)

    funded_status = plan_assets - pbo
    funded_percentage = (plan_assets / pbo * 100) if pbo > 0 else 100

    if funded_percentage >= 100:
        status = "OVERFUNDED"
    elif funded_percentage >= 80:
        status = "ADEQUATELY_FUNDED"
    elif funded_percentage >= 60:
        status = "UNDERFUNDED"
    else:
        status = "CRITICALLY_UNDERFUNDED"

    return {
        "plan_assets": plan_assets,
        "pbo": pbo,
        "funded_status": round(funded_status, 2),
        "funded_percentage": round(funded_percentage, 1),
        "status": status
    }


def calculate_pension_expense(
    pbo: float,
    plan_assets: float,
    assumptions: Dict,
    prior_service: float = 0
) -> Dict[str, Any]:
    """Calculate annual pension expense components."""
    discount_rate = assumptions.get("discount_rate", 0.055)
    expected_return = assumptions.get("expected_return", 0.07)

    # Service cost (simplified as % of PBO)
    service_cost = pbo * 0.05

    # Interest cost
    interest_cost = pbo * discount_rate

    # Expected return on assets
    expected_return_assets = plan_assets * expected_return

    # Net periodic pension cost
    net_cost = service_cost + interest_cost - expected_return_assets + prior_service

    return {
        "service_cost": round(service_cost, 2),
        "interest_cost": round(interest_cost, 2),
        "expected_return_on_assets": round(expected_return_assets, 2),
        "amortization_prior_service": round(prior_service, 2),
        "net_periodic_cost": round(net_cost, 2)
    }


def sensitivity_analysis(
    pbo: float,
    assumptions: Dict
) -> Dict[str, Any]:
    """Analyze sensitivity to assumption changes."""
    discount_rate = assumptions.get("discount_rate", 0.055)

    # 50bp change in discount rate
    discount_sensitivity = pbo * 0.10  # Approximate 10% impact per 50bp

    # 50bp change in salary growth
    salary_sensitivity = pbo * 0.03  # Approximate 3% impact

    return {
        "discount_rate_50bp_decrease": {
            "pbo_impact": round(discount_sensitivity, 2),
            "pbo_impact_pct": 10.0
        },
        "discount_rate_50bp_increase": {
            "pbo_impact": round(-discount_sensitivity, 2),
            "pbo_impact_pct": -10.0
        },
        "salary_growth_50bp_increase": {
            "pbo_impact": round(salary_sensitivity, 2),
            "pbo_impact_pct": 3.0
        }
    }


def calculate_pension(
    plan_id: str,
    participant_data: List[Dict],
    plan_provisions: Dict,
    actuarial_assumptions: Dict,
    asset_values: Dict,
    valuation_date: str
) -> Dict[str, Any]:
    """
    Calculate pension plan liabilities.

    Business Rules:
    1. PBO calculation with salary projection
    2. Discount rate application
    3. Mortality table assumptions
    4. Funding status assessment

    Args:
        plan_id: Plan identifier
        participant_data: Participant census
        plan_provisions: Benefit formula details
        actuarial_assumptions: Valuation assumptions
        asset_values: Plan asset data
        valuation_date: Valuation date

    Returns:
        Pension calculation results
    """
    assumptions = load_pension_assumptions()

    # Override with provided assumptions
    calc_assumptions = {**assumptions.get("default_assumptions", {}), **actuarial_assumptions}

    # Calculate PBO
    pbo_result = calculate_pbo(
        participant_data,
        plan_provisions,
        calc_assumptions
    )

    # Calculate ABO
    abo_result = calculate_abo(
        participant_data,
        plan_provisions,
        calc_assumptions
    )

    # Funding status
    funding_status = calculate_funding_status(
        pbo_result["total_pbo"],
        asset_values
    )

    # Expense components
    expense_components = calculate_pension_expense(
        pbo_result["total_pbo"],
        asset_values.get("market_value", 0),
        calc_assumptions
    )

    # Sensitivity analysis
    sensitivity = sensitivity_analysis(
        pbo_result["total_pbo"],
        calc_assumptions
    )

    return {
        "plan_id": plan_id,
        "valuation_date": valuation_date,
        "pbo": pbo_result["total_pbo"],
        "abo": abo_result["total_abo"],
        "funding_status": funding_status,
        "expense_components": expense_components,
        "sensitivity_analysis": sensitivity,
        "assumptions_used": calc_assumptions,
        "participant_summary": {
            "count": pbo_result["participant_count"]
        }
    }


if __name__ == "__main__":
    import json
    result = calculate_pension(
        plan_id="PEN-001",
        participant_data=[
            {"id": "EMP-001", "age": 55, "service_years": 25, "salary": 100000},
            {"id": "EMP-002", "age": 45, "service_years": 15, "salary": 80000},
            {"id": "EMP-003", "age": 60, "service_years": 30, "salary": 120000}
        ],
        plan_provisions={"formula": "final_average", "benefit_pct": 0.015},
        actuarial_assumptions={"discount_rate": 0.055, "salary_growth": 0.03},
        asset_values={"market_value": 50000000, "expected_return": 0.07},
        valuation_date="2025-12-31"
    )
    print(json.dumps(result, indent=2))
