"""
Retail Demand Forecasting Module

Analyzes retail demand patterns and generates inventory recommendations
using statistical forecasting methods with seasonality, promotional effects,
and price elasticity adjustments.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
import math


def load_csv_as_dict(filename: str, key_column: str) -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column, row.get('id', ''))
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


def get_promotional_lift(category: str, promotion_type: Optional[str]) -> float:
    """Get promotional lift factor by category and promotion type."""
    lift_factors = {
        "grocery": {"bogo": 3.0, "percentage_off": 2.5, "bundle": 2.0, "clearance": 3.5},
        "apparel": {"bogo": 4.0, "percentage_off": 3.5, "bundle": 2.5, "clearance": 4.5},
        "electronics": {"bogo": 4.5, "percentage_off": 4.0, "bundle": 3.0, "clearance": 5.0},
        "home": {"bogo": 3.5, "percentage_off": 3.0, "bundle": 2.5, "clearance": 4.0}
    }

    if not promotion_type:
        return 1.0

    category_lifts = lift_factors.get(category, lift_factors["grocery"])
    return category_lifts.get(promotion_type, 2.0)


def get_price_elasticity(category: str) -> float:
    """Get price elasticity coefficient by category."""
    elasticities = {
        "grocery": -1.2,
        "apparel": -2.0,
        "electronics": -2.5,
        "home": -1.8
    }
    return elasticities.get(category, -1.5)


def get_z_score(service_level: float) -> float:
    """Get Z-score for service level target."""
    z_scores = {
        0.90: 1.28,
        0.91: 1.34,
        0.92: 1.41,
        0.93: 1.48,
        0.94: 1.55,
        0.95: 1.65,
        0.96: 1.75,
        0.97: 1.88,
        0.98: 2.05,
        0.99: 2.33
    }
    # Find closest service level
    closest = min(z_scores.keys(), key=lambda x: abs(x - service_level))
    return z_scores[closest]


def detect_seasonality(historical_sales: List[float]) -> Dict[str, Any]:
    """Detect seasonality patterns in historical sales data."""
    if len(historical_sales) < 52:
        return {"detected": False, "patterns": []}

    # Calculate weekly averages
    avg_demand = sum(historical_sales) / len(historical_sales)

    # Detect weekly patterns (by week of year)
    seasonal_indices = []
    for i in range(52):
        if i < len(historical_sales):
            index = historical_sales[i] / avg_demand if avg_demand > 0 else 1.0
            seasonal_indices.append(round(index, 2))
        else:
            seasonal_indices.append(1.0)

    # Find peak and trough periods
    max_idx = seasonal_indices.index(max(seasonal_indices))
    min_idx = seasonal_indices.index(min(seasonal_indices))

    patterns = []
    if max(seasonal_indices) > 1.3:
        patterns.append(f"Peak season around week {max_idx + 1}")
    if min(seasonal_indices) < 0.7:
        patterns.append(f"Low season around week {min_idx + 1}")

    # Check for holiday patterns (weeks 47-52)
    holiday_avg = sum(seasonal_indices[46:52]) / 6 if len(seasonal_indices) >= 52 else 1.0
    if holiday_avg > 1.2:
        patterns.append("Holiday season lift detected")

    return {
        "detected": len(patterns) > 0,
        "patterns": patterns,
        "seasonal_indices": seasonal_indices[:12],  # Return first 12 weeks
        "peak_week": max_idx + 1,
        "trough_week": min_idx + 1,
        "seasonality_strength": round(max(seasonal_indices) - min(seasonal_indices), 2)
    }


def calculate_demand_statistics(historical_sales: List[float]) -> Dict[str, float]:
    """Calculate demand statistics from historical data."""
    n = len(historical_sales)
    if n == 0:
        return {"mean": 0, "std_dev": 0, "cv": 0}

    mean = sum(historical_sales) / n
    variance = sum((x - mean) ** 2 for x in historical_sales) / n
    std_dev = math.sqrt(variance)
    cv = std_dev / mean if mean > 0 else 0

    return {
        "mean": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "cv": round(cv, 2)
    }


def forecast_demand(
    historical_sales: List[float],
    forecast_weeks: int,
    seasonality: Dict[str, Any],
    price_adjustment: float,
    promotion_lift: float,
    cannibalization_factor: float
) -> List[float]:
    """Generate demand forecast."""
    stats = calculate_demand_statistics(historical_sales)
    base_demand = stats["mean"]

    forecasts = []
    for week in range(forecast_weeks):
        # Apply seasonality if detected
        if seasonality["detected"] and len(seasonality.get("seasonal_indices", [])) > week:
            seasonal_factor = seasonality["seasonal_indices"][week]
        else:
            seasonal_factor = 1.0

        # Calculate forecast
        forecast = base_demand * seasonal_factor * price_adjustment * promotion_lift * (1 - cannibalization_factor)
        forecasts.append(round(max(0, forecast), 0))

    return forecasts


def calculate_safety_stock(
    demand_std_dev: float,
    lead_time_days: int,
    service_level: float
) -> int:
    """Calculate safety stock using statistical method."""
    z_score = get_z_score(service_level)
    lead_time_weeks = lead_time_days / 7
    safety_stock = z_score * math.sqrt(lead_time_weeks) * demand_std_dev
    return int(math.ceil(safety_stock))


def calculate_reorder_point(
    avg_daily_demand: float,
    lead_time_days: int,
    safety_stock: int
) -> int:
    """Calculate reorder point."""
    return int(math.ceil(avg_daily_demand * lead_time_days + safety_stock))


def assess_inventory_risk(
    current_inventory: int,
    forecast_demand: List[float],
    lead_time_days: int,
    reorder_point: int
) -> Dict[str, str]:
    """Assess stockout and overstock risks."""
    total_forecast = sum(forecast_demand)
    avg_weekly_demand = total_forecast / len(forecast_demand) if forecast_demand else 0

    # Weeks of supply
    weeks_of_supply = current_inventory / avg_weekly_demand if avg_weekly_demand > 0 else 999

    # Stockout risk
    if current_inventory < reorder_point:
        stockout_risk = "high"
    elif weeks_of_supply < 2:
        stockout_risk = "medium"
    else:
        stockout_risk = "low"

    # Overstock risk
    if weeks_of_supply > 12:
        overstock_risk = "high"
    elif weeks_of_supply > 8:
        overstock_risk = "medium"
    else:
        overstock_risk = "low"

    return {
        "stockout_risk": stockout_risk,
        "overstock_risk": overstock_risk,
        "weeks_of_supply": round(weeks_of_supply, 1)
    }


def generate_optimization_actions(
    stockout_risk: str,
    overstock_risk: str,
    promotion_planned: bool,
    current_inventory: int,
    recommended_order: int
) -> List[str]:
    """Generate inventory optimization recommendations."""
    actions = []

    if stockout_risk == "high":
        actions.append("URGENT: Place expedited order to prevent stockout")
    elif stockout_risk == "medium":
        actions.append("Place replenishment order within 5 business days")

    if overstock_risk == "high":
        actions.append("Consider markdown or promotional activity to reduce excess inventory")
        actions.append("Evaluate return-to-vendor options for slow-moving stock")

    if promotion_planned and stockout_risk != "low":
        actions.append("Increase order quantity to support promotional demand lift")

    if recommended_order > 0:
        actions.append(f"Recommended order quantity: {recommended_order} units")

    if not actions:
        actions.append("Inventory levels optimal - maintain current replenishment cadence")

    return actions


def analyze_demand(
    sku_id: str,
    category: str,
    historical_sales: List[float],
    current_price: float,
    planned_price: Optional[float],
    promotion_planned: bool,
    promotion_type: Optional[str],
    lead_time_days: int,
    current_inventory: int,
    service_level_target: float,
    new_product_in_category: bool,
    forecast_weeks: int
) -> Dict[str, Any]:
    """
    Analyze retail demand and generate inventory recommendations.

    Returns comprehensive forecast with inventory optimization guidance.
    """
    # Validate inputs
    if len(historical_sales) < 4:
        return {
            "error": "Insufficient historical data - minimum 4 weeks required",
            "sku_id": sku_id
        }

    # Calculate demand statistics
    stats = calculate_demand_statistics(historical_sales)

    # Detect seasonality
    seasonality = detect_seasonality(historical_sales)

    # Calculate price adjustment
    if planned_price and planned_price != current_price:
        elasticity = get_price_elasticity(category)
        price_change_pct = (planned_price - current_price) / current_price
        price_adjustment = 1 + (elasticity * price_change_pct)
    else:
        price_adjustment = 1.0

    # Get promotional lift
    promotion_lift = get_promotional_lift(category, promotion_type) if promotion_planned else 1.0

    # Calculate cannibalization factor
    cannibalization_factor = 0.15 if new_product_in_category else 0.0

    # Generate forecast
    forecast = forecast_demand(
        historical_sales,
        forecast_weeks,
        seasonality,
        price_adjustment,
        promotion_lift,
        cannibalization_factor
    )

    # Calculate safety stock
    safety_stock = calculate_safety_stock(
        stats["std_dev"],
        lead_time_days,
        service_level_target
    )

    # Calculate reorder point
    avg_daily_demand = stats["mean"] / 7
    reorder_point = calculate_reorder_point(avg_daily_demand, lead_time_days, safety_stock)

    # Calculate recommended order quantity
    total_forecast_demand = sum(forecast)
    recommended_order = max(0, int(total_forecast_demand + safety_stock - current_inventory))

    # Assess inventory risks
    risks = assess_inventory_risk(current_inventory, forecast, lead_time_days, reorder_point)

    # Calculate sell-through rate
    if current_inventory + recommended_order > 0:
        expected_sell_through = total_forecast_demand / (current_inventory + recommended_order)
    else:
        expected_sell_through = 0

    # Calculate revenue forecast
    selling_price = planned_price if planned_price else current_price
    revenue_forecast = total_forecast_demand * selling_price

    # Generate optimization actions
    actions = generate_optimization_actions(
        risks["stockout_risk"],
        risks["overstock_risk"],
        promotion_planned,
        current_inventory,
        recommended_order
    )

    # Calculate forecast confidence
    if stats["cv"] < 0.3:
        confidence = 0.85
    elif stats["cv"] < 0.5:
        confidence = 0.70
    else:
        confidence = 0.55

    return {
        "sku_id": sku_id,
        "category": category,
        "forecast_demand": forecast,
        "forecast_confidence": confidence,
        "seasonality_detected": seasonality,
        "recommended_order_quantity": recommended_order,
        "reorder_point": reorder_point,
        "safety_stock": safety_stock,
        "stockout_risk": risks["stockout_risk"],
        "overstock_risk": risks["overstock_risk"],
        "weeks_of_supply": risks["weeks_of_supply"],
        "expected_sell_through_rate": round(expected_sell_through, 2),
        "revenue_forecast": round(revenue_forecast, 2),
        "optimization_actions": actions,
        "demand_statistics": stats,
        "adjustments_applied": {
            "price_adjustment": round(price_adjustment, 2),
            "promotional_lift": promotion_lift,
            "cannibalization_factor": cannibalization_factor
        }
    }


def main():
    """Example usage."""
    # Sample 52 weeks of historical sales
    historical = [120, 115, 130, 125, 140, 135, 128, 145, 150, 142, 138, 155,
                  160, 148, 165, 170, 158, 175, 180, 172, 168, 185, 190, 182,
                  178, 195, 200, 192, 188, 205, 210, 202, 198, 215, 220, 212,
                  208, 225, 230, 222, 218, 235, 240, 232, 228, 245, 250, 242,
                  238, 255, 260, 252]

    result = analyze_demand(
        sku_id="SKU-12345",
        category="apparel",
        historical_sales=historical,
        current_price=49.99,
        planned_price=39.99,
        promotion_planned=True,
        promotion_type="percentage_off",
        lead_time_days=14,
        current_inventory=450,
        service_level_target=0.95,
        new_product_in_category=False,
        forecast_weeks=8
    )

    print(f"SKU: {result['sku_id']}")
    print(f"Forecast Demand: {result['forecast_demand']}")
    print(f"Recommended Order: {result['recommended_order_quantity']}")
    print(f"Stockout Risk: {result['stockout_risk']}")
    print(f"Revenue Forecast: ${result['revenue_forecast']:,.2f}")


if __name__ == "__main__":
    main()
