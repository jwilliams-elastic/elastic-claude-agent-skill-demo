"""
Building Permit Assessment Module

Implements zoning and building code compliance checking for
permit application review.
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


def load_building_codes() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    zoning_districts_data = load_csv_as_dict("zoning_districts.csv")
    parking_requirements_data = load_key_value_csv("parking_requirements.csv")
    ada_requirements_data = load_key_value_csv("ada_requirements.csv")
    fire_code_data = load_key_value_csv("fire_code.csv")
    params = load_parameters()
    return {
        "zoning_districts": zoning_districts_data,
        "parking_requirements": parking_requirements_data,
        "ada_requirements": ada_requirements_data,
        "fire_code": fire_code_data,
        **params
    }


def check_zoning_use(
    proposed_use: str,
    permitted_uses: List[str],
    conditional_uses: List[str]
) -> Dict[str, Any]:
    """Check if proposed use is permitted in zone."""
    if proposed_use in permitted_uses:
        return {"permitted": True, "use_type": "by_right", "variance_needed": False}
    elif proposed_use in conditional_uses:
        return {"permitted": True, "use_type": "conditional", "variance_needed": True}
    else:
        return {"permitted": False, "use_type": "prohibited", "variance_needed": True}


def check_setbacks(
    proposed: Dict[str, float],
    required: Dict[str, float]
) -> Dict[str, Any]:
    """Check setback compliance."""
    violations = []
    compliant = True

    for side, req_distance in required.items():
        prop_distance = proposed.get(side, 0)
        if prop_distance < req_distance:
            compliant = False
            violations.append({
                "type": "setback",
                "location": side,
                "proposed": prop_distance,
                "required": req_distance,
                "deficiency": req_distance - prop_distance
            })

    return {
        "compliant": compliant,
        "violations": violations
    }


def check_building_height(
    proposed_height: float,
    proposed_stories: int,
    max_height: float,
    max_stories: int
) -> Dict[str, Any]:
    """Check building height compliance."""
    height_ok = proposed_height <= max_height
    stories_ok = proposed_stories <= max_stories

    return {
        "compliant": height_ok and stories_ok,
        "height_compliant": height_ok,
        "stories_compliant": stories_ok,
        "proposed_height": proposed_height,
        "max_height": max_height,
        "proposed_stories": proposed_stories,
        "max_stories": max_stories
    }


def calculate_parking_requirement(
    use_type: str,
    sqft: float,
    parking_ratios: Dict
) -> int:
    """Calculate required parking spaces."""
    ratio = parking_ratios.get(use_type, parking_ratios.get("default", 1.0))
    # Ratio is spaces per 1000 sqft
    required = (sqft / 1000) * ratio
    return int(required + 0.5)  # Round up


def assess_permit(
    permit_id: str,
    parcel_id: str,
    zoning_district: str,
    project_type: str,
    proposed_use: str,
    building_specs: Dict,
    setbacks: Dict,
    parking_spaces: int
) -> Dict[str, Any]:
    """
    Assess building permit application.

    Business Rules:
    1. Use must be permitted in zoning district
    2. Setbacks must meet minimums
    3. Height and stories within limits
    4. Parking meets requirements

    Args:
        permit_id: Permit application ID
        parcel_id: Property parcel number
        zoning_district: Zoning classification
        project_type: Type of construction
        proposed_use: Building use
        building_specs: Building specifications
        setbacks: Proposed setbacks
        parking_spaces: Proposed parking

    Returns:
        Permit assessment results
    """
    codes = load_building_codes()

    violations = []
    variances_needed = []
    conditions = []
    compliance_checks = 0
    compliant_checks = 0

    # Get zoning district requirements
    zone_req = codes["zoning_districts"].get(
        zoning_district,
        codes["zoning_districts"]["default"]
    )

    # Check use compliance
    use_check = check_zoning_use(
        proposed_use,
        zone_req["permitted_uses"],
        zone_req["conditional_uses"]
    )
    compliance_checks += 1

    if not use_check["permitted"]:
        violations.append({
            "code": "ZN-001",
            "description": f"Use '{proposed_use}' not permitted in {zoning_district}",
            "severity": "critical"
        })
        variances_needed.append("Use variance required")
    elif use_check["use_type"] == "conditional":
        conditions.append(f"Conditional use permit required for {proposed_use}")
        variances_needed.append("Conditional use permit")
        compliant_checks += 0.5
    else:
        compliant_checks += 1

    # Check setbacks
    setback_check = check_setbacks(setbacks, zone_req["setbacks"])
    compliance_checks += 1

    if not setback_check["compliant"]:
        for v in setback_check["violations"]:
            violations.append({
                "code": f"ZN-SB-{v['location'].upper()}",
                "description": f"{v['location'].title()} setback {v['proposed']}ft < required {v['required']}ft",
                "severity": "major"
            })
            variances_needed.append(f"{v['location'].title()} setback variance")
    else:
        compliant_checks += 1

    # Check height
    height_check = check_building_height(
        building_specs.get("height_ft", 0),
        building_specs.get("stories", 1),
        zone_req["max_height_ft"],
        zone_req["max_stories"]
    )
    compliance_checks += 1

    if not height_check["compliant"]:
        if not height_check["height_compliant"]:
            violations.append({
                "code": "ZN-HT-001",
                "description": f"Height {height_check['proposed_height']}ft exceeds max {height_check['max_height']}ft",
                "severity": "major"
            })
            variances_needed.append("Height variance")
        if not height_check["stories_compliant"]:
            violations.append({
                "code": "ZN-ST-001",
                "description": f"{height_check['proposed_stories']} stories exceeds max {height_check['max_stories']}",
                "severity": "major"
            })
    else:
        compliant_checks += 1

    # Check parking
    parking_ratios = codes["parking_requirements"]
    required_parking = calculate_parking_requirement(
        proposed_use,
        building_specs.get("sqft", 0),
        parking_ratios
    )
    compliance_checks += 1

    if parking_spaces < required_parking:
        violations.append({
            "code": "PK-001",
            "description": f"Parking {parking_spaces} spaces < required {required_parking} spaces",
            "severity": "major"
        })
        deficit = required_parking - parking_spaces
        conditions.append(f"Provide {deficit} additional parking spaces or payment in-lieu")
    else:
        compliant_checks += 1

    # Check FAR if applicable
    if "lot_size_sqft" in building_specs and zone_req.get("max_far"):
        lot_size = building_specs["lot_size_sqft"]
        building_sqft = building_specs.get("sqft", 0)
        proposed_far = building_sqft / lot_size if lot_size > 0 else 0

        compliance_checks += 1
        if proposed_far > zone_req["max_far"]:
            violations.append({
                "code": "ZN-FAR-001",
                "description": f"FAR {proposed_far:.2f} exceeds max {zone_req['max_far']}",
                "severity": "major"
            })
        else:
            compliant_checks += 1

    # Calculate compliance score
    compliance_score = (compliant_checks / compliance_checks * 100) if compliance_checks > 0 else 0

    # Determine permit status
    critical_violations = [v for v in violations if v["severity"] == "critical"]
    major_violations = [v for v in violations if v["severity"] == "major"]

    if critical_violations:
        permit_status = "DENIED"
    elif major_violations and not variances_needed:
        permit_status = "DENIED"
    elif variances_needed or conditions:
        permit_status = "CONDITIONAL"
    else:
        permit_status = "APPROVED"

    return {
        "permit_id": permit_id,
        "parcel_id": parcel_id,
        "permit_status": permit_status,
        "compliance_score": round(compliance_score, 1),
        "zoning_district": zoning_district,
        "proposed_use": proposed_use,
        "violations": violations,
        "variances_needed": variances_needed,
        "conditions": conditions,
        "parking_analysis": {
            "required": required_parking,
            "proposed": parking_spaces,
            "compliant": parking_spaces >= required_parking
        },
        "height_analysis": height_check,
        "setback_analysis": setback_check
    }


if __name__ == "__main__":
    import json
    result = assess_permit(
        permit_id="BP-2024-001",
        parcel_id="123-456-789",
        zoning_district="C-2",
        project_type="new_construction",
        proposed_use="retail",
        building_specs={"height_ft": 45, "stories": 3, "sqft": 15000, "lot_size_sqft": 20000},
        setbacks={"front": 20, "side": 10, "rear": 15},
        parking_spaces=45
    )
    print(json.dumps(result, indent=2))
