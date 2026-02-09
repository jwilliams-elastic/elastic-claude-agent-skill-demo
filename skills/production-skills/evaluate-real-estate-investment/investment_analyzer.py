"""
Real Estate Investment Analysis Module

Implements valuation models and risk-adjusted return calculations
for commercial real estate investment decisions.
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


def load_market_benchmarks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    markets_data = load_csv_as_dict("markets.csv")
    property_types_data = load_csv_as_dict("property_types.csv")
    financing_assumptions_data = load_key_value_csv("financing_assumptions.csv")
    params = load_parameters()
    return {
        "markets": markets_data,
        "property_types": property_types_data,
        "financing_assumptions": financing_assumptions_data,
        **params
    }


def calculate_cap_rate(noi: float, price: float) -> float:
    """Calculate capitalization rate."""
    if price <= 0:
        return 0.0
    return noi / price


def calculate_price_per_sf(price: float, sqft: int) -> float:
    """Calculate price per square foot."""
    if sqft <= 0:
        return 0.0
    return price / sqft


def project_noi(
    current_noi: float,
    occupancy: float,
    target_occupancy: float,
    escalation_rate: float,
    years: int = 5
) -> List[float]:
    """Project NOI over hold period."""
    projections = []

    # Stabilization adjustment
    occupancy_adjustment = target_occupancy / occupancy if occupancy > 0 else 1.0
    stabilized_noi = current_noi * min(occupancy_adjustment, 1.1)

    for year in range(years):
        if year == 0:
            projections.append(stabilized_noi)
        else:
            projections.append(projections[-1] * (1 + escalation_rate))

    return projections


def calculate_irr(
    initial_investment: float,
    cash_flows: List[float],
    terminal_value: float
) -> float:
    """Calculate IRR using Newton-Raphson approximation."""
    cash_flows = [-initial_investment] + cash_flows[:-1] + [cash_flows[-1] + terminal_value]

    # Initial guess
    irr = 0.10

    for _ in range(100):
        npv = sum(cf / (1 + irr) ** t for t, cf in enumerate(cash_flows))
        dnpv = sum(-t * cf / (1 + irr) ** (t + 1) for t, cf in enumerate(cash_flows))

        if abs(dnpv) < 1e-10:
            break

        irr = irr - npv / dnpv

        if abs(npv) < 1e-6:
            break

    return irr


def assess_risk(
    property_type: str,
    market: str,
    occupancy: float,
    walt: float,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Assess investment risk factors."""
    risks = []
    score = 100

    market_data = benchmarks["markets"].get(market, benchmarks["markets"]["default"])
    type_data = benchmarks["property_types"].get(property_type, benchmarks["property_types"]["default"])

    # Market risk
    market_risk = market_data.get("risk_premium", 0.02)
    if market_risk > 0.03:
        risks.append({"factor": "market_risk", "severity": "high", "description": "Elevated market risk"})
        score -= 20
    elif market_risk > 0.02:
        risks.append({"factor": "market_risk", "severity": "medium", "description": "Moderate market risk"})
        score -= 10

    # Occupancy risk
    if occupancy < 0.85:
        risks.append({"factor": "occupancy", "severity": "high", "description": f"Low occupancy at {occupancy:.0%}"})
        score -= 25
    elif occupancy < 0.90:
        risks.append({"factor": "occupancy", "severity": "medium", "description": f"Below-market occupancy"})
        score -= 10

    # Lease term risk
    if walt < 3.0:
        risks.append({"factor": "lease_term", "severity": "high", "description": "Short WALT increases rollover risk"})
        score -= 20
    elif walt < 5.0:
        risks.append({"factor": "lease_term", "severity": "medium", "description": "Moderate lease term"})
        score -= 10

    # Sector risk
    if type_data.get("sector_risk", "medium") == "high":
        risks.append({"factor": "sector", "severity": "medium", "description": f"{property_type} sector facing headwinds"})
        score -= 15

    return {
        "risks": risks,
        "score": max(0, score),
        "risk_level": "high" if score < 50 else "medium" if score < 75 else "low"
    }


