"""
Actuarial Reserve Calculation Module

Implements reserve calculation using loss development,
IBNR estimation, and statutory requirements.
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


def load_actuarial_tables() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    method_weights_data = load_key_value_csv("method_weights.csv")
    statutory_factors_data = load_csv_as_dict("statutory_factors.csv")
    adequacy_thresholds_data = load_key_value_csv("adequacy_thresholds.csv")
    industry_ldfs_data = load_csv_as_dict("industry_ldfs.csv")
    expense_factors_data = load_csv_as_dict("expense_factors.csv")
    discount_factors_data = load_csv_as_dict("discount_factors.csv")
    params = load_parameters()
    return {
        "method_weights": method_weights_data,
        "statutory_factors": statutory_factors_data,
        "adequacy_thresholds": adequacy_thresholds_data,
        "industry_ldfs": industry_ldfs_data,
        "expense_factors": expense_factors_data,
        "discount_factors": discount_factors_data,
        **params
    }


def calculate_development_factors(
    loss_triangles: Dict,
    method: str = "chain_ladder"
) -> Dict[str, Any]:
    """Calculate loss development factors from triangles."""
    paid_triangle = loss_triangles.get("paid", [])
    incurred_triangle = loss_triangles.get("incurred", [])

    paid_ldfs = []
    incurred_ldfs = []

    # Calculate paid LDFs using chain-ladder method
    if len(paid_triangle) >= 2:
        for col in range(len(paid_triangle[0]) - 1):
            sum_current = 0
            sum_prior = 0
            for row in range(len(paid_triangle) - col):
                if col + 1 < len(paid_triangle[row]):
                    sum_current += paid_triangle[row][col + 1]
                    sum_prior += paid_triangle[row][col]
            if sum_prior > 0:
                paid_ldfs.append(round(sum_current / sum_prior, 3))

    # Calculate incurred LDFs
    if len(incurred_triangle) >= 2:
        for col in range(len(incurred_triangle[0]) - 1):
            sum_current = 0
            sum_prior = 0
            for row in range(len(incurred_triangle) - col):
                if col + 1 < len(incurred_triangle[row]):
                    sum_current += incurred_triangle[row][col + 1]
                    sum_prior += incurred_triangle[row][col]
            if sum_prior > 0:
                incurred_ldfs.append(round(sum_current / sum_prior, 3))

    return {
        "paid_ldfs": paid_ldfs,
        "incurred_ldfs": incurred_ldfs,
        "method": method,
        "paid_to_ultimate": calculate_cumulative_ldf(paid_ldfs),
        "incurred_to_ultimate": calculate_cumulative_ldf(incurred_ldfs)
    }


def calculate_cumulative_ldf(ldfs: List[float]) -> List[float]:
    """Calculate cumulative LDFs to ultimate."""
    if not ldfs:
        return []

    cumulative = []
    cum_factor = 1.0
    for i in range(len(ldfs) - 1, -1, -1):
        cum_factor *= ldfs[i]
        cumulative.insert(0, round(cum_factor, 3))

    # Add tail factor
    cumulative.append(1.0)
    return cumulative


def estimate_ibnr(
    loss_triangles: Dict,
    development_factors: Dict,
    method_weights: Dict
) -> Dict[str, Any]:
    """Estimate IBNR using multiple methods."""
    paid_triangle = loss_triangles.get("paid", [])
    incurred_triangle = loss_triangles.get("incurred", [])

    paid_ldfs = development_factors.get("paid_to_ultimate", [])
    incurred_ldfs = development_factors.get("incurred_to_ultimate", [])

    paid_ultimate = []
    incurred_ultimate = []

    # Calculate ultimate losses by accident year
    for i, row in enumerate(paid_triangle):
        if i < len(paid_ldfs):
            current_paid = row[-1] if row else 0
            ultimate = current_paid * paid_ldfs[i]
            paid_ultimate.append(round(ultimate, 2))

    for i, row in enumerate(incurred_triangle):
        if i < len(incurred_ldfs):
            current_incurred = row[-1] if row else 0
            ultimate = current_incurred * incurred_ldfs[i]
            incurred_ultimate.append(round(ultimate, 2))

    # Calculate IBNR
    total_paid = sum(row[-1] for row in paid_triangle if row)
    total_incurred = sum(row[-1] for row in incurred_triangle if row)

    paid_ibnr = sum(paid_ultimate) - total_paid
    incurred_ibnr = sum(incurred_ultimate) - total_incurred

    # Weighted average
    paid_weight = method_weights.get("paid_development", 0.5)
    incurred_weight = method_weights.get("incurred_development", 0.5)

    weighted_ibnr = paid_ibnr * paid_weight + incurred_ibnr * incurred_weight

    return {
        "paid_development_ibnr": round(paid_ibnr, 2),
        "incurred_development_ibnr": round(incurred_ibnr, 2),
        "weighted_ibnr": round(weighted_ibnr, 2),
        "ultimate_by_year": {
            "paid_method": paid_ultimate,
            "incurred_method": incurred_ultimate
        }
    }


def assess_reserve_adequacy(
    current_reserve: float,
    indicated_reserve: float,
    prior_estimates: Dict,
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess reserve adequacy against indicated levels."""
    adequacy_ratio = current_reserve / indicated_reserve if indicated_reserve > 0 else 1.0

    prior_total = prior_estimates.get("total", indicated_reserve)
    development = current_reserve - prior_total

    # Determine adequacy status
    min_ratio = thresholds.get("min_adequacy_ratio", 0.95)
    max_ratio = thresholds.get("max_adequacy_ratio", 1.10)

    if adequacy_ratio < min_ratio:
        status = "POTENTIALLY_DEFICIENT"
    elif adequacy_ratio > max_ratio:
        status = "POTENTIALLY_REDUNDANT"
    else:
        status = "ADEQUATE"

    return {
        "status": status,
        "adequacy_ratio": round(adequacy_ratio, 3),
        "current_reserve": current_reserve,
        "indicated_reserve": indicated_reserve,
        "development_from_prior": round(development, 2)
    }


