"""
Crop Yield Optimization Module

Implements proprietary agronomic models for yield prediction and
optimization recommendations based on regional best practices.
"""

import csv
import ast
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
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
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
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
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


def load_crop_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    crops_data = load_csv_as_dict("crops.csv")
    fertilizer_conversions_data = load_key_value_csv("fertilizer_conversions.csv")
    nutrient_yield_impacts_data = load_key_value_csv("nutrient_yield_impacts.csv")
    params = load_parameters()
    return {
        "crops": crops_data,
        "fertilizer_conversions": fertilizer_conversions_data,
        "nutrient_yield_impacts": nutrient_yield_impacts_data,
        **params
    }


def calculate_nutrient_deficit(
    soil_analysis: Dict[str, float],
    optimal_levels: Dict[str, float]
) -> Dict[str, float]:
    """Calculate nutrient deficits against optimal levels."""
    deficits = {}
    for nutrient, optimal in optimal_levels.items():
        current = soil_analysis.get(nutrient, 0)
        deficits[nutrient] = max(0, optimal - current)
    return deficits


def estimate_water_stress(
    weather_forecast: Dict[str, Any],
    crop_water_needs: float,
    irrigation_available: bool
) -> Dict[str, Any]:
    """Estimate water stress impact on yield."""
    precip_chance = weather_forecast.get("precip_chance", 0)
    expected_precip = precip_chance * 0.5  # inches expected

    water_deficit = max(0, crop_water_needs - expected_precip)

    stress_factor = 1.0
    if water_deficit > 0:
        if irrigation_available:
            stress_factor = 0.98  # Minor stress even with irrigation
        else:
            stress_factor = max(0.6, 1 - (water_deficit * 0.1))

    return {
        "water_deficit_inches": round(water_deficit, 2),
        "stress_factor": stress_factor,
        "irrigation_needed": water_deficit > 0.5
    }


def optimize_yield(
    field_id: str,
    crop_type: str,
    soil_analysis: Dict[str, float],
    weather_forecast: Dict[str, Any],
    growth_stage: str,
    irrigation_available: bool,
    pest_pressure_score: float
) -> Dict[str, Any]:
    """
    Generate yield optimization recommendations.

    Business Rules:
    1. NPK ratios vary by crop and growth stage
    2. GDD accumulation predicts maturity
    3. Water stress index triggers irrigation
    4. Pest pressure adjusts yield predictions

    Args:
        field_id: Field identifier
        crop_type: Crop being grown
        soil_analysis: Soil test results
        weather_forecast: Weather forecast data
        growth_stage: Current growth stage
        irrigation_available: Irrigation availability
        pest_pressure_score: IPM pressure (0-10)

    Returns:
        Yield predictions and optimization recommendations
    """
    params = load_crop_parameters()

    crop_params = params["crops"].get(crop_type, params["crops"]["default"])
    stage_params = crop_params["growth_stages"].get(growth_stage, crop_params["growth_stages"]["default"])

    optimization_actions = []
    risk_factors = []
    fertilizer_recommendations = {}
    irrigation_schedule = []

    # Base yield potential
    base_yield = crop_params["base_yield_potential"]
    yield_multiplier = 1.0

    # Rule 1: Nutrient balance assessment
    optimal_nutrients = stage_params["optimal_nutrients"]
    deficits = calculate_nutrient_deficit(soil_analysis, optimal_nutrients)

    for nutrient, deficit in deficits.items():
        if deficit > 0:
            # Calculate fertilizer needed
            conversion = params["fertilizer_conversions"].get(nutrient, 1.0)
            lbs_needed = deficit * conversion
            fertilizer_recommendations[nutrient] = {
                "deficit_ppm": deficit,
                "application_lbs_per_acre": round(lbs_needed, 1),
                "timing": stage_params.get("fertilizer_timing", "immediate")
            }

            # Yield impact from deficiency
            impact = params["nutrient_yield_impacts"].get(nutrient, 0.02)
            yield_multiplier -= (deficit / optimal_nutrients[nutrient]) * impact

            optimization_actions.append(f"Apply {lbs_needed:.1f} lbs/acre {nutrient} fertilizer")

    # Rule 2: pH optimization
    optimal_ph = crop_params["optimal_ph"]
    current_ph = soil_analysis.get("pH", 7.0)
    if abs(current_ph - optimal_ph) > 0.5:
        risk_factors.append(f"Soil pH {current_ph} outside optimal range ({optimal_ph} ± 0.5)")
        yield_multiplier -= 0.05
        if current_ph < optimal_ph:
            optimization_actions.append("Apply lime to raise soil pH")
        else:
            optimization_actions.append("Apply sulfur to lower soil pH")

    # Rule 3: Water stress assessment
    water_needs = stage_params["water_needs_inches_per_week"]
    water_stress = estimate_water_stress(weather_forecast, water_needs, irrigation_available)

    if water_stress["irrigation_needed"]:
        yield_multiplier *= water_stress["stress_factor"]
        if irrigation_available:
            irrigation_schedule.append({
                "timing": "within_3_days",
                "amount_inches": water_stress["water_deficit_inches"],
                "priority": "high"
            })
            optimization_actions.append(f"Irrigate {water_stress['water_deficit_inches']} inches within 3 days")
        else:
            risk_factors.append(f"Water deficit of {water_stress['water_deficit_inches']} inches with no irrigation")

    # Rule 4: Pest pressure adjustment
    if pest_pressure_score > 5:
        pest_impact = (pest_pressure_score - 5) * 0.03
        yield_multiplier -= pest_impact
        risk_factors.append(f"Elevated pest pressure (score: {pest_pressure_score})")
        optimization_actions.append("Implement IPM intervention measures")

    # Calculate final yield prediction
    yield_prediction = round(base_yield * yield_multiplier, 1)

    # GDD-based maturity prediction
    gdd_accumulated = weather_forecast.get("gdd_forecast", 0)
    gdd_to_maturity = crop_params["gdd_to_maturity"] - gdd_accumulated

    return {
        "field_id": field_id,
        "crop_type": crop_type,
        "growth_stage": growth_stage,
        "yield_prediction": yield_prediction,
        "yield_unit": "bushels_per_acre",
        "yield_multiplier": round(yield_multiplier, 3),
        "optimization_actions": optimization_actions,
        "fertilizer_recommendations": fertilizer_recommendations,
        "irrigation_schedule": irrigation_schedule,
        "risk_factors": risk_factors,
        "gdd_to_maturity": gdd_to_maturity,
        "water_stress_analysis": water_stress
    }


if __name__ == "__main__":
    import json
    result = optimize_yield(
        field_id="FIELD-NW-042",
        crop_type="corn",
        soil_analysis={"N": 45, "P": 32, "K": 180, "pH": 6.5, "organic_matter": 3.2},
        weather_forecast={"avg_temp": 78, "precip_chance": 30, "gdd_forecast": 1850},
        growth_stage="V8",
        irrigation_available=True,
        pest_pressure_score=3.5
    )
    print(json.dumps(result, indent=2))
