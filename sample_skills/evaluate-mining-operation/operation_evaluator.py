"""
Mining Operation Evaluation Module

Implements efficiency analysis and benchmarking for mining operations
across different mining methods.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_mining_benchmarks() -> Dict[str, Any]:
    """Load mining benchmark data."""
    benchmarks_path = Path(__file__).parent / "mining_benchmarks.csv"
    benchmarks = {}

    with open(benchmarks_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            method = row["mining_method"]
            metric = row["metric"]
            if method not in benchmarks:
                benchmarks[method] = {}
            benchmarks[method][metric] = {
                "target": float(row["target"]),
                "minimum": float(row["minimum"]),
                "best_in_class": float(row["best_in_class"]),
                "unit": row["unit"],
                "weight": float(row["weight"])
            }

    return benchmarks


def calculate_ltifr(lost_time_incidents: int, hours_worked: int) -> float:
    """Calculate Lost Time Injury Frequency Rate."""
    if hours_worked == 0:
        return 0.0
    return (lost_time_incidents / hours_worked) * 1000000


def evaluate_equipment_performance(
    equipment_metrics: List[Dict],
    benchmarks: Dict
) -> Dict[str, Any]:
    """Evaluate equipment availability and utilization."""
    if not equipment_metrics:
        return {"score": 0, "findings": [], "bottlenecks": []}

    findings = []
    bottlenecks = []
    total_score = 0

    for equip in equipment_metrics:
        equip_type = equip.get("type", "unknown")
        availability = equip.get("availability", 0)
        utilization = equip.get("utilization", 0)

        avail_benchmark = benchmarks.get("equipment_availability", {})
        target_avail = avail_benchmark.get("target", 0.90)

        if availability < avail_benchmark.get("minimum", 0.85):
            bottlenecks.append({
                "type": "equipment_availability",
                "equipment": equip_type,
                "current": availability,
                "target": target_avail
            })
            score = 0.5
        elif availability >= target_avail:
            score = 1.0
        else:
            score = 0.75

        total_score += score

        findings.append({
            "equipment": equip_type,
            "availability": availability,
            "utilization": utilization,
            "score": score
        })

    avg_score = total_score / len(equipment_metrics)

    return {
        "score": round(avg_score, 2),
        "findings": findings,
        "bottlenecks": bottlenecks
    }


def evaluate_safety(
    safety_data: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Evaluate safety performance."""
    ltifr = calculate_ltifr(
        safety_data.get("lost_time_incidents", 0),
        safety_data.get("hours_worked", 1)
    )

    ltifr_benchmark = benchmarks.get("ltifr", {})
    target = ltifr_benchmark.get("target", 2.0)
    minimum = ltifr_benchmark.get("minimum", 5.0)

    if ltifr <= target:
        rating = "EXCELLENT"
        score = 1.0
    elif ltifr <= minimum:
        rating = "ACCEPTABLE"
        score = 0.75
    else:
        rating = "NEEDS_IMPROVEMENT"
        score = 0.5

    return {
        "ltifr": round(ltifr, 2),
        "target": target,
        "rating": rating,
        "score": score
    }


