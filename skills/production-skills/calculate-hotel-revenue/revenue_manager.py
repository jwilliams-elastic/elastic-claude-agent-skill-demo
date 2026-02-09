"""
Hotel Revenue Management Module

Implements demand forecasting and dynamic pricing algorithms
for hospitality revenue optimization.
"""

import csv
import statistics
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime



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


def load_demand_curves() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    room_types_data = load_csv_as_dict("room_types.csv")
    channels_data = load_csv_as_dict("channels.csv")
    booking_curves_data = load_key_value_csv("booking_curves.csv")
    seasonality_data = load_csv_as_dict("seasonality.csv")
    strategies_data = load_csv_as_dict("strategies.csv")
    params = load_parameters()
    return {
        "room_types": room_types_data,
        "channels": channels_data,
        "booking_curves": booking_curves_data,
        "seasonality": seasonality_data,
        "strategies": strategies_data,
        **params
    }


def get_day_of_week_factor(stay_date: str) -> float:
    """Get demand factor based on day of week."""
    date = datetime.strptime(stay_date, "%Y-%m-%d")
    day = date.weekday()

    # Weekend premium
    dow_factors = {
        0: 0.85,  # Monday
        1: 0.80,  # Tuesday
        2: 0.85,  # Wednesday
        3: 0.90,  # Thursday
        4: 1.10,  # Friday
        5: 1.20,  # Saturday
        6: 0.95   # Sunday
    }

    return dow_factors.get(day, 1.0)


def calculate_demand_forecast(
    current_occupancy: float,
    days_out: int,
    demand_indicators: Dict,
    booking_curve: Dict
) -> Dict[str, float]:
    """Forecast demand based on booking patterns."""
    # Get expected pickup from booking curve
    days_bucket = str(min(days_out, 90))
    if days_out <= 7:
        days_bucket = "7"
    elif days_out <= 14:
        days_bucket = "14"
    elif days_out <= 30:
        days_bucket = "30"
    elif days_out <= 60:
        days_bucket = "60"
    else:
        days_bucket = "90"

    expected_pickup = booking_curve.get(days_bucket, 0.3)

    # Base forecast
    base_forecast = current_occupancy + (1 - current_occupancy) * expected_pickup

    # Season adjustment
    season = demand_indicators.get("season", "shoulder")
    season_factors = {"high": 1.15, "shoulder": 1.0, "low": 0.85}
    season_factor = season_factors.get(season, 1.0)

    # Event adjustment
    event_factor = 1.2 if demand_indicators.get("special_event") else 1.0

    # Final forecast
    forecast = min(1.0, base_forecast * season_factor * event_factor)

    return {
        "base_forecast": base_forecast,
        "adjusted_forecast": forecast,
        "season_factor": season_factor,
        "event_factor": event_factor
    }


def calculate_optimal_rate(
    base_rate: float,
    demand_forecast: float,
    competitor_avg: float,
    price_elasticity: float,
    channel_factor: float
) -> Dict[str, float]:
    """Calculate optimal room rate."""
    # Demand-based adjustment
    if demand_forecast > 0.85:
        demand_premium = 1.20
    elif demand_forecast > 0.70:
        demand_premium = 1.10
    elif demand_forecast > 0.50:
        demand_premium = 1.0
    elif demand_forecast > 0.30:
        demand_premium = 0.90
    else:
        demand_premium = 0.80

    # Competitive positioning
    comp_index = base_rate / competitor_avg if competitor_avg > 0 else 1.0

    # Target rate
    target_rate = base_rate * demand_premium * channel_factor

    # Bounds
    rate_floor = base_rate * 0.7
    rate_ceiling = base_rate * 1.5

    optimal_rate = max(rate_floor, min(rate_ceiling, target_rate))

    return {
        "optimal_rate": round(optimal_rate, 2),
        "rate_floor": round(rate_floor, 2),
        "rate_ceiling": round(rate_ceiling, 2),
        "demand_premium": demand_premium,
        "competitive_index": round(comp_index, 2)
    }


def determine_strategy(
    demand_forecast: float,
    days_out: int,
    current_occupancy: float
) -> str:
    """Determine pricing strategy based on conditions."""
    if demand_forecast > 0.85 and days_out < 14:
        return "MAXIMIZE_RATE"
    elif demand_forecast > 0.70:
        return "YIELD_MANAGEMENT"
    elif demand_forecast < 0.40 and days_out < 7:
        return "DISTRESSED_INVENTORY"
    elif current_occupancy < 0.30 and days_out > 30:
        return "EARLY_BOOKING_INCENTIVE"
    else:
        return "STANDARD_PRICING"


