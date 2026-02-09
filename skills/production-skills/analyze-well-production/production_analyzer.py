"""
Oil & Gas Well Production Analysis Module

Implements decline curve analysis and production optimization
algorithms for reservoir engineering applications.
"""

import csv
import math
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime


def load_decline_models() -> Dict[str, Any]:
    """Load decline curve model parameters."""
    models_path = Path(__file__).parent / "decline_models.csv"
    models = {}

    with open(models_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = f"{row['reservoir_type']}_{row['completion_type']}"
            models[key] = {
                "decline_type": row["decline_type"],
                "initial_decline_rate": float(row["initial_decline_rate"]),
                "b_factor": float(row["b_factor"]),
                "terminal_decline": float(row["terminal_decline"]),
                "typical_eur_factor": float(row["typical_eur_factor"])
            }

    return models


def calculate_decline_rate(
    production_history: List[Dict],
    window_months: int = 6
) -> float:
    """Calculate current decline rate from production history."""
    if len(production_history) < 2:
        return 0.0

    recent = production_history[-window_months:] if len(production_history) >= window_months else production_history

    oil_values = [p["oil_bbl"] for p in recent]
    if oil_values[0] == 0:
        return 0.0

    # Simple exponential decline calculation
    decline_rate = (oil_values[0] - oil_values[-1]) / oil_values[0] / len(oil_values)
    return max(0, min(1, decline_rate))  # Bound between 0 and 1


def calculate_water_cut(production: Dict) -> float:
    """Calculate water cut percentage."""
    total_liquid = production.get("oil_bbl", 0) + production.get("water_bbl", 0)
    if total_liquid == 0:
        return 0.0
    return production.get("water_bbl", 0) / total_liquid


def estimate_eur(
    current_rate: float,
    decline_rate: float,
    b_factor: float,
    cumulative_production: float,
    economic_limit: float
) -> float:
    """Estimate ultimate recovery using Arps decline."""
    if decline_rate <= 0:
        return cumulative_production

    # Hyperbolic decline EUR formula
    if b_factor > 0 and b_factor < 1:
        # Hyperbolic to exponential transition
        eur = cumulative_production + (current_rate / decline_rate) * (
            1 - (economic_limit / current_rate) ** (1 - b_factor)
        ) / (1 - b_factor)
    else:
        # Exponential decline
        eur = cumulative_production + current_rate / decline_rate

    return round(eur, 0)


def evaluate_lift_efficiency(
    current_lift: str,
    wellhead_pressure: float,
    production_rate: float,
    water_cut: float
) -> Dict[str, Any]:
    """Evaluate artificial lift system efficiency."""
    lift_benchmarks = {
        "natural_flow": {"min_pressure": 200, "max_water_cut": 0.3},
        "rod_pump": {"min_pressure": 50, "max_water_cut": 0.8, "max_rate": 500},
        "esp": {"min_pressure": 100, "max_water_cut": 0.9, "min_rate": 200},
        "gas_lift": {"min_pressure": 150, "max_water_cut": 0.7}
    }

    benchmark = lift_benchmarks.get(current_lift, lift_benchmarks["rod_pump"])
    issues = []
    efficiency = 1.0

    if wellhead_pressure < benchmark.get("min_pressure", 0):
        issues.append("Wellhead pressure below optimal")
        efficiency -= 0.15

    if water_cut > benchmark.get("max_water_cut", 1.0):
        issues.append("Water cut exceeds lift method capability")
        efficiency -= 0.20

    if "max_rate" in benchmark and production_rate > benchmark["max_rate"]:
        issues.append("Production rate exceeds lift capacity")
        efficiency -= 0.10

    if "min_rate" in benchmark and production_rate < benchmark["min_rate"]:
        issues.append("Production rate below efficient operating range")
        efficiency -= 0.10

    return {
        "efficiency": round(max(0.5, efficiency), 2),
        "issues": issues,
        "optimal": len(issues) == 0
    }


def analyze_production(
    well_id: str,
    production_history: List[Dict],
    completion_type: str,
    reservoir_type: str,
    current_lift_method: str,
    wellhead_pressure: float,
    oil_price: float
) -> Dict[str, Any]:
    """
    Analyze well production and generate forecasts.

    Business Rules:
    1. Decline model selected by reservoir/completion type
    2. Water cut drives economic limit
    3. Production anomalies trigger interventions
    4. Lift method matched to well conditions

    Args:
        well_id: Well identifier
        production_history: Production data
        completion_type: Completion type
        reservoir_type: Reservoir type
        current_lift_method: Current artificial lift
        wellhead_pressure: Wellhead pressure
        oil_price: Oil price assumption

    Returns:
        Production analysis with forecasts and recommendations
    """
    models = load_decline_models()

    recommendations = []

    # Get decline model
    model_key = f"{reservoir_type}_{completion_type}"
    decline_model = models.get(model_key, models.get("conventional_conventional"))

    # Current production metrics
    if production_history:
        current_prod = production_history[-1]
        current_oil_rate = current_prod.get("oil_bbl", 0)
        water_cut = calculate_water_cut(current_prod)
        cumulative_oil = sum(p.get("oil_bbl", 0) for p in production_history)
    else:
        current_oil_rate = 0
        water_cut = 0
        cumulative_oil = 0

    # Calculate decline rate
    actual_decline = calculate_decline_rate(production_history)
    model_decline = decline_model["initial_decline_rate"]

    # Economic limit calculation
    operating_cost_per_bbl = 25  # Assumed LOE
    economic_limit_rate = operating_cost_per_bbl / oil_price * 30  # bbl/month

    # EUR estimation
    eur = estimate_eur(
        current_rate=current_oil_rate,
        decline_rate=actual_decline if actual_decline > 0 else model_decline,
        b_factor=decline_model["b_factor"],
        cumulative_production=cumulative_oil,
        economic_limit=economic_limit_rate
    )

    # Lift efficiency evaluation
    lift_eval = evaluate_lift_efficiency(
        current_lift_method,
        wellhead_pressure,
        current_oil_rate,
        water_cut
    )

    # Generate recommendations
    if actual_decline > model_decline * 1.5:
        recommendations.append({
            "type": "WORKOVER",
            "priority": "high",
            "description": "Decline rate exceeds expected - evaluate for intervention"
        })

    if water_cut > 0.7:
        recommendations.append({
            "type": "WATER_MANAGEMENT",
            "priority": "medium",
            "description": f"High water cut ({water_cut*100:.1f}%) - evaluate water shutoff options"
        })

    if not lift_eval["optimal"]:
        recommendations.append({
            "type": "LIFT_OPTIMIZATION",
            "priority": "medium",
            "description": f"Lift system issues: {', '.join(lift_eval['issues'])}"
        })

    if wellhead_pressure < 100 and current_lift_method == "natural_flow":
        recommendations.append({
            "type": "ARTIFICIAL_LIFT",
            "priority": "high",
            "description": "Low pressure - evaluate artificial lift installation"
        })

    # Decline forecast
    decline_forecast = {
        "current_rate_bopd": round(current_oil_rate / 30, 1),
        "decline_type": decline_model["decline_type"],
        "annual_decline_pct": round(actual_decline * 12 * 100, 1),
        "model_decline_pct": round(model_decline * 12 * 100, 1),
        "forecast_12mo": round(current_oil_rate * (1 - actual_decline) ** 12, 0),
        "forecast_24mo": round(current_oil_rate * (1 - actual_decline) ** 24, 0)
    }

    return {
        "well_id": well_id,
        "eur_estimate": eur,
        "cumulative_production": cumulative_oil,
        "remaining_reserves": max(0, eur - cumulative_oil),
        "decline_forecast": decline_forecast,
        "economic_limit": {
            "rate_bbl_month": round(economic_limit_rate, 1),
            "oil_price_assumption": oil_price,
            "operating_cost_assumption": operating_cost_per_bbl
        },
        "current_metrics": {
            "oil_rate_bbl_month": current_oil_rate,
            "water_cut_pct": round(water_cut * 100, 1),
            "wellhead_pressure_psi": wellhead_pressure
        },
        "lift_efficiency": lift_eval["efficiency"],
        "lift_issues": lift_eval["issues"],
        "optimization_recommendations": recommendations,
        "reservoir_type": reservoir_type,
        "completion_type": completion_type
    }


if __name__ == "__main__":
    import json

    result = analyze_production(
        well_id="42-123-45678",
        production_history=[
            {"month": "2025-01", "oil_bbl": 5000, "gas_mcf": 8000, "water_bbl": 2000},
            {"month": "2025-02", "oil_bbl": 4800, "gas_mcf": 7800, "water_bbl": 2200},
            {"month": "2025-03", "oil_bbl": 4600, "gas_mcf": 7600, "water_bbl": 2400},
            {"month": "2025-04", "oil_bbl": 4400, "gas_mcf": 7400, "water_bbl": 2600},
            {"month": "2025-05", "oil_bbl": 4200, "gas_mcf": 7200, "water_bbl": 2800},
            {"month": "2025-06", "oil_bbl": 4000, "gas_mcf": 7000, "water_bbl": 3000}
        ],
        completion_type="hydraulic_fracture",
        reservoir_type="shale",
        current_lift_method="rod_pump",
        wellhead_pressure=150,
        oil_price=75.00
    )
    print(json.dumps(result, indent=2))
