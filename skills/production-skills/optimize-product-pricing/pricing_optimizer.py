"""
Product Pricing Optimization Module

Implements demand elasticity models and margin optimization algorithms
for consumer product pricing strategies.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
import statistics



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


def load_pricing_models() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    categories_data = load_csv_as_dict("categories.csv")
    brand_tiers_data = load_csv_as_dict("brand_tiers.csv")
    channels_data = load_csv_as_dict("channels.csv")
    params = load_parameters()
    return {
        "categories": categories_data,
        "brand_tiers": brand_tiers_data,
        "channels": channels_data,
        **params
    }


def calculate_price_elasticity_impact(
    current_price: float,
    new_price: float,
    elasticity: float
) -> float:
    """Calculate volume change based on price elasticity."""
    price_change_pct = (new_price - current_price) / current_price
    volume_change_pct = -elasticity * price_change_pct
    return round(volume_change_pct, 4)


def calculate_competitive_position(
    price: float,
    competitor_prices: List[float]
) -> Dict[str, Any]:
    """Determine competitive price position."""
    if not competitor_prices:
        return {"position": "unknown", "index": 0, "rank": 0}

    avg_competitor = statistics.mean(competitor_prices)
    min_competitor = min(competitor_prices)
    max_competitor = max(competitor_prices)

    price_index = (price / avg_competitor) * 100

    if price_index < 90:
        position = "price_leader"
    elif price_index < 100:
        position = "below_market"
    elif price_index <= 105:
        position = "at_market"
    elif price_index <= 115:
        position = "above_market"
    else:
        position = "premium"

    # Calculate rank
    all_prices = sorted(competitor_prices + [price])
    rank = all_prices.index(price) + 1

    return {
        "position": position,
        "price_index": round(price_index, 1),
        "rank": rank,
        "of_total": len(all_prices),
        "vs_average": round(price - avg_competitor, 2),
        "vs_min": round(price - min_competitor, 2),
        "vs_max": round(price - max_competitor, 2)
    }


def calculate_optimal_price(
    base_cost: float,
    target_margin: float,
    elasticity: float,
    competitor_prices: List[float],
    brand_tier_multiplier: float,
    channel_margin_req: float
) -> Dict[str, Any]:
    """Calculate optimal price point."""
    # Cost-plus baseline
    min_price = base_cost / (1 - channel_margin_req)

    # Target margin price
    target_price = base_cost / (1 - target_margin)

    # Competitive benchmark
    comp_avg = statistics.mean(competitor_prices) if competitor_prices else target_price

    # Brand tier adjustment
    tier_adjusted_price = comp_avg * brand_tier_multiplier

    # Revenue optimization (simplified)
    # At higher elasticity, lean towards lower price
    elasticity_adjustment = 1 - (elasticity - 1) * 0.05
    optimal_base = tier_adjusted_price * elasticity_adjustment

    # Ensure minimum margin
    optimal_price = max(optimal_base, min_price)

    return {
        "optimal_price": round(optimal_price, 2),
        "min_viable_price": round(min_price, 2),
        "target_margin_price": round(target_price, 2),
        "competitive_benchmark": round(comp_avg, 2)
    }


def optimize_pricing(
    product_id: str,
    product_category: str,
    base_cost: float,
    competitor_prices: List[float],
    brand_tier: str,
    sales_channel: str,
    current_price: float,
    target_margin: float
) -> Dict[str, Any]:
    """
    Optimize product pricing strategy.

    Business Rules:
    1. Category elasticity curves drive price-demand relationship
    2. Brand tier determines competitive positioning band
    3. Channel requirements set minimum margins
    4. Promotional modeling for temporary price changes

    Args:
        product_id: Product identifier
        product_category: Product category
        base_cost: Unit cost
        competitor_prices: Competitor prices
        brand_tier: Brand positioning tier
        sales_channel: Distribution channel
        current_price: Current price
        target_margin: Target profit margin

    Returns:
        Pricing recommendation with analysis
    """
    models = load_pricing_models()

    # Get category model
    category_model = models["categories"].get(
        product_category,
        models["categories"]["default"]
    )

    # Get brand tier multiplier
    tier_config = models["brand_tiers"].get(brand_tier, models["brand_tiers"]["mainstream"])

    # Get channel requirements
    channel_config = models["channels"].get(sales_channel, models["channels"]["retail"])

    # Calculate optimal price
    price_calc = calculate_optimal_price(
        base_cost=base_cost,
        target_margin=target_margin,
        elasticity=category_model["price_elasticity"],
        competitor_prices=competitor_prices,
        brand_tier_multiplier=tier_config["price_multiplier"],
        channel_margin_req=channel_config["min_margin"]
    )

    optimal_price = price_calc["optimal_price"]

    # Calculate actual margin
    expected_margin = (optimal_price - base_cost) / optimal_price

    # Define price band
    price_band = {
        "minimum": price_calc["min_viable_price"],
        "optimal": optimal_price,
        "maximum": round(optimal_price * tier_config["max_premium"], 2),
        "psychological_price": round(optimal_price - 0.01, 2)  # .99 pricing
    }

    # Calculate elasticity impact vs current
    elasticity_impact = {
        "price_change_pct": round((optimal_price - current_price) / current_price * 100, 1),
        "expected_volume_change_pct": round(
            calculate_price_elasticity_impact(
                current_price,
                optimal_price,
                category_model["price_elasticity"]
            ) * 100, 1
        ),
        "elasticity_coefficient": category_model["price_elasticity"]
    }

    # Competitive analysis
    competitive_position = calculate_competitive_position(optimal_price, competitor_prices)

    # Promotional recommendations
    promo_discount = category_model["optimal_promo_discount"]
    promo_price = round(optimal_price * (1 - promo_discount), 2)

    return {
        "product_id": product_id,
        "product_category": product_category,
        "optimal_price": optimal_price,
        "current_price": current_price,
        "expected_margin": round(expected_margin, 3),
        "target_margin": target_margin,
        "base_cost": base_cost,
        "price_band": price_band,
        "elasticity_impact": elasticity_impact,
        "competitive_position": competitive_position,
        "brand_tier": brand_tier,
        "sales_channel": sales_channel,
        "promotional_recommendation": {
            "optimal_discount": f"{promo_discount*100:.0f}%",
            "promo_price": promo_price,
            "expected_volume_lift": f"{category_model['promo_volume_lift']*100:.0f}%"
        }
    }


if __name__ == "__main__":
    import json
    result = optimize_pricing(
        product_id="SKU-12345",
        product_category="personal_care",
        base_cost=4.50,
        competitor_prices=[8.99, 9.49, 7.99, 8.49],
        brand_tier="mainstream",
        sales_channel="retail",
        current_price=8.99,
        target_margin=0.40
    )
    print(json.dumps(result, indent=2))
