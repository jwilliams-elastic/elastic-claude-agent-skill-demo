"""
Investment Portfolio Risk Calculation Module

Implements proprietary risk metrics including VaR, volatility,
and concentration analysis for wealth management.
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


def load_market_data() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    securities_data = load_csv_as_dict("securities.csv")
    risk_profiles_data = load_csv_as_dict("risk_profiles.csv")
    stress_scenarios_data = load_key_value_csv("stress_scenarios.csv")
    correlation_matrix_data = load_csv_as_dict("correlation_matrix.csv")
    params = load_parameters()
    return {
        "securities": securities_data,
        "risk_profiles": risk_profiles_data,
        "stress_scenarios": stress_scenarios_data,
        "correlation_matrix": correlation_matrix_data,
        **params
    }


def calculate_position_var(
    value: float,
    volatility: float,
    confidence: float,
    days: int = 1
) -> float:
    """Calculate parametric VaR for a position."""
    # Z-scores for confidence levels
    z_scores = {0.95: 1.645, 0.99: 2.326}
    z = z_scores.get(confidence, 1.645)

    # Daily to period conversion
    var = value * volatility * z * math.sqrt(days / 252)
    return var


def calculate_portfolio_volatility(
    positions: List[Dict],
    market_data: Dict
) -> float:
    """Calculate portfolio volatility with correlations."""
    if not positions:
        return 0.0

    total_value = sum(p.get("value", 0) for p in positions)
    if total_value == 0:
        return 0.0

    # Calculate weighted average volatility (simplified)
    weighted_vol = 0
    for pos in positions:
        ticker = pos.get("ticker", "")
        value = pos.get("value", 0)
        weight = value / total_value

        security = market_data["securities"].get(ticker, market_data["securities"]["default"])
        vol = security["volatility"]

        weighted_vol += weight * vol

    # Apply diversification benefit (simplified)
    n_positions = len(positions)
    diversification = 1 - (0.1 * min(n_positions - 1, 10))

    return weighted_vol * diversification


def check_concentration(
    positions: List[Dict],
    limits: Dict
) -> List[Dict]:
    """Check position and sector concentration limits."""
    alerts = []

    total_value = sum(p.get("value", 0) for p in positions)
    if total_value == 0:
        return alerts

    # Position concentration
    for pos in positions:
        weight = pos.get("value", 0) / total_value
        if weight > limits["max_single_position"]:
            alerts.append({
                "type": "POSITION_CONCENTRATION",
                "ticker": pos.get("ticker"),
                "weight": round(weight * 100, 1),
                "limit": limits["max_single_position"] * 100,
                "severity": "high" if weight > limits["max_single_position"] * 1.5 else "medium"
            })

    # Sector concentration would require sector mapping
    return alerts


def calculate_liquidity_score(
    positions: List[Dict],
    market_data: Dict
) -> Dict[str, Any]:
    """Calculate portfolio liquidity score."""
    if not positions:
        return {"score": 100, "illiquid_positions": []}

    illiquid = []
    total_value = sum(p.get("value", 0) for p in positions)

    liquidity_weighted_score = 0
    for pos in positions:
        ticker = pos.get("ticker", "")
        value = pos.get("value", 0)
        weight = value / total_value if total_value > 0 else 0

        security = market_data["securities"].get(ticker, market_data["securities"]["default"])
        liq_score = security.get("liquidity_score", 50)

        liquidity_weighted_score += weight * liq_score

        if liq_score < 30:
            illiquid.append({"ticker": ticker, "liquidity_score": liq_score})

    return {
        "score": round(liquidity_weighted_score, 1),
        "illiquid_positions": illiquid
    }


def apply_stress_scenario(
    var: float,
    scenario: str,
    multipliers: Dict
) -> float:
    """Apply stress scenario multiplier to VaR."""
    multiplier = multipliers.get(scenario, 1.0)
    return var * multiplier


def calculate_portfolio_risk(
    portfolio_id: str,
    positions: List[Dict],
    client_risk_profile: str,
    time_horizon: str,
    benchmark: str,
    stress_scenario: str
) -> Dict[str, Any]:
    """
    Calculate portfolio risk metrics.

    Business Rules:
    1. VaR using historical simulation with scaling
    2. Concentration limits by risk profile
    3. Dynamic correlation in stress
    4. Liquidity scoring

    Args:
        portfolio_id: Portfolio identifier
        positions: Position holdings
        client_risk_profile: Client risk tolerance
        time_horizon: Investment horizon
        benchmark: Benchmark index
        stress_scenario: Stress test scenario

    Returns:
        Risk metrics and alerts
    """
    market_data = load_market_data()

    total_value = sum(p.get("value", 0) for p in positions)

    # Get risk profile limits
    profile_limits = market_data["risk_profiles"].get(
        client_risk_profile,
        market_data["risk_profiles"]["moderate"]
    )

    # Calculate portfolio volatility
    portfolio_vol = calculate_portfolio_volatility(positions, market_data)

    # Time horizon adjustment
    horizon_days = {"short": 21, "medium": 63, "long": 252}.get(time_horizon, 63)

    # Calculate VaR
    var_95 = calculate_position_var(total_value, portfolio_vol, 0.95, horizon_days)
    var_99 = calculate_position_var(total_value, portfolio_vol, 0.99, horizon_days)

    # Apply stress scenario
    stress_multipliers = market_data["stress_scenarios"]
    if stress_scenario != "none":
        var_95 = apply_stress_scenario(var_95, stress_scenario, stress_multipliers)
        var_99 = apply_stress_scenario(var_99, stress_scenario, stress_multipliers)

    # Check concentration limits
    concentration_alerts = check_concentration(positions, profile_limits)

    # Calculate liquidity
    liquidity = calculate_liquidity_score(positions, market_data)

    # Calculate overall risk score (1-100)
    risk_score = min(100, int(
        (portfolio_vol / 0.40) * 50 +  # Volatility component
        (len(concentration_alerts) * 10) +  # Concentration penalty
        ((100 - liquidity["score"]) / 2)  # Liquidity penalty
    ))

    # Suitability check
    max_risk = profile_limits["max_risk_score"]
    suitability = "SUITABLE" if risk_score <= max_risk else "REVIEW_REQUIRED"

    # Risk decomposition
    risk_decomposition = []
    for pos in positions:
        ticker = pos.get("ticker", "")
        value = pos.get("value", 0)
        weight = value / total_value if total_value > 0 else 0

        security = market_data["securities"].get(ticker, market_data["securities"]["default"])
        pos_var = calculate_position_var(value, security["volatility"], 0.95, horizon_days)

        risk_decomposition.append({
            "ticker": ticker,
            "value": value,
            "weight_pct": round(weight * 100, 2),
            "contribution_to_var": round(pos_var, 2)
        })

    return {
        "portfolio_id": portfolio_id,
        "total_value": total_value,
        "var_95": round(var_95, 2),
        "var_99": round(var_99, 2),
        "var_95_pct": round(var_95 / total_value * 100, 2) if total_value > 0 else 0,
        "volatility": round(portfolio_vol, 4),
        "volatility_annualized_pct": round(portfolio_vol * 100, 2),
        "risk_score": risk_score,
        "suitability": suitability,
        "concentration_alerts": concentration_alerts,
        "liquidity_score": liquidity["score"],
        "illiquid_positions": liquidity["illiquid_positions"],
        "risk_decomposition": risk_decomposition,
        "time_horizon": time_horizon,
        "stress_scenario": stress_scenario,
        "benchmark": benchmark
    }


if __name__ == "__main__":
    import json
    result = calculate_portfolio_risk(
        portfolio_id="PORT-12345",
        positions=[
            {"ticker": "AAPL", "quantity": 100, "value": 18500},
            {"ticker": "MSFT", "quantity": 50, "value": 19000},
            {"ticker": "GOOGL", "quantity": 20, "value": 28000},
            {"ticker": "BND", "quantity": 200, "value": 15000}
        ],
        client_risk_profile="moderate",
        time_horizon="medium",
        benchmark="SPY",
        stress_scenario="none"
    )
    print(json.dumps(result, indent=2))
