"""
Telecom Network Capacity Planning Module

Implements traffic forecasting and capacity planning algorithms
for telecommunications infrastructure.
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


def load_network_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    element_types_data = load_csv_as_dict("element_types.csv")
    service_tiers_data = load_csv_as_dict("service_tiers.csv")
    upgrade_paths_data = load_csv_as_dict("upgrade_paths.csv")
    cost_factors_data = load_csv_as_dict("cost_factors.csv")
    params = load_parameters()
    return {
        "element_types": element_types_data,
        "service_tiers": service_tiers_data,
        "upgrade_paths": upgrade_paths_data,
        "cost_factors": cost_factors_data,
        **params
    }


def calculate_growth_rate(traffic_history: List[float]) -> float:
    """Calculate compound growth rate from traffic history."""
    if len(traffic_history) < 2:
        return 0.0

    first = traffic_history[0]
    last = traffic_history[-1]
    periods = len(traffic_history) - 1

    if first <= 0:
        return 0.0

    cagr = (last / first) ** (1 / periods) - 1
    return cagr


def forecast_traffic(
    current_traffic: float,
    growth_rate: float,
    years: int,
    peak_multiplier: float
) -> List[Dict]:
    """Forecast traffic over planning horizon."""
    forecasts = []

    for year in range(1, years + 1):
        avg_traffic = current_traffic * (1 + growth_rate) ** year
        peak_traffic = avg_traffic * peak_multiplier

        forecasts.append({
            "year": year,
            "average_gbps": round(avg_traffic, 1),
            "peak_gbps": round(peak_traffic, 1)
        })

    return forecasts


def assess_congestion_risk(
    traffic_forecast: List[Dict],
    capacity: float,
    utilization_threshold: float
) -> List[Dict]:
    """Assess congestion risk for each forecast period."""
    risks = []

    for forecast in traffic_forecast:
        peak_utilization = forecast["peak_gbps"] / capacity
        avg_utilization = forecast["average_gbps"] / capacity

        if peak_utilization >= 1.0:
            risk_level = "critical"
            probability = 1.0
        elif peak_utilization >= utilization_threshold:
            risk_level = "high"
            probability = (peak_utilization - utilization_threshold) / (1 - utilization_threshold)
        elif avg_utilization >= utilization_threshold * 0.8:
            risk_level = "medium"
            probability = 0.3
        else:
            risk_level = "low"
            probability = 0.1

        risks.append({
            "year": forecast["year"],
            "peak_utilization_pct": round(peak_utilization * 100, 1),
            "risk_level": risk_level,
            "congestion_probability": round(probability, 2)
        })

    return risks


def plan_upgrades(
    congestion_risks: List[Dict],
    current_technology: str,
    upgrade_paths: Dict,
    service_tier: str
) -> Dict[str, Any]:
    """Plan capacity upgrades based on congestion forecast."""
    upgrades = []

    # Find first year with unacceptable risk
    trigger_year = None
    for risk in congestion_risks:
        threshold = "medium" if service_tier == "critical" else "high"
        if risk["risk_level"] in ["critical", "high"] or (
            service_tier == "critical" and risk["risk_level"] == "medium"
        ):
            trigger_year = risk["year"]
            break

    if trigger_year is None:
        return {"upgrades_needed": False, "timeline": []}

    # Determine upgrade path
    current_path = upgrade_paths.get(current_technology, upgrade_paths["default"])

    # Plan upgrade 1 year before trigger
    upgrade_year = max(1, trigger_year - 1)

    upgrades.append({
        "year": upgrade_year,
        "action": "capacity_upgrade",
        "from_technology": current_technology,
        "to_technology": current_path["next_technology"],
        "capacity_gain_pct": current_path["capacity_multiplier"] * 100 - 100
    })

    return {
        "upgrades_needed": True,
        "timeline": upgrades,
        "trigger_year": trigger_year,
        "recommended_upgrade_year": upgrade_year
    }


def estimate_investment(
    upgrades: List[Dict],
    element_type: str,
    cost_factors: Dict
) -> Dict[str, Any]:
    """Estimate CAPEX for planned upgrades."""
    element_costs = cost_factors.get(element_type, cost_factors["default"])

    total_capex = 0
    cost_breakdown = []

    for upgrade in upgrades:
        upgrade_type = upgrade.get("to_technology", "standard")
        base_cost = element_costs.get(upgrade_type, element_costs["base"])

        cost_breakdown.append({
            "year": upgrade["year"],
            "item": f"Upgrade to {upgrade_type}",
            "cost": base_cost
        })
        total_capex += base_cost

    return {
        "total_capex": total_capex,
        "cost_breakdown": cost_breakdown,
        "annual_opex_impact": total_capex * 0.15
    }


def calculate_capacity(
    network_element: str,
    element_type: str,
    current_capacity: float,
    traffic_history: List[float],
    service_tier: str,
    technology: str,
    forecast_years: int
) -> Dict[str, Any]:
    """
    Calculate network capacity requirements.

    Business Rules:
    1. Traffic growth modeling with CAGR
    2. Utilization thresholds by service tier
    3. Redundancy requirements
    4. Technology migration planning

    Args:
        network_element: Element identifier
        element_type: Type of network element
        current_capacity: Current capacity Gbps
        traffic_history: Historical traffic
        service_tier: Service tier level
        technology: Current technology
        forecast_years: Planning horizon

    Returns:
        Capacity planning results
    """
    params = load_network_parameters()

    element_params = params["element_types"].get(element_type, params["element_types"]["default"])
    tier_params = params["service_tiers"].get(service_tier, params["service_tiers"]["standard"])

    # Calculate growth rate
    growth_rate = calculate_growth_rate(traffic_history)

    # Use minimum growth if calculated is too low
    growth_rate = max(growth_rate, element_params["min_growth_rate"])

    # Current traffic (most recent)
    current_traffic = traffic_history[-1] if traffic_history else 0

    # Forecast traffic
    traffic_forecast = forecast_traffic(
        current_traffic,
        growth_rate,
        forecast_years,
        element_params["peak_multiplier"]
    )

    # Apply redundancy factor to capacity
    effective_capacity = current_capacity / tier_params["redundancy_factor"]

    # Assess congestion risk
    congestion_risks = assess_congestion_risk(
        traffic_forecast,
        effective_capacity,
        tier_params["utilization_threshold"]
    )

    # Plan upgrades
    upgrade_plan = plan_upgrades(
        congestion_risks,
        technology,
        params["upgrade_paths"],
        service_tier
    )

    # Estimate investment
    investment = estimate_investment(
        upgrade_plan.get("timeline", []),
        element_type,
        params["cost_factors"]
    )

    # Determine current utilization
    current_utilization = current_traffic / effective_capacity if effective_capacity > 0 else 0

    return {
        "network_element": network_element,
        "element_type": element_type,
        "current_capacity_gbps": current_capacity,
        "effective_capacity_gbps": round(effective_capacity, 1),
        "current_traffic_gbps": current_traffic,
        "current_utilization_pct": round(current_utilization * 100, 1),
        "growth_rate_annual": round(growth_rate * 100, 1),
        "upgrade_required": upgrade_plan["upgrades_needed"],
        "upgrade_timeline": upgrade_plan,
        "capacity_forecast": traffic_forecast,
        "congestion_risk": congestion_risks,
        "investment_estimate": investment,
        "service_tier": service_tier,
        "technology": technology
    }


if __name__ == "__main__":
    import json
    result = calculate_capacity(
        network_element="ROUTER-NYC-01",
        element_type="core_router",
        current_capacity=100.0,
        traffic_history=[45.2, 48.5, 52.1, 55.8, 60.3, 65.0],
        service_tier="critical",
        technology="100G",
        forecast_years=5
    )
    print(json.dumps(result, indent=2))
