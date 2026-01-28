"""
Break-Even Analysis Module

Implements break-even calculation including
contribution margin, sensitivity analysis, and scenario modeling.
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


def load_break_even_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    cost_classifications_data = load_csv_as_dict("cost_classifications.csv")
    margin_benchmarks_data = load_csv_as_dict("margin_benchmarks.csv")
    safety_margin_thresholds_data = load_key_value_csv("safety_margin_thresholds.csv")
    operating_leverage_interpretation_data = load_csv_as_dict("operating_leverage_interpretation.csv")
    scenario_assumptions_data = load_csv_as_dict("scenario_assumptions.csv")
    params = load_parameters()
    return {
        "cost_classifications": cost_classifications_data,
        "margin_benchmarks": margin_benchmarks_data,
        "safety_margin_thresholds": safety_margin_thresholds_data,
        "operating_leverage_interpretation": operating_leverage_interpretation_data,
        "scenario_assumptions": scenario_assumptions_data,
        **params
    }


def calculate_contribution_margin(
    unit_price: float,
    variable_cost_per_unit: float
) -> Dict[str, Any]:
    """Calculate contribution margin."""
    contribution_margin = unit_price - variable_cost_per_unit
    contribution_margin_ratio = contribution_margin / unit_price if unit_price > 0 else 0

    return {
        "unit_price": unit_price,
        "variable_cost_per_unit": variable_cost_per_unit,
        "contribution_margin": round(contribution_margin, 2),
        "contribution_margin_ratio": round(contribution_margin_ratio, 4)
    }


def calculate_break_even_units(
    fixed_costs: float,
    contribution_margin: float
) -> Dict[str, Any]:
    """Calculate break-even in units."""
    if contribution_margin <= 0:
        return {
            "break_even_units": None,
            "error": "Contribution margin must be positive"
        }

    break_even_units = fixed_costs / contribution_margin

    return {
        "fixed_costs": fixed_costs,
        "contribution_margin": contribution_margin,
        "break_even_units": round(break_even_units, 0)
    }


def calculate_break_even_revenue(
    fixed_costs: float,
    contribution_margin_ratio: float
) -> Dict[str, Any]:
    """Calculate break-even in revenue dollars."""
    if contribution_margin_ratio <= 0:
        return {
            "break_even_revenue": None,
            "error": "Contribution margin ratio must be positive"
        }

    break_even_revenue = fixed_costs / contribution_margin_ratio

    return {
        "fixed_costs": fixed_costs,
        "contribution_margin_ratio": contribution_margin_ratio,
        "break_even_revenue": round(break_even_revenue, 2)
    }


def calculate_target_profit_volume(
    fixed_costs: float,
    target_profit: float,
    contribution_margin: float
) -> Dict[str, Any]:
    """Calculate volume needed for target profit."""
    if contribution_margin <= 0:
        return {"error": "Contribution margin must be positive"}

    required_units = (fixed_costs + target_profit) / contribution_margin

    return {
        "fixed_costs": fixed_costs,
        "target_profit": target_profit,
        "contribution_margin": contribution_margin,
        "required_units": round(required_units, 0),
        "required_revenue": round(required_units * (contribution_margin + fixed_costs / required_units), 2) if required_units > 0 else 0
    }


def calculate_safety_margin(
    actual_sales: float,
    break_even_sales: float
) -> Dict[str, Any]:
    """Calculate margin of safety."""
    safety_margin = actual_sales - break_even_sales
    safety_margin_ratio = safety_margin / actual_sales if actual_sales > 0 else 0

    return {
        "actual_sales": actual_sales,
        "break_even_sales": break_even_sales,
        "safety_margin": round(safety_margin, 2),
        "safety_margin_ratio": round(safety_margin_ratio, 4),
        "safety_margin_pct": round(safety_margin_ratio * 100, 1)
    }


def calculate_operating_leverage(
    contribution_margin_total: float,
    operating_income: float
) -> Dict[str, Any]:
    """Calculate degree of operating leverage."""
    if operating_income <= 0:
        return {"dol": None, "error": "Operating income must be positive"}

    dol = contribution_margin_total / operating_income

    return {
        "contribution_margin_total": contribution_margin_total,
        "operating_income": operating_income,
        "degree_of_operating_leverage": round(dol, 2)
    }


def perform_sensitivity_analysis(
    base_price: float,
    base_variable_cost: float,
    base_fixed_costs: float,
    sensitivity_ranges: Dict
) -> Dict[str, Any]:
    """Perform sensitivity analysis on break-even."""
    results = []

    price_changes = sensitivity_ranges.get("price_change_pct", [-10, 0, 10])
    variable_changes = sensitivity_ranges.get("variable_cost_change_pct", [-10, 0, 10])

    for price_change in price_changes:
        for var_change in variable_changes:
            adjusted_price = base_price * (1 + price_change / 100)
            adjusted_variable = base_variable_cost * (1 + var_change / 100)

            cm = adjusted_price - adjusted_variable
            if cm > 0:
                be_units = base_fixed_costs / cm
                be_revenue = be_units * adjusted_price
            else:
                be_units = None
                be_revenue = None

            results.append({
                "price_change_pct": price_change,
                "variable_cost_change_pct": var_change,
                "break_even_units": round(be_units, 0) if be_units else None,
                "break_even_revenue": round(be_revenue, 0) if be_revenue else None
            })

    return {
        "sensitivity_results": results,
        "base_assumptions": {
            "price": base_price,
            "variable_cost": base_variable_cost,
            "fixed_costs": base_fixed_costs
        }
    }


def model_scenarios(
    base_price: float,
    base_variable_cost: float,
    base_fixed_costs: float,
    expected_volume: int,
    scenario_assumptions: Dict
) -> Dict[str, Any]:
    """Model different business scenarios."""
    scenarios = {}

    for scenario, multipliers in scenario_assumptions.items():
        price = base_price * multipliers.get("price_multiplier", 1.0)
        volume = expected_volume * multipliers.get("volume_multiplier", 1.0)

        cm = price - base_variable_cost
        total_cm = cm * volume
        operating_income = total_cm - base_fixed_costs

        scenarios[scenario] = {
            "price": round(price, 2),
            "volume": round(volume, 0),
            "contribution_margin": round(cm, 2),
            "total_contribution": round(total_cm, 2),
            "operating_income": round(operating_income, 2),
            "profitable": operating_income > 0
        }

    return scenarios


def calculate_multi_product_break_even(
    products: List[Dict]
) -> Dict[str, Any]:
    """Calculate break-even for multiple products."""
    total_weighted_cm = 0
    total_mix = 0

    product_analysis = []

    for product in products:
        price = product.get("price", 0)
        variable_cost = product.get("variable_cost", 0)
        sales_mix = product.get("sales_mix_pct", 0) / 100

        cm = price - variable_cost
        weighted_cm = cm * sales_mix

        total_weighted_cm += weighted_cm
        total_mix += sales_mix

        product_analysis.append({
            "product": product.get("name", "Unknown"),
            "price": price,
            "variable_cost": variable_cost,
            "contribution_margin": round(cm, 2),
            "sales_mix_pct": product.get("sales_mix_pct", 0),
            "weighted_contribution": round(weighted_cm, 2)
        })

    return {
        "products": product_analysis,
        "weighted_average_contribution_margin": round(total_weighted_cm, 2),
        "total_sales_mix": round(total_mix * 100, 1)
    }


def assess_risk_level(
    safety_margin_ratio: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess risk level based on safety margin."""
    if safety_margin_ratio < thresholds.get("high_risk", 0.10):
        risk_level = "HIGH"
        recommendation = "Increase sales volume or reduce costs urgently"
    elif safety_margin_ratio < thresholds.get("moderate_risk", 0.20):
        risk_level = "MODERATE"
        recommendation = "Monitor closely and develop contingency plans"
    elif safety_margin_ratio < thresholds.get("low_risk", 0.30):
        risk_level = "LOW"
        recommendation = "Continue monitoring, consider growth investments"
    else:
        risk_level = "MINIMAL"
        recommendation = "Strong position, focus on optimization"

    return {
        "risk_level": risk_level,
        "safety_margin_ratio": round(safety_margin_ratio, 4),
        "recommendation": recommendation
    }


