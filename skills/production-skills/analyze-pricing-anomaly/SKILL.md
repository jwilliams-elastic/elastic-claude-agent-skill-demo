# Skill: Analyze Pricing Anomaly

## Domain
retail

## Description
Analyzes pricing data to detect anomalies, competitive pricing gaps, and margin optimization opportunities using statistical methods.

## Tags
pricing, analytics, retail, anomaly-detection, margin, competitive

## Use Cases
- Price error detection
- Competitive price monitoring
- Margin analysis
- Promotional effectiveness

## Proprietary Business Rules

### Rule 1: Statistical Anomaly Detection
Z-score and IQR-based outlier identification.

### Rule 2: Competitive Gap Analysis
Price positioning versus competition.

### Rule 3: Margin Threshold Alerts
Margin below acceptable thresholds.

### Rule 4: Price Elasticity Impact
Estimated volume impact of pricing changes.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `pricing_data` (list): Product pricing records
- `historical_prices` (list): Historical price data
- `competitive_prices` (dict): Competitor pricing
- `cost_data` (dict): Product costs
- `sales_data` (list): Sales volume data

## Output
- `anomalies_detected` (list): Pricing anomalies
- `competitive_analysis` (dict): Competitive positioning
- `margin_alerts` (list): Margin concerns
- `optimization_opportunities` (list): Pricing recommendations
- `summary_statistics` (dict): Analysis summary

## Implementation
The analysis logic is implemented in `pricing_analyzer.py` and references data from CSV files:
- `anomaly_detection_thresholds.csv` - Reference data
- `statistical_parameters.csv` - Reference data
- `anomaly_categories.csv` - Reference data
- `product_category_rules.csv` - Reference data
- `customer_segment_pricing.csv` - Reference data
- `approval_thresholds.csv` - Reference data
- `time_based_patterns.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from pricing_analyzer import analyze_pricing

result = analyze_pricing(
    analysis_id="PRC-001",
    pricing_data=[{"sku": "SKU-001", "price": 29.99, "list_price": 34.99}],
    historical_prices=[{"sku": "SKU-001", "date": "2025-11-01", "price": 24.99}],
    competitive_prices={"SKU-001": {"competitor_a": 27.99, "competitor_b": 31.99}},
    cost_data={"SKU-001": {"unit_cost": 15.00}},
    sales_data=[{"sku": "SKU-001", "units": 500, "period": "2025-12"}]
)

print(f"Anomalies Found: {len(result['anomalies_detected'])}")
```

## Test Execution
```python
from pricing_analyzer import analyze_pricing

result = analyze_pricing(
    analysis_id=input_data.get('analysis_id'),
    pricing_data=input_data.get('pricing_data', []),
    historical_prices=input_data.get('historical_prices', []),
    competitive_prices=input_data.get('competitive_prices', {}),
    cost_data=input_data.get('cost_data', {}),
    sales_data=input_data.get('sales_data', [])
)
```
