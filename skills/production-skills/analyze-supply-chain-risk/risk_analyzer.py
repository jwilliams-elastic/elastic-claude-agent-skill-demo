"""
Supply Chain Risk Analysis Module

Implements supply chain vulnerability assessment and
disruption scenario modeling.
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


def load_risk_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    thresholds_data = load_csv_as_dict("thresholds.csv")
    country_risks_data = load_csv_as_dict("country_risks.csv")
    scenarios_data = load_csv_as_dict("scenarios.csv")
    category_weights_data = load_key_value_csv("category_weights.csv")
    params = load_parameters()
    return {
        "thresholds": thresholds_data,
        "country_risks": country_risks_data,
        "scenarios": scenarios_data,
        "category_weights": category_weights_data,
        **params
    }


def assess_supplier_concentration(
    suppliers: List[Dict],
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess single-source and concentration risk."""
    if not suppliers:
        return {"score": 100, "issues": ["No supplier data"]}

    issues = []
    score = 0

    # Check for single source
    if len(suppliers) == 1:
        issues.append("Single source supplier - critical dependency")
        score = 90

    # Check for concentration
    max_spend = max(s.get("spend_pct", 0) for s in suppliers)
    if max_spend > thresholds["concentration_critical"]:
        issues.append(f"Supplier concentration {max_spend:.0%} exceeds critical threshold")
        score = max(score, 80)
    elif max_spend > thresholds["concentration_warning"]:
        issues.append(f"Supplier concentration {max_spend:.0%} exceeds warning threshold")
        score = max(score, 50)

    return {
        "score": score,
        "issues": issues,
        "supplier_count": len(suppliers),
        "max_concentration": max_spend
    }


def assess_geographic_risk(
    suppliers: List[Dict],
    routes: List[Dict],
    country_risks: Dict
) -> Dict[str, Any]:
    """Assess geographic concentration and country risk."""
    issues = []
    score = 0

    # Analyze supplier locations
    locations = {}
    for supplier in suppliers:
        loc = supplier.get("location", "unknown")
        spend = supplier.get("spend_pct", 0)
        if loc not in locations:
            locations[loc] = 0
        locations[loc] += spend

    # Check country risk
    for loc, spend in locations.items():
        risk_level = country_risks.get(loc, {}).get("risk_level", "medium")
        if risk_level == "high" and spend > 0.2:
            issues.append(f"High-risk country {loc} represents {spend:.0%} of supply")
            score = max(score, 70)
        elif risk_level == "elevated" and spend > 0.4:
            issues.append(f"Elevated-risk country {loc} represents {spend:.0%} of supply")
            score = max(score, 50)

    # Check regional concentration
    if len(locations) == 1:
        issues.append("All suppliers in single country - geographic concentration")
        score = max(score, 60)

    return {
        "score": score,
        "issues": issues,
        "geographic_distribution": locations
    }


def assess_inventory_risk(
    inventory_levels: Dict,
    demand_forecast: Dict,
    suppliers: List[Dict]
) -> Dict[str, Any]:
    """Assess inventory coverage and buffer adequacy."""
    on_hand = inventory_levels.get("on_hand", 0)
    safety_stock = inventory_levels.get("safety_stock", 0)
    monthly_demand = demand_forecast.get("monthly", 1)

    # Days of supply
    dos = (on_hand / (monthly_demand / 30)) if monthly_demand > 0 else 0

    # Get max lead time
    max_lead_time = max((s.get("lead_time_days", 30) for s in suppliers), default=30)

    issues = []
    score = 0

    if dos < max_lead_time:
        issues.append(f"Inventory cover ({dos:.0f} days) less than lead time ({max_lead_time} days)")
        score = 80
    elif dos < max_lead_time * 1.5:
        issues.append(f"Inventory buffer below recommended level")
        score = 50

    if on_hand < safety_stock:
        issues.append("Inventory below safety stock level")
        score = max(score, 70)

    return {
        "score": score,
        "issues": issues,
        "days_of_supply": round(dos, 1),
        "max_lead_time": max_lead_time
    }