def calculate_statutory_minimum(
    premium_data: Dict,
    line_of_business: str,
    statutory_factors: Dict
) -> float:
    """Calculate statutory minimum reserve."""
    factors = statutory_factors.get(line_of_business, statutory_factors.get("default", {}))

    earned_premium = sum(premium_data.values())
    loss_ratio_factor = factors.get("loss_ratio", 0.65)
    minimum_factor = factors.get("minimum_factor", 0.5)

    statutory_minimum = earned_premium * loss_ratio_factor * minimum_factor

    return round(statutory_minimum, 2)


def calculate_reserve(
    valuation_date: str,
    loss_triangles: Dict,
    case_reserves: Dict,
    premium_data: Dict,
    line_of_business: str,
    prior_estimates: Dict
) -> Dict[str, Any]:
    """
    Calculate actuarial reserves.

    Business Rules:
    1. Loss development factor calculation
    2. IBNR estimation using multiple methods
    3. Case reserve adequacy assessment
    4. Statutory minimum compliance

    Args:
        valuation_date: Reserve valuation date
        loss_triangles: Historical loss data
        case_reserves: Current case reserves
        premium_data: Earned premium by period
        line_of_business: Insurance line
        prior_estimates: Previous reserve estimates

    Returns:
        Reserve calculation results
    """
    tables = load_actuarial_tables()

    # Calculate development factors
    development_factors = calculate_development_factors(
        loss_triangles,
        method="chain_ladder"
    )

    # Estimate IBNR
    ibnr_result = estimate_ibnr(
        loss_triangles,
        development_factors,
        tables.get("method_weights", {})
    )

    # Total indicated reserve
    current_case = case_reserves.get("open_claims", 0)
    indicated_ibnr = ibnr_result.get("weighted_ibnr", 0)
    indicated_total = current_case + indicated_ibnr

    # Statutory minimum
    statutory_minimum = calculate_statutory_minimum(
        premium_data,
        line_of_business,
        tables.get("statutory_factors", {})
    )

    # Final reserve (higher of indicated or statutory)
    total_reserve = max(indicated_total, statutory_minimum)

    # Adequacy assessment
    adequacy_assessment = assess_reserve_adequacy(
        total_reserve,
        indicated_total,
        prior_estimates,
        tables.get("adequacy_thresholds", {})
    )

    return {
        "valuation_date": valuation_date,
        "line_of_business": line_of_business,
        "total_reserve": round(total_reserve, 2),
        "components": {
            "case_reserves": current_case,
            "ibnr_estimate": round(indicated_ibnr, 2)
        },
        "ibnr_estimate": round(indicated_ibnr, 2),
        "development_factors": development_factors,
        "ibnr_analysis": ibnr_result,
        "statutory_minimum": statutory_minimum,
        "adequacy_assessment": adequacy_assessment
    }


if __name__ == "__main__":
    import json
    result = calculate_reserve(
        valuation_date="2025-12-31",
        loss_triangles={
            "paid": [[100, 150, 180], [120, 175], [140]],
            "incurred": [[150, 190, 200], [180, 220], [200]]
        },
        case_reserves={"open_claims": 500000, "claim_count": 150},
        premium_data={"earned_2024": 5000000, "earned_2025": 5500000},
        line_of_business="commercial_auto",
        prior_estimates={"total": 2000000, "ibnr": 800000}
    )
    print(json.dumps(result, indent=2))
