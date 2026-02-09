"""
Aircraft Component Certification Module

Implements FAA/EASA airworthiness certification checks based on
proprietary compliance matrices and safety criticality classifications.
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


def load_certification_matrix() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    dal_requirements_data = load_csv_as_dict("dal_requirements.csv")
    aircraft_zones_data = load_csv_as_dict("aircraft_zones.csv")
    ndt_methods_data = load_csv_as_dict("ndt_methods.csv")
    params = load_parameters()
    return {
        "dal_requirements": dal_requirements_data,
        "aircraft_zones": aircraft_zones_data,
        "ndt_methods": ndt_methods_data,
        **params
    }


def validate_material_traceability(
    material_certs: List[str],
    required_certs: int
) -> Dict[str, Any]:
    """Validate material certificate chain."""
    return {
        "complete": len(material_certs) >= required_certs,
        "certificates_provided": len(material_certs),
        "certificates_required": required_certs,
        "gap": max(0, required_certs - len(material_certs))
    }


def evaluate_ndt_compliance(
    ndt_results: Dict[str, str],
    required_methods: List[str]
) -> Dict[str, Any]:
    """Evaluate NDT results against requirements."""
    missing_methods = [m for m in required_methods if m not in ndt_results]
    failed_methods = [m for m, r in ndt_results.items() if r != "PASS"]

    return {
        "compliant": len(missing_methods) == 0 and len(failed_methods) == 0,
        "missing_methods": missing_methods,
        "failed_methods": failed_methods,
        "passed_methods": [m for m, r in ndt_results.items() if r == "PASS"]
    }


def certify_component(
    part_number: str,
    serial_number: str,
    dal_level: str,
    material_certs: List[str],
    ndt_results: Dict[str, str],
    cycles_remaining: Optional[int],
    installation_location: str
) -> Dict[str, Any]:
    """
    Certify aircraft component for airworthiness.

    Business Rules:
    1. DAL level determines testing/documentation requirements
    2. Material traceability must be complete
    3. NDT requirements based on zone criticality
    4. Life-limited parts tracked against cycles

    Args:
        part_number: Aircraft part number
        serial_number: Component serial number
        dal_level: Design Assurance Level (A-E)
        material_certs: Material certificate references
        ndt_results: NDT test results by method
        cycles_remaining: Remaining life cycles
        installation_location: Aircraft zone

    Returns:
        Certification decision with compliance details
    """
    matrix = load_certification_matrix()

    certification_status = "CERTIFIED"
    limitations = []
    findings = []

    # Get DAL requirements
    dal_requirements = matrix["dal_requirements"].get(dal_level, matrix["dal_requirements"]["C"])

    # Get zone requirements
    zone_info = matrix["aircraft_zones"].get(installation_location, matrix["aircraft_zones"]["default"])

    # Rule 1: DAL enforcement - check documentation level
    required_cert_count = dal_requirements["min_material_certs"]
    traceability = validate_material_traceability(material_certs, required_cert_count)

    if not traceability["complete"]:
        certification_status = "REJECTED"
        findings.append({
            "code": "MAT-001",
            "severity": "CRITICAL",
            "description": f"Incomplete material traceability: {traceability['gap']} certificates missing"
        })

    # Rule 2: NDT requirements based on zone
    required_ndt = zone_info["required_ndt_methods"]
    ndt_compliance = evaluate_ndt_compliance(ndt_results, required_ndt)

    if not ndt_compliance["compliant"]:
        if ndt_compliance["failed_methods"]:
            certification_status = "REJECTED"
            findings.append({
                "code": "NDT-001",
                "severity": "CRITICAL",
                "description": f"NDT failures: {', '.join(ndt_compliance['failed_methods'])}"
            })
        if ndt_compliance["missing_methods"]:
            if certification_status != "REJECTED":
                certification_status = "CONDITIONAL"
            findings.append({
                "code": "NDT-002",
                "severity": "MAJOR",
                "description": f"Missing NDT methods: {', '.join(ndt_compliance['missing_methods'])}"
            })
            limitations.append(f"Complete NDT: {', '.join(ndt_compliance['missing_methods'])}")

    # Rule 3: Life-limited part tracking
    if cycles_remaining is not None:
        cycle_threshold = dal_requirements["cycle_warning_threshold"]
        if cycles_remaining <= 0:
            certification_status = "REJECTED"
            findings.append({
                "code": "LLP-001",
                "severity": "CRITICAL",
                "description": "Life-limited part has exceeded cycle limit"
            })
        elif cycles_remaining < cycle_threshold:
            limitations.append(f"Part approaching life limit: {cycles_remaining} cycles remaining")
            findings.append({
                "code": "LLP-002",
                "severity": "ADVISORY",
                "description": f"Cycles remaining ({cycles_remaining}) below threshold ({cycle_threshold})"
            })

    # Rule 4: Zone-specific limitations
    if zone_info["fatigue_critical"] and dal_level in ["A", "B"]:
        limitations.append("Enhanced inspection interval required for fatigue-critical zone")

    # Generate airworthiness tag if certified
    airworthiness_tag = None
    if certification_status in ["CERTIFIED", "CONDITIONAL"]:
        airworthiness_tag = f"8130-{datetime.now().strftime('%Y%m%d')}-{serial_number[-5:]}"

    # Calculate next inspection
    inspection_interval_days = dal_requirements["inspection_interval_days"]
    next_inspection = {
        "due_date": (datetime.now() + timedelta(days=inspection_interval_days)).strftime("%Y-%m-%d"),
        "type": zone_info["inspection_type"],
        "interval_days": inspection_interval_days
    }

    return {
        "part_number": part_number,
        "serial_number": serial_number,
        "certification_status": certification_status,
        "airworthiness_tag": airworthiness_tag,
        "dal_level": dal_level,
        "limitations": limitations,
        "findings": findings,
        "next_inspection": next_inspection,
        "compliance_matrix": {
            "material_traceability": traceability,
            "ndt_compliance": ndt_compliance,
            "zone_requirements": zone_info
        }
    }


if __name__ == "__main__":
    import json
    result = certify_component(
        part_number="737-400-2456",
        serial_number="SN-2024-78901",
        dal_level="B",
        material_certs=["MC-2024-001", "MC-2024-002"],
        ndt_results={"ultrasonic": "PASS", "eddy_current": "PASS"},
        cycles_remaining=15000,
        installation_location="ZONE-41"
    )
    print(json.dumps(result, indent=2))
