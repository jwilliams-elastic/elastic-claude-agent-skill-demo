"""
Capacity Utilization Calculation Module

Implements capacity utilization analysis including
resource utilization, bottleneck identification, and planning.
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


def load_capacity_config() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    utilization_thresholds_data = load_csv_as_dict("utilization_thresholds.csv")
    capacity_types_data = load_csv_as_dict("capacity_types.csv")
    efficiency_factors_data = load_key_value_csv("efficiency_factors.csv")
    resource_categories_data = load_csv_as_dict("resource_categories.csv")
    bottleneck_analysis_data = load_key_value_csv("bottleneck_analysis.csv")
    cost_implications_data = load_key_value_csv("cost_implications.csv")
    planning_horizons_data = load_csv_as_dict("planning_horizons.csv")
    industry_benchmarks_data = load_csv_as_dict("industry_benchmarks.csv")
    params = load_parameters()
    return {
        "utilization_thresholds": utilization_thresholds_data,
        "capacity_types": capacity_types_data,
        "efficiency_factors": efficiency_factors_data,
        "resource_categories": resource_categories_data,
        "bottleneck_analysis": bottleneck_analysis_data,
        "cost_implications": cost_implications_data,
        "planning_horizons": planning_horizons_data,
        "industry_benchmarks": industry_benchmarks_data,
        **params
    }


def calculate_utilization_rate(
    actual_output: float,
    available_capacity: float
) -> Dict[str, Any]:
    """Calculate basic utilization rate."""
    if available_capacity <= 0:
        return {"error": "Invalid capacity"}

    utilization = actual_output / available_capacity
    utilization_pct = utilization * 100

    return {
        "actual_output": actual_output,
        "available_capacity": available_capacity,
        "utilization_rate": round(utilization, 4),
        "utilization_pct": round(utilization_pct, 1)
    }


def calculate_effective_capacity(
    design_capacity: float,
    efficiency_factors: Dict
) -> Dict[str, Any]:
    """Calculate effective capacity from design capacity."""
    total_loss = sum(efficiency_factors.values())
    efficiency_rate = 1 - total_loss
    effective_capacity = design_capacity * efficiency_rate

    factor_breakdown = {
        factor: round(design_capacity * loss, 2)
        for factor, loss in efficiency_factors.items()
    }

    return {
        "design_capacity": design_capacity,
        "efficiency_rate": round(efficiency_rate, 3),
        "total_loss_pct": round(total_loss * 100, 1),
        "effective_capacity": round(effective_capacity, 2),
        "loss_breakdown": factor_breakdown
    }


def assess_utilization_status(
    utilization: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess utilization status against thresholds."""
    optimal_min = thresholds.get("optimal_range", {}).get("min", 0.75)
    optimal_max = thresholds.get("optimal_range", {}).get("max", 0.90)
    warning_low = thresholds.get("warning_low", 0.60)
    warning_high = thresholds.get("warning_high", 0.95)
    critical_low = thresholds.get("critical_low", 0.50)

    if utilization < critical_low:
        status = "CRITICAL_UNDERUTILIZED"
        action = "urgent_capacity_reduction"
    elif utilization < warning_low:
        status = "UNDERUTILIZED"
        action = "evaluate_capacity_needs"
    elif utilization < optimal_min:
        status = "BELOW_OPTIMAL"
        action = "increase_demand_or_reduce_capacity"
    elif utilization <= optimal_max:
        status = "OPTIMAL"
        action = "maintain_current_levels"
    elif utilization <= warning_high:
        status = "ABOVE_OPTIMAL"
        action = "monitor_for_constraints"
    else:
        status = "OVERUTILIZED"
        action = "add_capacity_urgently"

    return {
        "utilization": utilization,
        "status": status,
        "recommended_action": action,
        "optimal_range": f"{optimal_min * 100:.0f}%-{optimal_max * 100:.0f}%"
    }


def calculate_oee_components(
    available_time: float,
    actual_running_time: float,
    ideal_cycle_time: float,
    actual_output: float,
    good_units: float
) -> Dict[str, Any]:
    """Calculate OEE (Overall Equipment Effectiveness) components."""
    # Availability
    availability = actual_running_time / available_time if available_time > 0 else 0

    # Performance
    theoretical_output = actual_running_time / ideal_cycle_time if ideal_cycle_time > 0 else 0
    performance = actual_output / theoretical_output if theoretical_output > 0 else 0

    # Quality
    quality = good_units / actual_output if actual_output > 0 else 0

    # OEE
    oee = availability * performance * quality

    return {
        "availability": {
            "value": round(availability, 4),
            "pct": round(availability * 100, 1),
            "available_time": available_time,
            "actual_running_time": actual_running_time
        },
        "performance": {
            "value": round(performance, 4),
            "pct": round(performance * 100, 1),
            "actual_output": actual_output,
            "theoretical_output": round(theoretical_output, 0)
        },
        "quality": {
            "value": round(quality, 4),
            "pct": round(quality * 100, 1),
            "good_units": good_units,
            "total_units": actual_output
        },
        "oee": {
            "value": round(oee, 4),
            "pct": round(oee * 100, 1)
        }
    }


