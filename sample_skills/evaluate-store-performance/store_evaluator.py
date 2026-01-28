"""
Store Performance Evaluation Module

Implements retail store performance assessment including
sales productivity, efficiency metrics, and benchmarking.
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


def load_store_metrics() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    performance_metrics_data = load_csv_as_dict("performance_metrics.csv")
    benchmarks_by_format_data = load_csv_as_dict("benchmarks_by_format.csv")
    performance_tiers_data = load_csv_as_dict("performance_tiers.csv")
    comp_sales_thresholds_data = load_key_value_csv("comp_sales_thresholds.csv")
    four_wall_contribution_data = load_key_value_csv("four_wall_contribution.csv")
    shrinkage_benchmarks_data = load_key_value_csv("shrinkage_benchmarks.csv")
    category_mix_targets_data = load_key_value_csv("category_mix_targets.csv")
    params = load_parameters()
    return {
        "performance_metrics": performance_metrics_data,
        "benchmarks_by_format": benchmarks_by_format_data,
        "performance_tiers": performance_tiers_data,
        "comp_sales_thresholds": comp_sales_thresholds_data,
        "four_wall_contribution": four_wall_contribution_data,
        "shrinkage_benchmarks": shrinkage_benchmarks_data,
        "category_mix_targets": category_mix_targets_data,
        **params
    }


def calculate_sales_productivity(
    total_sales: float,
    selling_sqft: float,
    labor_hours: float
) -> Dict[str, Any]:
    """Calculate sales productivity metrics."""
    sales_per_sqft = total_sales / selling_sqft if selling_sqft > 0 else 0
    sales_per_labor_hour = total_sales / labor_hours if labor_hours > 0 else 0

    return {
        "total_sales": total_sales,
        "selling_sqft": selling_sqft,
        "labor_hours": labor_hours,
        "sales_per_sqft": round(sales_per_sqft, 2),
        "sales_per_labor_hour": round(sales_per_labor_hour, 2)
    }


def calculate_conversion_metrics(
    transactions: int,
    traffic: int,
    total_sales: float
) -> Dict[str, Any]:
    """Calculate conversion and transaction metrics."""
    conversion_rate = (transactions / traffic * 100) if traffic > 0 else 0
    avg_transaction = total_sales / transactions if transactions > 0 else 0
    units_per_transaction = 0  # Would need unit data

    return {
        "traffic": traffic,
        "transactions": transactions,
        "conversion_rate": round(conversion_rate, 1),
        "average_transaction_value": round(avg_transaction, 2)
    }


def calculate_comp_sales(
    current_period_sales: float,
    prior_period_sales: float
) -> Dict[str, Any]:
    """Calculate comparable store sales."""
    if prior_period_sales <= 0:
        return {"error": "Invalid prior period sales"}

    comp_change = (current_period_sales - prior_period_sales) / prior_period_sales
    comp_change_pct = comp_change * 100

    return {
        "current_sales": current_period_sales,
        "prior_sales": prior_period_sales,
        "comp_change": round(comp_change, 4),
        "comp_change_pct": round(comp_change_pct, 1)
    }


def calculate_four_wall_profit(
    gross_sales: float,
    cost_of_goods: float,
    store_expenses: float,
    four_wall_config: Dict
) -> Dict[str, Any]:
    """Calculate four-wall contribution."""
    gross_margin = gross_sales - cost_of_goods
    gross_margin_pct = (gross_margin / gross_sales * 100) if gross_sales > 0 else 0

    four_wall_contribution = gross_margin - store_expenses
    four_wall_margin = (four_wall_contribution / gross_sales * 100) if gross_sales > 0 else 0

    target_margin = four_wall_config.get("target_margin", 0.20) * 100
    minimum_margin = four_wall_config.get("minimum_margin", 0.10) * 100

    return {
        "gross_sales": gross_sales,
        "cost_of_goods": cost_of_goods,
        "gross_margin": round(gross_margin, 2),
        "gross_margin_pct": round(gross_margin_pct, 1),
        "store_expenses": store_expenses,
        "four_wall_contribution": round(four_wall_contribution, 2),
        "four_wall_margin_pct": round(four_wall_margin, 1),
        "meets_target": four_wall_margin >= target_margin,
        "meets_minimum": four_wall_margin >= minimum_margin
    }


def benchmark_performance(
    metrics: Dict,
    store_format: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Benchmark store against format standards."""
    format_benchmark = benchmarks.get(store_format, benchmarks.get("specialty", {}))

    comparisons = {}

    # Sales per sqft
    sales_sqft = metrics.get("sales_per_sqft", 0)
    benchmark_sqft = format_benchmark.get("sales_sqft", 300)
    comparisons["sales_per_sqft"] = {
        "actual": sales_sqft,
        "benchmark": benchmark_sqft,
        "vs_benchmark_pct": round((sales_sqft / benchmark_sqft - 1) * 100, 1) if benchmark_sqft > 0 else 0
    }

    # Conversion rate
    conversion = metrics.get("conversion_rate", 0)
    benchmark_conv = format_benchmark.get("conversion", 30)
    comparisons["conversion_rate"] = {
        "actual": conversion,
        "benchmark": benchmark_conv,
        "vs_benchmark_pct": round((conversion / benchmark_conv - 1) * 100, 1) if benchmark_conv > 0 else 0
    }

    # Average transaction
    avg_trans = metrics.get("average_transaction_value", 0)
    benchmark_trans = format_benchmark.get("avg_transaction", 50)
    comparisons["average_transaction"] = {
        "actual": avg_trans,
        "benchmark": benchmark_trans,
        "vs_benchmark_pct": round((avg_trans / benchmark_trans - 1) * 100, 1) if benchmark_trans > 0 else 0
    }

    # Labor efficiency
    labor_eff = metrics.get("sales_per_labor_hour", 0)
    benchmark_labor = format_benchmark.get("labor_efficiency", 100)
    comparisons["labor_efficiency"] = {
        "actual": labor_eff,
        "benchmark": benchmark_labor,
        "vs_benchmark_pct": round((labor_eff / benchmark_labor - 1) * 100, 1) if benchmark_labor > 0 else 0
    }

    # Calculate overall benchmark score
    scores = []
    for metric, data in comparisons.items():
        vs_benchmark = data["vs_benchmark_pct"]
        if vs_benchmark >= 10:
            scores.append(100)
        elif vs_benchmark >= 0:
            scores.append(80)
        elif vs_benchmark >= -10:
            scores.append(60)
        else:
            scores.append(40)

    overall_score = sum(scores) / len(scores) if scores else 50

    return {
        "store_format": store_format,
        "metric_comparisons": comparisons,
        "overall_benchmark_score": round(overall_score, 1)
    }


