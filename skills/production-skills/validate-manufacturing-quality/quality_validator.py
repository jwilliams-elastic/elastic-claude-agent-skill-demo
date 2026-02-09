"""
Manufacturing Quality Validation Module

Implements quality assessment including
defect analysis, SPC monitoring, and capability analysis.
"""

import csv
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
import math



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


def load_quality_standards() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    quality_metrics_data = load_csv_as_dict("quality_metrics.csv")
    inspection_types_data = load_csv_as_dict("inspection_types.csv")
    aql_tables_data = load_csv_as_dict("aql_tables.csv")
    defect_categories_data = load_csv_as_dict("defect_categories.csv")
    spc_rules_data = load_csv_as_dict("spc_rules.csv")
    corrective_action_thresholds_data = load_csv_as_dict("corrective_action_thresholds.csv")
    certification_requirements_data = load_csv_as_dict("certification_requirements.csv")
    params = load_parameters()
    return {
        "quality_metrics": quality_metrics_data,
        "inspection_types": inspection_types_data,
        "aql_tables": aql_tables_data,
        "defect_categories": defect_categories_data,
        "spc_rules": spc_rules_data,
        "corrective_action_thresholds": corrective_action_thresholds_data,
        "certification_requirements": certification_requirements_data,
        **params
    }


def calculate_defect_rate(
    total_units: int,
    defective_units: int
) -> Dict[str, Any]:
    """Calculate defect rate in PPM."""
    if total_units <= 0:
        return {"error": "Invalid unit count"}

    defect_rate_pct = (defective_units / total_units) * 100
    defect_rate_ppm = (defective_units / total_units) * 1000000

    return {
        "total_units": total_units,
        "defective_units": defective_units,
        "defect_rate_pct": round(defect_rate_pct, 4),
        "defect_rate_ppm": round(defect_rate_ppm, 0)
    }


def calculate_first_pass_yield(
    units_started: int,
    units_passed_first_time: int
) -> Dict[str, Any]:
    """Calculate first pass yield."""
    if units_started <= 0:
        return {"error": "Invalid unit count"}

    fpy = (units_passed_first_time / units_started) * 100

    return {
        "units_started": units_started,
        "units_passed_first_time": units_passed_first_time,
        "first_pass_yield_pct": round(fpy, 2)
    }


def calculate_cpk(
    measurements: List[float],
    usl: float,
    lsl: float
) -> Dict[str, Any]:
    """Calculate process capability index (Cpk)."""
    if len(measurements) < 2:
        return {"error": "Insufficient measurements"}

    n = len(measurements)
    mean = sum(measurements) / n
    variance = sum((x - mean) ** 2 for x in measurements) / (n - 1)
    std_dev = math.sqrt(variance)

    if std_dev == 0:
        return {"error": "Zero standard deviation"}

    cpu = (usl - mean) / (3 * std_dev)
    cpl = (mean - lsl) / (3 * std_dev)
    cpk = min(cpu, cpl)

    # Cp (potential capability)
    cp = (usl - lsl) / (6 * std_dev)

    return {
        "mean": round(mean, 4),
        "std_dev": round(std_dev, 4),
        "usl": usl,
        "lsl": lsl,
        "cp": round(cp, 3),
        "cpk": round(cpk, 3),
        "cpu": round(cpu, 3),
        "cpl": round(cpl, 3)
    }


def calculate_oee(
    availability_pct: float,
    performance_pct: float,
    quality_pct: float
) -> Dict[str, Any]:
    """Calculate Overall Equipment Effectiveness."""
    oee = (availability_pct / 100) * (performance_pct / 100) * (quality_pct / 100) * 100

    return {
        "availability_pct": availability_pct,
        "performance_pct": performance_pct,
        "quality_pct": quality_pct,
        "oee_pct": round(oee, 2)
    }


def score_metric(
    value: float,
    thresholds: Dict,
    higher_is_better: bool = True
) -> Dict[str, Any]:
    """Score a quality metric."""
    if higher_is_better:
        if value >= thresholds.get("excellent", 99):
            rating = "EXCELLENT"
            score = 100
        elif value >= thresholds.get("good", 95):
            rating = "GOOD"
            score = 80
        elif value >= thresholds.get("acceptable", 90):
            rating = "ACCEPTABLE"
            score = 60
        else:
            rating = "POOR"
            score = 30
    else:
        if value <= thresholds.get("excellent", 100):
            rating = "EXCELLENT"
            score = 100
        elif value <= thresholds.get("good", 500):
            rating = "GOOD"
            score = 80
        elif value <= thresholds.get("acceptable", 1000):
            rating = "ACCEPTABLE"
            score = 60
        else:
            rating = "POOR"
            score = 30

    return {"value": value, "rating": rating, "score": score}


