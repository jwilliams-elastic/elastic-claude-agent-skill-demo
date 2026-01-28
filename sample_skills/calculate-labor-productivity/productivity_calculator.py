"""
Labor Productivity Calculation Module

Implements labor productivity analysis including
output metrics, benchmarking, and efficiency factors.
"""

import csv
import ast
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
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
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
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
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


def load_productivity_standards() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    productivity_metrics_data = load_csv_as_dict("productivity_metrics.csv")
    industry_benchmarks_data = load_csv_as_dict("industry_benchmarks.csv")
    efficiency_factors_data = load_csv_as_dict("efficiency_factors.csv")
    performance_ratings_data = load_csv_as_dict("performance_ratings.csv")
    adjustment_factors_data = load_csv_as_dict("adjustment_factors.csv")
    cost_components_data = load_csv_as_dict("cost_components.csv")
    params = load_parameters()
    return {
        "productivity_metrics": productivity_metrics_data,
        "industry_benchmarks": industry_benchmarks_data,
        "efficiency_factors": efficiency_factors_data,
        "performance_ratings": performance_ratings_data,
        "adjustment_factors": adjustment_factors_data,
        "cost_components": cost_components_data,
        **params
    }


def calculate_output_per_hour(
    total_output: float,
    total_labor_hours: float,
    output_unit: str
) -> Dict[str, Any]:
    """Calculate output per labor hour."""
    if total_labor_hours <= 0:
        return {"error": "Invalid labor hours"}

    output_per_hour = total_output / total_labor_hours

    return {
        "total_output": total_output,
        "total_labor_hours": total_labor_hours,
        "output_per_hour": round(output_per_hour, 2),
        "output_unit": output_unit
    }


def calculate_revenue_per_employee(
    total_revenue: float,
    fte_count: float
) -> Dict[str, Any]:
    """Calculate revenue per full-time equivalent employee."""
    if fte_count <= 0:
        return {"error": "Invalid FTE count"}

    revenue_per_fte = total_revenue / fte_count

    return {
        "total_revenue": total_revenue,
        "fte_count": fte_count,
        "revenue_per_employee": round(revenue_per_fte, 2)
    }


def calculate_value_added_per_employee(
    revenue: float,
    material_costs: float,
    fte_count: float
) -> Dict[str, Any]:
    """Calculate value added per employee."""
    if fte_count <= 0:
        return {"error": "Invalid FTE count"}

    value_added = revenue - material_costs
    value_added_per_fte = value_added / fte_count

    return {
        "revenue": revenue,
        "material_costs": material_costs,
        "value_added": round(value_added, 2),
        "value_added_per_employee": round(value_added_per_fte, 2)
    }


def calculate_labor_cost_ratio(
    total_labor_cost: float,
    total_revenue: float
) -> Dict[str, Any]:
    """Calculate labor cost as percentage of revenue."""
    if total_revenue <= 0:
        return {"error": "Invalid revenue"}

    ratio = total_labor_cost / total_revenue

    return {
        "total_labor_cost": total_labor_cost,
        "total_revenue": total_revenue,
        "labor_cost_ratio": round(ratio, 4),
        "labor_cost_pct": round(ratio * 100, 1)
    }


def apply_adjustment_factors(
    base_productivity: float,
    experience_level: str,
    shift_type: str,
    overtime_hours: float,
    regular_hours: float,
    adjustment_factors: Dict
) -> Dict[str, Any]:
    """Apply adjustment factors to base productivity."""
    # Experience adjustment
    exp_factor = adjustment_factors.get("experience_level", {}).get(experience_level, 1.0)

    # Shift adjustment
    shift_factor = adjustment_factors.get("shift_type", {}).get(shift_type, 1.0)

    # Overtime adjustment
    total_hours = regular_hours + overtime_hours
    overtime_pct = overtime_hours / total_hours if total_hours > 0 else 0

    if overtime_pct <= 0.10:
        ot_factor = adjustment_factors.get("overtime", {}).get("regular", 1.0)
    elif overtime_pct <= 0.25:
        ot_factor = adjustment_factors.get("overtime", {}).get("overtime_1_4", 0.90)
    else:
        ot_factor = adjustment_factors.get("overtime", {}).get("overtime_4_plus", 0.80)

    # Combined adjustment
    combined_factor = exp_factor * shift_factor * ot_factor
    adjusted_productivity = base_productivity * combined_factor

    return {
        "base_productivity": base_productivity,
        "experience_factor": exp_factor,
        "shift_factor": shift_factor,
        "overtime_factor": ot_factor,
        "combined_factor": round(combined_factor, 3),
        "adjusted_productivity": round(adjusted_productivity, 2)
    }


