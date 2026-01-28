"""
Shipping Route Optimization Module

Implements multimodal route optimization considering cost,
time, and carbon emissions for freight transportation.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def load_transit_matrix() -> Dict[str, Any]:
    """Load transit time and cost matrix."""
    matrix_path = Path(__file__).parent / "transit_matrix.csv"
    routes = []

    with open(matrix_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            routes.append({
                "origin": row["origin"],
                "destination": row["destination"],
                "mode": row["mode"],
                "transit_days": float(row["transit_days"]),
                "cost_per_kg": float(row["cost_per_kg"]),
                "cost_per_cbm": float(row["cost_per_cbm"]),
                "carbon_kg_per_kg": float(row["carbon_kg_per_kg"]),
                "service_levels": row["service_levels"].split("|")
            })

    return {"routes": routes}


def find_direct_routes(
    origin_port: str,
    destination_port: str,
    routes: List[Dict]
) -> List[Dict]:
    """Find direct routes between origin and destination."""
    return [
        r for r in routes
        if r["origin"] == origin_port and r["destination"] == destination_port
    ]


def calculate_route_cost(
    route: Dict,
    weight_kg: float,
    volume_cbm: float
) -> float:
    """Calculate total cost for a route."""
    weight_cost = weight_kg * route["cost_per_kg"]
    volume_cost = volume_cbm * route["cost_per_cbm"]

    # Use higher of weight or volume cost (dimensional weight)
    return max(weight_cost, volume_cost)


def calculate_carbon_footprint(
    route: Dict,
    weight_kg: float
) -> float:
    """Calculate carbon emissions for a route."""
    return weight_kg * route["carbon_kg_per_kg"]


def score_route(
    route: Dict,
    transit_days: float,
    cost: float,
    carbon: float,
    preferences: Dict,
    deadline_days: float
) -> float:
    """Score route based on weighted preferences."""
    # Normalize scores (lower is better, so invert for scoring)
    max_transit = 60
    max_cost = 50000
    max_carbon = 10000

    transit_score = 1 - min(transit_days / max_transit, 1)
    cost_score = 1 - min(cost / max_cost, 1)
    carbon_score = 1 - min(carbon / max_carbon, 1)

    # Check deadline
    if transit_days > deadline_days:
        transit_score *= 0.5  # Penalize late delivery

    # Weighted score
    score = (
        transit_score * preferences.get("speed", 0.33) +
        cost_score * preferences.get("cost", 0.34) +
        carbon_score * preferences.get("sustainability", 0.33)
    )

    return score


def optimize_route(
    shipment_id: str,
    origin: Dict,
    destination: Dict,
    cargo_specs: Dict,
    service_level: str,
    delivery_deadline: str,
    preferences: Dict
) -> Dict[str, Any]:
    """
    Optimize shipping route for a shipment.

    Business Rules:
    1. Mode selection by shipment characteristics
    2. Hub network routing optimization
    3. Carbon footprint calculation
    4. Service level filtering

    Args:
        shipment_id: Shipment identifier
        origin: Origin location
        destination: Destination location
        cargo_specs: Cargo specifications
        service_level: Required service level
        delivery_deadline: Required delivery date
        preferences: Optimization preferences

    Returns:
        Optimized route recommendations
    """
    matrix = load_transit_matrix()

    origin_port = origin.get("port", "")
    destination_port = destination.get("port", "")
    weight_kg = cargo_specs.get("weight_kg", 0)
    volume_cbm = cargo_specs.get("volume_cbm", 0)

    # Calculate deadline days
    if delivery_deadline:
        deadline_date = datetime.strptime(delivery_deadline, "%Y-%m-%d")
        deadline_days = (deadline_date - datetime.now()).days
    else:
        deadline_days = 999

    # Find available routes
    direct_routes = find_direct_routes(origin_port, destination_port, matrix["routes"])

    # Filter by service level
    eligible_routes = [
        r for r in direct_routes
        if service_level in r["service_levels"]
    ]

    # If no direct routes, try common hubs (simplified)
    if not eligible_routes:
        eligible_routes = direct_routes  # Fall back to all direct routes

    # Score each route
    scored_routes = []
    for route in eligible_routes:
        cost = calculate_route_cost(route, weight_kg, volume_cbm)
        carbon = calculate_carbon_footprint(route, weight_kg)

        score = score_route(
            route,
            route["transit_days"],
            cost,
            carbon,
            preferences,
            deadline_days
        )

        scored_routes.append({
            "route": route,
            "cost": cost,
            "carbon_kg": carbon,
            "transit_days": route["transit_days"],
            "mode": route["mode"],
            "score": score,
            "meets_deadline": route["transit_days"] <= deadline_days
        })

    # Sort by score
    scored_routes.sort(key=lambda x: x["score"], reverse=True)

    # Build response
    if scored_routes:
        best = scored_routes[0]

        recommended_route = {
            "origin_port": origin_port,
            "destination_port": destination_port,
            "mode": best["mode"],
            "transit_days": best["transit_days"],
            "legs": [
                {
                    "from": origin_port,
                    "to": destination_port,
                    "mode": best["mode"],
                    "carrier": "Primary Carrier",
                    "transit_days": best["transit_days"]
                }
            ]
        }

        total_cost = best["cost"]
        carbon_footprint = best["carbon_kg"]
        transit_time = best["transit_days"]

    else:
        recommended_route = None
        total_cost = 0
        carbon_footprint = 0
        transit_time = 0

    # Alternative routes
    alternative_routes = [
        {
            "mode": r["mode"],
            "transit_days": r["transit_days"],
            "cost": round(r["cost"], 2),
            "carbon_kg": round(r["carbon_kg"], 2),
            "meets_deadline": r["meets_deadline"]
        }
        for r in scored_routes[1:4]
    ]

    # Estimated delivery date
    eta = datetime.now() + timedelta(days=transit_time)

    return {
        "shipment_id": shipment_id,
        "recommended_route": recommended_route,
        "alternative_routes": alternative_routes,
        "transit_time_days": transit_time,
        "estimated_delivery": eta.strftime("%Y-%m-%d"),
        "total_cost": round(total_cost, 2),
        "carbon_footprint_kg": round(carbon_footprint, 2),
        "meets_deadline": transit_time <= deadline_days,
        "origin": origin,
        "destination": destination,
        "service_level": service_level,
        "cargo_summary": cargo_specs
    }


if __name__ == "__main__":
    import json

    result = optimize_route(
        shipment_id="SHIP-2024-001",
        origin={"city": "Shanghai", "country": "CN", "port": "CNSHA"},
        destination={"city": "Chicago", "country": "US", "port": "USCHI"},
        cargo_specs={"weight_kg": 5000, "volume_cbm": 25, "type": "general"},
        service_level="standard",
        delivery_deadline="2026-02-15",
        preferences={"cost": 0.5, "speed": 0.3, "sustainability": 0.2}
    )
    print(json.dumps(result, indent=2))
