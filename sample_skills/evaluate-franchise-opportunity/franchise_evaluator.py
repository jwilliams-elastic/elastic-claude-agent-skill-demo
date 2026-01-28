"""
Franchise Opportunity Evaluation Module

Implements franchise investment analysis using unit economics,
territory potential, and franchisor assessment.
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


def load_franchise_benchmarks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    category_benchmarks_data = load_csv_as_dict("category_benchmarks.csv")
    market_factors_data = load_csv_as_dict("market_factors.csv")
    franchisor_standards_data = load_key_value_csv("franchisor_standards.csv")
    projection_params_data = load_key_value_csv("projection_params.csv")
    evaluation_weights_data = load_key_value_csv("evaluation_weights.csv")
    investment_thresholds_data = load_key_value_csv("investment_thresholds.csv")
    royalty_benchmarks_data = load_csv_as_dict("royalty_benchmarks.csv")
    params = load_parameters()
    return {
        "category_benchmarks": category_benchmarks_data,
        "market_factors": market_factors_data,
        "franchisor_standards": franchisor_standards_data,
        "projection_params": projection_params_data,
        "evaluation_weights": evaluation_weights_data,
        "investment_thresholds": investment_thresholds_data,
        "royalty_benchmarks": royalty_benchmarks_data,
        **params
    }


def analyze_unit_economics(
    unit_financials: Dict,
    investment_terms: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Analyze per-unit financial performance."""
    avg_revenue = unit_financials.get("avg_revenue", 0)
    avg_ebitda_margin = unit_financials.get("avg_ebitda_margin", 0)

    franchise_fee = investment_terms.get("franchise_fee", 0)
    buildout = investment_terms.get("buildout", 0)
    royalty_pct = investment_terms.get("royalty_pct", 0)

    total_investment = franchise_fee + buildout

    # Calculate annual EBITDA
    gross_ebitda = avg_revenue * avg_ebitda_margin
    royalty_cost = avg_revenue * royalty_pct
    net_ebitda = gross_ebitda - royalty_cost

    # Payback period
    payback_years = total_investment / net_ebitda if net_ebitda > 0 else float('inf')

    # Cash-on-cash return
    cash_on_cash = net_ebitda / total_investment if total_investment > 0 else 0

    # Compare to benchmarks
    category_benchmarks = benchmarks.get("category_benchmarks", {})
    benchmark_payback = category_benchmarks.get("avg_payback_years", 4)
    benchmark_coc = category_benchmarks.get("avg_cash_on_cash", 0.20)

    score = 50  # Base score
    if payback_years < benchmark_payback:
        score += 20
    elif payback_years > benchmark_payback * 1.5:
        score -= 20

    if cash_on_cash > benchmark_coc:
        score += 15
    elif cash_on_cash < benchmark_coc * 0.5:
        score -= 15

    return {
        "score": max(0, min(100, score)),
        "total_investment": total_investment,
        "annual_revenue_est": avg_revenue,
        "annual_ebitda_est": round(net_ebitda, 2),
        "payback_years": round(payback_years, 2),
        "cash_on_cash_return": round(cash_on_cash, 3),
        "royalty_burden": royalty_pct
    }


def assess_territory_potential(
    territory_data: Dict,
    franchise_info: Dict,
    market_factors: Dict
) -> Dict[str, Any]:
    """Assess territory market potential."""
    population = territory_data.get("population", 0)
    median_income = territory_data.get("median_income", 0)
    competitors = territory_data.get("competitors", 0)

    category = franchise_info.get("category", "general")

    # Calculate market potential
    category_factors = market_factors.get(category, {})
    income_threshold = category_factors.get("min_median_income", 50000)
    pop_per_unit = category_factors.get("population_per_unit", 25000)

    # Territory capacity
    territory_capacity = population / pop_per_unit if pop_per_unit > 0 else 0
    available_capacity = max(0, territory_capacity - competitors)

    # Income adequacy
    income_adequate = median_income >= income_threshold

    # Competitive density
    competitive_density = competitors / (population / 100000) if population > 0 else 0

    # Score calculation
    score = 50
    if available_capacity > 1:
        score += 25
    elif available_capacity > 0.5:
        score += 10

    if income_adequate:
        score += 15

    if competitive_density < 2:
        score += 10
    elif competitive_density > 5:
        score -= 15

    return {
        "score": max(0, min(100, score)),
        "population": population,
        "median_income": median_income,
        "territory_capacity": round(territory_capacity, 1),
        "competitors": competitors,
        "available_opportunity": round(available_capacity, 1),
        "competitive_density": round(competitive_density, 2),
        "income_adequate": income_adequate
    }