def benchmark_productivity(
    productivity_metrics: Dict,
    industry: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Compare productivity against industry benchmarks."""
    industry_bench = benchmarks.get(industry, {})

    comparisons = []

    # Output per hour comparison
    if "output_per_hour" in productivity_metrics:
        target = industry_bench.get("output_per_hour", {}).get("target", 0)
        actual = productivity_metrics["output_per_hour"].get("output_per_hour", 0)
        variance = ((actual / target) - 1) * 100 if target > 0 else 0
        comparisons.append({
            "metric": "output_per_hour",
            "actual": actual,
            "target": target,
            "variance_pct": round(variance, 1),
            "unit": industry_bench.get("output_per_hour", {}).get("unit", "units")
        })

    # Revenue per employee comparison
    if "revenue_per_employee" in productivity_metrics:
        target = industry_bench.get("revenue_per_employee", {}).get("target", 0)
        actual = productivity_metrics["revenue_per_employee"].get("revenue_per_employee", 0)
        variance = ((actual / target) - 1) * 100 if target > 0 else 0
        comparisons.append({
            "metric": "revenue_per_employee",
            "actual": actual,
            "target": target,
            "variance_pct": round(variance, 1),
            "unit": "USD"
        })

    # Labor cost ratio comparison
    if "labor_cost_ratio" in productivity_metrics:
        target = industry_bench.get("labor_cost_ratio", {}).get("target", 0)
        actual = productivity_metrics["labor_cost_ratio"].get("labor_cost_ratio", 0)
        # Lower is better for cost ratio
        variance = ((target / actual) - 1) * 100 if actual > 0 else 0
        comparisons.append({
            "metric": "labor_cost_ratio",
            "actual": actual,
            "target": target,
            "variance_pct": round(variance, 1),
            "unit": "ratio"
        })

    # Overall assessment
    avg_variance = sum(c["variance_pct"] for c in comparisons) / len(comparisons) if comparisons else 0

    if avg_variance >= 10:
        performance = "ABOVE_BENCHMARK"
    elif avg_variance >= -10:
        performance = "AT_BENCHMARK"
    else:
        performance = "BELOW_BENCHMARK"

    return {
        "industry": industry,
        "comparisons": comparisons,
        "average_variance_pct": round(avg_variance, 1),
        "overall_performance": performance
    }


def rate_performance(
    productivity_percentile: float,
    ratings: Dict
) -> Dict[str, Any]:
    """Rate productivity performance based on percentile."""
    for rating_name, rating_config in ratings.items():
        if productivity_percentile >= rating_config.get("min_percentile", 0):
            return {
                "percentile": productivity_percentile,
                "rating": rating_name.upper().replace("_", " "),
                "multiplier": rating_config.get("multiplier", 1.0)
            }

    return {
        "percentile": productivity_percentile,
        "rating": "NEEDS IMPROVEMENT",
        "multiplier": 0.70
    }


def calculate_efficiency_breakdown(
    total_hours: float,
    efficiency_factors: Dict
) -> Dict[str, Any]:
    """Break down labor hours by efficiency category."""
    breakdown = {}

    for factor, factor_data in efficiency_factors.items():
        # Handle both dict format (from CSV) and flat format
        if isinstance(factor_data, dict):
            weight = factor_data.get("weight", 0)
        else:
            weight = factor_data
        hours = total_hours * weight
        breakdown[factor] = {
            "hours": round(hours, 1),
            "percentage": round(weight * 100, 1)
        }

    # Extract weights for productive time calculation
    direct_labor_data = efficiency_factors.get("direct_labor", {})
    indirect_labor_data = efficiency_factors.get("indirect_labor", {})
    direct_weight = direct_labor_data.get("weight", 0) if isinstance(direct_labor_data, dict) else direct_labor_data
    indirect_weight = indirect_labor_data.get("weight", 0) if isinstance(indirect_labor_data, dict) else indirect_labor_data
    productive_time = direct_weight + indirect_weight

    return {
        "total_hours": total_hours,
        "breakdown": breakdown,
        "productive_time_pct": round(productive_time * 100, 1),
        "non_productive_time_pct": round((1 - productive_time) * 100, 1)
    }


def calculate_labor_productivity(
    analysis_id: str,
    department: str,
    industry: str,
    total_output: float,
    output_unit: str,
    total_labor_hours: float,
    fte_count: float,
    total_revenue: float,
    material_costs: float,
    total_labor_cost: float,
    experience_level: str,
    shift_type: str,
    overtime_hours: float,
    analysis_period: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Calculate labor productivity.

    Business Rules:
    1. Multiple productivity metric calculations
    2. Adjustment factor application
    3. Industry benchmarking
    4. Performance rating

    Args:
        analysis_id: Analysis identifier
        department: Department or unit name
        industry: Industry for benchmarking
        total_output: Total units produced
        output_unit: Unit of measurement
        total_labor_hours: Total labor hours worked
        fte_count: Full-time equivalent count
        total_revenue: Total revenue generated
        material_costs: Material/input costs
        total_labor_cost: Total labor costs
        experience_level: Workforce experience level
        shift_type: Type of shift worked
        overtime_hours: Overtime hours worked
        analysis_period: Period analyzed
        analysis_date: Analysis date

    Returns:
        Labor productivity analysis results
    """
    config = load_productivity_standards()
    benchmarks = config.get("industry_benchmarks", {})
    adjustment_factors = config.get("adjustment_factors", {})
    efficiency_factors = config.get("efficiency_factors", {})
    ratings = config.get("performance_ratings", {})

    # Calculate core productivity metrics
    output_per_hour = calculate_output_per_hour(total_output, total_labor_hours, output_unit)
    revenue_per_emp = calculate_revenue_per_employee(total_revenue, fte_count)
    value_added = calculate_value_added_per_employee(total_revenue, material_costs, fte_count)
    labor_cost = calculate_labor_cost_ratio(total_labor_cost, total_revenue)

    productivity_metrics = {
        "output_per_hour": output_per_hour,
        "revenue_per_employee": revenue_per_emp,
        "value_added_per_employee": value_added,
        "labor_cost_ratio": labor_cost
    }

    # Apply adjustments
    regular_hours = total_labor_hours - overtime_hours
    adjusted = apply_adjustment_factors(
        output_per_hour.get("output_per_hour", 0),
        experience_level,
        shift_type,
        overtime_hours,
        regular_hours,
        adjustment_factors
    )

    # Benchmark comparison
    benchmark_results = benchmark_productivity(productivity_metrics, industry, benchmarks)

    # Calculate percentile (simplified based on benchmark variance)
    variance = benchmark_results.get("average_variance_pct", 0)
    percentile = min(max(50 + variance, 0), 100)

    # Rate performance
    performance_rating = rate_performance(percentile, ratings)

    # Efficiency breakdown
    efficiency_breakdown = calculate_efficiency_breakdown(total_labor_hours, efficiency_factors)

    return {
        "analysis_id": analysis_id,
        "department": department,
        "industry": industry,
        "analysis_date": analysis_date,
        "analysis_period": analysis_period,
        "productivity_metrics": productivity_metrics,
        "adjusted_productivity": adjusted,
        "benchmark_comparison": benchmark_results,
        "performance_rating": performance_rating,
        "efficiency_breakdown": efficiency_breakdown,
        "summary": {
            "output_per_hour": output_per_hour.get("output_per_hour", 0),
            "revenue_per_employee": revenue_per_emp.get("revenue_per_employee", 0),
            "labor_cost_pct": labor_cost.get("labor_cost_pct", 0),
            "overall_rating": performance_rating["rating"]
        }
    }


if __name__ == "__main__":
    import json
    result = calculate_labor_productivity(
        analysis_id="PROD-001",
        department="Manufacturing - Assembly",
        industry="manufacturing",
        total_output=45000,
        output_unit="units",
        total_labor_hours=1200,
        fte_count=15,
        total_revenue=4500000,
        material_costs=1800000,
        total_labor_cost=900000,
        experience_level="mid",
        shift_type="day",
        overtime_hours=150,
        analysis_period="2026-01",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
