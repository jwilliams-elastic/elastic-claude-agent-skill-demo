"""
Depreciation Schedule Calculation Module

Implements depreciation calculation using
multiple methods including MACRS, straight-line, and accelerated methods.
"""

import csv
import ast
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


def load_depreciation_methods() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    depreciation_methods_data = load_csv_as_dict("depreciation_methods.csv")
    asset_categories_data = load_csv_as_dict("asset_categories.csv")
    section_179_limits_data = load_csv_as_dict("section_179_limits.csv")
    bonus_depreciation_data = load_csv_as_dict("bonus_depreciation.csv")
    accounting_standards_data = load_csv_as_dict("accounting_standards.csv")
    params = load_parameters()
    return {
        "depreciation_methods": depreciation_methods_data,
        "asset_categories": asset_categories_data,
        "section_179_limits": section_179_limits_data,
        "bonus_depreciation": bonus_depreciation_data,
        "accounting_standards": accounting_standards_data,
        **params
    }


def calculate_straight_line(
    cost: float,
    salvage_value: float,
    useful_life_years: int
) -> List[Dict]:
    """Calculate straight-line depreciation schedule."""
    depreciable_base = cost - salvage_value
    annual_depreciation = depreciable_base / useful_life_years

    schedule = []
    accumulated = 0

    for year in range(1, useful_life_years + 1):
        accumulated += annual_depreciation
        book_value = cost - accumulated

        schedule.append({
            "year": year,
            "depreciation_expense": round(annual_depreciation, 2),
            "accumulated_depreciation": round(accumulated, 2),
            "book_value": round(book_value, 2)
        })

    return schedule


def calculate_declining_balance(
    cost: float,
    salvage_value: float,
    useful_life_years: int,
    rate_multiplier: float = 2.0
) -> List[Dict]:
    """Calculate declining balance depreciation schedule."""
    rate = (1 / useful_life_years) * rate_multiplier
    schedule = []
    book_value = cost
    accumulated = 0

    for year in range(1, useful_life_years + 1):
        # Don't depreciate below salvage value
        max_depreciation = book_value - salvage_value
        depreciation = min(book_value * rate, max_depreciation)

        if depreciation < 0:
            depreciation = 0

        accumulated += depreciation
        book_value = cost - accumulated

        schedule.append({
            "year": year,
            "depreciation_expense": round(depreciation, 2),
            "accumulated_depreciation": round(accumulated, 2),
            "book_value": round(book_value, 2)
        })

    return schedule


def calculate_sum_of_years_digits(
    cost: float,
    salvage_value: float,
    useful_life_years: int
) -> List[Dict]:
    """Calculate sum-of-years-digits depreciation schedule."""
    depreciable_base = cost - salvage_value
    sum_of_years = sum(range(1, useful_life_years + 1))

    schedule = []
    accumulated = 0

    for year in range(1, useful_life_years + 1):
        remaining_life = useful_life_years - year + 1
        depreciation = (remaining_life / sum_of_years) * depreciable_base

        accumulated += depreciation
        book_value = cost - accumulated

        schedule.append({
            "year": year,
            "depreciation_expense": round(depreciation, 2),
            "accumulated_depreciation": round(accumulated, 2),
            "book_value": round(book_value, 2)
        })

    return schedule


def calculate_units_of_production(
    cost: float,
    salvage_value: float,
    total_units: int,
    units_per_year: List[int]
) -> List[Dict]:
    """Calculate units-of-production depreciation schedule."""
    depreciable_base = cost - salvage_value
    rate_per_unit = depreciable_base / total_units

    schedule = []
    accumulated = 0

    for year, units in enumerate(units_per_year, 1):
        depreciation = units * rate_per_unit
        accumulated += depreciation
        book_value = cost - accumulated

        schedule.append({
            "year": year,
            "units_produced": units,
            "depreciation_expense": round(depreciation, 2),
            "accumulated_depreciation": round(accumulated, 2),
            "book_value": round(max(book_value, salvage_value), 2)
        })

    return schedule