def evaluate_franchisor(
    franchisor_data: Dict,
    franchise_info: Dict,
    franchisor_benchmarks: Dict
) -> Dict[str, Any]:
    """Evaluate franchisor track record."""
    issues = []
    strengths = []

    years_franchising = franchisor_data.get("years_franchising", 0)
    franchisee_satisfaction = franchisor_data.get("franchisee_satisfaction", 0)
    units_nationwide = franchise_info.get("units_nationwide", 0)

    # Experience check
    if years_franchising < 3:
        issues.append("Limited franchising track record (<3 years)")
    elif years_franchising >= 10:
        strengths.append(f"Established franchisor ({years_franchising} years)")

    # Satisfaction check
    min_satisfaction = franchisor_benchmarks.get("min_satisfaction", 70)
    if franchisee_satisfaction < min_satisfaction:
        issues.append(f"Franchisee satisfaction {franchisee_satisfaction}% below benchmark")
    elif franchisee_satisfaction >= 85:
        strengths.append(f"High franchisee satisfaction ({franchisee_satisfaction}%)")

    # Scale check
    if units_nationwide < 50:
        issues.append("Limited system scale may affect support/buying power")
    elif units_nationwide >= 200:
        strengths.append(f"Well-established system ({units_nationwide} units)")

    # Unit growth (would need historical data)
    closure_rate = franchisor_data.get("closure_rate", 0.05)
    if closure_rate > 0.10:
        issues.append(f"High unit closure rate ({closure_rate:.1%})")

    score = 50
    score += len(strengths) * 15
    score -= len(issues) * 10

    return {
        "score": max(0, min(100, score)),
        "years_franchising": years_franchising,
        "franchisee_satisfaction": franchisee_satisfaction,
        "units_nationwide": units_nationwide,
        "strengths": strengths,
        "concerns": issues
    }


def calculate_return_projections(
    unit_economics: Dict,
    investment_terms: Dict,
    projection_params: Dict
) -> Dict[str, Any]:
    """Calculate financial return projections."""
    total_investment = unit_economics.get("total_investment", 0)
    annual_ebitda = unit_economics.get("annual_ebitda_est", 0)

    growth_rate = projection_params.get("revenue_growth_rate", 0.03)
    discount_rate = projection_params.get("discount_rate", 0.12)
    projection_years = projection_params.get("years", 10)

    # Project cash flows
    cash_flows = [-total_investment]
    current_ebitda = annual_ebitda

    for year in range(1, projection_years + 1):
        current_ebitda *= (1 + growth_rate)
        cash_flows.append(current_ebitda)

    # Add terminal value (5x EBITDA multiple)
    terminal_multiple = projection_params.get("terminal_multiple", 5)
    terminal_value = current_ebitda * terminal_multiple
    cash_flows[-1] += terminal_value

    # Calculate IRR (simplified Newton-Raphson)
    irr = 0.15  # Initial guess
    for _ in range(50):
        npv = sum(cf / (1 + irr) ** t for t, cf in enumerate(cash_flows))
        npv_derivative = sum(-t * cf / (1 + irr) ** (t + 1) for t, cf in enumerate(cash_flows))
        if abs(npv_derivative) > 0.0001:
            irr = irr - npv / npv_derivative

    # Calculate NPV at discount rate
    npv = sum(cf / (1 + discount_rate) ** t for t, cf in enumerate(cash_flows))

    return {
        "projected_irr": round(max(0, min(1, irr)), 3),
        "npv_at_discount_rate": round(npv, 2),
        "discount_rate_used": discount_rate,
        "payback_years": unit_economics.get("payback_years"),
        "year_5_cumulative_cash": round(sum(cash_flows[1:6]), 2),
        "terminal_value": round(terminal_value, 2)
    }


