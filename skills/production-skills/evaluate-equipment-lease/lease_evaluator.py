"""
Equipment Lease Evaluation Module

Implements lease vs buy analysis using NPV calculations,
residual value estimation, and total cost of ownership.
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


def load_equipment_economics() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    depreciation_data = load_key_value_csv("depreciation.csv")
    maintenance_costs_data = load_csv_as_dict("maintenance_costs.csv")
    lease_market_rates_data = load_csv_as_dict("lease_market_rates.csv")
    utilization_factors_data = load_csv_as_dict("utilization_factors.csv")
    financing_benchmarks_data = load_key_value_csv("financing_benchmarks.csv")
    tax_considerations_data = load_key_value_csv("tax_considerations.csv")
    params = load_parameters()
    return {
        "depreciation": depreciation_data,
        "maintenance_costs": maintenance_costs_data,
        "lease_market_rates": lease_market_rates_data,
        "utilization_factors": utilization_factors_data,
        "financing_benchmarks": financing_benchmarks_data,
        "tax_considerations": tax_considerations_data,
        **params
    }


def calculate_npv(
    cash_flows: List[float],
    discount_rate: float
) -> float:
    """Calculate net present value of cash flows."""
    npv = 0
    for t, cf in enumerate(cash_flows):
        npv += cf / ((1 + discount_rate) ** t)
    return npv


def analyze_lease_option(
    lease_terms: Dict,
    financial_params: Dict,
    equipment_specs: Dict
) -> Dict[str, Any]:
    """Analyze the lease financing option."""
    monthly_payment = lease_terms.get("monthly_payment", 0)
    term_months = lease_terms.get("term_months", 60)
    buyout = lease_terms.get("buyout", 0)

    discount_rate = financial_params.get("discount_rate", 0.08)
    tax_rate = financial_params.get("tax_rate", 0.25)
    monthly_discount = discount_rate / 12

    # Calculate after-tax lease payments (lease payments are tax deductible)
    after_tax_payment = monthly_payment * (1 - tax_rate)

    # Build cash flow schedule
    cash_flows = [0]  # Initial outlay
    for month in range(1, term_months + 1):
        cash_flows.append(-after_tax_payment)

    # Add buyout at end if exercised
    if buyout > 0:
        cash_flows[-1] -= buyout

    # Calculate NPV
    annual_flows = []
    for year in range((term_months // 12) + 1):
        start = year * 12
        end = min(start + 12, len(cash_flows))
        annual_flows.append(sum(cash_flows[start:end]))

    npv_lease = calculate_npv(annual_flows, discount_rate)

    total_payments = monthly_payment * term_months + buyout

    return {
        "npv": round(npv_lease, 2),
        "total_payments": round(total_payments, 2),
        "monthly_payment": monthly_payment,
        "term_months": term_months,
        "buyout": buyout,
        "after_tax_monthly": round(after_tax_payment, 2)
    }


def analyze_purchase_option(
    purchase_price: float,
    equipment_specs: Dict,
    financial_params: Dict,
    depreciation_schedule: Dict
) -> Dict[str, Any]:
    """Analyze the purchase financing option."""
    useful_life = equipment_specs.get("useful_life_years", 7)
    discount_rate = financial_params.get("discount_rate", 0.08)
    tax_rate = financial_params.get("tax_rate", 0.25)

    # Calculate depreciation tax shield
    depreciation_method = depreciation_schedule.get("method", "straight_line")
    annual_depreciation = purchase_price / useful_life
    tax_shield_per_year = annual_depreciation * tax_rate

    # Estimate residual value
    residual_pct = depreciation_schedule.get("residual_pct", 0.15)
    residual_value = purchase_price * residual_pct

    # Build cash flows
    cash_flows = [-purchase_price]  # Initial purchase
    for year in range(1, useful_life + 1):
        if year < useful_life:
            cash_flows.append(tax_shield_per_year)
        else:
            # Final year includes residual value
            cash_flows.append(tax_shield_per_year + residual_value)

    npv_purchase = calculate_npv(cash_flows, discount_rate)

    return {
        "npv": round(npv_purchase, 2),
        "purchase_price": purchase_price,
        "residual_value": round(residual_value, 2),
        "annual_depreciation": round(annual_depreciation, 2),
        "annual_tax_shield": round(tax_shield_per_year, 2),
        "useful_life_years": useful_life
    }


def calculate_tco(
    equipment_specs: Dict,
    usage_profile: Dict,
    maintenance_costs: Dict,
    years: int
) -> Dict[str, Any]:
    """Calculate total cost of ownership."""
    hours_per_year = usage_profile.get("hours_per_year", 2000)
    intensity = usage_profile.get("intensity", "medium")

    # Base maintenance per hour
    equipment_type = equipment_specs.get("type", "general")
    base_maintenance = maintenance_costs.get("base_per_hour", {}).get(equipment_type, 15)

    # Intensity multiplier
    intensity_mult = {"light": 0.8, "medium": 1.0, "heavy": 1.3}.get(intensity, 1.0)

    annual_maintenance = hours_per_year * base_maintenance * intensity_mult

    # Fuel/energy costs
    fuel_per_hour = maintenance_costs.get("fuel_per_hour", {}).get(equipment_type, 25)
    annual_fuel = hours_per_year * fuel_per_hour

    # Insurance and other
    insurance_pct = maintenance_costs.get("insurance_pct", 0.02)

    tco_breakdown = {
        "maintenance": round(annual_maintenance * years, 2),
        "fuel_energy": round(annual_fuel * years, 2),
        "insurance_estimated": "varies by acquisition method"
    }

    annual_operating = annual_maintenance + annual_fuel

    return {
        "annual_operating_cost": round(annual_operating, 2),
        "total_operating_cost": round(annual_operating * years, 2),
        "breakdown": tco_breakdown,
        "per_hour_cost": round((annual_maintenance + annual_fuel) / hours_per_year, 2)
    }


def find_break_even(
    lease_analysis: Dict,
    purchase_analysis: Dict,
    financial_params: Dict
) -> Dict[str, Any]:
    """Find break-even point between lease and purchase."""
    lease_npv = abs(lease_analysis["npv"])
    purchase_npv = abs(purchase_analysis["npv"])

    lease_monthly = lease_analysis["monthly_payment"]
    term_months = lease_analysis["term_months"]

    # Simplified break-even calculation
    if lease_npv < purchase_npv:
        # Lease is better - calculate how long until purchase becomes better
        npv_diff = purchase_npv - lease_npv
        break_even_months = term_months + (npv_diff / lease_monthly) if lease_monthly > 0 else term_months
    else:
        # Purchase is better from start
        break_even_months = 0

    return {
        "break_even_months": round(break_even_months, 1),
        "break_even_years": round(break_even_months / 12, 2),
        "lease_npv": lease_npv,
        "purchase_npv": purchase_npv,
        "npv_advantage": round(purchase_npv - lease_npv, 2)
    }


def evaluate_lease(
    equipment_id: str,
    equipment_specs: Dict,
    lease_terms: Dict,
    purchase_price: float,
    usage_profile: Dict,
    financial_params: Dict
) -> Dict[str, Any]:
    """
    Evaluate equipment lease vs purchase.

    Business Rules:
    1. NPV comparison of lease vs buy
    2. Residual value estimation
    3. Tax benefit analysis
    4. Total cost of ownership

    Args:
        equipment_id: Equipment identifier
        equipment_specs: Equipment details
        lease_terms: Proposed lease terms
        purchase_price: Cash purchase price
        usage_profile: Expected utilization
        financial_params: Company financial parameters

    Returns:
        Lease evaluation results
    """
    economics = load_equipment_economics()

    risk_factors = []

    # Analyze lease option
    lease_analysis = analyze_lease_option(
        lease_terms,
        financial_params,
        equipment_specs
    )

    # Analyze purchase option
    purchase_analysis = analyze_purchase_option(
        purchase_price,
        equipment_specs,
        financial_params,
        economics.get("depreciation", {})
    )

    # Calculate TCO
    useful_life = equipment_specs.get("useful_life_years", 7)
    tco_analysis = calculate_tco(
        equipment_specs,
        usage_profile,
        economics.get("maintenance_costs", {}),
        useful_life
    )

    # Find break-even
    break_even = find_break_even(
        lease_analysis,
        purchase_analysis,
        financial_params
    )

    # Determine recommendation
    lease_npv = abs(lease_analysis["npv"])
    purchase_npv = abs(purchase_analysis["npv"])

    if lease_npv < purchase_npv * 0.95:
        recommendation = "LEASE"
        rationale = "Lease provides better NPV by more than 5%"
    elif purchase_npv < lease_npv * 0.95:
        recommendation = "PURCHASE"
        rationale = "Purchase provides better NPV by more than 5%"
    else:
        recommendation = "EITHER"
        rationale = "NPV difference less than 5% - consider strategic factors"

    # Add risk factors
    intensity = usage_profile.get("intensity", "medium")
    if intensity == "heavy":
        risk_factors.append({
            "factor": "High utilization",
            "impact": "May accelerate depreciation beyond estimates",
            "recommendation": "Lease may reduce ownership risk"
        })

    term_months = lease_terms.get("term_months", 60)
    if term_months > useful_life * 12 * 0.7:
        risk_factors.append({
            "factor": "Long lease term",
            "impact": "Lease term approaches useful life",
            "recommendation": "Consider purchase for long-term use"
        })

    return {
        "equipment_id": equipment_id,
        "recommendation": recommendation,
        "rationale": rationale,
        "npv_comparison": {
            "lease_npv": lease_analysis["npv"],
            "purchase_npv": purchase_analysis["npv"],
            "advantage": "lease" if lease_npv < purchase_npv else "purchase",
            "savings": round(abs(purchase_npv - lease_npv), 2)
        },
        "lease_analysis": lease_analysis,
        "purchase_analysis": purchase_analysis,
        "tco_analysis": tco_analysis,
        "break_even_point": break_even,
        "risk_factors": risk_factors
    }


if __name__ == "__main__":
    import json
    result = evaluate_lease(
        equipment_id="EQ-2026-001",
        equipment_specs={"type": "excavator", "model": "CAT 320", "useful_life_years": 10},
        lease_terms={"monthly_payment": 5000, "term_months": 60, "buyout": 50000},
        purchase_price=350000,
        usage_profile={"hours_per_year": 2000, "intensity": "heavy"},
        financial_params={"discount_rate": 0.08, "tax_rate": 0.25}
    )
    print(json.dumps(result, indent=2))
