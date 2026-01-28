"""
Retail Inventory Optimization Module

Implements demand forecasting and inventory optimization algorithms
for retail stock management.
"""

import csv
import math
import statistics
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


def load_inventory_params() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    seasonality_factors_data = load_key_value_csv("seasonality_factors.csv")
    z_scores_data = load_key_value_csv("z_scores.csv")
    store_clusters_data = load_csv_as_dict("store_clusters.csv")
    markdown_rules_data = load_key_value_csv("markdown_rules.csv")
    replenishment_rules_data = load_key_value_csv("replenishment_rules.csv")
    params = load_parameters()
    return {
        "seasonality_factors": seasonality_factors_data,
        "z_scores": z_scores_data,
        "store_clusters": store_clusters_data,
        "markdown_rules": markdown_rules_data,
        "replenishment_rules": replenishment_rules_data,
        **params
    }


def calculate_demand_forecast(
    sales_history: List[int],
    seasonality_factor: float,
    promo_lift: float
) -> Dict[str, float]:
    """Calculate demand forecast."""
    if not sales_history:
        return {"daily_forecast": 0, "std_dev": 0}

    # Simple moving average with adjustments
    avg_daily = statistics.mean(sales_history)
    std_dev = statistics.stdev(sales_history) if len(sales_history) > 1 else 0

    # Apply seasonality and promo
    forecast = avg_daily * seasonality_factor * promo_lift

    return {
        "daily_forecast": forecast,
        "std_dev": std_dev,
        "base_demand": avg_daily,
        "seasonality_adjusted": avg_daily * seasonality_factor
    }


def calculate_safety_stock(
    std_dev: float,
    lead_time: int,
    service_level: float,
    z_scores: Dict
) -> int:
    """Calculate safety stock based on demand variability."""
    # Get z-score for service level
    z = z_scores.get(str(service_level), 1.65)

    # Safety stock formula: z * std_dev * sqrt(lead_time)
    safety_stock = z * std_dev * math.sqrt(lead_time)

    return max(0, int(math.ceil(safety_stock)))


def calculate_reorder_point(
    daily_forecast: float,
    lead_time: int,
    safety_stock: int
) -> int:
    """Calculate reorder point."""
    return int(math.ceil(daily_forecast * lead_time + safety_stock))


def calculate_economic_order_qty(
    annual_demand: float,
    ordering_cost: float,
    holding_cost_pct: float,
    unit_cost: float
) -> int:
    """Calculate economic order quantity."""
    if annual_demand <= 0 or unit_cost <= 0:
        return 0

    holding_cost = unit_cost * holding_cost_pct

    # EOQ formula: sqrt(2 * D * S / H)
    eoq = math.sqrt(2 * annual_demand * ordering_cost / holding_cost)

    return max(1, int(round(eoq)))


def assess_stockout_risk(
    current_stock: int,
    daily_forecast: float,
    lead_time: int,
    std_dev: float
) -> float:
    """Assess probability of stockout during lead time."""
    if current_stock <= 0:
        return 1.0

    if daily_forecast <= 0:
        return 0.0

    # Demand during lead time
    expected_demand = daily_forecast * lead_time
    demand_std = std_dev * math.sqrt(lead_time)

    if demand_std <= 0:
        return 0.0 if current_stock >= expected_demand else 1.0

    # Z-score for current stock
    z = (current_stock - expected_demand) / demand_std

    # Approximate probability using normal distribution
    # Using simple approximation
    if z >= 3:
        return 0.001
    elif z >= 2:
        return 0.02
    elif z >= 1:
        return 0.16
    elif z >= 0:
        return 0.50
    elif z >= -1:
        return 0.84
    else:
        return 0.95


def evaluate_markdown_need(
    current_stock: int,
    daily_forecast: float,
    weeks_remaining: int,
    sell_through_target: float
) -> Dict[str, Any]:
    """Evaluate if markdown is needed."""
    if daily_forecast <= 0:
        return {"markdown_needed": False, "reason": "No demand data"}

    days_remaining = weeks_remaining * 7
    projected_sales = daily_forecast * days_remaining

    current_sell_through = projected_sales / current_stock if current_stock > 0 else 0

    if current_sell_through < sell_through_target:
        weeks_to_clear = current_stock / (daily_forecast * 7) if daily_forecast > 0 else float('inf')

        return {
            "markdown_needed": True,
            "projected_sell_through": round(current_sell_through, 2),
            "target_sell_through": sell_through_target,
            "weeks_to_clear_current": round(weeks_to_clear, 1),
            "recommended_action": "Consider 20-30% markdown to accelerate sell-through"
        }

    return {
        "markdown_needed": False,
        "projected_sell_through": round(current_sell_through, 2),
        "target_sell_through": sell_through_target
    }


