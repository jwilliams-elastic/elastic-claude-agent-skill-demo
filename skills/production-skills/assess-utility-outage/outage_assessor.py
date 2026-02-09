"""
Utility Outage Impact Assessment Module

Implements outage impact scoring and restoration priority
algorithms for utility service management.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta



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


def load_outage_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    customer_weights_data = load_key_value_csv("customer_weights.csv")
    damage_complexity_data = load_csv_as_dict("damage_complexity.csv")
    # Load critical facilities as lists and combine into a single dict by zone
    critical_facilities_data = {
        "north": load_csv_as_list("critical_facilities_north.csv"),
        "south": load_csv_as_list("critical_facilities_south.csv"),
        "east": load_csv_as_list("critical_facilities_east.csv"),
        "west": load_csv_as_list("critical_facilities_west.csv"),
    }
    priority_thresholds_data = load_key_value_csv("priority_thresholds.csv")
    restoration_standards_data = load_csv_as_dict("restoration_standards.csv")
    params = load_parameters()
    return {
        "customer_weights": customer_weights_data,
        "damage_complexity": damage_complexity_data,
        "critical_facilities": critical_facilities_data,
        "priority_thresholds": priority_thresholds_data,
        "restoration_standards": restoration_standards_data,
        **params
    }


def calculate_customer_impact(
    customer_counts: Dict[str, int],
    weights: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate weighted customer impact score."""
    total_customers = sum(customer_counts.values())
    weighted_impact = 0

    impact_details = []
    for customer_class, count in customer_counts.items():
        weight = weights.get(customer_class, 1.0)
        impact = count * weight
        weighted_impact += impact

        impact_details.append({
            "class": customer_class,
            "count": count,
            "weight": weight,
            "weighted_impact": impact
        })

    return {
        "total_customers": total_customers,
        "weighted_impact": weighted_impact,
        "details": impact_details
    }


def identify_critical_facilities(
    affected_area: Dict,
    critical_db: Dict
) -> List[Dict]:
    """Identify critical facilities in affected area."""
    zone = affected_area.get("zone", "")
    critical = []

    for facility in critical_db.get(zone, []):
        critical.append({
            "name": facility["name"],
            "type": facility["type"],
            "priority": facility["priority"],
            "backup_power_hours": facility.get("backup_power_hours", 0)
        })

    return critical


def assess_damage_complexity(
    damage_reports: List[Dict],
    complexity_factors: Dict
) -> Dict[str, Any]:
    """Assess restoration complexity from damage reports."""
    total_complexity = 0
    damage_summary = []

    for report in damage_reports:
        damage_type = report.get("type", "unknown")
        severity = report.get("severity", "minor")

        type_factor = complexity_factors.get(damage_type, {})
        base_hours = type_factor.get("base_hours", 2)
        severity_multiplier = {"minor": 0.5, "moderate": 1.0, "major": 2.0}.get(severity, 1.0)

        complexity = base_hours * severity_multiplier
        total_complexity += complexity

        damage_summary.append({
            "type": damage_type,
            "severity": severity,
            "estimated_hours": complexity
        })

    return {
        "total_complexity_hours": total_complexity,
        "damage_summary": damage_summary
    }


def calculate_etr(
    complexity_hours: float,
    available_crews: int,
    weather_modifier: float,
    crew_efficiency: float = 0.8
) -> Dict[str, Any]:
    """Calculate estimated time to restoration."""
    if available_crews <= 0:
        return {"hours": 999, "confidence": "low"}

    # Base calculation
    effective_crews = available_crews * crew_efficiency
    parallel_factor = min(effective_crews, complexity_hours / 2)  # Diminishing returns

    base_hours = complexity_hours / max(1, parallel_factor)

    # Weather adjustment
    adjusted_hours = base_hours * weather_modifier

    # Round up to nearest hour
    etr_hours = int(adjusted_hours + 0.99)

    # Confidence based on data quality
    confidence = "high" if available_crews > 5 else "medium" if available_crews > 2 else "low"

    etr_time = datetime.now() + timedelta(hours=etr_hours)

    return {
        "hours": etr_hours,
        "estimated_time": etr_time.strftime("%Y-%m-%d %H:%M"),
        "confidence": confidence
    }


