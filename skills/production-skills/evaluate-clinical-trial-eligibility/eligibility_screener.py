"""
Clinical Trial Eligibility Screening Module

Implements protocol-specific patient screening against inclusion/exclusion
criteria for clinical trial enrollment.
"""

import csv
import ast
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


def load_protocol_criteria() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    protocols_data = load_csv_as_dict("protocols.csv")
    lab_time_windows_data = load_key_value_csv("lab_time_windows.csv")
    score_thresholds_data = load_key_value_csv("score_thresholds.csv")
    params = load_parameters()
    return {
        "protocols": protocols_data,
        "lab_time_windows": lab_time_windows_data,
        "score_thresholds": score_thresholds_data,
        **params
    }


def check_age_criteria(age: int, criteria: Dict) -> Dict[str, Any]:
    """Check age against protocol criteria."""
    min_age = criteria.get("min_age", 0)
    max_age = criteria.get("max_age", 150)

    meets_criteria = min_age <= age <= max_age

    return {
        "criteria": "age",
        "meets_criteria": meets_criteria,
        "patient_value": age,
        "required_range": f"{min_age}-{max_age}",
        "weight": criteria.get("weight", 1.0)
    }


def check_diagnosis_criteria(
    diagnosis_codes: List[str],
    required_codes: List[str],
    excluded_codes: List[str]
) -> Dict[str, Any]:
    """Check diagnosis codes against protocol."""
    # Check for required diagnoses
    has_required = any(
        any(code.startswith(req) for req in required_codes)
        for code in diagnosis_codes
    )

    # Check for excluded diagnoses
    has_excluded = any(
        any(code.startswith(exc) for exc in excluded_codes)
        for code in diagnosis_codes
    )

    return {
        "has_required_diagnosis": has_required,
        "has_excluded_diagnosis": has_excluded,
        "matched_codes": [c for c in diagnosis_codes if any(c.startswith(r) for r in required_codes)],
        "exclusion_codes": [c for c in diagnosis_codes if any(c.startswith(e) for e in excluded_codes)]
    }


def check_lab_values(
    lab_results: List[Dict],
    lab_criteria: Dict
) -> Dict[str, Any]:
    """Check lab values against protocol requirements."""
    findings = []
    missing_labs = []

    for test_name, requirements in lab_criteria.items():
        # Find most recent result for this test
        matching_results = [r for r in lab_results if r.get("test") == test_name]

        if not matching_results:
            missing_labs.append(test_name)
            continue

        latest = max(matching_results, key=lambda x: x.get("date", ""))
        value = latest.get("value")

        min_val = requirements.get("min")
        max_val = requirements.get("max")

        in_range = True
        if min_val is not None and value < min_val:
            in_range = False
        if max_val is not None and value > max_val:
            in_range = False

        findings.append({
            "test": test_name,
            "value": value,
            "in_range": in_range,
            "required_range": f"{min_val}-{max_val}",
            "date": latest.get("date")
        })

    return {
        "findings": findings,
        "missing_labs": missing_labs,
        "all_in_range": all(f["in_range"] for f in findings)
    }


def check_medications(
    current_medications: List[str],
    prohibited_medications: List[Dict]
) -> Dict[str, Any]:
    """Check for prohibited medications."""
    conflicts = []

    current_lower = [m.lower() for m in current_medications]

    for prohibited in prohibited_medications:
        med_name = prohibited["name"].lower()
        if med_name in current_lower:
            conflicts.append({
                "medication": prohibited["name"],
                "reason": prohibited.get("reason", "Prohibited by protocol"),
                "washout_days": prohibited.get("washout_days", 0)
            })

    return {
        "has_conflicts": len(conflicts) > 0,
        "conflicts": conflicts
    }