def identify_bottlenecks(
    resources: List[Dict],
    threshold: float
) -> Dict[str, Any]:
    """Identify capacity bottlenecks."""
    bottlenecks = []
    near_bottlenecks = []

    for resource in resources:
        utilization = resource.get("utilization", 0)
        resource_id = resource.get("resource_id", "")

        if utilization >= threshold:
            bottlenecks.append({
                "resource_id": resource_id,
                "resource_name": resource.get("resource_name", ""),
                "utilization": utilization,
                "excess_demand": round((utilization - 1) * resource.get("capacity", 0), 2) if utilization > 1 else 0
            })
        elif utilization >= threshold - 0.05:
            near_bottlenecks.append({
                "resource_id": resource_id,
                "resource_name": resource.get("resource_name", ""),
                "utilization": utilization,
                "buffer_remaining": round((threshold - utilization) * resource.get("capacity", 0), 2)
            })

    # Sort by utilization descending
    bottlenecks.sort(key=lambda x: x["utilization"], reverse=True)
    near_bottlenecks.sort(key=lambda x: x["utilization"], reverse=True)

    return {
        "bottleneck_count": len(bottlenecks),
        "bottlenecks": bottlenecks,
        "near_bottleneck_count": len(near_bottlenecks),
        "near_bottlenecks": near_bottlenecks,
        "system_constrained": len(bottlenecks) > 0
    }


def calculate_capacity_gap(
    current_capacity: float,
    forecasted_demand: float
) -> Dict[str, Any]:
    """Calculate gap between capacity and demand."""
    gap = current_capacity - forecasted_demand
    gap_pct = gap / current_capacity if current_capacity > 0 else 0

    if gap > 0:
        status = "SURPLUS"
        action = "capacity_available"
    elif gap > -current_capacity * 0.1:
        status = "TIGHT"
        action = "monitor_closely"
    else:
        status = "DEFICIT"
        action = "expand_capacity"

    return {
        "current_capacity": current_capacity,
        "forecasted_demand": forecasted_demand,
        "capacity_gap": round(gap, 2),
        "gap_pct": round(gap_pct * 100, 1),
        "status": status,
        "recommended_action": action
    }


def calculate_cost_impact(
    utilization: float,
    capacity_cost: float,
    cost_config: Dict
) -> Dict[str, Any]:
    """Calculate cost impact of utilization level."""
    overtime_threshold = cost_config.get("overtime_threshold", 0.85)
    overtime_premium = cost_config.get("overtime_premium", 1.5)
    underutilization_cost_pct = cost_config.get("underutilization_cost_pct", 0.20)

    overtime_cost = 0
    underutilization_cost = 0

    if utilization > overtime_threshold:
        overtime_portion = utilization - overtime_threshold
        overtime_cost = capacity_cost * overtime_portion * (overtime_premium - 1)

    if utilization < 0.70:
        unused_capacity = 0.70 - utilization
        underutilization_cost = capacity_cost * unused_capacity * underutilization_cost_pct

    return {
        "base_capacity_cost": capacity_cost,
        "overtime_cost": round(overtime_cost, 2),
        "underutilization_cost": round(underutilization_cost, 2),
        "total_cost_impact": round(overtime_cost + underutilization_cost, 2),
        "cost_efficiency": "optimal" if overtime_cost == 0 and underutilization_cost == 0 else "suboptimal"
    }


