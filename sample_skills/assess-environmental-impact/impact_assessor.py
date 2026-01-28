"""
Environmental Impact Assessment Module

Implements environmental impact analysis including
emissions calculation, regulatory compliance, and mitigation planning.
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


def load_environmental_factors() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    impact_categories_data = load_csv_as_dict("impact_categories.csv")
    emission_factors_data = load_csv_as_dict("emission_factors.csv")
    severity_thresholds_data = load_csv_as_dict("severity_thresholds.csv")
    regulatory_limits_data = load_csv_as_dict("regulatory_limits.csv")
    mitigation_effectiveness_data = load_csv_as_dict("mitigation_effectiveness.csv")
    lifecycle_stages_data = load_csv_as_dict("lifecycle_stages.csv")
    params = load_parameters()
    return {
        "impact_categories": impact_categories_data,
        "emission_factors": emission_factors_data,
        "severity_thresholds": severity_thresholds_data,
        "regulatory_limits": regulatory_limits_data,
        "mitigation_effectiveness": mitigation_effectiveness_data,
        "lifecycle_stages": lifecycle_stages_data,
        **params
    }


def calculate_carbon_emissions(
    energy_consumption: Dict,
    transportation: Dict,
    fuel_usage: Dict,
    emission_factors: Dict
) -> Dict[str, Any]:
    """Calculate total carbon emissions."""
    emissions = {}
    total_emissions = 0

    # Energy emissions
    energy_emissions = 0
    for source, kwh in energy_consumption.items():
        factor = emission_factors.get("electricity", {}).get(source, 0.42)
        source_emissions = kwh * factor
        energy_emissions += source_emissions
        emissions[f"electricity_{source}"] = round(source_emissions, 2)

    emissions["electricity_total"] = round(energy_emissions, 2)
    total_emissions += energy_emissions

    # Transportation emissions
    transport_emissions = 0
    for mode, data in transportation.items():
        factor = emission_factors.get("transportation", {}).get(mode, 0.05)
        tonne_km = data.get("tonnes", 0) * data.get("km", 0)
        mode_emissions = tonne_km * factor
        transport_emissions += mode_emissions
        emissions[f"transport_{mode}"] = round(mode_emissions, 2)

    emissions["transport_total"] = round(transport_emissions, 2)
    total_emissions += transport_emissions

    # Fuel combustion emissions
    fuel_emissions = 0
    for fuel_type, liters in fuel_usage.items():
        factor = emission_factors.get("fuel_combustion", {}).get(fuel_type, 2.0)
        fuel_type_emissions = liters * factor
        fuel_emissions += fuel_type_emissions
        emissions[f"fuel_{fuel_type}"] = round(fuel_type_emissions, 2)

    emissions["fuel_total"] = round(fuel_emissions, 2)
    total_emissions += fuel_emissions

    return {
        "emissions_breakdown": emissions,
        "total_co2_kg": round(total_emissions, 2),
        "total_co2_tonnes": round(total_emissions / 1000, 2)
    }


def calculate_category_impact(
    category_name: str,
    category_config: Dict,
    category_data: Dict
) -> Dict[str, Any]:
    """Calculate impact score for a single category."""
    metrics = category_config.get("metrics", [])
    weight = category_config.get("weight", 0)

    metric_scores = []
    total_score = 0

    for metric in metrics:
        if metric in category_data:
            value = category_data[metric]
            # Normalize to 0-100 scale (higher = more impact/worse)
            normalized = min(value, 100)
            total_score += normalized
            metric_scores.append({
                "metric": metric,
                "value": value,
                "normalized_score": normalized
            })

    avg_score = total_score / len(metric_scores) if metric_scores else 0

    return {
        "category": category_name,
        "weight": weight,
        "raw_score": round(avg_score, 1),
        "weighted_score": round(avg_score * weight, 2),
        "metrics": metric_scores
    }


def assess_impact_severity(
    total_score: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Assess overall impact severity."""
    for severity, config in sorted(
        thresholds.items(),
        key=lambda x: x[1].get("min_score", 0),
        reverse=True
    ):
        if total_score >= config.get("min_score", 0):
            return {
                "severity": severity.upper(),
                "score": total_score,
                "threshold": config.get("min_score", 0),
                "recommended_action": config.get("action", "")
            }

    return {
        "severity": "MINIMAL",
        "score": total_score,
        "threshold": 0,
        "recommended_action": "maintain_practices"
    }


