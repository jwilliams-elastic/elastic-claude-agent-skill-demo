"""
Carbon Footprint Calculation Module

Implements GHG Protocol methodology for organizational
carbon footprint calculation across all scopes.
"""

import csv
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


def load_emission_factors() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    scope1_data = load_csv_as_dict("scope1.csv")
    scope2_data = load_csv_as_dict("scope2.csv")
    scope3_data = load_csv_as_dict("scope3.csv")
    thresholds_data = load_key_value_csv("thresholds.csv")
    gwp_values_data = load_key_value_csv("gwp_values.csv")
    params = load_parameters()
    return {
        "scope1": scope1_data,
        "scope2": scope2_data,
        "scope3": scope3_data,
        "thresholds": thresholds_data,
        "gwp_values": gwp_values_data,
        **params
    }


def calculate_scope1_emissions(
    activities: List[Dict],
    factors: Dict
) -> Dict[str, Any]:
    """Calculate Scope 1 direct emissions."""
    emissions_by_source = {}
    total_emissions = 0
    data_quality_scores = []

    for activity in activities:
        activity_type = activity.get("type", "unknown")
        quantity = activity.get("quantity", 0)
        unit = activity.get("unit", "")

        # Get emission factor
        factor_info = factors.get("scope1", {}).get(activity_type, {})
        factor = factor_info.get("factor", 0)
        factor_unit = factor_info.get("unit", "")

        # Calculate emissions (kg CO2e)
        emissions_kg = quantity * factor
        emissions_tonnes = emissions_kg / 1000

        emissions_by_source[activity_type] = {
            "quantity": quantity,
            "unit": unit,
            "emissions_tco2e": round(emissions_tonnes, 2),
            "factor_used": factor
        }

        total_emissions += emissions_tonnes
        data_quality_scores.append(factor_info.get("data_quality", 3))

    avg_quality = sum(data_quality_scores) / len(data_quality_scores) if data_quality_scores else 3

    return {
        "total_tco2e": round(total_emissions, 2),
        "by_source": emissions_by_source,
        "data_quality": round(avg_quality, 1)
    }


def calculate_scope2_emissions(
    scope2_data: Dict,
    factors: Dict
) -> Dict[str, Any]:
    """Calculate Scope 2 indirect emissions from purchased energy."""
    electricity_kwh = scope2_data.get("electricity_kwh", 0)
    grid_region = scope2_data.get("grid_region", "US-AVG")
    steam_mmbtu = scope2_data.get("steam_mmbtu", 0)

    # Get grid emission factor
    grid_factors = factors.get("scope2", {}).get("electricity", {})
    ef_electricity = grid_factors.get(grid_region, grid_factors.get("US-AVG", 0.4))

    # Calculate location-based emissions
    electricity_emissions = (electricity_kwh * ef_electricity) / 1000  # tonnes

    # Steam emissions
    steam_factor = factors.get("scope2", {}).get("steam", {}).get("factor", 0.055)
    steam_emissions = (steam_mmbtu * steam_factor) / 1000

    total_emissions = electricity_emissions + steam_emissions

    # Market-based calculation if RECs provided
    recs_mwh = scope2_data.get("recs_mwh", 0)
    market_based = electricity_emissions - (recs_mwh * ef_electricity)
    market_based = max(0, market_based)

    return {
        "total_tco2e": round(total_emissions, 2),
        "location_based": round(total_emissions, 2),
        "market_based": round(market_based, 2),
        "electricity": {
            "kwh": electricity_kwh,
            "emissions_tco2e": round(electricity_emissions, 2),
            "grid_region": grid_region,
            "factor": ef_electricity
        },
        "steam": {
            "mmbtu": steam_mmbtu,
            "emissions_tco2e": round(steam_emissions, 2)
        },
        "renewable_offset": recs_mwh
    }


def calculate_scope3_emissions(
    categories: List[Dict],
    factors: Dict
) -> Dict[str, Any]:
    """Calculate Scope 3 value chain emissions."""
    emissions_by_category = {}
    total_emissions = 0

    scope3_factors = factors.get("scope3", {})

    for category_data in categories:
        category = category_data.get("category", "unknown")
        data = category_data.get("data", {})

        category_factors = scope3_factors.get(category, {})
        category_emissions = 0

        if category == "business_travel":
            air_miles = data.get("air_miles", 0)
            air_factor = category_factors.get("air_per_mile", 0.255)
            category_emissions = (air_miles * air_factor) / 1000

            car_miles = data.get("car_miles", 0)
            car_factor = category_factors.get("car_per_mile", 0.404)
            category_emissions += (car_miles * car_factor) / 1000

        elif category == "employee_commuting":
            employees = data.get("employees", 0)
            avg_commute = data.get("avg_commute_miles", 20)
            work_days = data.get("work_days_per_year", 230)
            commute_factor = category_factors.get("avg_per_mile", 0.35)
            category_emissions = (employees * avg_commute * 2 * work_days * commute_factor) / 1000

        elif category == "purchased_goods":
            spend = data.get("spend_usd", 0)
            spend_factor = category_factors.get("per_usd", 0.0005)
            category_emissions = spend * spend_factor

        elif category == "waste":
            tonnes = data.get("tonnes", 0)
            waste_factor = category_factors.get("per_tonne", 0.5)
            category_emissions = tonnes * waste_factor

        emissions_by_category[category] = {
            "emissions_tco2e": round(category_emissions, 2),
            "data_provided": data
        }
        total_emissions += category_emissions

    return {
        "total_tco2e": round(total_emissions, 2),
        "by_category": emissions_by_category
    }


