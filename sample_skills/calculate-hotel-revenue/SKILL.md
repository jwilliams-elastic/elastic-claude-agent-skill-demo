# Skill: Calculate Hotel Revenue Management

## Domain
travel_leisure

## Description
Optimizes hotel room pricing and inventory allocation using demand forecasting, competitive positioning, and revenue management algorithms.

## Tags
hospitality, revenue-management, pricing, demand-forecasting, travel

## Use Cases
- Dynamic pricing optimization
- Demand forecasting
- Inventory allocation by channel
- Competitive rate analysis

## Proprietary Business Rules

### Rule 1: Demand Forecasting
Historical booking patterns with day-of-week and seasonal adjustments.

### Rule 2: Price Elasticity
Room type and segment-specific price sensitivity curves.

### Rule 3: Minimum Length of Stay
MLOS rules based on demand intensity periods.

### Rule 4: Channel Mix Optimization
Rate parity and channel allocation strategies.

## Input Parameters
- `property_id` (string): Hotel property identifier
- `room_type` (string): Room category
- `stay_date` (string): Date for pricing
- `current_occupancy` (float): Current booking level
- `competitor_rates` (list): Competitive rate data
- `days_out` (int): Days until stay date
- `demand_indicators` (dict): Events, seasonality flags
- `channel` (string): Distribution channel

## Output
- `recommended_rate` (float): Optimal room rate
- `rate_range` (dict): Min/max rate bounds
- `occupancy_forecast` (float): Expected occupancy
- `revenue_forecast` (float): Expected revenue
- `pricing_strategy` (string): Strategy recommendation

## Implementation
The revenue logic is implemented in `revenue_manager.py` and references demand curves from CSV files:
- `room_types.csv` - Reference data
- `channels.csv` - Reference data
- `booking_curves.csv` - Reference data
- `seasonality.csv` - Reference data
- `strategies.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from revenue_manager import calculate_revenue

result = calculate_revenue(
    property_id="HOTEL-001",
    room_type="standard_king",
    stay_date="2026-02-14",
    current_occupancy=0.45,
    competitor_rates=[189, 199, 175, 209],
    days_out=21,
    demand_indicators={"special_event": True, "season": "high"},
    channel="direct"
)

print(f"Recommended Rate: ${result['recommended_rate']}")
```

## Test Execution
```python
from revenue_manager import calculate_revenue

result = calculate_revenue(
    property_id=input_data.get('property_id'),
    room_type=input_data.get('room_type'),
    stay_date=input_data.get('stay_date'),
    current_occupancy=input_data.get('current_occupancy', 0),
    competitor_rates=input_data.get('competitor_rates', []),
    days_out=input_data.get('days_out', 30),
    demand_indicators=input_data.get('demand_indicators', {}),
    channel=input_data.get('channel', 'ota')
)
```