def evaluate_franchise(
    opportunity_id: str,
    franchise_info: Dict,
    territory_data: Dict,
    investment_terms: Dict,
    unit_financials: Dict,
    franchisor_data: Dict
) -> Dict[str, Any]:
    """
    Evaluate franchise investment opportunity.

    Business Rules:
    1. Unit economics validation
    2. Territory potential assessment
    3. Franchisor track record evaluation
    4. Investment return modeling

    Args:
        opportunity_id: Opportunity identifier
        franchise_info: Franchise concept details
        territory_data: Market demographics
        investment_terms: Investment requirements
        unit_financials: Unit-level economics
        franchisor_data: Franchisor information

    Returns:
        Franchise evaluation results
    """
    benchmarks = load_franchise_benchmarks()

    risk_factors = []

    # Unit economics analysis
    unit_economics = analyze_unit_economics(
        unit_financials,
        investment_terms,
        benchmarks
    )

    if unit_economics["payback_years"] > 5:
        risk_factors.append({
            "factor": "Long payback period",
            "detail": f"{unit_economics['payback_years']:.1f} years",
            "severity": "medium"
        })

    # Territory assessment
    territory_assessment = assess_territory_potential(
        territory_data,
        franchise_info,
        benchmarks.get("market_factors", {})
    )

    if territory_assessment["available_opportunity"] < 0.5:
        risk_factors.append({
            "factor": "Limited territory opportunity",
            "detail": f"Market capacity: {territory_assessment['available_opportunity']:.1f}",
            "severity": "high"
        })

    # Franchisor evaluation
    franchisor_eval = evaluate_franchisor(
        franchisor_data,
        franchise_info,
        benchmarks.get("franchisor_standards", {})
    )

    if franchisor_eval["concerns"]:
        for concern in franchisor_eval["concerns"]:
            risk_factors.append({
                "factor": "Franchisor concern",
                "detail": concern,
                "severity": "medium"
            })

    # Return projections
    return_projections = calculate_return_projections(
        unit_economics,
        investment_terms,
        benchmarks.get("projection_params", {})
    )

    # Calculate overall score
    weights = benchmarks.get("evaluation_weights", {})
    investment_score = (
        unit_economics["score"] * weights.get("unit_economics", 0.40) +
        territory_assessment["score"] * weights.get("territory", 0.30) +
        franchisor_eval["score"] * weights.get("franchisor", 0.30)
    )

    return {
        "opportunity_id": opportunity_id,
        "investment_score": round(investment_score, 1),
        "unit_economics": unit_economics,
        "territory_assessment": territory_assessment,
        "franchisor_evaluation": franchisor_eval,
        "return_projections": return_projections,
        "risk_factors": risk_factors,
        "recommendation": "FAVORABLE" if investment_score >= 70 else "CAUTIOUS" if investment_score >= 50 else "NOT_RECOMMENDED"
    }


if __name__ == "__main__":
    import json
    result = evaluate_franchise(
        opportunity_id="FRN-001",
        franchise_info={"brand": "FastServe", "category": "QSR", "units_nationwide": 500},
        territory_data={"population": 150000, "median_income": 65000, "competitors": 3},
        investment_terms={"franchise_fee": 45000, "buildout": 350000, "royalty_pct": 0.06},
        unit_financials={"avg_revenue": 1200000, "avg_ebitda_margin": 0.15},
        franchisor_data={"years_franchising": 15, "franchisee_satisfaction": 85, "closure_rate": 0.03}
    )
    print(json.dumps(result, indent=2))