def check_regulatory_compliance(
    measurements: Dict,
    regulatory_limits: Dict
) -> Dict[str, Any]:
    """Check compliance with regulatory limits."""
    compliance_results = []
    violations = []

    # Air quality
    for pollutant, value in measurements.get("air_quality", {}).items():
        limit_config = regulatory_limits.get("air_quality", {}).get(pollutant, {})
        limit = limit_config.get("limit", float("inf"))
        unit = limit_config.get("unit", "")

        compliant = value <= limit
        result = {
            "category": "air_quality",
            "parameter": pollutant,
            "measured_value": value,
            "limit": limit,
            "unit": unit,
            "compliant": compliant
        }
        compliance_results.append(result)
        if not compliant:
            violations.append(result)

    # Water discharge
    for parameter, value in measurements.get("water_discharge", {}).items():
        limit_config = regulatory_limits.get("water_discharge", {}).get(parameter, {})

        if parameter == "ph":
            min_limit = limit_config.get("min", 0)
            max_limit = limit_config.get("max", 14)
            compliant = min_limit <= value <= max_limit
            limit_str = f"{min_limit}-{max_limit}"
        else:
            limit = limit_config.get("limit", float("inf"))
            unit = limit_config.get("unit", "")
            compliant = value <= limit
            limit_str = f"{limit} {unit}"

        result = {
            "category": "water_discharge",
            "parameter": parameter,
            "measured_value": value,
            "limit": limit_str,
            "compliant": compliant
        }
        compliance_results.append(result)
        if not compliant:
            violations.append(result)

    # Noise
    for period, value in measurements.get("noise", {}).items():
        limit_config = regulatory_limits.get("noise", {}).get(period, {})
        limit = limit_config.get("limit", float("inf"))
        unit = limit_config.get("unit", "dB")

        compliant = value <= limit
        result = {
            "category": "noise",
            "parameter": f"noise_{period}",
            "measured_value": value,
            "limit": limit,
            "unit": unit,
            "compliant": compliant
        }
        compliance_results.append(result)
        if not compliant:
            violations.append(result)

    return {
        "total_parameters_checked": len(compliance_results),
        "compliant_parameters": len(compliance_results) - len(violations),
        "violations": len(violations),
        "compliance_rate": round((len(compliance_results) - len(violations)) / len(compliance_results) * 100, 1) if compliance_results else 100,
        "violation_details": violations,
        "overall_compliant": len(violations) == 0
    }


def calculate_lifecycle_impact(
    total_impact: float,
    lifecycle_stages: Dict,
    stage_data: Dict
) -> Dict[str, Any]:
    """Calculate impact by lifecycle stage."""
    stage_impacts = []

    for stage, config in lifecycle_stages.items():
        typical_share = config.get("typical_impact_share", 0)
        actual_share = stage_data.get(stage, typical_share)
        stage_impact = total_impact * actual_share

        stage_impacts.append({
            "stage": stage,
            "typical_share_pct": round(typical_share * 100, 1),
            "actual_share_pct": round(actual_share * 100, 1),
            "impact_value": round(stage_impact, 2)
        })

    return {
        "total_impact": total_impact,
        "stage_breakdown": stage_impacts
    }


def recommend_mitigation(
    severity: str,
    carbon_emissions: float,
    mitigation_options: Dict
) -> List[Dict]:
    """Recommend mitigation strategies."""
    recommendations = []

    for strategy, config in mitigation_options.items():
        reduction_pct = config.get("reduction_pct", 0)
        cost_factor = config.get("cost_factor", 1.0)

        potential_reduction = carbon_emissions * reduction_pct

        recommendations.append({
            "strategy": strategy.replace("_", " ").title(),
            "potential_reduction_kg": round(potential_reduction, 2),
            "reduction_pct": round(reduction_pct * 100, 1),
            "cost_factor": cost_factor,
            "cost_effectiveness": round(potential_reduction / cost_factor, 2) if cost_factor > 0 else 0
        })

    # Sort by cost effectiveness
    recommendations.sort(key=lambda x: x["cost_effectiveness"], reverse=True)

    return recommendations