def calculate_revenue_forecast(
    rate: float,
    occupancy_forecast: float,
    rooms_available: int
) -> Dict[str, float]:
    """Calculate revenue forecast."""
    rooms_sold = int(rooms_available * occupancy_forecast)
    total_revenue = rooms_sold * rate
    revpar = (total_revenue / rooms_available) if rooms_available > 0 else 0

    return {
        "rooms_forecast": rooms_sold,
        "revenue_forecast": round(total_revenue, 2),
        "revpar": round(revpar, 2)
    }


def calculate_revenue(
    property_id: str,
    room_type: str,
    stay_date: str,
    current_occupancy: float,
    competitor_rates: List[float],
    days_out: int,
    demand_indicators: Dict,
    channel: str
) -> Dict[str, Any]:
    """
    Calculate optimal hotel room pricing.

    Business Rules:
    1. Demand forecasting with booking curves
    2. Price elasticity by segment
    3. MLOS rules for high demand
    4. Channel-specific pricing

    Args:
        property_id: Hotel identifier
        room_type: Room category
        stay_date: Date for pricing
        current_occupancy: Current booking level
        competitor_rates: Competitive rates
        days_out: Days until stay date
        demand_indicators: Demand signals
        channel: Distribution channel

    Returns:
        Revenue management recommendations
    """
    curves = load_demand_curves()

    room_config = curves["room_types"].get(room_type, curves["room_types"]["default"])
    channel_config = curves["channels"].get(channel, curves["channels"]["ota"])

    # Day of week factor
    dow_factor = get_day_of_week_factor(stay_date)

    # Competitor analysis
    competitor_avg = statistics.mean(competitor_rates) if competitor_rates else room_config["base_rate"]
    competitor_min = min(competitor_rates) if competitor_rates else room_config["base_rate"] * 0.8
    competitor_max = max(competitor_rates) if competitor_rates else room_config["base_rate"] * 1.2

    # Demand forecast
    demand = calculate_demand_forecast(
        current_occupancy,
        days_out,
        demand_indicators,
        curves["booking_curves"]
    )

    # Adjust for day of week
    occupancy_forecast = min(1.0, demand["adjusted_forecast"] * dow_factor)

    # Calculate optimal rate
    base_rate = room_config["base_rate"]
    rate_calc = calculate_optimal_rate(
        base_rate,
        occupancy_forecast,
        competitor_avg,
        room_config["price_elasticity"],
        channel_config["rate_factor"]
    )

    # Determine strategy
    strategy = determine_strategy(occupancy_forecast, days_out, current_occupancy)

    # Revenue forecast (assuming 100 rooms)
    rooms_available = 100
    revenue = calculate_revenue_forecast(
        rate_calc["optimal_rate"],
        occupancy_forecast,
        rooms_available
    )

    # MLOS recommendation
    if occupancy_forecast > 0.85 and days_out < 14:
        mlos_recommendation = 2
    elif occupancy_forecast > 0.90:
        mlos_recommendation = 3
    else:
        mlos_recommendation = 1

    return {
        "property_id": property_id,
        "room_type": room_type,
        "stay_date": stay_date,
        "recommended_rate": rate_calc["optimal_rate"],
        "rate_range": {
            "floor": rate_calc["rate_floor"],
            "ceiling": rate_calc["rate_ceiling"]
        },
        "occupancy_forecast": round(occupancy_forecast, 2),
        "revenue_forecast": revenue["revenue_forecast"],
        "revpar_forecast": revenue["revpar"],
        "pricing_strategy": strategy,
        "competitive_analysis": {
            "avg_competitor_rate": round(competitor_avg, 2),
            "rate_position": "above" if rate_calc["optimal_rate"] > competitor_avg else "below",
            "index_vs_comp": round(rate_calc["optimal_rate"] / competitor_avg * 100, 1)
        },
        "demand_signals": demand,
        "channel": channel,
        "days_out": days_out,
        "mlos_recommendation": mlos_recommendation
    }


if __name__ == "__main__":
    import json
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
    print(json.dumps(result, indent=2))
