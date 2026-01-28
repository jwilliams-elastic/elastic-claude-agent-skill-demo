"""
Fleet Efficiency Calculation Module

Implements fleet operational efficiency analysis including
utilization, fuel economy, and maintenance optimization.
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


def load_fleet_benchmarks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    utilization_data = load_key_value_csv("utilization.csv")
    fuel_data = load_key_value_csv("fuel.csv")
    maintenance_intervals_data = load_csv_as_dict("maintenance_intervals.csv")
    driver_benchmarks_data = load_key_value_csv("driver_benchmarks.csv")
    score_weights_data = load_key_value_csv("score_weights.csv")
    cost_factors_data = load_key_value_csv("cost_factors.csv")
    compliance_data = load_key_value_csv("compliance.csv")
    params = load_parameters()
    return {
        "utilization": utilization_data,
        "fuel": fuel_data,
        "maintenance_intervals": maintenance_intervals_data,
        "driver_benchmarks": driver_benchmarks_data,
        "score_weights": score_weights_data,
        "cost_factors": cost_factors_data,
        "compliance": compliance_data,
        **params
    }


def calculate_utilization(
    vehicle_data: List[Dict],
    trip_history: List[Dict],
    benchmarks: Dict
) -> Dict[str, Any]:
    """Calculate fleet utilization metrics."""
    if not vehicle_data:
        return {"error": "No vehicle data provided"}

    vehicle_metrics = {}
    total_capacity = 0
    total_utilized = 0

    for vehicle in vehicle_data:
        vehicle_id = vehicle.get("id", "unknown")
        capacity = vehicle.get("capacity_tons", 0)
        total_capacity += capacity

        # Find trips for this vehicle
        vehicle_trips = [t for t in trip_history if t.get("vehicle_id") == vehicle_id]

        if vehicle_trips:
            avg_load = sum(t.get("load_pct", 0) for t in vehicle_trips) / len(vehicle_trips)
            total_miles = sum(t.get("miles", 0) for t in vehicle_trips)
            loaded_miles = sum(t.get("miles", 0) * t.get("load_pct", 0) for t in vehicle_trips)
        else:
            avg_load = 0
            total_miles = 0
            loaded_miles = 0

        vehicle_metrics[vehicle_id] = {
            "avg_load_pct": round(avg_load, 2),
            "total_miles": total_miles,
            "loaded_miles": round(loaded_miles, 0),
            "empty_mile_pct": round(1 - (loaded_miles / total_miles), 2) if total_miles > 0 else 0
        }

        total_utilized += capacity * avg_load

    fleet_utilization = total_utilized / total_capacity if total_capacity > 0 else 0

    benchmark_util = benchmarks.get("target_utilization", 0.75)
    score = min(100, (fleet_utilization / benchmark_util) * 100)

    return {
        "fleet_utilization_pct": round(fleet_utilization, 2),
        "vehicle_metrics": vehicle_metrics,
        "benchmark_utilization": benchmark_util,
        "utilization_score": round(score, 1)
    }


def analyze_fuel_efficiency(
    fuel_records: List[Dict],
    trip_history: List[Dict],
    benchmarks: Dict
) -> Dict[str, Any]:
    """Analyze fuel efficiency metrics."""
    vehicle_mpg = {}
    total_gallons = 0
    total_miles = 0

    for record in fuel_records:
        vehicle_id = record.get("vehicle_id", "unknown")
        gallons = record.get("gallons", 0)
        miles = record.get("miles", 0)

        if vehicle_id not in vehicle_mpg:
            vehicle_mpg[vehicle_id] = {"gallons": 0, "miles": 0}

        vehicle_mpg[vehicle_id]["gallons"] += gallons
        vehicle_mpg[vehicle_id]["miles"] += miles
        total_gallons += gallons
        total_miles += miles

    # Calculate MPG for each vehicle
    for vehicle_id, data in vehicle_mpg.items():
        if data["gallons"] > 0:
            data["mpg"] = round(data["miles"] / data["gallons"], 2)
        else:
            data["mpg"] = 0

    fleet_mpg = total_miles / total_gallons if total_gallons > 0 else 0

    benchmark_mpg = benchmarks.get("target_mpg", 6.5)
    efficiency_score = min(100, (fleet_mpg / benchmark_mpg) * 100)

    # Identify underperformers
    underperformers = [
        {"vehicle_id": vid, "mpg": data["mpg"]}
        for vid, data in vehicle_mpg.items()
        if data["mpg"] < benchmark_mpg * 0.85 and data["mpg"] > 0
    ]

    return {
        "fleet_mpg": round(fleet_mpg, 2),
        "vehicle_mpg": vehicle_mpg,
        "benchmark_mpg": benchmark_mpg,
        "fuel_efficiency_score": round(efficiency_score, 1),
        "underperforming_vehicles": underperformers,
        "total_fuel_cost_est": round(total_gallons * benchmarks.get("fuel_price", 4.00), 2)
    }


def forecast_maintenance(
    vehicle_data: List[Dict],
    maintenance_logs: List[Dict],
    maintenance_intervals: Dict
) -> List[Dict]:
    """Forecast upcoming maintenance needs."""
    forecasts = []

    for vehicle in vehicle_data:
        vehicle_id = vehicle.get("id", "unknown")
        vehicle_type = vehicle.get("type", "truck")

        # Get intervals for this vehicle type
        intervals = maintenance_intervals.get(vehicle_type, maintenance_intervals.get("default", {}))

        # Find most recent maintenance by type
        vehicle_maintenance = [m for m in maintenance_logs if m.get("vehicle_id") == vehicle_id]

        for maint_type, interval in intervals.items():
            # Find last occurrence
            last_maint = None
            last_odometer = 0
            for m in vehicle_maintenance:
                if m.get("type") == maint_type:
                    last_maint = m
                    last_odometer = m.get("odometer", 0)

            # Current odometer (estimate from trips or use provided)
            current_odometer = vehicle.get("current_odometer", last_odometer + 5000)

            miles_since = current_odometer - last_odometer
            miles_until_due = interval - miles_since

            if miles_until_due <= 1000:
                priority = "urgent"
            elif miles_until_due <= 3000:
                priority = "soon"
            else:
                priority = "scheduled"

            if miles_until_due <= 5000:
                forecasts.append({
                    "vehicle_id": vehicle_id,
                    "maintenance_type": maint_type,
                    "miles_until_due": max(0, miles_until_due),
                    "priority": priority,
                    "last_performed_odometer": last_odometer
                })

    # Sort by urgency
    priority_order = {"urgent": 0, "soon": 1, "scheduled": 2}
    forecasts.sort(key=lambda x: (priority_order.get(x["priority"], 3), x["miles_until_due"]))

    return forecasts


def evaluate_driver_performance(
    driver_metrics: Dict,
    driver_benchmarks: Dict
) -> Dict[str, Any]:
    """Evaluate driver efficiency and safety."""
    findings = []
    score = 100

    avg_speed = driver_metrics.get("avg_speed", 0)
    idle_time_pct = driver_metrics.get("idle_time_pct", 0)
    hard_brakes_per_100mi = driver_metrics.get("hard_brakes_per_100mi", 0)
    speeding_events = driver_metrics.get("speeding_events", 0)

    # Speed efficiency
    optimal_speed_min = driver_benchmarks.get("optimal_speed_min", 55)
    optimal_speed_max = driver_benchmarks.get("optimal_speed_max", 65)

    if avg_speed < optimal_speed_min:
        findings.append({"metric": "speed", "issue": "Below optimal speed range", "impact": "low"})
        score -= 5
    elif avg_speed > optimal_speed_max:
        findings.append({"metric": "speed", "issue": "Above optimal speed range", "impact": "medium"})
        score -= 10

    # Idle time
    max_idle = driver_benchmarks.get("max_idle_pct", 0.10)
    if idle_time_pct > max_idle:
        findings.append({"metric": "idle_time", "issue": f"Idle time {idle_time_pct:.1%} exceeds {max_idle:.1%}", "impact": "medium"})
        score -= 15

    # Safety events
    max_hard_brakes = driver_benchmarks.get("max_hard_brakes_per_100mi", 5)
    if hard_brakes_per_100mi > max_hard_brakes:
        findings.append({"metric": "hard_braking", "issue": "Excessive hard braking events", "impact": "high"})
        score -= 20

    return {
        "driver_score": max(0, score),
        "findings": findings,
        "metrics_evaluated": driver_metrics
    }


def generate_optimization_recommendations(
    utilization: Dict,
    fuel_analysis: Dict,
    maintenance_forecast: List[Dict],
    driver_performance: Dict
) -> List[Dict]:
    """Generate fleet optimization recommendations."""
    recommendations = []

    # Utilization recommendations
    if utilization.get("fleet_utilization_pct", 0) < 0.70:
        recommendations.append({
            "category": "utilization",
            "priority": "high",
            "recommendation": "Consider fleet right-sizing or route optimization",
            "potential_impact": "10-15% cost reduction"
        })

    # Fuel recommendations
    for vehicle in fuel_analysis.get("underperforming_vehicles", []):
        recommendations.append({
            "category": "fuel_efficiency",
            "priority": "medium",
            "recommendation": f"Investigate low MPG for vehicle {vehicle['vehicle_id']}",
            "potential_impact": "Improved fuel cost"
        })

    # Maintenance recommendations
    urgent_maintenance = [m for m in maintenance_forecast if m["priority"] == "urgent"]
    if urgent_maintenance:
        recommendations.append({
            "category": "maintenance",
            "priority": "urgent",
            "recommendation": f"Schedule {len(urgent_maintenance)} urgent maintenance items",
            "potential_impact": "Prevent breakdowns and costly repairs"
        })

    # Driver recommendations
    if driver_performance.get("driver_score", 100) < 80:
        recommendations.append({
            "category": "driver_performance",
            "priority": "medium",
            "recommendation": "Implement driver coaching program",
            "potential_impact": "Improved safety and fuel efficiency"
        })

    return recommendations


def calculate_fleet_efficiency(
    fleet_id: str,
    vehicle_data: List[Dict],
    trip_history: List[Dict],
    fuel_records: List[Dict],
    maintenance_logs: List[Dict],
    driver_metrics: Dict
) -> Dict[str, Any]:
    """
    Calculate fleet operational efficiency.

    Business Rules:
    1. Fleet utilization measurement
    2. Fuel economy analysis
    3. Maintenance interval optimization
    4. Driver performance scoring

    Args:
        fleet_id: Fleet identifier
        vehicle_data: Vehicle details
        trip_history: Recent trips
        fuel_records: Fuel consumption
        maintenance_logs: Maintenance history
        driver_metrics: Driver performance

    Returns:
        Fleet efficiency analysis
    """
    benchmarks = load_fleet_benchmarks()

    # Utilization analysis
    utilization_metrics = calculate_utilization(
        vehicle_data,
        trip_history,
        benchmarks.get("utilization", {})
    )

    # Fuel analysis
    fuel_analysis = analyze_fuel_efficiency(
        fuel_records,
        trip_history,
        benchmarks.get("fuel", {})
    )

    # Maintenance forecast
    maintenance_forecast = forecast_maintenance(
        vehicle_data,
        maintenance_logs,
        benchmarks.get("maintenance_intervals", {})
    )

    # Driver performance
    driver_performance = evaluate_driver_performance(
        driver_metrics,
        benchmarks.get("driver_benchmarks", {})
    )

    # Calculate overall efficiency score
    weights = benchmarks.get("score_weights", {})
    fleet_efficiency_score = (
        utilization_metrics.get("utilization_score", 0) * weights.get("utilization", 0.30) +
        fuel_analysis.get("fuel_efficiency_score", 0) * weights.get("fuel", 0.30) +
        driver_performance.get("driver_score", 0) * weights.get("driver", 0.20) +
        (100 - len([m for m in maintenance_forecast if m["priority"] == "urgent"]) * 10) * weights.get("maintenance", 0.20)
    )

    # Generate recommendations
    recommendations = generate_optimization_recommendations(
        utilization_metrics,
        fuel_analysis,
        maintenance_forecast,
        driver_performance
    )

    return {
        "fleet_id": fleet_id,
        "fleet_efficiency_score": round(fleet_efficiency_score, 1),
        "utilization_metrics": utilization_metrics,
        "fuel_analysis": fuel_analysis,
        "maintenance_forecast": maintenance_forecast,
        "driver_performance": driver_performance,
        "optimization_recommendations": recommendations
    }


if __name__ == "__main__":
    import json
    result = calculate_fleet_efficiency(
        fleet_id="FLT-001",
        vehicle_data=[
            {"id": "VH-001", "type": "semi", "capacity_tons": 20, "current_odometer": 150000},
            {"id": "VH-002", "type": "semi", "capacity_tons": 20, "current_odometer": 120000}
        ],
        trip_history=[
            {"vehicle_id": "VH-001", "miles": 500, "load_pct": 0.85},
            {"vehicle_id": "VH-001", "miles": 450, "load_pct": 0.70},
            {"vehicle_id": "VH-002", "miles": 600, "load_pct": 0.90}
        ],
        fuel_records=[
            {"vehicle_id": "VH-001", "gallons": 80, "miles": 500},
            {"vehicle_id": "VH-002", "gallons": 85, "miles": 600}
        ],
        maintenance_logs=[
            {"vehicle_id": "VH-001", "type": "oil_change", "odometer": 145000},
            {"vehicle_id": "VH-002", "type": "oil_change", "odometer": 115000}
        ],
        driver_metrics={"avg_speed": 58, "idle_time_pct": 0.12, "hard_brakes_per_100mi": 3}
    )
    print(json.dumps(result, indent=2))
