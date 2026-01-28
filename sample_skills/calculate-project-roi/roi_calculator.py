"""
Project ROI Calculation Module

Implements project return on investment analysis including
NPV, IRR, payback period, and sensitivity analysis.
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


def load_roi_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    discount_rates_data = load_key_value_csv("discount_rates.csv")
    project_categories_data = load_csv_as_dict("project_categories.csv")
    benefit_categories_data = load_csv_as_dict("benefit_categories.csv")
    cost_categories_data = load_csv_as_dict("cost_categories.csv")
    hurdle_rates_data = load_key_value_csv("hurdle_rates.csv")
    payback_thresholds_data = load_key_value_csv("payback_thresholds.csv")
    npv_thresholds_data = load_key_value_csv("npv_thresholds.csv")
    sensitivity_scenarios_data = load_csv_as_dict("sensitivity_scenarios.csv")
    risk_adjustments_data = load_csv_as_dict("risk_adjustments.csv")
    params = load_parameters()
    return {
        "discount_rates": discount_rates_data,
        "project_categories": project_categories_data,
        "benefit_categories": benefit_categories_data,
        "cost_categories": cost_categories_data,
        "hurdle_rates": hurdle_rates_data,
        "payback_thresholds": payback_thresholds_data,
        "npv_thresholds": npv_thresholds_data,
        "sensitivity_scenarios": sensitivity_scenarios_data,
        "risk_adjustments": risk_adjustments_data,
        **params
    }


def calculate_total_costs(
    costs: List[Dict],
    project_years: int,
    cost_categories: Dict
) -> Dict[str, Any]:
    """Calculate total project costs over time."""
    yearly_costs = [0] * (project_years + 1)  # Year 0 through project_years
    cost_breakdown = {}

    for cost in costs:
        category = cost.get("category", "implementation")
        amount = cost.get("amount", 0)
        year = cost.get("year", 0)
        cost_config = cost_categories.get(category, {"type": "one_time"})

        if cost_config.get("type") == "one_time":
            if year <= project_years:
                yearly_costs[year] += amount
                cost_breakdown[category] = cost_breakdown.get(category, 0) + amount
        else:  # recurring
            growth_rate = cost_config.get("growth_rate", 0)
            recurring_amount = amount
            for y in range(1, project_years + 1):
                yearly_costs[y] += recurring_amount
                cost_breakdown[category] = cost_breakdown.get(category, 0) + recurring_amount
                recurring_amount *= (1 + growth_rate)

    return {
        "yearly_costs": [round(c, 2) for c in yearly_costs],
        "total_cost": round(sum(yearly_costs), 2),
        "cost_breakdown": cost_breakdown
    }


def calculate_total_benefits(
    benefits: List[Dict],
    project_years: int,
    benefit_categories: Dict
) -> Dict[str, Any]:
    """Calculate total project benefits over time."""
    yearly_benefits = [0] * (project_years + 1)
    benefit_breakdown = {}
    risk_adjusted_benefits = [0] * (project_years + 1)

    for benefit in benefits:
        category = benefit.get("category", "hard_savings")
        amount = benefit.get("annual_amount", 0)
        start_year = benefit.get("start_year", 1)
        growth_rate = benefit.get("growth_rate", 0)

        config = benefit_categories.get(category, {"confidence": 0.50, "weight": 0.5})
        confidence = config.get("confidence", 0.50)
        weight = config.get("weight", 0.5)

        current_amount = amount
        for y in range(start_year, project_years + 1):
            yearly_benefits[y] += current_amount
            risk_adjusted_benefits[y] += current_amount * confidence * weight
            benefit_breakdown[category] = benefit_breakdown.get(category, 0) + current_amount
            current_amount *= (1 + growth_rate)

    return {
        "yearly_benefits": [round(b, 2) for b in yearly_benefits],
        "total_benefits": round(sum(yearly_benefits), 2),
        "risk_adjusted_yearly": [round(b, 2) for b in risk_adjusted_benefits],
        "risk_adjusted_total": round(sum(risk_adjusted_benefits), 2),
        "benefit_breakdown": benefit_breakdown
    }


def calculate_net_cash_flows(
    yearly_costs: List[float],
    yearly_benefits: List[float]
) -> List[float]:
    """Calculate net cash flows."""
    return [round(b - c, 2) for b, c in zip(yearly_benefits, yearly_costs)]


def calculate_npv(
    cash_flows: List[float],
    discount_rate: float
) -> Dict[str, Any]:
    """Calculate Net Present Value."""
    npv = 0
    discounted_flows = []

    for year, cf in enumerate(cash_flows):
        discount_factor = (1 + discount_rate) ** year
        discounted_cf = cf / discount_factor
        npv += discounted_cf
        discounted_flows.append({
            "year": year,
            "cash_flow": cf,
            "discount_factor": round(discount_factor, 4),
            "present_value": round(discounted_cf, 2)
        })

    return {
        "npv": round(npv, 2),
        "discount_rate": discount_rate,
        "discounted_flows": discounted_flows
    }


def calculate_irr(
    cash_flows: List[float],
    max_iterations: int = 100,
    tolerance: float = 0.0001
) -> Dict[str, Any]:
    """Calculate Internal Rate of Return using Newton-Raphson method."""
    if len(cash_flows) < 2:
        return {"irr": None, "error": "Insufficient cash flows"}

    # Initial guess
    irr = 0.10

    for _ in range(max_iterations):
        npv = sum(cf / (1 + irr) ** i for i, cf in enumerate(cash_flows))
        npv_derivative = sum(-i * cf / (1 + irr) ** (i + 1) for i, cf in enumerate(cash_flows))

        if abs(npv_derivative) < tolerance:
            break

        new_irr = irr - npv / npv_derivative

        if abs(new_irr - irr) < tolerance:
            return {"irr": round(new_irr, 4), "irr_pct": round(new_irr * 100, 2)}

        irr = new_irr

    return {"irr": round(irr, 4), "irr_pct": round(irr * 100, 2)}


def calculate_payback_period(
    cash_flows: List[float]
) -> Dict[str, Any]:
    """Calculate payback period."""
    cumulative = 0
    payback_year = None

    cumulative_flows = []

    for year, cf in enumerate(cash_flows):
        cumulative += cf
        cumulative_flows.append({
            "year": year,
            "cash_flow": cf,
            "cumulative": round(cumulative, 2)
        })

        if payback_year is None and cumulative >= 0 and year > 0:
            # Interpolate for fractional year
            prev_cumulative = cumulative - cf
            if cf != 0:
                fraction = -prev_cumulative / cf
                payback_year = year - 1 + fraction

    return {
        "payback_period_years": round(payback_year, 2) if payback_year else None,
        "cumulative_flows": cumulative_flows,
        "total_return": round(cumulative, 2)
    }


def calculate_roi(
    total_benefits: float,
    total_costs: float
) -> Dict[str, Any]:
    """Calculate simple ROI."""
    if total_costs == 0:
        return {"error": "Zero costs"}

    net_benefit = total_benefits - total_costs
    roi = net_benefit / total_costs
    roi_pct = roi * 100

    return {
        "total_benefits": total_benefits,
        "total_costs": total_costs,
        "net_benefit": round(net_benefit, 2),
        "roi": round(roi, 4),
        "roi_pct": round(roi_pct, 1)
    }


def apply_risk_adjustments(
    base_value: float,
    risk_factors: Dict,
    risk_config: Dict
) -> Dict[str, Any]:
    """Apply risk adjustments to value."""
    adjustment_factor = 1.0
    adjustments = []

    for factor_type, factor_value in risk_factors.items():
        type_config = risk_config.get(factor_type, {})
        factor = type_config.get(factor_value, 0.8)
        adjustment_factor *= factor
        adjustments.append({
            "factor": factor_type,
            "level": factor_value,
            "adjustment": factor
        })

    adjusted_value = base_value * adjustment_factor

    return {
        "base_value": base_value,
        "adjustment_factor": round(adjustment_factor, 3),
        "adjusted_value": round(adjusted_value, 2),
        "adjustments": adjustments
    }


def perform_sensitivity_analysis(
    base_costs: float,
    base_benefits: float,
    scenarios: Dict
) -> Dict[str, Any]:
    """Perform sensitivity analysis."""
    results = {}

    for scenario_name, factors in scenarios.items():
        adj_benefits = base_benefits * factors.get("benefit_factor", 1.0)
        adj_costs = base_costs * factors.get("cost_factor", 1.0)
        net_benefit = adj_benefits - adj_costs
        roi = (net_benefit / adj_costs * 100) if adj_costs > 0 else 0

        results[scenario_name] = {
            "adjusted_benefits": round(adj_benefits, 2),
            "adjusted_costs": round(adj_costs, 2),
            "net_benefit": round(net_benefit, 2),
            "roi_pct": round(roi, 1)
        }

    return results


def evaluate_against_hurdles(
    roi: float,
    npv: float,
    payback: float,
    hurdle_rates: Dict,
    payback_thresholds: Dict,
    npv_thresholds: Dict
) -> Dict[str, Any]:
    """Evaluate project against hurdle rates."""
    evaluations = []

    # ROI evaluation
    if roi >= hurdle_rates.get("exceptional_roi", 0.50):
        roi_rating = "EXCEPTIONAL"
    elif roi >= hurdle_rates.get("target_roi", 0.25):
        roi_rating = "EXCEEDS_TARGET"
    elif roi >= hurdle_rates.get("minimum_roi", 0.15):
        roi_rating = "MEETS_MINIMUM"
    else:
        roi_rating = "BELOW_THRESHOLD"

    evaluations.append({"metric": "ROI", "value": roi, "rating": roi_rating})

    # NPV evaluation
    if npv >= npv_thresholds.get("strong", 1000000):
        npv_rating = "STRONG"
    elif npv >= npv_thresholds.get("acceptable", 100000):
        npv_rating = "ACCEPTABLE"
    elif npv >= npv_thresholds.get("marginal", 0):
        npv_rating = "MARGINAL"
    else:
        npv_rating = "NEGATIVE"

    evaluations.append({"metric": "NPV", "value": npv, "rating": npv_rating})

    # Payback evaluation
    if payback and payback <= payback_thresholds.get("excellent", 1):
        payback_rating = "EXCELLENT"
    elif payback and payback <= payback_thresholds.get("good", 2):
        payback_rating = "GOOD"
    elif payback and payback <= payback_thresholds.get("acceptable", 3):
        payback_rating = "ACCEPTABLE"
    elif payback and payback <= payback_thresholds.get("marginal", 5):
        payback_rating = "MARGINAL"
    else:
        payback_rating = "POOR"

    evaluations.append({"metric": "Payback", "value": payback, "rating": payback_rating})

    # Overall recommendation
    passing_metrics = sum(1 for e in evaluations if e["rating"] not in ["BELOW_THRESHOLD", "NEGATIVE", "POOR"])
    overall = "RECOMMEND" if passing_metrics >= 2 else "CONDITIONAL" if passing_metrics >= 1 else "NOT_RECOMMENDED"

    return {
        "evaluations": evaluations,
        "overall_recommendation": overall
    }


def calculate_project_roi(
    project_id: str,
    project_name: str,
    project_category: str,
    project_years: int,
    costs: List[Dict],
    benefits: List[Dict],
    risk_factors: Dict,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Calculate project ROI.

    Business Rules:
    1. NPV and IRR calculation
    2. Payback period analysis
    3. Risk-adjusted returns
    4. Sensitivity analysis

    Args:
        project_id: Project identifier
        project_name: Project name
        project_category: Category for benchmarking
        project_years: Analysis period
        costs: Project cost items
        benefits: Expected benefits
        risk_factors: Risk assessment factors
        analysis_date: Analysis date

    Returns:
        Project ROI analysis results
    """
    params = load_roi_parameters()
    discount_rates = params.get("discount_rates", {})
    cost_categories = params.get("cost_categories", {})
    benefit_categories = params.get("benefit_categories", {})

    # Get risk profile for project category
    category_config = params.get("project_categories", {}).get(project_category, {})
    risk_profile = category_config.get("risk_profile", "medium")
    discount_rate = discount_rates.get(f"{risk_profile}_risk", 0.12)

    # Calculate costs and benefits
    costs_result = calculate_total_costs(costs, project_years, cost_categories)
    benefits_result = calculate_total_benefits(benefits, project_years, benefit_categories)

    # Calculate cash flows
    cash_flows = calculate_net_cash_flows(
        costs_result["yearly_costs"],
        benefits_result["yearly_benefits"]
    )

    # Calculate NPV
    npv_result = calculate_npv(cash_flows, discount_rate)

    # Calculate IRR
    irr_result = calculate_irr(cash_flows)

    # Calculate payback
    payback_result = calculate_payback_period(cash_flows)

    # Calculate simple ROI
    roi_result = calculate_roi(
        benefits_result["total_benefits"],
        costs_result["total_cost"]
    )

    # Apply risk adjustments
    risk_adjusted = apply_risk_adjustments(
        npv_result["npv"],
        risk_factors,
        params.get("risk_adjustments", {})
    )

    # Sensitivity analysis
    sensitivity = perform_sensitivity_analysis(
        costs_result["total_cost"],
        benefits_result["total_benefits"],
        params.get("sensitivity_scenarios", {})
    )

    # Evaluate against hurdles
    evaluation = evaluate_against_hurdles(
        roi_result.get("roi", 0),
        npv_result["npv"],
        payback_result.get("payback_period_years"),
        params.get("hurdle_rates", {}),
        params.get("payback_thresholds", {}),
        params.get("npv_thresholds", {})
    )

    return {
        "project_id": project_id,
        "project_name": project_name,
        "project_category": project_category,
        "analysis_date": analysis_date,
        "analysis_period_years": project_years,
        "discount_rate": discount_rate,
        "financial_summary": {
            "total_investment": costs_result["total_cost"],
            "total_benefits": benefits_result["total_benefits"],
            "net_benefit": roi_result.get("net_benefit", 0),
            "roi_pct": roi_result.get("roi_pct", 0),
            "npv": npv_result["npv"],
            "irr_pct": irr_result.get("irr_pct"),
            "payback_years": payback_result.get("payback_period_years")
        },
        "cost_analysis": costs_result,
        "benefit_analysis": benefits_result,
        "cash_flow_analysis": {
            "net_cash_flows": cash_flows,
            "npv_details": npv_result,
            "payback_details": payback_result
        },
        "risk_adjusted_analysis": risk_adjusted,
        "sensitivity_analysis": sensitivity,
        "evaluation": evaluation
    }


if __name__ == "__main__":
    import json
    result = calculate_project_roi(
        project_id="PRJ-001",
        project_name="ERP Implementation",
        project_category="infrastructure",
        project_years=5,
        costs=[
            {"category": "capital", "amount": 500000, "year": 0},
            {"category": "implementation", "amount": 200000, "year": 0},
            {"category": "training", "amount": 50000, "year": 1},
            {"category": "maintenance", "amount": 75000, "year": 1}
        ],
        benefits=[
            {"category": "hard_savings", "annual_amount": 200000, "start_year": 2, "growth_rate": 0.05},
            {"category": "soft_savings", "annual_amount": 100000, "start_year": 2, "growth_rate": 0.03},
            {"category": "revenue_increase", "annual_amount": 150000, "start_year": 3, "growth_rate": 0.10}
        ],
        risk_factors={
            "technology_maturity": "established",
            "implementation_complexity": "high",
            "organizational_readiness": "medium"
        },
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