def calculate_break_even(
    analysis_id: str,
    unit_price: float,
    variable_cost_per_unit: float,
    fixed_costs: float,
    expected_sales_units: int,
    target_profit: Optional[float],
    products: Optional[List[Dict]],
    industry: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Calculate break-even analysis.

    Business Rules:
    1. Contribution margin calculation
    2. Break-even point determination
    3. Sensitivity analysis
    4. Margin of safety assessment

    Args:
        analysis_id: Analysis identifier
        unit_price: Selling price per unit
        variable_cost_per_unit: Variable cost per unit
        fixed_costs: Total fixed costs
        expected_sales_units: Expected sales volume
        target_profit: Target profit (optional)
        products: Multi-product data (optional)
        industry: Industry for benchmarking
        analysis_date: Analysis date

    Returns:
        Break-even analysis results
    """
    params = load_break_even_parameters()
    benchmarks = params.get("margin_benchmarks", {}).get(industry, {})

    # Calculate contribution margin
    cm_result = calculate_contribution_margin(unit_price, variable_cost_per_unit)

    # Calculate break-even units
    be_units = calculate_break_even_units(fixed_costs, cm_result["contribution_margin"])

    # Calculate break-even revenue
    be_revenue = calculate_break_even_revenue(fixed_costs, cm_result["contribution_margin_ratio"])

    # Calculate safety margin
    expected_revenue = expected_sales_units * unit_price
    safety = calculate_safety_margin(expected_revenue, be_revenue.get("break_even_revenue", 0))

    # Calculate operating leverage
    total_cm = cm_result["contribution_margin"] * expected_sales_units
    operating_income = total_cm - fixed_costs
    leverage = calculate_operating_leverage(total_cm, operating_income) if operating_income > 0 else {"degree_of_operating_leverage": None}

    # Target profit analysis
    target_analysis = None
    if target_profit:
        target_analysis = calculate_target_profit_volume(
            fixed_costs,
            target_profit,
            cm_result["contribution_margin"]
        )

    # Sensitivity analysis
    sensitivity = perform_sensitivity_analysis(
        unit_price,
        variable_cost_per_unit,
        fixed_costs,
        params.get("sensitivity_ranges", {})
    )

    # Scenario modeling
    scenarios = model_scenarios(
        unit_price,
        variable_cost_per_unit,
        fixed_costs,
        expected_sales_units,
        params.get("scenario_assumptions", {})
    )

    # Multi-product analysis
    multi_product = None
    if products:
        multi_product = calculate_multi_product_break_even(products)

    # Risk assessment
    risk = assess_risk_level(
        safety["safety_margin_ratio"],
        params.get("safety_margin_thresholds", {})
    )

    # Compare to benchmarks
    benchmark_comparison = {
        "contribution_margin_ratio": cm_result["contribution_margin_ratio"],
        "benchmark_ratio": benchmarks.get("typical_contribution_margin", 0.40),
        "vs_benchmark": "above" if cm_result["contribution_margin_ratio"] > benchmarks.get("typical_contribution_margin", 0.40) else "below"
    }

    return {
        "analysis_id": analysis_id,
        "analysis_date": analysis_date,
        "industry": industry,
        "inputs": {
            "unit_price": unit_price,
            "variable_cost_per_unit": variable_cost_per_unit,
            "fixed_costs": fixed_costs,
            "expected_sales_units": expected_sales_units
        },
        "contribution_margin": cm_result,
        "break_even": {
            "units": be_units,
            "revenue": be_revenue
        },
        "safety_margin": safety,
        "operating_leverage": leverage,
        "target_profit_analysis": target_analysis,
        "sensitivity_analysis": sensitivity,
        "scenario_analysis": scenarios,
        "multi_product_analysis": multi_product,
        "risk_assessment": risk,
        "benchmark_comparison": benchmark_comparison,
        "summary": {
            "break_even_units": be_units.get("break_even_units", 0),
            "break_even_revenue": be_revenue.get("break_even_revenue", 0),
            "safety_margin_pct": safety["safety_margin_pct"],
            "risk_level": risk["risk_level"],
            "expected_profit": round(operating_income, 2)
        }
    }


if __name__ == "__main__":
    import json
    result = calculate_break_even(
        analysis_id="BE-001",
        unit_price=50.00,
        variable_cost_per_unit=30.00,
        fixed_costs=200000,
        expected_sales_units=15000,
        target_profit=100000,
        products=None,
        industry="manufacturing",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