def determine_priority(
    impact_score: float,
    critical_facilities: List[Dict],
    has_safety_concern: bool
) -> str:
    """Determine restoration priority level."""
    if has_safety_concern:
        return "EMERGENCY"

    has_critical = any(f["priority"] == "critical" for f in critical_facilities)
    if has_critical:
        return "CRITICAL"

    if impact_score > 10000:
        return "HIGH"
    elif impact_score > 5000:
        return "MEDIUM"
    else:
        return "NORMAL"


def assess_outage(
    outage_id: str,
    affected_area: Dict,
    customer_counts: Dict[str, int],
    damage_reports: List[Dict],
    weather_conditions: Dict,
    available_crews: int
) -> Dict[str, Any]:
    """
    Assess utility outage impact and restoration needs.

    Business Rules:
    1. Weighted customer impact scoring
    2. Priority matrix based on impact and safety
    3. Resource allocation by damage complexity
    4. ETR calculation with weather factors

    Args:
        outage_id: Outage identifier
        affected_area: Geographic area
        customer_counts: Customers by class
        damage_reports: Field damage data
        weather_conditions: Weather data
        available_crews: Available crews

    Returns:
        Outage assessment results
    """
    params = load_outage_parameters()

    # Calculate customer impact
    customer_impact = calculate_customer_impact(
        customer_counts,
        params["customer_weights"]
    )

    # Identify critical facilities
    critical_facilities = identify_critical_facilities(
        affected_area,
        params["critical_facilities"]
    )

    # Assess damage complexity
    damage_assessment = assess_damage_complexity(
        damage_reports,
        params["damage_complexity"]
    )

    # Check for safety concerns
    safety_types = ["downed_wire", "fire", "explosion", "structural_damage"]
    has_safety_concern = any(
        r.get("type") in safety_types
        for r in damage_reports
    )

    # Weather modifier
    wind_speed = weather_conditions.get("wind_mph", 0)
    if wind_speed > 40:
        weather_modifier = 2.0
    elif wind_speed > 25:
        weather_modifier = 1.5
    else:
        weather_modifier = 1.0

    # Calculate ETR
    etr = calculate_etr(
        damage_assessment["total_complexity_hours"],
        available_crews,
        weather_modifier
    )

    # Calculate overall impact score
    impact_score = customer_impact["weighted_impact"]
    if critical_facilities:
        impact_score *= 1.5
    if has_safety_concern:
        impact_score *= 2.0

    # Determine priority
    priority_level = determine_priority(
        impact_score,
        critical_facilities,
        has_safety_concern
    )

    # Resource requirements
    crews_needed = max(1, int(damage_assessment["total_complexity_hours"] / 4))
    resource_requirements = {
        "crews_needed": crews_needed,
        "crews_available": available_crews,
        "crews_gap": max(0, crews_needed - available_crews),
        "equipment": ["bucket_truck", "line_truck"] if any(
            d["type"] in ["downed_wire", "pole_damage"]
            for d in damage_reports
        ) else ["service_truck"]
    }

    return {
        "outage_id": outage_id,
        "impact_score": round(impact_score, 0),
        "priority_level": priority_level,
        "customer_impact": customer_impact,
        "critical_facilities": critical_facilities,
        "damage_assessment": damage_assessment,
        "estimated_restoration": etr,
        "resource_requirements": resource_requirements,
        "safety_concerns": has_safety_concern,
        "weather_impact": {
            "modifier": weather_modifier,
            "conditions": weather_conditions
        }
    }


if __name__ == "__main__":
    import json
    result = assess_outage(
        outage_id="OUT-2024-001",
        affected_area={"zone": "north", "substations": ["SUB-101"]},
        customer_counts={"residential": 5000, "commercial": 200, "industrial": 15},
        damage_reports=[
            {"type": "downed_wire", "severity": "major"},
            {"type": "transformer_damage", "severity": "moderate"}
        ],
        weather_conditions={"wind_mph": 45, "precipitation": "rain"},
        available_crews=12
    )
    print(json.dumps(result, indent=2))