def assess_environmental_impact(
    assessment_id: str,
    facility_name: str,
    energy_consumption: Dict,
    transportation: Dict,
    fuel_usage: Dict,
    category_measurements: Dict,
    regulatory_measurements: Dict,
    lifecycle_stage_data: Optional[Dict],
    assessment_period: str,
    assessment_date: str
) -> Dict[str, Any]:
    """
    Assess environmental impact.

    Business Rules:
    1. Carbon emissions calculation
    2. Multi-category impact scoring
    3. Regulatory compliance check
    4. Mitigation recommendations

    Args:
        assessment_id: Assessment identifier
        facility_name: Facility name
        energy_consumption: Energy usage by source
        transportation: Transportation data
        fuel_usage: Fuel consumption data
        category_measurements: Impact measurements by category
        regulatory_measurements: Regulatory compliance measurements
        lifecycle_stage_data: Optional lifecycle stage breakdown
        assessment_period: Period assessed
        assessment_date: Assessment date

    Returns:
        Environmental impact assessment results
    """
    config = load_environmental_factors()
    impact_categories = config.get("impact_categories", {})
    emission_factors = config.get("emission_factors", {})
    severity_thresholds = config.get("severity_thresholds", {})
    regulatory_limits = config.get("regulatory_limits", {})
    mitigation_options = config.get("mitigation_effectiveness", {})
    lifecycle_stages = config.get("lifecycle_stages", {})

    # Calculate carbon emissions
    carbon = calculate_carbon_emissions(
        energy_consumption,
        transportation,
        fuel_usage,
        emission_factors
    )

    # Calculate category impacts
    category_impacts = []
    total_weighted_score = 0

    for cat_name, cat_config in impact_categories.items():
        cat_data = category_measurements.get(cat_name, {})
        cat_impact = calculate_category_impact(cat_name, cat_config, cat_data)
        category_impacts.append(cat_impact)
        total_weighted_score += cat_impact["weighted_score"]

    # Assess severity
    severity = assess_impact_severity(total_weighted_score, severity_thresholds)

    # Check regulatory compliance
    compliance = check_regulatory_compliance(regulatory_measurements, regulatory_limits)

    # Lifecycle analysis
    lifecycle_impact = None
    if lifecycle_stage_data:
        lifecycle_impact = calculate_lifecycle_impact(
            carbon["total_co2_kg"],
            lifecycle_stages,
            lifecycle_stage_data
        )

    # Mitigation recommendations
    mitigation_recs = recommend_mitigation(
        severity["severity"],
        carbon["total_co2_kg"],
        mitigation_options
    )

    return {
        "assessment_id": assessment_id,
        "facility_name": facility_name,
        "assessment_date": assessment_date,
        "assessment_period": assessment_period,
        "carbon_footprint": carbon,
        "impact_by_category": category_impacts,
        "overall_impact": {
            "total_weighted_score": round(total_weighted_score, 1),
            "severity": severity
        },
        "regulatory_compliance": compliance,
        "lifecycle_analysis": lifecycle_impact,
        "mitigation_recommendations": mitigation_recs,
        "assessment_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = assess_environmental_impact(
        assessment_id="ENV-001",
        facility_name="Manufacturing Plant A",
        energy_consumption={
            "grid_average": 500000,
            "renewable": 100000
        },
        transportation={
            "road_freight": {"tonnes": 1000, "km": 500},
            "sea_freight": {"tonnes": 5000, "km": 10000}
        },
        fuel_usage={
            "diesel": 10000,
            "natural_gas": 25000
        },
        category_measurements={
            "climate_change": {"ghg_emissions": 75, "carbon_footprint": 70, "energy_consumption": 65},
            "water_use": {"water_consumption": 55, "water_discharge": 45, "water_quality": 40},
            "pollution": {"air_emissions": 50, "water_pollution": 35, "soil_contamination": 20}
        },
        regulatory_measurements={
            "air_quality": {"pm25": 22, "pm10": 45, "nox": 35},
            "water_discharge": {"bod": 25, "cod": 100, "tss": 30, "ph": 7.2},
            "noise": {"day": 62, "night": 52}
        },
        lifecycle_stage_data={
            "raw_materials": 0.35,
            "manufacturing": 0.30,
            "transportation": 0.10,
            "use_phase": 0.15,
            "end_of_life": 0.10
        },
        assessment_period="2025",
        assessment_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