def benchmark_performance(
    utilization: float,
    industry: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Benchmark utilization against industry standards."""
    industry_benchmark = benchmarks.get(industry, benchmarks.get("manufacturing_discrete", {}))
    target = industry_benchmark.get("target", 0.85)
    world_class = industry_benchmark.get("world_class", 0.92)

    vs_target = utilization - target
    vs_world_class = utilization - world_class

    if utilization >= world_class:
        performance_level = "WORLD_CLASS"
    elif utilization >= target:
        performance_level = "ABOVE_TARGET"
    elif utilization >= target - 0.10:
        performance_level = "NEAR_TARGET"
    else:
        performance_level = "BELOW_TARGET"

    return {
        "utilization": round(utilization * 100, 1),
        "industry": industry,
        "target_pct": round(target * 100, 1),
        "world_class_pct": round(world_class * 100, 1),
        "vs_target_pct": round(vs_target * 100, 1),
        "vs_world_class_pct": round(vs_world_class * 100, 1),
        "performance_level": performance_level
    }


def calculate_capacity_utilization(
    facility_id: str,
    resources: List[Dict],
    actual_output: float,
    design_capacity: float,
    oee_data: Optional[Dict],
    forecasted_demand: float,
    capacity_cost: float,
    industry: str,
    analysis_period: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Calculate capacity utilization.

    Business Rules:
    1. Multi-resource utilization tracking
    2. OEE calculation
    3. Bottleneck identification
    4. Capacity planning analysis

    Args:
        facility_id: Facility identifier
        resources: Resource utilization data
        actual_output: Actual production output
        design_capacity: Design capacity
        oee_data: OEE component data
        forecasted_demand: Forecasted demand
        capacity_cost: Capacity operating cost
        industry: Industry for benchmarking
        analysis_period: Analysis period
        analysis_date: Analysis date

    Returns:
        Capacity utilization analysis results
    """
    config = load_capacity_config()
    thresholds = config.get("utilization_thresholds", {})
    efficiency_factors = config.get("efficiency_factors", {})
    cost_config = config.get("cost_implications", {})
    benchmarks = config.get("industry_benchmarks", {})
    bottleneck_config = config.get("bottleneck_analysis", {})

    # Calculate effective capacity
    effective = calculate_effective_capacity(design_capacity, efficiency_factors)

    # Calculate overall utilization
    utilization = calculate_utilization_rate(actual_output, effective["effective_capacity"])

    # Assess status
    status = assess_utilization_status(
        utilization.get("utilization_rate", 0),
        thresholds
    )

    # Calculate OEE if data provided
    oee_result = None
    if oee_data:
        oee_result = calculate_oee_components(
            oee_data.get("available_time", 0),
            oee_data.get("actual_running_time", 0),
            oee_data.get("ideal_cycle_time", 0),
            oee_data.get("actual_output", actual_output),
            oee_data.get("good_units", actual_output)
        )

    # Identify bottlenecks
    bottlenecks = identify_bottlenecks(
        resources,
        bottleneck_config.get("bottleneck_threshold", 0.90)
    )

    # Capacity gap analysis
    capacity_gap = calculate_capacity_gap(
        effective["effective_capacity"],
        forecasted_demand
    )

    # Cost impact
    cost_impact = calculate_cost_impact(
        utilization.get("utilization_rate", 0),
        capacity_cost,
        cost_config
    )

    # Benchmark
    benchmark = benchmark_performance(
        utilization.get("utilization_rate", 0),
        industry,
        benchmarks
    )

    return {
        "facility_id": facility_id,
        "analysis_date": analysis_date,
        "analysis_period": analysis_period,
        "capacity_analysis": {
            "design_capacity": design_capacity,
            "effective_capacity": effective,
            "actual_output": actual_output
        },
        "utilization": utilization,
        "status_assessment": status,
        "oee_analysis": oee_result,
        "bottleneck_analysis": bottlenecks,
        "capacity_planning": capacity_gap,
        "cost_analysis": cost_impact,
        "benchmark_comparison": benchmark,
        "recommendations": generate_recommendations(
            status,
            bottlenecks,
            capacity_gap,
            benchmark
        )
    }


def generate_recommendations(
    status: Dict,
    bottlenecks: Dict,
    capacity_gap: Dict,
    benchmark: Dict
) -> List[str]:
    """Generate capacity recommendations."""
    recommendations = []

    if status["status"] in ["CRITICAL_UNDERUTILIZED", "UNDERUTILIZED"]:
        recommendations.append("Evaluate demand generation or capacity rationalization")

    if status["status"] == "OVERUTILIZED":
        recommendations.append("Add capacity to prevent quality and delivery issues")

    if bottlenecks["system_constrained"]:
        recommendations.append(f"Address {bottlenecks['bottleneck_count']} bottleneck resources")

    if capacity_gap["status"] == "DEFICIT":
        recommendations.append("Plan capacity expansion to meet forecasted demand")

    if benchmark["performance_level"] == "BELOW_TARGET":
        recommendations.append("Implement improvement initiatives to reach target utilization")

    return recommendations


if __name__ == "__main__":
    import json
    result = calculate_capacity_utilization(
        facility_id="FAC-001",
        resources=[
            {"resource_id": "M-001", "resource_name": "CNC Machine 1", "utilization": 0.92, "capacity": 160},
            {"resource_id": "M-002", "resource_name": "CNC Machine 2", "utilization": 0.78, "capacity": 160},
            {"resource_id": "L-001", "resource_name": "Assembly Line", "utilization": 0.85, "capacity": 200}
        ],
        actual_output=8500,
        design_capacity=10000,
        oee_data={
            "available_time": 480,
            "actual_running_time": 420,
            "ideal_cycle_time": 0.05,
            "actual_output": 8500,
            "good_units": 8350
        },
        forecasted_demand=9200,
        capacity_cost=150000,
        industry="manufacturing_discrete",
        analysis_period="2026-01",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
