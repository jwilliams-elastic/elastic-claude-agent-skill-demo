"""
Inventory Turnover Calculation Module

Implements inventory turnover analysis including
ABC classification, carrying costs, and performance benchmarking.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_csv_as_dict(filename: str, key_column: str) -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column)
            # Convert numeric values
            for k, v in row.items():
                try:
                    row[k] = float(v)
                except ValueError:
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
            for k, v in row.items():
                try:
                    row[k] = float(v)
                except ValueError:
                    pass
            result.append(row)
    return result


def load_parameters() -> Dict[str, float]:
    """Load parameters CSV as key-value dictionary."""
    csv_path = Path(__file__).parent / "parameters.csv"
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            try:
                result[row['parameter']] = float(row['value'])
            except ValueError:
                result[row['parameter']] = row['value']
    return result


def load_inventory_benchmarks() -> Dict[str, Any]:
    """Load all inventory benchmark data from CSV files."""
    params = load_parameters()

    return {
        "industry_benchmarks": load_csv_as_dict("industry_benchmarks.csv", "industry"),
        "performance_thresholds": load_csv_as_dict("performance_thresholds.csv", "rating"),
        "abc_classification": load_csv_as_dict("abc_classification.csv", "class"),
        "carrying_cost_components": load_csv_as_dict("carrying_costs.csv", "component"),
        "stockout_impact": {
            "lost_sale_pct": params.get("lost_sale_pct", 0.40),
            "backorder_pct": params.get("backorder_pct", 0.35),
            "substitute_pct": params.get("substitute_pct", 0.25)
        },
        "seasonal_adjustments": {
            "Q1": params.get("seasonal_Q1", 0.85),
            "Q2": params.get("seasonal_Q2", 1.0),
            "Q3": params.get("seasonal_Q3", 1.05),
            "Q4": params.get("seasonal_Q4", 1.30)
        },
        "slow_moving_thresholds": {
            "days_no_movement": params.get("slow_moving_days_threshold", 90),
            "turns_below": params.get("slow_moving_turns_threshold", 2.0)
        },
        "dead_stock_threshold_days": params.get("dead_stock_threshold_days", 180)
    }


def calculate_turnover_ratio(
    cost_of_goods_sold: float,
    average_inventory: float
) -> Dict[str, Any]:
    """Calculate inventory turnover ratio."""
    if average_inventory <= 0:
        return {"turnover_ratio": 0, "days_inventory": 365, "error": "Invalid inventory value"}

    turnover_ratio = cost_of_goods_sold / average_inventory
    days_inventory = 365 / turnover_ratio if turnover_ratio > 0 else 365

    return {
        "turnover_ratio": round(turnover_ratio, 2),
        "days_inventory": round(days_inventory, 1),
        "cogs": cost_of_goods_sold,
        "average_inventory": average_inventory
    }


def benchmark_performance(
    turnover_ratio: float,
    industry: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Benchmark turnover against industry standards."""
    industry_benchmark = benchmarks.get(industry, benchmarks.get("default", {}))
    benchmark_ratio = industry_benchmark.get("turnover_ratio", 6.0)
    benchmark_days = industry_benchmark.get("days_inventory", 61)

    performance_ratio = turnover_ratio / benchmark_ratio if benchmark_ratio > 0 else 0

    if performance_ratio >= 1.25:
        rating = "EXCELLENT"
    elif performance_ratio >= 1.0:
        rating = "GOOD"
    elif performance_ratio >= 0.8:
        rating = "AVERAGE"
    elif performance_ratio >= 0.6:
        rating = "BELOW_AVERAGE"
    else:
        rating = "POOR"

    return {
        "industry": industry,
        "benchmark_turnover": benchmark_ratio,
        "benchmark_days": benchmark_days,
        "performance_ratio": round(performance_ratio, 2),
        "rating": rating,
        "gap_to_benchmark": round(turnover_ratio - benchmark_ratio, 2)
    }