def calculate_macrs(
    cost: float,
    macrs_class: str,
    macrs_tables: Dict
) -> List[Dict]:
    """Calculate MACRS depreciation schedule."""
    rates = macrs_tables.get(macrs_class, macrs_tables.get("5-year", []))

    schedule = []
    accumulated = 0

    for year, rate in enumerate(rates, 1):
        depreciation = cost * rate
        accumulated += depreciation
        book_value = cost - accumulated

        schedule.append({
            "year": year,
            "macrs_rate": round(rate * 100, 2),
            "depreciation_expense": round(depreciation, 2),
            "accumulated_depreciation": round(accumulated, 2),
            "book_value": round(book_value, 2)
        })

    return schedule


def apply_section_179(
    cost: float,
    section_179_limits: Dict,
    year: str
) -> Dict[str, Any]:
    """Calculate Section 179 deduction if applicable."""
    limits = section_179_limits.get(year, {"max_deduction": 0, "phase_out_threshold": 0})
    max_deduction = limits.get("max_deduction", 0)
    phase_out = limits.get("phase_out_threshold", 0)

    if cost > phase_out:
        reduction = cost - phase_out
        available_deduction = max(0, max_deduction - reduction)
    else:
        available_deduction = min(cost, max_deduction)

    return {
        "section_179_eligible": cost <= phase_out + max_deduction,
        "max_deduction_available": available_deduction,
        "remaining_basis": cost - available_deduction if available_deduction > 0 else cost
    }


def apply_bonus_depreciation(
    basis: float,
    bonus_config: Dict,
    year: str
) -> Dict[str, Any]:
    """Calculate bonus depreciation if applicable."""
    rate = bonus_config.get(year, {}).get("rate", 0)
    bonus_amount = basis * rate
    remaining_basis = basis - bonus_amount

    return {
        "bonus_rate": rate,
        "bonus_depreciation": round(bonus_amount, 2),
        "remaining_basis": round(remaining_basis, 2)
    }


def compare_methods(
    cost: float,
    salvage_value: float,
    useful_life: int,
    macrs_class: str,
    macrs_tables: Dict
) -> Dict[str, Any]:
    """Compare depreciation across methods."""
    methods_comparison = {}

    # Straight-line
    sl_schedule = calculate_straight_line(cost, salvage_value, useful_life)
    methods_comparison["straight_line"] = {
        "year_1_depreciation": sl_schedule[0]["depreciation_expense"] if sl_schedule else 0,
        "total_depreciation": sum(s["depreciation_expense"] for s in sl_schedule)
    }

    # Double declining balance
    ddb_schedule = calculate_declining_balance(cost, salvage_value, useful_life, 2.0)
    methods_comparison["double_declining"] = {
        "year_1_depreciation": ddb_schedule[0]["depreciation_expense"] if ddb_schedule else 0,
        "total_depreciation": sum(s["depreciation_expense"] for s in ddb_schedule)
    }

    # Sum of years digits
    syd_schedule = calculate_sum_of_years_digits(cost, salvage_value, useful_life)
    methods_comparison["sum_of_years_digits"] = {
        "year_1_depreciation": syd_schedule[0]["depreciation_expense"] if syd_schedule else 0,
        "total_depreciation": sum(s["depreciation_expense"] for s in syd_schedule)
    }

    # MACRS
    macrs_schedule = calculate_macrs(cost, macrs_class, macrs_tables)
    methods_comparison["macrs"] = {
        "year_1_depreciation": macrs_schedule[0]["depreciation_expense"] if macrs_schedule else 0,
        "total_depreciation": sum(s["depreciation_expense"] for s in macrs_schedule)
    }

    return methods_comparison