def evaluate_energy_efficiency(
    energy_consumption: Dict,
    production_tonnes: float,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Evaluate energy intensity."""
    diesel = energy_consumption.get("diesel_liters", 0)
    electricity = energy_consumption.get("electricity_kwh", 0)

    # Convert to energy equivalent (GJ)
    diesel_gj = diesel * 0.0384  # GJ per liter
    electricity_gj = electricity * 0.0036  # GJ per kWh
    total_energy_gj = diesel_gj + electricity_gj

    if production_tonnes > 0:
        energy_intensity = total_energy_gj / production_tonnes
    else:
        energy_intensity = 0

    benchmark = benchmarks.get("energy_intensity", {})
    target = benchmark.get("target", 0.05)
    best = benchmark.get("best_in_class", 0.03)

    if energy_intensity <= best:
        rating = "BEST_IN_CLASS"
        score = 1.0
    elif energy_intensity <= target:
        rating = "ON_TARGET"
        score = 0.85
    else:
        rating = "ABOVE_TARGET"
        score = 0.6

    return {
        "energy_intensity_gj_per_tonne": round(energy_intensity, 4),
        "target": target,
        "best_in_class": best,
        "rating": rating,
        "score": score
    }


def evaluate_operation(
    operation_id: str,
    mining_method: str,
    production_data: Dict,
    equipment_metrics: List[Dict],
    safety_data: Dict,
    energy_consumption: Dict,
    labor_data: Dict
) -> Dict[str, Any]:
    """
    Evaluate mining operation efficiency.

    Business Rules:
    1. Equipment availability targets by type
    2. Grade reconciliation variance limits
    3. LTIFR thresholds
    4. Energy intensity benchmarks

    Args:
        operation_id: Operation identifier
        mining_method: Mining method type
        production_data: Production metrics
        equipment_metrics: Equipment performance
        safety_data: Safety metrics
        energy_consumption: Energy usage
        labor_data: Labor metrics

    Returns:
        Operation evaluation with recommendations
    """
    benchmarks = load_mining_benchmarks()
    method_benchmarks = benchmarks.get(mining_method, benchmarks.get("open_pit", {}))

    bottlenecks = []
    optimization_opportunities = []

    # Equipment evaluation
    equipment_eval = evaluate_equipment_performance(equipment_metrics, method_benchmarks)
    bottlenecks.extend(equipment_eval.get("bottlenecks", []))

    # Safety evaluation
    safety_eval = evaluate_safety(safety_data, method_benchmarks)
    if safety_eval["rating"] == "NEEDS_IMPROVEMENT":
        optimization_opportunities.append({
            "category": "safety",
            "recommendation": "Implement enhanced safety training and hazard identification program",
            "potential_impact": "Reduce LTIFR by 30-50%"
        })

    # Energy evaluation
    tonnes_mined = production_data.get("tonnes_mined", 0)
    energy_eval = evaluate_energy_efficiency(energy_consumption, tonnes_mined, method_benchmarks)

    if energy_eval["rating"] == "ABOVE_TARGET":
        optimization_opportunities.append({
            "category": "energy",
            "recommendation": "Conduct energy audit and optimize haul truck dispatch",
            "potential_impact": f"Reduce energy intensity to {energy_eval['target']} GJ/t"
        })

    # Labor productivity
    productivity = labor_data.get("productivity_tonnes_per_person", 0)
    prod_benchmark = method_benchmarks.get("labor_productivity", {})
    prod_target = prod_benchmark.get("target", 1500)

    if productivity < prod_target:
        optimization_opportunities.append({
            "category": "labor",
            "recommendation": "Review workforce deployment and automation opportunities",
            "potential_impact": f"Increase productivity to {prod_target} t/person"
        })
        labor_score = productivity / prod_target
    else:
        labor_score = 1.0

    # Calculate overall efficiency score
    weights = {
        "equipment": 0.30,
        "safety": 0.25,
        "energy": 0.25,
        "labor": 0.20
    }

    efficiency_score = (
        equipment_eval["score"] * weights["equipment"] +
        safety_eval["score"] * weights["safety"] +
        energy_eval["score"] * weights["energy"] +
        labor_score * weights["labor"]
    ) * 100

    # Benchmark comparison
    benchmark_comparison = {
        "equipment_availability": equipment_eval,
        "safety": safety_eval,
        "energy_efficiency": energy_eval,
        "labor_productivity": {
            "current": productivity,
            "target": prod_target,
            "score": round(labor_score, 2)
        }
    }

    return {
        "operation_id": operation_id,
        "mining_method": mining_method,
        "efficiency_score": round(efficiency_score, 1),
        "safety_rating": safety_eval["rating"],
        "production_summary": {
            "tonnes_mined": tonnes_mined,
            "ore_grade": production_data.get("ore_grade"),
            "strip_ratio": production_data.get("strip_ratio")
        },
        "bottlenecks": bottlenecks,
        "optimization_opportunities": optimization_opportunities,
        "benchmark_comparison": benchmark_comparison
    }


if __name__ == "__main__":
    import json

    result = evaluate_operation(
        operation_id="MINE-001",
        mining_method="open_pit",
        production_data={"tonnes_mined": 500000, "ore_grade": 0.8, "strip_ratio": 3.5},
        equipment_metrics=[
            {"type": "haul_truck", "availability": 0.88, "utilization": 0.75},
            {"type": "excavator", "availability": 0.92, "utilization": 0.80}
        ],
        safety_data={"lost_time_incidents": 1, "hours_worked": 250000, "near_misses": 15},
        energy_consumption={"diesel_liters": 1500000, "electricity_kwh": 8000000},
        labor_data={"headcount": 350, "productivity_tonnes_per_person": 1428}
    )
    print(json.dumps(result, indent=2))