def evaluate_investment(
    property_id: str,
    property_type: str,
    market: str,
    asking_price: float,
    noi: float,
    square_feet: int,
    occupancy: float,
    lease_terms: Dict,
    capex_needed: float
) -> Dict[str, Any]:
    """
    Evaluate real estate investment opportunity.

    Business Rules:
    1. Cap rate benchmarking by market/type
    2. NOI projection methodology
    3. Risk-adjusted return calculation
    4. DSCR requirements

    Args:
        property_id: Property identifier
        property_type: Property type
        market: Market identifier
        asking_price: Purchase price
        noi: Net operating income
        square_feet: Rentable area
        occupancy: Current occupancy
        lease_terms: Lease details
        capex_needed: Required capex

    Returns:
        Investment analysis results
    """
    benchmarks = load_market_benchmarks()

    market_data = benchmarks["markets"].get(market, benchmarks["markets"]["default"])
    type_data = benchmarks["property_types"].get(property_type, benchmarks["property_types"]["default"])

    # Calculate key metrics
    cap_rate = calculate_cap_rate(noi, asking_price)
    price_per_sf = calculate_price_per_sf(asking_price, square_feet)

    # Compare to benchmarks
    benchmark_cap = type_data["benchmark_cap_rate"] + market_data.get("cap_rate_adjustment", 0)
    cap_rate_spread = cap_rate - benchmark_cap

    benchmark_psf = type_data["benchmark_price_psf"] * market_data.get("price_multiplier", 1.0)

    # Project cash flows
    walt = lease_terms.get("walt", 5.0)
    escalations = lease_terms.get("escalations", 0.025)
    hold_period = 5

    noi_projections = project_noi(
        noi,
        occupancy,
        market_data.get("stabilized_occupancy", 0.93),
        escalations,
        hold_period
    )

    # Terminal value at exit cap rate
    exit_cap = benchmark_cap + 0.0025  # Assume slight cap rate expansion
    terminal_value = noi_projections[-1] / exit_cap

    # Calculate total investment
    total_investment = asking_price + capex_needed

    # Calculate IRR
    projected_irr = calculate_irr(total_investment, noi_projections, terminal_value)

    # Risk assessment
    risk_assessment = assess_risk(property_type, market, occupancy, walt, benchmarks)

    # Apply risk premium to required return
    required_return = type_data["required_return"] + market_data.get("risk_premium", 0)

    # Valuation range
    low_value = noi / (benchmark_cap + 0.01)
    high_value = noi / (benchmark_cap - 0.005)

    valuation_range = {
        "low": round(low_value, 0),
        "mid": round((low_value + high_value) / 2, 0),
        "high": round(high_value, 0),
        "asking_vs_mid": round((asking_price / ((low_value + high_value) / 2) - 1) * 100, 1)
    }

    # Investment rating
    irr_spread = projected_irr - required_return

    if irr_spread >= 0.02 and risk_assessment["score"] >= 60:
        investment_rating = "BUY"
    elif irr_spread >= 0 and risk_assessment["score"] >= 50:
        investment_rating = "HOLD"
    else:
        investment_rating = "PASS"

    return {
        "property_id": property_id,
        "investment_rating": investment_rating,
        "cap_rate": round(cap_rate, 4),
        "cap_rate_vs_benchmark": round(cap_rate_spread * 100, 1),
        "price_per_sf": round(price_per_sf, 2),
        "price_psf_vs_benchmark": round((price_per_sf / benchmark_psf - 1) * 100, 1),
        "projected_irr": round(projected_irr, 4),
        "required_return": round(required_return, 4),
        "irr_spread": round(irr_spread * 100, 1),
        "risk_score": risk_assessment["score"],
        "risk_level": risk_assessment["risk_level"],
        "risk_factors": risk_assessment["risks"],
        "valuation_range": valuation_range,
        "noi_projections": [round(n, 0) for n in noi_projections],
        "terminal_value": round(terminal_value, 0),
        "total_investment": total_investment,
        "property_type": property_type,
        "market": market
    }


if __name__ == "__main__":
    import json
    result = evaluate_investment(
        property_id="PROP-2024-001",
        property_type="office",
        market="NYC",
        asking_price=50000000,
        noi=3000000,
        square_feet=100000,
        occupancy=0.92,
        lease_terms={"walt": 5.2, "escalations": 0.03},
        capex_needed=2000000
    )
    print(json.dumps(result, indent=2))
