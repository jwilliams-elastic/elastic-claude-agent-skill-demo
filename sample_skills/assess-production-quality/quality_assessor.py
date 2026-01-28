"""
Production Line Quality Assessment Module

Implements proprietary quality control rules based on statistical process
control and manufacturing standards specific to the organization.
"""

import csv
import ast
import statistics
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


def load_tolerance_specs() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    parts_data = load_csv_as_dict("parts.csv")
    cpk_thresholds_data = load_key_value_csv("cpk_thresholds.csv")
    lot_quality_history_data = load_csv_as_dict("lot_quality_history.csv")
    production_lines_data = load_csv_as_dict("production_lines.csv")
    params = load_parameters()
    return {
        "parts": parts_data,
        "cpk_thresholds": cpk_thresholds_data,
        "lot_quality_history": lot_quality_history_data,
        "production_lines": production_lines_data,
        **params
    }


def calculate_cpk(measurements: List[float], usl: float, lsl: float) -> float:
    """Calculate process capability index (Cpk)."""
    if len(measurements) < 2:
        return 0.0

    mean = statistics.mean(measurements)
    std_dev = statistics.stdev(measurements)

    if std_dev == 0:
        return float('inf')

    cpu = (usl - mean) / (3 * std_dev)
    cpl = (mean - lsl) / (3 * std_dev)

    return min(cpu, cpl)


def detect_trend(measurements: List[float], consecutive: int = 3) -> bool:
    """Detect consecutive trending in measurements."""
    if len(measurements) < consecutive:
        return False

    recent = measurements[-consecutive:]
    increasing = all(recent[i] < recent[i+1] for i in range(len(recent)-1))
    decreasing = all(recent[i] > recent[i+1] for i in range(len(recent)-1))

    return increasing or decreasing


def assess_quality(
    part_number: str,
    measurements: List[float],
    dimension_type: str,
    material_lot: str,
    production_line: str,
    operator_id: str
) -> Dict[str, Any]:
    """
    Assess production quality against proprietary standards.

    Business Rules:
    1. Parts must fall within ±3 sigma control limits
    2. Three consecutive trending measurements trigger drift alert
    3. Critical dimensions have zero tolerance for out-of-spec
    4. Defects correlated with material lots

    Args:
        part_number: Part identifier
        measurements: List of measurement values
        dimension_type: critical, major, or minor
        material_lot: Material lot identifier
        production_line: Production line ID
        operator_id: Operator ID

    Returns:
        Quality assessment results with recommendations
    """
    specs = load_tolerance_specs()

    defects = []
    recommendations = []
    quality_status = "PASS"

    # Get specifications for this part
    part_specs = specs["parts"].get(part_number, specs["parts"]["default"])
    dim_specs = part_specs["dimensions"].get(dimension_type, part_specs["dimensions"]["major"])

    nominal = dim_specs["nominal"]
    usl = nominal + dim_specs["upper_tolerance"]
    lsl = nominal - dim_specs["lower_tolerance"]

    # Rule 1: Control limit enforcement
    out_of_spec = [m for m in measurements if m < lsl or m > usl]
    if out_of_spec:
        defects.append({
            "type": "OUT_OF_SPEC",
            "values": out_of_spec,
            "limits": {"usl": usl, "lsl": lsl}
        })

        # Rule 3: Critical dimension zero tolerance
        if dimension_type == "critical":
            quality_status = "FAIL"
            recommendations.append("IMMEDIATE_LINE_STOP: Critical dimension out of spec")
            recommendations.append("Quarantine all parts from current production run")
        else:
            quality_status = "FAIL"
            recommendations.append("Inspect and segregate non-conforming parts")

    # Rule 2: Consecutive deviation detection
    if detect_trend(measurements):
        if quality_status == "PASS":
            quality_status = "ALERT"
        defects.append({
            "type": "PROCESS_DRIFT",
            "description": "Three or more consecutive trending measurements detected"
        })
        recommendations.append("Investigate process drift - check tool wear, material variation")

    # Calculate process capability
    cpk = calculate_cpk(measurements, usl, lsl)

    if cpk < specs["cpk_thresholds"]["minimum"]:
        if quality_status == "PASS":
            quality_status = "ALERT"
        recommendations.append(f"Process capability Cpk={cpk:.2f} below minimum {specs['cpk_thresholds']['minimum']}")

    # Rule 4: Material lot correlation
    lot_history = specs["lot_quality_history"].get(material_lot, {})
    lot_correlation = {
        "lot_id": material_lot,
        "historical_defect_rate": lot_history.get("defect_rate", 0),
        "supplier": lot_history.get("supplier", "unknown"),
        "correlation_flag": lot_history.get("defect_rate", 0) > 0.02
    }

    if lot_correlation["correlation_flag"]:
        recommendations.append(f"Material lot {material_lot} has elevated defect history - increase inspection frequency")

    return {
        "part_number": part_number,
        "quality_status": quality_status,
        "defects_found": defects,
        "process_capability": round(cpk, 3),
        "measurements_analyzed": len(measurements),
        "recommendations": recommendations,
        "lot_correlation": lot_correlation,
        "production_line": production_line,
        "operator_id": operator_id
    }


if __name__ == "__main__":
    import json
    # Example usage
    result = assess_quality(
        part_number="MFG-2024-001",
        measurements=[10.02, 10.01, 10.03, 9.98, 10.00, 10.04, 10.05, 10.06],
        dimension_type="critical",
        material_lot="LOT-A-2024-0156",
        production_line="LINE-07",
        operator_id="OP-445"
    )
    print(json.dumps(result, indent=2))
