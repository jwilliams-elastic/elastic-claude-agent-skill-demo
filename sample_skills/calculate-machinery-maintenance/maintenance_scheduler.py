"""
Machinery Maintenance Scheduling Module

Implements predictive maintenance algorithms using reliability
modeling and condition-based monitoring.
"""

import csv
import ast
import math
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


def load_equipment_parameters() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    equipment_types_data = load_csv_as_dict("equipment_types.csv")
    params = load_parameters()
    return {
        "equipment_types": equipment_types_data,
        **params
    }


def calculate_weibull_probability(
    time: float,
    shape: float,
    scale: float
) -> float:
    """Calculate failure probability using Weibull distribution."""
    if time <= 0 or scale <= 0:
        return 0.0
    return 1 - math.exp(-((time / scale) ** shape))


def estimate_remaining_useful_life(
    current_hours: float,
    shape: float,
    scale: float,
    target_reliability: float = 0.9
) -> float:
    """Estimate remaining useful life to target reliability."""
    # Solve for time where R(t) = target_reliability
    # R(t) = exp(-(t/scale)^shape) = target_reliability
    # t = scale * (-ln(target_reliability))^(1/shape)

    if target_reliability <= 0 or target_reliability >= 1:
        return 0

    target_time = scale * ((-math.log(target_reliability)) ** (1 / shape))
    rul = max(0, target_time - current_hours)

    return round(rul, 0)


def check_condition_thresholds(
    sensor_data: Dict,
    thresholds: Dict
) -> List[Dict]:
    """Check sensor readings against condition thresholds."""
    alerts = []

    for sensor, value in sensor_data.items():
        threshold_config = thresholds.get(sensor)
        if not threshold_config:
            continue

        warning = threshold_config.get("warning")
        critical = threshold_config.get("critical")

        if critical and value >= critical:
            alerts.append({
                "sensor": sensor,
                "value": value,
                "threshold": critical,
                "level": "critical",
                "action": "immediate_inspection"
            })
        elif warning and value >= warning:
            alerts.append({
                "sensor": sensor,
                "value": value,
                "threshold": warning,
                "level": "warning",
                "action": "schedule_inspection"
            })

    return alerts


def calculate_maintenance_cost(
    maintenance_type: str,
    costs: Dict,
    failure_probability: float
) -> Dict[str, float]:
    """Calculate expected maintenance costs."""
    preventive_cost = costs.get("preventive", 1000)
    corrective_cost = costs.get("corrective", 5000)
    downtime_cost = costs.get("downtime_per_hour", 500)

    # Expected cost of waiting
    expected_corrective = failure_probability * (corrective_cost + downtime_cost * 24)

    # Expected cost of preventive now
    expected_preventive = preventive_cost + downtime_cost * 4  # 4 hours planned downtime

    return {
        "preventive_cost": round(expected_preventive, 2),
        "expected_corrective_cost": round(expected_corrective, 2),
        "recommended_action": "preventive" if expected_preventive < expected_corrective else "monitor"
    }


def calculate_maintenance(
    equipment_id: str,
    equipment_type: str,
    operating_hours: float,
    sensor_data: Dict,
    maintenance_history: List[Dict],
    parts_inventory: Dict
) -> Dict[str, Any]:
    """
    Calculate optimal maintenance schedule.

    Business Rules:
    1. Condition-based maintenance triggers
    2. Weibull failure probability modeling
    3. Cost-benefit optimization
    4. Parts availability consideration

    Args:
        equipment_id: Equipment identifier
        equipment_type: Equipment type
        operating_hours: Current operating hours
        sensor_data: Sensor readings
        maintenance_history: Maintenance records
        parts_inventory: Spare parts on hand

    Returns:
        Maintenance schedule recommendations
    """
    params = load_equipment_parameters()

    equipment_params = params["equipment_types"].get(
        equipment_type,
        params["equipment_types"]["default"]
    )

    # Check condition thresholds
    condition_alerts = check_condition_thresholds(
        sensor_data,
        equipment_params["sensor_thresholds"]
    )

    # Calculate time since last major maintenance
    hours_since_maintenance = operating_hours
    if maintenance_history:
        # Simplified - would need actual hours tracking
        hours_since_maintenance = min(operating_hours, 2000)

    # Calculate failure probability
    shape = equipment_params["weibull_shape"]
    scale = equipment_params["weibull_scale"]

    current_failure_prob = calculate_weibull_probability(
        hours_since_maintenance, shape, scale
    )

    # 30-day failure probability
    hours_per_month = 720  # Assuming 24/7 operation
    future_failure_prob = calculate_weibull_probability(
        hours_since_maintenance + hours_per_month, shape, scale
    )

    # Estimate RUL
    rul_hours = estimate_remaining_useful_life(
        hours_since_maintenance, shape, scale, 0.9
    )

    # Cost analysis
    cost_analysis = calculate_maintenance_cost(
        "preventive",
        equipment_params["maintenance_costs"],
        future_failure_prob - current_failure_prob
    )

    # Determine maintenance recommendation
    if any(a["level"] == "critical" for a in condition_alerts):
        maintenance_urgency = "immediate"
        maintenance_type = "corrective"
        days_until = 0
    elif any(a["level"] == "warning" for a in condition_alerts):
        maintenance_urgency = "soon"
        maintenance_type = "preventive"
        days_until = 7
    elif current_failure_prob > 0.2:
        maintenance_urgency = "scheduled"
        maintenance_type = "preventive"
        days_until = 14
    elif rul_hours < hours_per_month:
        maintenance_urgency = "scheduled"
        maintenance_type = "preventive"
        days_until = int(rul_hours / 24)
    else:
        maintenance_urgency = "normal"
        maintenance_type = "preventive"
        days_until = int(rul_hours / 24)

    # Check parts availability
    parts_needed = equipment_params.get("standard_parts", [])
    parts_status = []
    for part in parts_needed:
        available = parts_inventory.get(part, 0)
        parts_status.append({
            "part": part,
            "required": 1,
            "available": available,
            "sufficient": available >= 1
        })

    parts_available = all(p["sufficient"] for p in parts_status)

    # Adjust schedule if parts not available
    if not parts_available and maintenance_urgency != "immediate":
        days_until = max(days_until, params["parts_lead_time_days"])

    next_maintenance_date = datetime.now() + timedelta(days=days_until)

    return {
        "equipment_id": equipment_id,
        "equipment_type": equipment_type,
        "operating_hours": operating_hours,
        "next_maintenance": {
            "date": next_maintenance_date.strftime("%Y-%m-%d"),
            "type": maintenance_type,
            "urgency": maintenance_urgency,
            "days_until": days_until
        },
        "failure_probability": {
            "current": round(current_failure_prob, 3),
            "30_day": round(future_failure_prob, 3)
        },
        "remaining_useful_life": {
            "hours": rul_hours,
            "days": int(rul_hours / 24),
            "confidence": 0.9
        },
        "condition_alerts": condition_alerts,
        "parts_needed": parts_status,
        "parts_available": parts_available,
        "cost_analysis": cost_analysis
    }


if __name__ == "__main__":
    import json
    result = calculate_maintenance(
        equipment_id="PUMP-001",
        equipment_type="centrifugal_pump",
        operating_hours=8500,
        sensor_data={"vibration_mm_s": 4.2, "temperature_c": 65, "pressure_bar": 8.5},
        maintenance_history=[{"date": "2025-06-15", "type": "bearing_replacement"}],
        parts_inventory={"bearings": 2, "seals": 5, "impeller": 0}
    )
    print(json.dumps(result, indent=2))