def classify_abc(
    items: List[Dict]
) -> Dict[str, Any]:
    """Classify inventory items using ABC analysis."""
    # Sort by revenue contribution
    sorted_items = sorted(items, key=lambda x: x.get("revenue", 0), reverse=True)
    total_revenue = sum(item.get("revenue", 0) for item in sorted_items)

    classifications = {"A": [], "B": [], "C": []}
    cumulative_revenue = 0

    for item in sorted_items:
        revenue = item.get("revenue", 0)
        cumulative_revenue += revenue
        cumulative_pct = cumulative_revenue / total_revenue if total_revenue > 0 else 0

        if cumulative_pct <= 0.80:
            item["classification"] = "A"
            classifications["A"].append(item)
        elif cumulative_pct <= 0.95:
            item["classification"] = "B"
            classifications["B"].append(item)
        else:
            item["classification"] = "C"
            classifications["C"].append(item)

    return {
        "class_A": {
            "item_count": len(classifications["A"]),
            "revenue_pct": round(sum(i.get("revenue", 0) for i in classifications["A"]) / total_revenue * 100, 1) if total_revenue > 0 else 0
        },
        "class_B": {
            "item_count": len(classifications["B"]),
            "revenue_pct": round(sum(i.get("revenue", 0) for i in classifications["B"]) / total_revenue * 100, 1) if total_revenue > 0 else 0
        },
        "class_C": {
            "item_count": len(classifications["C"]),
            "revenue_pct": round(sum(i.get("revenue", 0) for i in classifications["C"]) / total_revenue * 100, 1) if total_revenue > 0 else 0
        },
        "classified_items": sorted_items[:20]  # Top 20 for sample
    }


def calculate_carrying_cost(
    average_inventory_value: float,
    cost_components: Dict
) -> Dict[str, Any]:
    """Calculate inventory carrying cost."""
    # Extract rates from CSV structure (each component is a dict with 'rate' key)
    rates = {k: v.get("rate", v) if isinstance(v, dict) else v
             for k, v in cost_components.items()}

    total_rate = sum(rates.values())
    total_carrying_cost = average_inventory_value * total_rate

    component_costs = {}
    for component, rate in rates.items():
        component_costs[component] = round(average_inventory_value * rate, 2)

    return {
        "average_inventory_value": average_inventory_value,
        "total_carrying_rate": round(total_rate * 100, 1),
        "annual_carrying_cost": round(total_carrying_cost, 2),
        "cost_breakdown": component_costs
    }


def identify_slow_moving(
    items: List[Dict],
    thresholds: Dict
) -> Dict[str, Any]:
    """Identify slow-moving and dead stock."""
    days_threshold = thresholds.get("days_no_movement", 90)
    turns_threshold = thresholds.get("turns_below", 2.0)
    dead_threshold = thresholds.get("dead_stock_threshold_days", 180)

    slow_moving = []
    dead_stock = []

    for item in items:
        days_since_sale = item.get("days_since_last_sale", 0)
        item_turns = item.get("turnover_ratio", 0)

        if days_since_sale >= dead_threshold:
            dead_stock.append({
                "sku": item.get("sku", ""),
                "days_since_sale": days_since_sale,
                "inventory_value": item.get("inventory_value", 0)
            })
        elif days_since_sale >= days_threshold or item_turns < turns_threshold:
            slow_moving.append({
                "sku": item.get("sku", ""),
                "days_since_sale": days_since_sale,
                "turnover_ratio": item_turns,
                "inventory_value": item.get("inventory_value", 0)
            })

    return {
        "slow_moving_items": slow_moving[:10],
        "slow_moving_count": len(slow_moving),
        "slow_moving_value": sum(i["inventory_value"] for i in slow_moving),
        "dead_stock_items": dead_stock[:10],
        "dead_stock_count": len(dead_stock),
        "dead_stock_value": sum(i["inventory_value"] for i in dead_stock)
    }


def calculate_stockout_cost(
    stockout_events: List[Dict],
    impact_rates: Dict
) -> Dict[str, Any]:
    """Calculate cost of stockouts."""
    total_lost_sales = 0
    total_events = len(stockout_events)

    for event in stockout_events:
        potential_revenue = event.get("potential_revenue", 0)
        lost_sale_pct = impact_rates.get("lost_sale_pct", 0.40)
        total_lost_sales += potential_revenue * lost_sale_pct

    return {
        "stockout_events": total_events,
        "estimated_lost_sales": round(total_lost_sales, 2),
        "lost_sale_rate": impact_rates.get("lost_sale_pct", 0.40)
    }


def apply_seasonal_adjustment(
    turnover_ratio: float,
    quarter: str,
    seasonal_factors: Dict
) -> Dict[str, Any]:
    """Apply seasonal adjustment to turnover."""
    adjustment_factor = seasonal_factors.get(quarter, 1.0)
    adjusted_ratio = turnover_ratio / adjustment_factor

    return {
        "raw_turnover": turnover_ratio,
        "quarter": quarter,
        "seasonal_factor": adjustment_factor,
        "seasonally_adjusted_turnover": round(adjusted_ratio, 2)
    }