def evaluate_eligibility(
    patient_id: str,
    protocol_id: str,
    demographics: Dict,
    diagnosis_codes: List[str],
    lab_results: List[Dict],
    medications: List[str],
    medical_history: List[str]
) -> Dict[str, Any]:
    """
    Evaluate patient eligibility for clinical trial.

    Business Rules:
    1. Inclusion criteria weighted scoring
    2. Hard exclusions immediately disqualify
    3. Lab values within time windows
    4. Prohibited medications with washout

    Args:
        patient_id: Patient identifier
        protocol_id: Protocol identifier
        demographics: Patient demographics
        diagnosis_codes: ICD-10 codes
        lab_results: Lab values
        medications: Current medications
        medical_history: Medical history codes

    Returns:
        Eligibility determination with details
    """
    criteria_db = load_protocol_criteria()

    protocol = criteria_db["protocols"].get(
        protocol_id,
        criteria_db["protocols"]["default"]
    )

    exclusion_flags = []
    inclusion_results = []
    missing_data = []
    inclusion_score = 0
    max_score = 0

    # Check demographics
    age = demographics.get("age")
    if age is None:
        missing_data.append("age")
    else:
        age_check = check_age_criteria(age, protocol["inclusion"]["age"])
        inclusion_results.append(age_check)
        max_score += age_check["weight"]
        if age_check["meets_criteria"]:
            inclusion_score += age_check["weight"]
        else:
            exclusion_flags.append({
                "criterion": "AGE_OUT_OF_RANGE",
                "description": f"Age {age} outside range {age_check['required_range']}"
            })

    # Check diagnosis
    diagnosis_check = check_diagnosis_criteria(
        diagnosis_codes,
        protocol["inclusion"]["diagnosis_codes"],
        protocol["exclusion"]["diagnosis_codes"]
    )

    if not diagnosis_check["has_required_diagnosis"]:
        exclusion_flags.append({
            "criterion": "MISSING_REQUIRED_DIAGNOSIS",
            "description": "Patient does not have required diagnosis for this trial"
        })
    else:
        inclusion_score += 2.0
    max_score += 2.0

    if diagnosis_check["has_excluded_diagnosis"]:
        exclusion_flags.append({
            "criterion": "EXCLUDED_DIAGNOSIS",
            "description": f"Patient has excluded diagnosis: {diagnosis_check['exclusion_codes']}"
        })

    # Check lab values
    lab_check = check_lab_values(lab_results, protocol["inclusion"]["lab_requirements"])

    for missing in lab_check["missing_labs"]:
        missing_data.append(f"lab_{missing}")

    for finding in lab_check["findings"]:
        if not finding["in_range"]:
            exclusion_flags.append({
                "criterion": f"LAB_OUT_OF_RANGE_{finding['test']}",
                "description": f"{finding['test']} value {finding['value']} outside range {finding['required_range']}"
            })

    if lab_check["all_in_range"] and not lab_check["missing_labs"]:
        inclusion_score += 1.5
    max_score += 1.5

    # Check medications
    med_check = check_medications(medications, protocol["exclusion"]["prohibited_medications"])

    for conflict in med_check["conflicts"]:
        exclusion_flags.append({
            "criterion": "PROHIBITED_MEDICATION",
            "description": f"Taking prohibited medication: {conflict['medication']} - {conflict['reason']}",
            "washout_days": conflict["washout_days"]
        })

    # Check medical history exclusions
    history_exclusions = protocol["exclusion"].get("medical_history_codes", [])
    for code in medical_history:
        if any(code.startswith(exc) for exc in history_exclusions):
            exclusion_flags.append({
                "criterion": "EXCLUDED_MEDICAL_HISTORY",
                "description": f"Medical history exclusion: {code}"
            })

    # Determine eligibility status
    hard_exclusions = [e for e in exclusion_flags if e["criterion"] in
                       ["EXCLUDED_DIAGNOSIS", "EXCLUDED_MEDICAL_HISTORY"]]

    if hard_exclusions:
        eligibility_status = "INELIGIBLE"
    elif missing_data:
        eligibility_status = "PENDING_REVIEW"
    elif exclusion_flags:
        eligibility_status = "INELIGIBLE"
    elif inclusion_score >= max_score * 0.8:
        eligibility_status = "ELIGIBLE"
    else:
        eligibility_status = "PENDING_REVIEW"

    # Generate recommendations
    recommendations = []
    if eligibility_status == "ELIGIBLE":
        recommendations.append("Schedule screening visit")
        recommendations.append("Obtain informed consent")
    elif eligibility_status == "PENDING_REVIEW":
        if missing_data:
            recommendations.append(f"Obtain missing data: {', '.join(missing_data)}")
        recommendations.append("Medical review required for final determination")
    else:
        if med_check["conflicts"]:
            washout = max(c["washout_days"] for c in med_check["conflicts"])
            recommendations.append(f"Consider re-screening after {washout}-day washout period")

    return {
        "patient_id": patient_id,
        "protocol_id": protocol_id,
        "eligibility_status": eligibility_status,
        "inclusion_score": round(inclusion_score, 2),
        "max_score": round(max_score, 2),
        "score_percentage": round(inclusion_score / max_score * 100, 1) if max_score > 0 else 0,
        "exclusion_flags": exclusion_flags,
        "missing_data": missing_data,
        "recommendations": recommendations,
        "lab_assessment": lab_check,
        "medication_assessment": med_check
    }


if __name__ == "__main__":
    import json
    result = evaluate_eligibility(
        patient_id="PT-12345",
        protocol_id="ONCO-2024-001",
        demographics={"age": 58, "sex": "F", "ethnicity": "caucasian"},
        diagnosis_codes=["C50.911", "Z85.3"],
        lab_results=[
            {"test": "ANC", "value": 1800, "date": "2026-01-10"},
            {"test": "platelets", "value": 180000, "date": "2026-01-10"},
            {"test": "creatinine", "value": 0.9, "date": "2026-01-10"}
        ],
        medications=["metformin", "lisinopril"],
        medical_history=["Z86.73"]
    )
    print(json.dumps(result, indent=2))
