"""
Workload Capacity Calculation Module

Implements workload capacity planning including
resource utilization, skill matching, and demand forecasting.
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


def load_capacity_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    utilization_targets_data = load_key_value_csv("utilization_targets.csv")
    resource_types_data = load_csv_as_dict("resource_types.csv")
    task_complexity_factors_data = load_key_value_csv("task_complexity_factors.csv")
    skill_match_efficiency_data = load_key_value_csv("skill_match_efficiency.csv")
    overhead_factors_data = load_key_value_csv("overhead_factors.csv")
    buffer_recommendations_data = load_key_value_csv("buffer_recommendations.csv")
    seasonal_adjustments_data = load_key_value_csv("seasonal_adjustments.csv")
    ramp_up_factors_data = load_key_value_csv("ramp_up_factors.csv")
    params = load_parameters()
    return {
        "utilization_targets": utilization_targets_data,
        "resource_types": resource_types_data,
        "task_complexity_factors": task_complexity_factors_data,
        "skill_match_efficiency": skill_match_efficiency_data,
        "overhead_factors": overhead_factors_data,
        "buffer_recommendations": buffer_recommendations_data,
        "seasonal_adjustments": seasonal_adjustments_data,
        "ramp_up_factors": ramp_up_factors_data,
        **params
    }


def calculate_resource_capacity(
    resources: List[Dict],
    resource_types: Dict,
    overhead_factors: Dict
) -> Dict[str, Any]:
    """Calculate total resource capacity."""
    total_capacity_hours = 0
    total_productive_hours = 0
    resource_breakdown = []

    total_overhead = sum(overhead_factors.values())

    for resource in resources:
        resource_type = resource.get("type", "analyst")
        headcount = resource.get("headcount", 1)
        availability_pct = resource.get("availability_pct", 1.0)

        type_config = resource_types.get(resource_type, resource_types.get("analyst", {}))
        capacity_hours = type_config.get("capacity_hours_week", 40)
        productive_ratio = type_config.get("productive_ratio", 0.80)

        # Weekly capacity
        raw_capacity = capacity_hours * headcount * availability_pct
        productive_capacity = raw_capacity * productive_ratio * (1 - total_overhead)

        total_capacity_hours += raw_capacity
        total_productive_hours += productive_capacity

        resource_breakdown.append({
            "resource_type": resource_type,
            "headcount": headcount,
            "availability_pct": availability_pct,
            "raw_capacity_hours": round(raw_capacity, 1),
            "productive_capacity_hours": round(productive_capacity, 1)
        })

    return {
        "total_raw_capacity_hours": round(total_capacity_hours, 1),
        "total_productive_capacity_hours": round(total_productive_hours, 1),
        "overhead_factor": round(total_overhead * 100, 1),
        "resource_breakdown": resource_breakdown
    }


def calculate_demand(
    tasks: List[Dict],
    complexity_factors: Dict,
    skill_efficiency: Dict
) -> Dict[str, Any]:
    """Calculate workload demand from tasks."""
    total_base_hours = 0
    total_adjusted_hours = 0
    task_details = []

    for task in tasks:
        base_hours = task.get("estimated_hours", 0)
        complexity = task.get("complexity", "moderate")
        skill_level = task.get("assigned_skill_level", "proficient")

        complexity_factor = complexity_factors.get(complexity, 1.3)
        skill_factor = skill_efficiency.get(skill_level, 1.15)

        adjusted_hours = base_hours * complexity_factor * skill_factor

        total_base_hours += base_hours
        total_adjusted_hours += adjusted_hours

        task_details.append({
            "task_id": task.get("id", ""),
            "task_name": task.get("name", ""),
            "base_hours": base_hours,
            "complexity": complexity,
            "complexity_factor": complexity_factor,
            "skill_factor": skill_factor,
            "adjusted_hours": round(adjusted_hours, 1)
        })

    return {
        "total_base_hours": round(total_base_hours, 1),
        "total_adjusted_hours": round(total_adjusted_hours, 1),
        "adjustment_ratio": round(total_adjusted_hours / total_base_hours, 2) if total_base_hours > 0 else 1,
        "task_count": len(tasks),
        "task_details": task_details[:10]  # Top 10 for sample
    }


def calculate_utilization(
    capacity_hours: float,
    demand_hours: float,
    targets: Dict
) -> Dict[str, Any]:
    """Calculate utilization metrics."""
    utilization = demand_hours / capacity_hours if capacity_hours > 0 else 0

    if utilization < targets.get("optimal_min", 0.70):
        status = "UNDERUTILIZED"
    elif utilization <= targets.get("optimal_max", 0.85):
        status = "OPTIMAL"
    elif utilization <= targets.get("warning_threshold", 0.90):
        status = "WARNING"
    elif utilization <= targets.get("critical_threshold", 0.95):
        status = "HIGH"
    else:
        status = "OVERLOADED"

    available_hours = max(0, capacity_hours - demand_hours)

    return {
        "utilization_pct": round(utilization * 100, 1),
        "status": status,
        "available_hours": round(available_hours, 1),
        "capacity_hours": round(capacity_hours, 1),
        "demand_hours": round(demand_hours, 1)
    }


def calculate_buffer_requirement(
    demand_hours: float,
    risk_level: str,
    buffer_config: Dict
) -> Dict[str, Any]:
    """Calculate recommended capacity buffer."""
    buffer_pct = buffer_config.get(risk_level, buffer_config.get("medium_risk", 0.15))
    buffer_hours = demand_hours * buffer_pct
    recommended_capacity = demand_hours + buffer_hours

    return {
        "risk_level": risk_level,
        "buffer_pct": round(buffer_pct * 100, 1),
        "buffer_hours": round(buffer_hours, 1),
        "recommended_capacity": round(recommended_capacity, 1)
    }


def forecast_capacity_needs(
    current_demand: float,
    growth_rate: float,
    periods: int
) -> List[Dict]:
    """Forecast future capacity needs."""
    forecasts = []
    demand = current_demand

    for period in range(1, periods + 1):
        demand = demand * (1 + growth_rate)
        forecasts.append({
            "period": period,
            "forecasted_demand": round(demand, 1),
            "growth_applied": round(growth_rate * 100, 1)
        })

    return forecasts


def identify_bottlenecks(
    resources: List[Dict],
    tasks: List[Dict],
    resource_types: Dict
) -> List[Dict]:
    """Identify capacity bottlenecks by skill."""
    skill_demand = {}
    skill_capacity = {}

    # Aggregate demand by skill
    for task in tasks:
        skill_required = task.get("skill_required", "general")
        hours = task.get("estimated_hours", 0)
        skill_demand[skill_required] = skill_demand.get(skill_required, 0) + hours

    # Aggregate capacity by skill
    for resource in resources:
        skills = resource.get("skills", ["general"])
        resource_type = resource.get("type", "analyst")
        headcount = resource.get("headcount", 1)

        type_config = resource_types.get(resource_type, {})
        capacity = type_config.get("capacity_hours_week", 40) * type_config.get("productive_ratio", 0.80) * headcount

        for skill in skills:
            skill_capacity[skill] = skill_capacity.get(skill, 0) + capacity

    # Identify bottlenecks
    bottlenecks = []
    for skill, demand in skill_demand.items():
        capacity = skill_capacity.get(skill, 0)
        if capacity < demand:
            bottlenecks.append({
                "skill": skill,
                "demand_hours": round(demand, 1),
                "capacity_hours": round(capacity, 1),
                "gap_hours": round(demand - capacity, 1),
                "severity": "critical" if demand > capacity * 1.5 else "moderate"
            })

    return sorted(bottlenecks, key=lambda x: x["gap_hours"], reverse=True)


def calculate_cost_projection(
    resources: List[Dict],
    resource_types: Dict,
    weeks: int
) -> Dict[str, Any]:
    """Calculate resource cost projection."""
    total_cost = 0
    cost_breakdown = []

    for resource in resources:
        resource_type = resource.get("type", "analyst")
        headcount = resource.get("headcount", 1)

        type_config = resource_types.get(resource_type, {})
        hourly_rate = type_config.get("cost_per_hour", 100)
        hours_per_week = type_config.get("capacity_hours_week", 40)

        weekly_cost = hourly_rate * hours_per_week * headcount
        period_cost = weekly_cost * weeks
        total_cost += period_cost

        cost_breakdown.append({
            "resource_type": resource_type,
            "headcount": headcount,
            "hourly_rate": hourly_rate,
            "weekly_cost": round(weekly_cost, 2),
            "period_cost": round(period_cost, 2)
        })

    return {
        "total_cost": round(total_cost, 2),
        "weeks": weeks,
        "cost_breakdown": cost_breakdown
    }


def calculate_workload_capacity(
    team_id: str,
    resources: List[Dict],
    tasks: List[Dict],
    risk_level: str,
    growth_rate: float,
    forecast_periods: int,
    quarter: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Calculate workload capacity and utilization.

    Business Rules:
    1. Resource capacity calculation
    2. Demand estimation with complexity
    3. Utilization and buffer analysis
    4. Bottleneck identification

    Args:
        team_id: Team identifier
        resources: Resource allocation data
        tasks: Task workload data
        risk_level: Risk level for buffer calculation
        growth_rate: Expected demand growth rate
        forecast_periods: Number of periods to forecast
        quarter: Current quarter for seasonal adjustment
        analysis_date: Analysis date

    Returns:
        Workload capacity analysis results
    """
    params = load_capacity_parameters()

    # Apply seasonal adjustment
    seasonal_factor = params.get("seasonal_adjustments", {}).get(quarter, 1.0)

    # Calculate capacity
    capacity = calculate_resource_capacity(
        resources,
        params.get("resource_types", {}),
        params.get("overhead_factors", {})
    )

    # Adjust for seasonality
    adjusted_capacity = capacity["total_productive_capacity_hours"] * seasonal_factor

    # Calculate demand
    demand = calculate_demand(
        tasks,
        params.get("task_complexity_factors", {}),
        params.get("skill_match_efficiency", {})
    )

    # Calculate utilization
    utilization = calculate_utilization(
        adjusted_capacity,
        demand["total_adjusted_hours"],
        params.get("utilization_targets", {})
    )

    # Calculate buffer
    buffer = calculate_buffer_requirement(
        demand["total_adjusted_hours"],
        risk_level,
        params.get("buffer_recommendations", {})
    )

    # Forecast capacity needs
    forecast = forecast_capacity_needs(
        demand["total_adjusted_hours"],
        growth_rate,
        forecast_periods
    )

    # Identify bottlenecks
    bottlenecks = identify_bottlenecks(
        resources,
        tasks,
        params.get("resource_types", {})
    )

    # Cost projection
    cost = calculate_cost_projection(
        resources,
        params.get("resource_types", {}),
        4  # 4-week projection
    )

    # Recommendations
    recommendations = []
    if utilization["status"] == "OVERLOADED":
        recommendations.append("Increase headcount or reduce scope")
    if utilization["status"] == "UNDERUTILIZED":
        recommendations.append("Consider resource reallocation")
    if bottlenecks:
        recommendations.append(f"Address {len(bottlenecks)} skill bottlenecks")

    return {
        "team_id": team_id,
        "analysis_date": analysis_date,
        "quarter": quarter,
        "seasonal_factor": seasonal_factor,
        "capacity_analysis": capacity,
        "demand_analysis": demand,
        "utilization": utilization,
        "buffer_analysis": buffer,
        "capacity_forecast": forecast,
        "bottlenecks": bottlenecks[:5],
        "cost_projection": cost,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    import json
    result = calculate_workload_capacity(
        team_id="TEAM-001",
        resources=[
            {"type": "developer", "headcount": 5, "availability_pct": 0.90, "skills": ["python", "java"]},
            {"type": "analyst", "headcount": 2, "availability_pct": 1.0, "skills": ["analysis", "sql"]},
            {"type": "designer", "headcount": 1, "availability_pct": 0.80, "skills": ["ui", "ux"]}
        ],
        tasks=[
            {"id": "T-001", "name": "API Development", "estimated_hours": 40, "complexity": "complex", "skill_required": "python"},
            {"id": "T-002", "name": "Data Analysis", "estimated_hours": 20, "complexity": "moderate", "skill_required": "sql"},
            {"id": "T-003", "name": "UI Design", "estimated_hours": 30, "complexity": "moderate", "skill_required": "ui"}
        ],
        risk_level="medium_risk",
        growth_rate=0.05,
        forecast_periods=4,
        quarter="Q1",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