def identify_reduction_opportunities(
    scope1: Dict,
    scope2: Dict,
    scope3: Dict,
    thresholds: Dict
) -> List[Dict]:
    """Identify emission reduction opportunities."""
    opportunities = []

    # Check electricity as biggest opportunity
    electricity_emissions = scope2.get("electricity", {}).get("emissions_tco2e", 0)
    if electricity_emissions > 100:
        opportunities.append({
            "category": "scope2_electricity",
            "current_emissions": electricity_emissions,
            "opportunity": "Renewable energy procurement",
            "potential_reduction_pct": 80,
            "priority": "high"
        })

    # Check natural gas
    scope1_sources = scope1.get("by_source", {})
    if "natural_gas" in scope1_sources:
        ng_emissions = scope1_sources["natural_gas"]["emissions_tco2e"]
        if ng_emissions > 50:
            opportunities.append({
                "category": "scope1_natural_gas",
                "current_emissions": ng_emissions,
                "opportunity": "Electrification or efficiency improvements",
                "potential_reduction_pct": 30,
                "priority": "medium"
            })

    # Check business travel
    scope3_cats = scope3.get("by_category", {})
    if "business_travel" in scope3_cats:
        travel_emissions = scope3_cats["business_travel"]["emissions_tco2e"]
        if travel_emissions > 20:
            opportunities.append({
                "category": "scope3_travel",
                "current_emissions": travel_emissions,
                "opportunity": "Virtual meeting policies and sustainable aviation fuel",
                "potential_reduction_pct": 40,
                "priority": "medium"
            })

    return opportunities


def calculate_footprint(
    organization_id: str,
    reporting_period: Dict,
    scope1_activities: List[Dict],
    scope2_data: Dict,
    scope3_categories: List[Dict],
    baseline_year: Dict
) -> Dict[str, Any]:
    """
    Calculate organizational carbon footprint.

    Business Rules:
    1. GHG Protocol scope classification
    2. Activity-specific emission factors
    3. Data quality scoring
    4. Reduction opportunity identification

    Args:
        organization_id: Organization ID
        reporting_period: Reporting dates
        scope1_activities: Direct emissions
        scope2_data: Purchased energy
        scope3_categories: Value chain emissions
        baseline_year: Comparison baseline

    Returns:
        Carbon footprint calculation results
    """
    factors = load_emission_factors()

    # Calculate each scope
    scope1_result = calculate_scope1_emissions(scope1_activities, factors)
    scope2_result = calculate_scope2_emissions(scope2_data, factors)
    scope3_result = calculate_scope3_emissions(scope3_categories, factors)

    # Total emissions
    total_emissions = (
        scope1_result["total_tco2e"] +
        scope2_result["total_tco2e"] +
        scope3_result["total_tco2e"]
    )

    # Identify opportunities
    reduction_opportunities = identify_reduction_opportunities(
        scope1_result,
        scope2_result,
        scope3_result,
        factors.get("thresholds", {})
    )

    # Calculate vs baseline
    baseline_emissions = baseline_year.get("total_emissions", total_emissions)
    baseline_yr = baseline_year.get("year", "N/A")
    change_vs_baseline = ((total_emissions - baseline_emissions) / baseline_emissions * 100
                          if baseline_emissions > 0 else 0)

    # Data quality score
    quality_scores = [
        scope1_result.get("data_quality", 3),
        4,  # Scope 2 typically has good data
        2   # Scope 3 typically has lower quality
    ]
    avg_quality = sum(quality_scores) / len(quality_scores)

    return {
        "organization_id": organization_id,
        "reporting_period": reporting_period,
        "total_emissions": round(total_emissions, 2),
        "emissions_by_scope": {
            "scope1": scope1_result,
            "scope2": scope2_result,
            "scope3": scope3_result
        },
        "intensity_metrics": {
            "total_tco2e": round(total_emissions, 2)
        },
        "baseline_comparison": {
            "baseline_year": baseline_yr,
            "baseline_emissions": baseline_emissions,
            "change_pct": round(change_vs_baseline, 1)
        },
        "reduction_opportunities": reduction_opportunities,
        "data_quality_score": round(avg_quality, 1)
    }


if __name__ == "__main__":
    import json
    result = calculate_footprint(
        organization_id="ORG-001",
        reporting_period={"start": "2025-01-01", "end": "2025-12-31"},
        scope1_activities=[
            {"type": "natural_gas", "quantity": 50000, "unit": "therms"},
            {"type": "fleet_gasoline", "quantity": 20000, "unit": "gallons"}
        ],
        scope2_data={"electricity_kwh": 1000000, "grid_region": "US-WECC"},
        scope3_categories=[
            {"category": "business_travel", "data": {"air_miles": 500000, "car_miles": 50000}},
            {"category": "employee_commuting", "data": {"employees": 200, "avg_commute_miles": 15}}
        ],
        baseline_year={"year": 2020, "total_emissions": 5000}
    )
    print(json.dumps(result, indent=2))
