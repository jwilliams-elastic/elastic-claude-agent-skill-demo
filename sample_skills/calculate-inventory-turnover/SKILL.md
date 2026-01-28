# Skill: Calculate Inventory Turnover

## Domain
retail

## Description
Calculates inventory turnover metrics and identifies slow-moving inventory for working capital optimization and markdown planning.

## Tags
inventory, turnover, retail, working-capital, supply-chain, merchandising

## Use Cases
- Inventory efficiency analysis
- Working capital optimization
- Slow-mover identification
- Markdown planning

## Proprietary Business Rules

### Rule 1: Turnover Calculation
Days of inventory and turns calculation by category.

### Rule 2: ABC Classification
Inventory classification by velocity and value.

### Rule 3: Aging Analysis
Inventory aging bucket classification.

### Rule 4: Markdown Trigger
Automatic markdown recommendation triggers.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `inventory_data` (list): Current inventory positions
- `sales_data` (list): Sales history
- `category_info` (dict): Category hierarchies
- `cost_data` (dict): Inventory cost information
- `analysis_period` (dict): Analysis time range

## Output
- `overall_turnover` (float): Overall inventory turns
- `category_turnover` (dict): Turnover by category
- `slow_movers` (list): Slow-moving inventory items
- `aging_analysis` (dict): Inventory aging breakdown
- `recommendations` (list): Optimization recommendations

## Implementation
The calculation logic is implemented in `turnover_calculator.py` and references data from CSV files:
- `industry_benchmarks.csv` - Industry-specific turnover benchmarks
- `performance_thresholds.csv` - Performance rating thresholds
- `abc_classification.csv` - ABC inventory classification parameters
- `carrying_costs.csv` - Inventory carrying cost components
- `parameters.csv` - Additional configuration parameters

## Usage Example
```python
from turnover_calculator import calculate_turnover

result = calculate_turnover(
    analysis_id="INV-001",
    inventory_data=[{"sku": "SKU-001", "units": 500, "cost": 10000}],
    sales_data=[{"sku": "SKU-001", "units_sold": 100, "period": "2025-12"}],
    category_info={"SKU-001": {"category": "apparel", "subcategory": "tops"}},
    cost_data={"avg_cost_method": "weighted_average"},
    analysis_period={"start": "2025-01-01", "end": "2025-12-31"}
)

print(f"Overall Turnover: {result['overall_turnover']} turns")
```

## Test Execution
```python
from turnover_calculator import calculate_turnover

result = calculate_turnover(
    analysis_id=input_data.get('analysis_id'),
    inventory_data=input_data.get('inventory_data', []),
    sales_data=input_data.get('sales_data', []),
    category_info=input_data.get('category_info', {}),
    cost_data=input_data.get('cost_data', {}),
    analysis_period=input_data.get('analysis_period', {})
)
```