def optimize_inventory(
    sku: str,
    store_id: str,
    current_stock: int,
    sales_history: List[int],
    lead_time_days: int,
    service_level: float,
    promotion_planned: bool,
    season: str
) -> Dict[str, Any]:
    """
    Optimize retail inventory levels.

    Business Rules:
    1. Demand forecasting with seasonality
    2. Dynamic safety stock calculation
    3. Store cluster adjustments
    4. Markdown timing optimization

    Args:
        sku: Product SKU
        store_id: Store identifier
        current_stock: Current inventory
        sales_history: Daily sales history
        lead_time_days: Supplier lead time
        service_level: Target service level
        promotion_planned: Promotion flag
        season: Current season

    Returns:
        Inventory optimization recommendations
    """
    params = load_inventory_params()

    # Get seasonality factor
    seasonality = params["seasonality_factors"].get(season, 1.0)

    # Get promotion lift
    promo_lift = params["promotion_lift"] if promotion_planned else 1.0

    # Forecast demand
    forecast = calculate_demand_forecast(sales_history, seasonality, promo_lift)

    # Calculate safety stock
    safety_stock = calculate_safety_stock(
        forecast["std_dev"],
        lead_time_days,
        service_level,
        params["z_scores"]
    )

    # Calculate reorder point
    reorder_point = calculate_reorder_point(
        forecast["daily_forecast"],
        lead_time_days,
        safety_stock
    )

    # Calculate days of supply
    days_of_supply = int(current_stock / forecast["daily_forecast"]) if forecast["daily_forecast"] > 0 else 999

    # Assess stockout risk
    stockout_risk = assess_stockout_risk(
        current_stock,
        forecast["daily_forecast"],
        lead_time_days,
        forecast["std_dev"]
    )

    # Calculate order quantity
    annual_demand = forecast["daily_forecast"] * 365
    order_qty = calculate_economic_order_qty(
        annual_demand,
        params["ordering_cost"],
        params["holding_cost_pct"],
        params["avg_unit_cost"]
    )

    # Determine reorder recommendation
    if current_stock <= reorder_point:
        reorder_recommendation = {
            "action": "ORDER_NOW",
            "quantity": order_qty,
            "urgency": "high" if stockout_risk > 0.5 else "medium"
        }
    elif current_stock <= reorder_point * 1.2:
        reorder_recommendation = {
            "action": "PREPARE_ORDER",
            "quantity": order_qty,
            "urgency": "low"
        }
    else:
        reorder_recommendation = {
            "action": "NO_ACTION",
            "next_review_days": max(1, int(days_of_supply - lead_time_days - 7))
        }

    # Evaluate markdown need
    markdown_recommendation = evaluate_markdown_need(
        current_stock,
        forecast["daily_forecast"],
        params["weeks_in_season"],
        params["sell_through_target"]
    )

    return {
        "sku": sku,
        "store_id": store_id,
        "current_stock": current_stock,
        "reorder_recommendation": reorder_recommendation,
        "safety_stock": safety_stock,
        "reorder_point": reorder_point,
        "stockout_risk": round(stockout_risk, 3),
        "days_of_supply": days_of_supply,
        "demand_forecast": {
            "daily": round(forecast["daily_forecast"], 1),
            "weekly": round(forecast["daily_forecast"] * 7, 1),
            "monthly": round(forecast["daily_forecast"] * 30, 1)
        },
        "markdown_recommendation": markdown_recommendation,
        "seasonality_factor": seasonality,
        "promotion_planned": promotion_planned
    }


if __name__ == "__main__":
    import json
    result = optimize_inventory(
        sku="SKU-12345",
        store_id="STORE-001",
        current_stock=150,
        sales_history=[12, 15, 10, 18, 14, 16, 11, 13, 17, 15, 12, 14],
        lead_time_days=7,
        service_level=0.95,
        promotion_planned=True,
        season="spring"
    )
    print(json.dumps(result, indent=2))
