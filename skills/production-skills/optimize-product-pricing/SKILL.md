# Skill: Optimize Product Pricing

## Domain
consumer_products

## Description
Calculates optimal product pricing using demand elasticity models, competitive positioning analysis, and margin optimization algorithms specific to consumer product categories.

## Tags
consumer-products, pricing-strategy, revenue-optimization, demand-modeling, margin-analysis

## Use Cases
- New product price setting
- Promotional pricing optimization
- Competitive price response
- Channel-specific pricing

## Proprietary Business Rules

### Rule 1: Price Elasticity Application
Category-specific elasticity curves determine price-demand relationships for optimal revenue calculation.

### Rule 2: Competitive Position Bands
Price positioning relative to competitors based on brand tier and product attributes.

### Rule 3: Channel Margin Requirements
Different margin requirements for retail, e-commerce, and wholesale channels.

### Rule 4: Promotional Lift Modeling
Price reduction impact on volume with diminishing returns above threshold discounts.

## Input Parameters
- `product_id` (string): Product identifier
- `product_category` (string): Product category
- `base_cost` (float): Product unit cost
- `competitor_prices` (list): Competitor price points
- `brand_tier` (string): Premium, mainstream, value
- `sales_channel` (string): Retail, ecommerce, wholesale
- `current_price` (float): Current selling price
- `target_margin` (float): Target profit margin percentage

## Output
- `optimal_price` (float): Recommended price point
- `expected_margin` (float): Expected profit margin
- `price_band` (dict): Min/max price range
- `elasticity_impact` (dict): Volume impact projections
- `competitive_position` (string): Position vs competitors

## Implementation
The pricing logic is implemented in `pricing_optimizer.py` and references elasticity data from CSV files:
- `categories.csv` - Reference data
- `brand_tiers.csv` - Reference data
- `channels.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from pricing_optimizer import optimize_pricing

result = optimize_pricing(
    product_id="SKU-12345",
    product_category="personal_care",
    base_cost=4.50,
    competitor_prices=[8.99, 9.49, 7.99],
    brand_tier="mainstream",
    sales_channel="retail",
    current_price=8.99,
    target_margin=0.40
)

print(f"Optimal Price: ${result['optimal_price']}")
```

## Test Execution
```python
from pricing_optimizer import optimize_pricing

result = optimize_pricing(
    product_id=input_data.get('product_id'),
    product_category=input_data.get('product_category'),
    base_cost=input_data.get('base_cost'),
    competitor_prices=input_data.get('competitor_prices', []),
    brand_tier=input_data.get('brand_tier', 'mainstream'),
    sales_channel=input_data.get('sales_channel', 'retail'),
    current_price=input_data.get('current_price'),
    target_margin=input_data.get('target_margin', 0.30)
)
```
