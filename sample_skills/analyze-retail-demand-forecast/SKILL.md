# Skill: Analyze Retail Demand Forecast

## Domain
retail

## Description
Analyzes retail demand patterns and generates inventory recommendations using statistical forecasting methods. Incorporates seasonality, promotional effects, price elasticity, and external factors to optimize stock levels while minimizing both stockouts and overstock situations.

## Business Rules
This skill implements retail demand forecasting with inventory optimization:

1. **Seasonality Detection**: Automatic detection of weekly, monthly, and annual seasonality patterns
2. **Promotional Lift Factors**: Category-specific lift multipliers (Grocery: 2.5x, Apparel: 3.5x, Electronics: 4.0x)
3. **Safety Stock Formula**: Safety stock = Z-score × √(lead_time) × demand_std_dev (Z=1.65 for 95% service level)
4. **Reorder Point**: ROP = (avg_daily_demand × lead_time_days) + safety_stock
5. **Price Elasticity Adjustment**: Demand_adjusted = base_demand × (1 + elasticity × price_change_pct)
6. **Cannibalization Factor**: New product introductions reduce existing SKU demand by 10-30% in same category

## Input Parameters
- `sku_id` (string): Product SKU identifier
- `category` (string): Product category (e.g., "grocery", "apparel", "electronics", "home")
- `historical_sales` (list): Last 52 weeks of sales units [week1, week2, ...]
- `current_price` (float): Current selling price ($)
- `planned_price` (float, optional): Planned price for forecast period
- `promotion_planned` (bool): Whether promotion is planned in forecast period
- `promotion_type` (string, optional): "bogo", "percentage_off", "bundle", "clearance"
- `lead_time_days` (int): Supplier lead time in days
- `current_inventory` (int): Current stock on hand
- `service_level_target` (float): Target service level (0.90-0.99)
- `new_product_in_category` (bool): Whether new competing product launching
- `forecast_weeks` (int): Number of weeks to forecast (1-12)

## Output
Returns a demand forecast with inventory recommendations:
- `forecast_demand` (list): Predicted demand by week
- `forecast_confidence` (float): Model confidence score (0-1)
- `seasonality_detected` (dict): Detected seasonal patterns
- `recommended_order_quantity` (int): Suggested order quantity
- `reorder_point` (int): Inventory level triggering reorder
- `safety_stock` (int): Recommended safety stock units
- `stockout_risk` (string): "low", "medium", "high"
- `overstock_risk` (string): "low", "medium", "high"
- `expected_sell_through_rate` (float): Predicted sell-through percentage
- `revenue_forecast` (float): Projected revenue for forecast period
- `optimization_actions` (list): Recommended inventory actions

## Usage Example
```python
from demand_forecast import analyze_demand

result = analyze_demand(
    sku_id="SKU-12345",
    category="apparel",
    historical_sales=[120, 115, 130, 125, ...],  # 52 weeks
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
```

## Tags
retail, demand-forecasting, inventory, supply-chain, analytics, merchandising, optimization

## Implementation
The forecasting logic is implemented in `demand_forecast.py` and references:
- `promotional_lift.csv` - Lift factors by category and promotion type
- `seasonality_indices.csv` - Seasonal adjustment factors
- `elasticity_coefficients.csv` - Price elasticity by category
- `service_level_factors.csv` - Z-scores for service level targets
