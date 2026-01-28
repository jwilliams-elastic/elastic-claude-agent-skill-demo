# Skill: Optimize Retail Inventory

## Domain
retail

## Description
Analyzes sales patterns, stock levels, and demand forecasts to optimize inventory allocation and replenishment across retail locations.

## Tags
retail, inventory-management, demand-forecasting, supply-chain, stock-optimization

## Use Cases
- Inventory replenishment planning
- Stock allocation optimization
- Markdown timing decisions
- Safety stock calculation

## Proprietary Business Rules

### Rule 1: Demand Forecasting
Proprietary demand model using historical sales, seasonality, and promotional calendars.

### Rule 2: Safety Stock Calculation
Dynamic safety stock based on demand variability and service level targets.

### Rule 3: Store Clustering
Allocation adjustments based on store performance clusters.

### Rule 4: Markdown Optimization
Optimal markdown timing based on sell-through velocity.

## Input Parameters
- `sku` (string): Product SKU
- `store_id` (string): Store identifier
- `current_stock` (int): Current inventory on hand
- `sales_history` (list): Historical daily sales
- `lead_time_days` (int): Supplier lead time
- `service_level` (float): Target service level (0-1)
- `promotion_planned` (bool): Upcoming promotion flag
- `season` (string): Current season

## Output
- `reorder_recommendation` (dict): Quantity and timing
- `safety_stock` (int): Recommended safety stock
- `stockout_risk` (float): Probability of stockout
- `days_of_supply` (int): Current days of supply
- `markdown_recommendation` (dict): Markdown timing if applicable

## Implementation
The optimization logic is implemented in `inventory_optimizer.py` and references parameters from CSV files:
- `seasonality_factors.csv` - Reference data
- `z_scores.csv` - Reference data
- `store_clusters.csv` - Reference data
- `markdown_rules.csv` - Reference data
- `replenishment_rules.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from inventory_optimizer import optimize_inventory

result = optimize_inventory(
    sku="SKU-12345",
    store_id="STORE-001",
    current_stock=150,
    sales_history=[12, 15, 10, 18, 14, 16, 11],
    lead_time_days=7,
    service_level=0.95,
    promotion_planned=True,
    season="spring"
)

print(f"Reorder: {result['reorder_recommendation']}")
```

## Test Execution
```python
from inventory_optimizer import optimize_inventory

result = optimize_inventory(
    sku=input_data.get('sku'),
    store_id=input_data.get('store_id'),
    current_stock=input_data.get('current_stock', 0),
    sales_history=input_data.get('sales_history', []),
    lead_time_days=input_data.get('lead_time_days', 7),
    service_level=input_data.get('service_level', 0.95),
    promotion_planned=input_data.get('promotion_planned', False),
    season=input_data.get('season', 'base')
)
```
