"""
Drug Interaction Validation Module

Implements clinical decision support for medication safety
including drug-drug interactions and contraindications.
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


def load_drug_database() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    interactions_data = load_csv_as_dict("interactions.csv")
    drug_classes_data = load_csv_as_dict("drug_classes.csv")
    severity_definitions_data = load_key_value_csv("severity_definitions.csv")
    params = load_parameters()
    return {
        "interactions": interactions_data,
        "drug_classes": drug_classes_data,
        "severity_definitions": severity_definitions_data,
        **params
    }


def check_drug_interaction(
    drug1: str,
    drug2: str,
    interactions: Dict
) -> Optional[Dict]:
    """Check for interaction between two drugs."""
    key1 = f"{drug1.lower()}_{drug2.lower()}"
    key2 = f"{drug2.lower()}_{drug1.lower()}"

    return interactions.get(key1) or interactions.get(key2)


def check_therapeutic_duplication(
    medications: List[Dict],
    drug_classes: Dict
) -> List[Dict]:
    """Check for therapeutic duplications."""
    duplications = []
    class_counts = {}

    for med in medications:
        drug_name = med.get("name", "").lower()
        drug_info = drug_classes.get(drug_name, {})
        therapeutic_class = drug_info.get("class")

        if therapeutic_class:
            if therapeutic_class not in class_counts:
                class_counts[therapeutic_class] = []
            class_counts[therapeutic_class].append(drug_name)

    for class_name, drugs in class_counts.items():
        if len(drugs) > 1:
            duplications.append({
                "therapeutic_class": class_name,
                "drugs_involved": drugs,
                "recommendation": f"Review need for multiple {class_name} agents"
            })

    return duplications


def adjust_for_patient_factors(
    interaction: Dict,
    patient_factors: Dict
) -> Dict:
    """Adjust interaction severity based on patient factors."""
    adjusted = interaction.copy()
    severity_modifier = 0

    age = patient_factors.get("age", 50)
    if age > 65:
        severity_modifier += 1
        adjusted["age_risk"] = "Elderly patient - increased risk"

    egfr = patient_factors.get("egfr", 90)
    if egfr < 30:
        severity_modifier += 2
        adjusted["renal_risk"] = "Severe renal impairment - dose adjustment needed"
    elif egfr < 60:
        severity_modifier += 1
        adjusted["renal_risk"] = "Moderate renal impairment - monitor closely"

    hepatic = patient_factors.get("hepatic_function", "normal")
    if hepatic == "impaired":
        severity_modifier += 1
        adjusted["hepatic_risk"] = "Hepatic impairment - consider alternatives"

    original_severity = adjusted.get("severity", 3)
    adjusted["adjusted_severity"] = min(5, original_severity + severity_modifier)

    return adjusted


def validate_interactions(
    patient_id: str,
    medications: List[Dict],
    patient_factors: Dict,
    allergies: List[str],
    diagnosis_codes: List[str]
) -> Dict[str, Any]:
    """
    Validate medications for interactions and safety.

    Business Rules:
    1. Multi-level severity classification
    2. Patient factor adjustments
    3. Therapeutic duplication detection
    4. Administration timing recommendations

    Args:
        patient_id: Patient identifier
        medications: List of medications
        patient_factors: Patient characteristics
        allergies: Known allergies
        diagnosis_codes: Active diagnoses

    Returns:
        Interaction validation results
    """
    db = load_drug_database()

    interactions_found = []
    recommendations = []
    dose_adjustments = []

    # Check all medication pairs for interactions
    med_names = [m.get("name", "").lower() for m in medications]

    for i, med1 in enumerate(med_names):
        for med2 in med_names[i+1:]:
            interaction = check_drug_interaction(med1, med2, db["interactions"])
            if interaction:
                adjusted = adjust_for_patient_factors(interaction, patient_factors)
                interactions_found.append({
                    "drugs": [med1, med2],
                    "severity": adjusted["adjusted_severity"],
                    "description": interaction.get("description"),
                    "mechanism": interaction.get("mechanism"),
                    "management": interaction.get("management"),
                    "patient_factors": {
                        k: v for k, v in adjusted.items()
                        if k.endswith("_risk")
                    }
                })

                if interaction.get("management"):
                    recommendations.append({
                        "type": "interaction_management",
                        "drugs": [med1, med2],
                        "recommendation": interaction["management"]
                    })

    # Check therapeutic duplications
    duplications = check_therapeutic_duplication(medications, db["drug_classes"])

    # Check for renal dose adjustments
    egfr = patient_factors.get("egfr", 90)
    for med in medications:
        drug_name = med.get("name", "").lower()
        drug_info = db["drug_classes"].get(drug_name, {})

        if drug_info.get("renal_dosing") and egfr < 60:
            dose_adjustments.append({
                "drug": drug_name,
                "reason": "Renal impairment",
                "current_dose": med.get("dose"),
                "recommendation": drug_info["renal_dosing"].get(
                    "moderate" if egfr >= 30 else "severe",
                    "Consult pharmacist"
                )
            })

    # Check allergies
    allergy_alerts = []
    for med in medications:
        drug_name = med.get("name", "").lower()
        drug_info = db["drug_classes"].get(drug_name, {})
        cross_reactivity = drug_info.get("cross_reactivity", [])

        for allergy in allergies:
            if allergy.lower() in cross_reactivity or allergy.lower() == drug_name:
                allergy_alerts.append({
                    "drug": drug_name,
                    "allergy": allergy,
                    "severity": "high",
                    "recommendation": "Avoid - potential allergic reaction"
                })

    # Calculate overall severity score
    if interactions_found:
        max_severity = max(i["severity"] for i in interactions_found)
    else:
        max_severity = 0

    if allergy_alerts:
        max_severity = max(max_severity, 5)

    severity_score = max_severity * 20  # Scale to 0-100

    return {
        "patient_id": patient_id,
        "medications_checked": len(medications),
        "interactions_found": interactions_found,
        "severity_score": severity_score,
        "recommendations": recommendations,
        "therapeutic_duplications": duplications,
        "dose_adjustments": dose_adjustments,
        "allergy_alerts": allergy_alerts,
        "safe_to_dispense": severity_score < 60 and len(allergy_alerts) == 0
    }


if __name__ == "__main__":
    import json
    result = validate_interactions(
        patient_id="PT-12345",
        medications=[
            {"name": "warfarin", "dose": "5mg", "frequency": "daily"},
            {"name": "aspirin", "dose": "81mg", "frequency": "daily"},
            {"name": "omeprazole", "dose": "20mg", "frequency": "daily"}
        ],
        patient_factors={"age": 72, "egfr": 45, "weight_kg": 70},
        allergies=["penicillin"],
        diagnosis_codes=["I48.0", "Z79.01"]
    )
    print(json.dumps(result, indent=2))