def analyze_disruption_scenarios(
    suppliers: List[Dict],
    inventory_levels: Dict,
    demand_forecast: Dict,
    scenarios: Dict
) -> Dict[str, Any]:
    """Model impact of disruption scenarios."""
    results = {}

    on_hand = inventory_levels.get("on_hand", 0)
    monthly_demand = demand_forecast.get("monthly", 1)
    daily_demand = monthly_demand / 30

    for scenario_name, scenario in scenarios.items():
        duration_days = scenario.get("duration_days", 30)
        supply_reduction = scenario.get("supply_reduction", 1.0)

        demand_during = daily_demand * duration_days
        supply_during = demand_during * (1 - supply_reduction)
        shortfall = max(0, demand_during - on_hand - supply_during)

        results[scenario_name] = {
            "duration_days": duration_days,
            "demand": round(demand_during, 0),
            "supply_available": round(supply_during + on_hand, 0),
            "shortfall": round(shortfall, 0),
            "stockout_likely": shortfall > 0
        }

    return results


def analyze_risk(
    product_id: str,
    suppliers: List[Dict],
    inventory_levels: Dict,
    demand_forecast: Dict,
    logistics_routes: List[Dict],
    historical_disruptions: List[Dict]
) -> Dict[str, Any]:
    """
    Analyze supply chain risks.

    Business Rules:
    1. Single source dependency scoring
    2. Geographic concentration risk
    3. Supplier financial health
    4. Lead time variability analysis

    Args:
        product_id: Product identifier
        suppliers: Supplier data
        inventory_levels: Inventory data
        demand_forecast: Demand forecast
        logistics_routes: Logistics data
        historical_disruptions: Past disruptions

    Returns:
        Supply chain risk assessment
    """
    params = load_risk_parameters()

    risk_categories = {}
    vulnerable_nodes = []
    recommendations = []

    # Supplier concentration risk
    concentration_risk = assess_supplier_concentration(
        suppliers, params["thresholds"]["concentration"]
    )
    risk_categories["supplier_concentration"] = concentration_risk

    if concentration_risk["score"] > 50:
        vulnerable_nodes.append({
            "type": "supplier",
            "issue": "concentration",
            "severity": "high" if concentration_risk["score"] > 70 else "medium"
        })
        recommendations.append({
            "priority": "high",
            "action": "Qualify additional suppliers to reduce concentration risk"
        })

    # Geographic risk
    geo_risk = assess_geographic_risk(
        suppliers, logistics_routes, params["country_risks"]
    )
    risk_categories["geographic"] = geo_risk

    if geo_risk["score"] > 50:
        recommendations.append({
            "priority": "medium",
            "action": "Develop supply sources in alternative regions"
        })

    # Inventory risk
    inventory_risk = assess_inventory_risk(
        inventory_levels, demand_forecast, suppliers
    )
    risk_categories["inventory"] = inventory_risk

    if inventory_risk["score"] > 50:
        recommendations.append({
            "priority": "high",
            "action": "Increase safety stock to cover lead time variability"
        })

    # Scenario analysis
    scenario_impacts = analyze_disruption_scenarios(
        suppliers, inventory_levels, demand_forecast, params["scenarios"]
    )

    # Calculate overall risk score
    weights = params["category_weights"]
    overall_score = (
        concentration_risk["score"] * weights["concentration"] +
        geo_risk["score"] * weights["geographic"] +
        inventory_risk["score"] * weights["inventory"]
    )

    return {
        "product_id": product_id,
        "overall_risk_score": round(overall_score, 1),
        "risk_level": "high" if overall_score > 70 else "medium" if overall_score > 40 else "low",
        "risk_categories": risk_categories,
        "vulnerable_nodes": vulnerable_nodes,
        "mitigation_recommendations": recommendations,
        "scenario_impacts": scenario_impacts
    }


if __name__ == "__main__":
    import json
    result = analyze_risk(
        product_id="PROD-001",
        suppliers=[
            {"id": "SUP-A", "location": "CN", "spend_pct": 0.6, "lead_time_days": 45},
            {"id": "SUP-B", "location": "TW", "spend_pct": 0.4, "lead_time_days": 35}
        ],
        inventory_levels={"on_hand": 5000, "safety_stock": 2000},
        demand_forecast={"monthly": 3000},
        logistics_routes=[{"mode": "ocean", "origin": "CN", "transit_days": 28}],
        historical_disruptions=[{"date": "2025-03", "duration_days": 14, "cause": "port_congestion"}]
    )
    print(json.dumps(result, indent=2))