def analyze_defect_pareto(
    defects: List[Dict]
) -> Dict[str, Any]:
    """Analyze defects using Pareto analysis."""
    # Group by defect type
    defect_counts = {}
    for defect in defects:
        defect_type = defect.get("type", "unknown")
        defect_counts[defect_type] = defect_counts.get(defect_type, 0) + 1

    total_defects = sum(defect_counts.values())

    # Sort by count descending
    sorted_defects = sorted(defect_counts.items(), key=lambda x: x[1], reverse=True)

    pareto_analysis = []
    cumulative_pct = 0

    for defect_type, count in sorted_defects:
        pct = (count / total_defects * 100) if total_defects > 0 else 0
        cumulative_pct += pct

        pareto_analysis.append({
            "defect_type": defect_type,
            "count": count,
            "percentage": round(pct, 1),
            "cumulative_pct": round(cumulative_pct, 1)
        })

    # Identify vital few (80% of defects)
    vital_few = [d for d in pareto_analysis if d["cumulative_pct"] <= 80]

    return {
        "total_defects": total_defects,
        "unique_defect_types": len(defect_counts),
        "pareto_analysis": pareto_analysis[:10],
        "vital_few": vital_few,
        "vital_few_count": len(vital_few)
    }


def check_spc_rules(
    measurements: List[float],
    mean: float,
    std_dev: float,
    spc_rules: Dict
) -> List[Dict]:
    """Check for SPC control chart rule violations."""
    violations = []

    upper_3sigma = mean + 3 * std_dev
    lower_3sigma = mean - 3 * std_dev
    upper_2sigma = mean + 2 * std_dev
    lower_2sigma = mean - 2 * std_dev

    # Rule 1: Point beyond 3 sigma
    for i, m in enumerate(measurements):
        if m > upper_3sigma or m < lower_3sigma:
            violations.append({
                "rule": "rule_1",
                "description": spc_rules.get("rule_1", {}).get("description", ""),
                "point_index": i,
                "value": m,
                "severity": "high"
            })

    # Rule 2: 9 points in a row on same side
    for i in range(len(measurements) - 8):
        window = measurements[i:i+9]
        if all(m > mean for m in window) or all(m < mean for m in window):
            violations.append({
                "rule": "rule_2",
                "description": spc_rules.get("rule_2", {}).get("description", ""),
                "start_index": i,
                "severity": "medium"
            })
            break

    # Rule 3: 6 points trending
    for i in range(len(measurements) - 5):
        window = measurements[i:i+6]
        increasing = all(window[j] < window[j+1] for j in range(5))
        decreasing = all(window[j] > window[j+1] for j in range(5))
        if increasing or decreasing:
            violations.append({
                "rule": "rule_3",
                "description": spc_rules.get("rule_3", {}).get("description", ""),
                "start_index": i,
                "trend": "increasing" if increasing else "decreasing",
                "severity": "medium"
            })
            break

    return violations


def determine_inspection_result(
    sample_size: int,
    defects_found: int,
    aql_table: Dict,
    lot_size: int
) -> Dict[str, Any]:
    """Determine lot acceptance based on AQL sampling."""
    # Find appropriate sample plan
    sample_plan = None
    for range_key, plan in aql_table.items():
        parts = range_key.split("_")
        if len(parts) == 2:
            min_lot = int(parts[0])
            max_lot = int(parts[1])
            if min_lot <= lot_size <= max_lot:
                sample_plan = plan
                break

    if not sample_plan:
        return {"error": "No applicable sampling plan"}

    accept_number = sample_plan.get("accept", 0)
    reject_number = sample_plan.get("reject", 1)

    if defects_found <= accept_number:
        decision = "ACCEPT"
    elif defects_found >= reject_number:
        decision = "REJECT"
    else:
        decision = "TIGHTEN_INSPECTION"

    return {
        "lot_size": lot_size,
        "sample_size": sample_size,
        "defects_found": defects_found,
        "accept_number": accept_number,
        "reject_number": reject_number,
        "decision": decision
    }