def calculate_inventory_turnover(
    entity_id: str,
    cost_of_goods_sold: float,
    beginning_inventory: float,
    ending_inventory: float,
    inventory_items: List[Dict],
    stockout_events: List[Dict],
    industry: str,
    quarter: str,
    analysis_period: str
) -> Dict[str, Any]:
    """
    Calculate inventory turnover and related metrics.

    Business Rules:
    1. Turnover ratio calculation
    2. ABC inventory classification
    3. Carrying cost analysis
    4. Slow-moving stock identification

    Args:
        entity_id: Entity identifier
        cost_of_goods_sold: COGS for period
        beginning_inventory: Beginning inventory value
        ending_inventory: Ending inventory value
        inventory_items: Individual inventory items
        stockout_events: Stockout events during period
        industry: Industry classification
        quarter: Quarter for seasonal adjustment
        analysis_period: Analysis period description

    Returns:
        Inventory turnover analysis results
    """
    benchmarks = load_inventory_benchmarks()

    # Calculate average inventory
    average_inventory = (beginning_inventory + ending_inventory) / 2

    # Calculate turnover ratio
    turnover = calculate_turnover_ratio(cost_of_goods_sold, average_inventory)

    # Benchmark performance
    benchmark = benchmark_performance(
        turnover["turnover_ratio"],
        industry,
        benchmarks.get("industry_benchmarks", {})
    )

    # ABC classification
    abc_analysis = classify_abc(inventory_items)

    # Calculate carrying cost
    carrying_cost = calculate_carrying_cost(
        average_inventory,
        benchmarks.get("carrying_cost_components", {})
    )

    # Identify slow-moving inventory
    slow_moving = identify_slow_moving(
        inventory_items,
        benchmarks.get("slow_moving_thresholds", {})
    )

    # Calculate stockout cost
    stockout_cost = calculate_stockout_cost(
        stockout_events,
        benchmarks.get("stockout_impact", {})
    )

    # Seasonal adjustment
    seasonal = apply_seasonal_adjustment(
        turnover["turnover_ratio"],
        quarter,
        benchmarks.get("seasonal_adjustments", {})
    )

    return {
        "entity_id": entity_id,
        "analysis_period": analysis_period,
        "turnover_metrics": turnover,
        "benchmark_comparison": benchmark,
        "abc_classification": abc_analysis,
        "carrying_cost_analysis": carrying_cost,
        "slow_moving_analysis": slow_moving,
        "stockout_analysis": stockout_cost,
        "seasonal_adjustment": seasonal,
        "recommendations": generate_recommendations(
            benchmark["rating"],
            slow_moving,
            stockout_cost
        )
    }


def generate_recommendations(
    performance_rating: str,
    slow_moving: Dict,
    stockout: Dict
) -> List[str]:
    """Generate inventory management recommendations."""
    recommendations = []

    if performance_rating in ["POOR", "BELOW_AVERAGE"]:
        recommendations.append("Review and reduce excess inventory levels")
        recommendations.append("Implement demand forecasting improvements")

    if slow_moving["dead_stock_count"] > 0:
        recommendations.append(f"Liquidate {slow_moving['dead_stock_count']} dead stock items")

    if slow_moving["slow_moving_count"] > 10:
        recommendations.append("Implement promotional strategies for slow-moving items")

    if stockout["stockout_events"] > 5:
        recommendations.append("Review safety stock levels for high-velocity items")
        recommendations.append("Improve supplier lead time management")

    return recommendations


if __name__ == "__main__":
    import json
    result = calculate_inventory_turnover(
        entity_id="STORE-001",
        cost_of_goods_sold=5000000,
        beginning_inventory=400000,
        ending_inventory=450000,
        inventory_items=[
            {"sku": "SKU-001", "revenue": 100000, "inventory_value": 20000, "days_since_last_sale": 5, "turnover_ratio": 12},
            {"sku": "SKU-002", "revenue": 80000, "inventory_value": 15000, "days_since_last_sale": 10, "turnover_ratio": 10},
            {"sku": "SKU-003", "revenue": 5000, "inventory_value": 8000, "days_since_last_sale": 120, "turnover_ratio": 1.5}
        ],
        stockout_events=[
            {"sku": "SKU-001", "potential_revenue": 5000},
            {"sku": "SKU-002", "potential_revenue": 3000}
        ],
        industry="grocery",
        quarter="Q4",
        analysis_period="2025-Q4"
    )
    print(json.dumps(result, indent=2))