def classify_comp_performance(
    comp_change: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Classify comp sales performance."""
    if comp_change >= thresholds.get("strong_growth", 0.05):
        classification = "STRONG_GROWTH"
        trend = "positive"
    elif comp_change >= thresholds.get("moderate_growth", 0.02):
        classification = "MODERATE_GROWTH"
        trend = "positive"
    elif comp_change >= thresholds.get("flat", 0):
        classification = "FLAT"
        trend = "neutral"
    elif comp_change >= thresholds.get("decline", -0.03):
        classification = "DECLINE"
        trend = "negative"
    else:
        classification = "SIGNIFICANT_DECLINE"
        trend = "negative"

    return {
        "classification": classification,
        "trend": trend,
        "comp_change": comp_change
    }


def determine_performance_tier(
    overall_score: float,
    tiers: Dict
) -> Dict[str, Any]:
    """Determine store performance tier."""
    if overall_score >= tiers.get("top_performer", {}).get("percentile", 90):
        tier = "TOP_PERFORMER"
        action = tiers.get("top_performer", {}).get("action", "flagship_model")
    elif overall_score >= tiers.get("above_average", {}).get("percentile", 75):
        tier = "ABOVE_AVERAGE"
        action = tiers.get("above_average", {}).get("action", "maintain_investment")
    elif overall_score >= tiers.get("average", {}).get("percentile", 50):
        tier = "AVERAGE"
        action = tiers.get("average", {}).get("action", "improvement_plan")
    elif overall_score >= tiers.get("below_average", {}).get("percentile", 25):
        tier = "BELOW_AVERAGE"
        action = tiers.get("below_average", {}).get("action", "turnaround_review")
    else:
        tier = "UNDERPERFORMING"
        action = tiers.get("underperforming", {}).get("action", "closure_consideration")

    return {
        "tier": tier,
        "score": overall_score,
        "recommended_action": action
    }


def analyze_shrinkage(
    shrinkage_amount: float,
    total_sales: float,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Analyze inventory shrinkage."""
    shrinkage_rate = shrinkage_amount / total_sales if total_sales > 0 else 0

    if shrinkage_rate <= benchmarks.get("excellent", 0.005):
        rating = "EXCELLENT"
    elif shrinkage_rate <= benchmarks.get("good", 0.010):
        rating = "GOOD"
    elif shrinkage_rate <= benchmarks.get("acceptable", 0.015):
        rating = "ACCEPTABLE"
    elif shrinkage_rate <= benchmarks.get("concerning", 0.020):
        rating = "CONCERNING"
    else:
        rating = "POOR"

    return {
        "shrinkage_amount": shrinkage_amount,
        "shrinkage_rate": round(shrinkage_rate, 4),
        "shrinkage_rate_pct": round(shrinkage_rate * 100, 2),
        "rating": rating
    }


def calculate_overall_score(
    productivity: Dict,
    conversion: Dict,
    four_wall: Dict,
    benchmark: Dict,
    weights: Dict
) -> float:
    """Calculate overall store performance score."""
    scores = {}

    # Normalize scores to 0-100 scale
    # Sales per sqft score
    sales_sqft = productivity.get("sales_per_sqft", 0)
    scores["sales_per_sqft"] = min(100, (sales_sqft / 500) * 100)

    # Conversion score
    conv_rate = conversion.get("conversion_rate", 0)
    scores["conversion_rate"] = min(100, conv_rate)

    # Average transaction score (normalized to $100 = 100)
    avg_trans = conversion.get("average_transaction_value", 0)
    scores["average_transaction"] = min(100, avg_trans)

    # Labor efficiency score
    labor_eff = productivity.get("sales_per_labor_hour", 0)
    scores["labor_efficiency"] = min(100, (labor_eff / 150) * 100)

    # Four wall margin score
    four_wall_margin = four_wall.get("four_wall_margin_pct", 0)
    scores["four_wall_margin"] = min(100, (four_wall_margin / 25) * 100)

    # Weighted average
    weighted_sum = sum(
        scores.get(metric.replace("_", "_"), 50) * config.get("weight", 0.2)
        for metric, config in weights.items()
        if metric in scores
    )

    return round(weighted_sum, 1)


def evaluate_store_performance(
    store_id: str,
    store_name: str,
    store_format: str,
    current_period_sales: float,
    prior_period_sales: float,
    traffic: int,
    transactions: int,
    selling_sqft: float,
    labor_hours: float,
    cost_of_goods: float,
    store_expenses: float,
    shrinkage: float,
    evaluation_period: str,
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate store performance.

    Business Rules:
    1. Sales productivity analysis
    2. Conversion and transaction metrics
    3. Four-wall profitability
    4. Benchmark comparison

    Args:
        store_id: Store identifier
        store_name: Store name
        store_format: Store format type
        current_period_sales: Current period sales
        prior_period_sales: Prior period sales for comp
        traffic: Customer traffic count
        transactions: Number of transactions
        selling_sqft: Selling square footage
        labor_hours: Total labor hours
        cost_of_goods: Cost of goods sold
        store_expenses: Direct store expenses
        shrinkage: Inventory shrinkage amount
        evaluation_period: Period evaluated
        evaluation_date: Evaluation date

    Returns:
        Store performance evaluation results
    """
    config = load_store_metrics()

    # Calculate productivity
    productivity = calculate_sales_productivity(
        current_period_sales,
        selling_sqft,
        labor_hours
    )

    # Calculate conversion
    conversion = calculate_conversion_metrics(
        transactions,
        traffic,
        current_period_sales
    )

    # Calculate comp sales
    comp = calculate_comp_sales(current_period_sales, prior_period_sales)

    # Classify comp performance
    comp_classification = classify_comp_performance(
        comp.get("comp_change", 0),
        config.get("comp_sales_thresholds", {})
    )

    # Calculate four-wall
    four_wall = calculate_four_wall_profit(
        current_period_sales,
        cost_of_goods,
        store_expenses,
        config.get("four_wall_contribution", {})
    )

    # Benchmark performance
    all_metrics = {**productivity, **conversion}
    benchmark = benchmark_performance(
        all_metrics,
        store_format,
        config.get("benchmarks_by_format", {})
    )

    # Analyze shrinkage
    shrinkage_analysis = analyze_shrinkage(
        shrinkage,
        current_period_sales,
        config.get("shrinkage_benchmarks", {})
    )

    # Calculate overall score
    overall_score = calculate_overall_score(
        productivity,
        conversion,
        four_wall,
        benchmark,
        config.get("performance_metrics", {})
    )

    # Determine tier
    tier = determine_performance_tier(
        overall_score,
        config.get("performance_tiers", {})
    )

    return {
        "store_id": store_id,
        "store_name": store_name,
        "store_format": store_format,
        "evaluation_period": evaluation_period,
        "evaluation_date": evaluation_date,
        "sales_productivity": productivity,
        "conversion_metrics": conversion,
        "comp_sales": {**comp, **comp_classification},
        "four_wall_analysis": four_wall,
        "benchmark_comparison": benchmark,
        "shrinkage_analysis": shrinkage_analysis,
        "overall_score": overall_score,
        "performance_tier": tier,
        "recommendations": generate_recommendations(
            productivity,
            conversion,
            four_wall,
            shrinkage_analysis,
            tier
        )
    }


def generate_recommendations(
    productivity: Dict,
    conversion: Dict,
    four_wall: Dict,
    shrinkage: Dict,
    tier: Dict
) -> List[str]:
    """Generate improvement recommendations."""
    recommendations = []

    if conversion.get("conversion_rate", 0) < 30:
        recommendations.append("Focus on improving customer engagement and conversion")

    if productivity.get("sales_per_labor_hour", 0) < 100:
        recommendations.append("Review labor scheduling to improve efficiency")

    if not four_wall.get("meets_minimum", True):
        recommendations.append("Address expense structure or margin improvement")

    if shrinkage.get("rating") in ["CONCERNING", "POOR"]:
        recommendations.append("Implement loss prevention measures")

    if tier.get("tier") in ["BELOW_AVERAGE", "UNDERPERFORMING"]:
        recommendations.append("Develop comprehensive turnaround plan")

    return recommendations


if __name__ == "__main__":
    import json
    result = evaluate_store_performance(
        store_id="STR-001",
        store_name="Downtown Flagship",
        store_format="specialty",
        current_period_sales=850000,
        prior_period_sales=820000,
        traffic=25000,
        transactions=8500,
        selling_sqft=2500,
        labor_hours=6500,
        cost_of_goods=425000,
        store_expenses=255000,
        shrinkage=8500,
        evaluation_period="2026-01",
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