def validate_manufacturing_quality(
    batch_id: str,
    total_units: int,
    defective_units: int,
    first_pass_units: int,
    measurements: List[float],
    usl: float,
    lsl: float,
    defects: List[Dict],
    oee_data: Dict,
    inspection_type: str,
    validation_date: str
) -> Dict[str, Any]:
    """
    Validate manufacturing quality.

    Business Rules:
    1. Defect rate calculation (PPM)
    2. Process capability (Cpk) analysis
    3. SPC rule violation detection
    4. Pareto analysis of defects

    Args:
        batch_id: Batch identifier
        total_units: Total units produced
        defective_units: Defective units count
        first_pass_units: Units passed first time
        measurements: Process measurements
        usl: Upper specification limit
        lsl: Lower specification limit
        defects: List of defect details
        oee_data: OEE component data
        inspection_type: Type of inspection
        validation_date: Validation date

    Returns:
        Quality validation results
    """
    standards = load_quality_standards()
    metrics = standards.get("quality_metrics", {})
    spc_rules = standards.get("spc_rules", {})

    # Calculate defect rate
    defect_rate = calculate_defect_rate(total_units, defective_units)
    defect_score = score_metric(
        defect_rate.get("defect_rate_ppm", 0),
        metrics.get("defect_rate", {}),
        higher_is_better=False
    )

    # Calculate FPY
    fpy = calculate_first_pass_yield(total_units, first_pass_units)
    fpy_score = score_metric(
        fpy.get("first_pass_yield_pct", 0),
        metrics.get("first_pass_yield", {}),
        higher_is_better=True
    )

    # Calculate Cpk
    cpk_result = calculate_cpk(measurements, usl, lsl)
    cpk_score = None
    if "cpk" in cpk_result:
        cpk_score = score_metric(
            cpk_result["cpk"],
            metrics.get("cpk", {}),
            higher_is_better=True
        )

    # Calculate OEE
    oee_result = calculate_oee(
        oee_data.get("availability_pct", 100),
        oee_data.get("performance_pct", 100),
        oee_data.get("quality_pct", 100)
    )
    oee_score = score_metric(
        oee_result["oee_pct"],
        metrics.get("oee", {}),
        higher_is_better=True
    )

    # Pareto analysis
    pareto = analyze_defect_pareto(defects)

    # SPC analysis
    spc_violations = []
    if cpk_result.get("mean") and cpk_result.get("std_dev"):
        spc_violations = check_spc_rules(
            measurements,
            cpk_result["mean"],
            cpk_result["std_dev"],
            spc_rules
        )

    # Inspection result
    inspection_config = standards.get("inspection_types", {}).get(inspection_type, {})
    aql_table = standards.get("aql_tables", {}).get(inspection_config.get("sampling_level", "S2"), {})
    inspection_result = determine_inspection_result(
        len(measurements) if measurements else 50,
        defective_units,
        aql_table,
        total_units
    )

    # Calculate overall quality score
    scores = [defect_score["score"], fpy_score["score"], oee_score["score"]]
    if cpk_score:
        scores.append(cpk_score["score"])
    overall_score = sum(scores) / len(scores)

    # Determine status
    if overall_score >= 85:
        status = "PASS"
    elif overall_score >= 60:
        status = "CONDITIONAL_PASS"
    else:
        status = "FAIL"

    return {
        "batch_id": batch_id,
        "validation_date": validation_date,
        "inspection_type": inspection_type,
        "metrics": {
            "defect_rate": {**defect_rate, "score": defect_score},
            "first_pass_yield": {**fpy, "score": fpy_score},
            "process_capability": {**cpk_result, "score": cpk_score} if cpk_result.get("cpk") else cpk_result,
            "oee": {**oee_result, "score": oee_score}
        },
        "defect_analysis": pareto,
        "spc_analysis": {
            "violations": spc_violations,
            "violation_count": len(spc_violations),
            "in_control": len(spc_violations) == 0
        },
        "inspection_result": inspection_result,
        "overall_quality_score": round(overall_score, 1),
        "status": status,
        "corrective_actions_required": status == "FAIL" or len(spc_violations) > 0
    }


if __name__ == "__main__":
    import json
    result = validate_manufacturing_quality(
        batch_id="BATCH-001",
        total_units=1000,
        defective_units=5,
        first_pass_units=970,
        measurements=[10.02, 10.01, 9.98, 10.03, 9.99, 10.00, 10.01, 9.97, 10.02, 10.00,
                      10.04, 9.96, 10.01, 9.99, 10.02, 10.00, 9.98, 10.03, 10.01, 9.99],
        usl=10.10,
        lsl=9.90,
        defects=[
            {"type": "dimensional", "severity": "minor"},
            {"type": "surface_finish", "severity": "major"},
            {"type": "dimensional", "severity": "minor"},
            {"type": "dimensional", "severity": "minor"},
            {"type": "missing_feature", "severity": "critical"}
        ],
        oee_data={"availability_pct": 92, "performance_pct": 88, "quality_pct": 99.5},
        inspection_type="final",
        validation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