def calculate_depreciation_schedule(
    asset_id: str,
    asset_description: str,
    asset_category: str,
    acquisition_cost: float,
    acquisition_date: str,
    depreciation_method: str,
    apply_section_179_election: bool,
    apply_bonus_depreciation_election: bool,
    units_per_year: Optional[List[int]] = None,
    total_units: Optional[int] = None
) -> Dict[str, Any]:
    """
    Calculate depreciation schedule.

    Business Rules:
    1. Multiple depreciation method support
    2. MACRS for tax purposes
    3. Section 179 and bonus depreciation
    4. Book vs. tax depreciation tracking

    Args:
        asset_id: Asset identifier
        asset_description: Asset description
        asset_category: Category for useful life
        acquisition_cost: Asset cost
        acquisition_date: Date acquired
        depreciation_method: Method to use
        apply_section_179_election: Apply Section 179
        apply_bonus_depreciation_election: Apply bonus depreciation
        units_per_year: Units produced each year (for units of production)
        total_units: Total expected units (for units of production)

    Returns:
        Depreciation schedule results
    """
    config = load_depreciation_methods()
    categories = config.get("asset_categories", {})
    macrs_tables = config.get("macrs_tables", {})

    # Get asset category parameters
    category_config = categories.get(asset_category, categories.get("machinery", {}))
    useful_life = category_config.get("useful_life_years", 7)
    salvage_pct = category_config.get("salvage_pct", 0.10)
    macrs_class = category_config.get("macrs_class", "7-year")

    salvage_value = acquisition_cost * salvage_pct

    # Apply Section 179 if elected
    basis = acquisition_cost
    section_179_result = None
    if apply_section_179_election:
        acquisition_year = acquisition_date[:4]
        section_179_result = apply_section_179(
            acquisition_cost,
            config.get("section_179_limits", {}),
            acquisition_year
        )
        basis = section_179_result["remaining_basis"]

    # Apply bonus depreciation if elected
    bonus_result = None
    if apply_bonus_depreciation_election and basis > 0:
        acquisition_year = acquisition_date[:4]
        bonus_result = apply_bonus_depreciation(
            basis,
            config.get("bonus_depreciation", {}),
            acquisition_year
        )
        basis = bonus_result["remaining_basis"]

    # Calculate depreciation schedule based on method
    if depreciation_method == "straight_line":
        schedule = calculate_straight_line(basis, salvage_value * (basis / acquisition_cost), useful_life)
    elif depreciation_method == "declining_balance":
        schedule = calculate_declining_balance(basis, salvage_value * (basis / acquisition_cost), useful_life, 2.0)
    elif depreciation_method == "sum_of_years_digits":
        schedule = calculate_sum_of_years_digits(basis, salvage_value * (basis / acquisition_cost), useful_life)
    elif depreciation_method == "units_of_production" and units_per_year and total_units:
        schedule = calculate_units_of_production(basis, salvage_value * (basis / acquisition_cost), total_units, units_per_year)
    elif depreciation_method == "macrs":
        schedule = calculate_macrs(basis, macrs_class, macrs_tables)
    else:
        schedule = calculate_straight_line(basis, salvage_value * (basis / acquisition_cost), useful_life)

    # Compare methods
    comparison = compare_methods(basis, salvage_value * (basis / acquisition_cost), useful_life, macrs_class, macrs_tables)

    # Calculate totals
    total_depreciation = sum(s["depreciation_expense"] for s in schedule)
    if section_179_result:
        total_depreciation += section_179_result.get("max_deduction_available", 0)
    if bonus_result:
        total_depreciation += bonus_result.get("bonus_depreciation", 0)

    return {
        "asset_id": asset_id,
        "asset_description": asset_description,
        "asset_category": asset_category,
        "acquisition_cost": acquisition_cost,
        "acquisition_date": acquisition_date,
        "depreciation_method": depreciation_method,
        "parameters": {
            "useful_life_years": useful_life,
            "salvage_value": round(salvage_value, 2),
            "macrs_class": macrs_class
        },
        "section_179": section_179_result,
        "bonus_depreciation": bonus_result,
        "depreciable_basis": round(basis, 2),
        "depreciation_schedule": schedule,
        "method_comparison": comparison,
        "summary": {
            "total_depreciation": round(total_depreciation, 2),
            "final_book_value": schedule[-1]["book_value"] if schedule else acquisition_cost,
            "schedule_years": len(schedule)
        }
    }


if __name__ == "__main__":
    import json
    result = calculate_depreciation_schedule(
        asset_id="AST-001",
        asset_description="Manufacturing Equipment",
        asset_category="machinery",
        acquisition_cost=150000,
        acquisition_date="2026-01-15",
        depreciation_method="macrs",
        apply_section_179_election=True,
        apply_bonus_depreciation_election=True
    )
    print(json.dumps(result, indent=2))
