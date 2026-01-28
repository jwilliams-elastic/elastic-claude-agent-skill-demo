"""
Chemical Compound Safety Analysis Module

Implements GHS-compliant hazard classification and proprietary safety
assessment algorithms for chemical handling and exposure management.
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


def load_chemical_hazards() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    compounds_data = load_csv_as_dict("compounds.csv")
    incompatibility_matrix_data = load_csv_as_dict("incompatibility_matrix.csv")
    params = load_parameters()
    return {
        "compounds": compounds_data,
        "incompatibility_matrix": incompatibility_matrix_data,
        **params
    }


def calculate_exposure_limit(
    base_limit: float,
    concentration: float,
    duration_factor: float
) -> float:
    """Calculate adjusted exposure limit."""
    adjusted = base_limit * (100 / concentration) * duration_factor
    return round(adjusted, 2)


def check_incompatibility(
    primary_compound: str,
    mixing_compounds: List[str],
    incompatibility_matrix: Dict
) -> List[Dict]:
    """Check for chemical incompatibilities."""
    incompatibilities = []

    compound_incompat = incompatibility_matrix.get(primary_compound, {})
    for compound in mixing_compounds:
        if compound in compound_incompat.get("incompatible_with", []):
            incompatibilities.append({
                "compound": compound,
                "reaction_type": compound_incompat.get("reaction_type", "unknown"),
                "severity": compound_incompat.get("severity", "moderate"),
                "products": compound_incompat.get("products", [])
            })

    return incompatibilities


def determine_ppe(
    hazard_categories: Dict,
    exposure_route: str,
    concentration: float
) -> List[Dict]:
    """Determine required PPE based on hazards."""
    ppe_list = []

    # Eye protection based on hazards
    if hazard_categories.get("eye_damage") or hazard_categories.get("skin_corrosion"):
        ppe_list.append({
            "equipment": "Chemical splash goggles",
            "standard": "ANSI Z87.1",
            "required": True
        })
        if hazard_categories.get("skin_corrosion") == 1:
            ppe_list.append({
                "equipment": "Face shield",
                "standard": "ANSI Z87.1",
                "required": True
            })

    # Respiratory protection
    if exposure_route == "inhalation":
        if concentration > 50:
            ppe_list.append({
                "equipment": "Full-face respirator with organic vapor cartridge",
                "standard": "NIOSH",
                "required": True
            })
        elif concentration > 10:
            ppe_list.append({
                "equipment": "Half-face respirator with appropriate cartridge",
                "standard": "NIOSH",
                "required": True
            })

    # Skin protection
    if hazard_categories.get("skin_sensitization") or hazard_categories.get("skin_corrosion"):
        ppe_list.append({
            "equipment": "Chemical-resistant gloves",
            "material": "Nitrile or neoprene",
            "required": True
        })

    # Body protection
    if concentration > 75 or hazard_categories.get("skin_corrosion"):
        ppe_list.append({
            "equipment": "Chemical-resistant apron or suit",
            "standard": "Per SDS recommendation",
            "required": True
        })

    return ppe_list


def analyze_safety(
    compound_id: str,
    chemical_formula: str,
    concentration: float,
    exposure_route: str,
    exposure_duration: str,
    mixing_compounds: List[str]
) -> Dict[str, Any]:
    """
    Analyze chemical safety and hazard classification.

    Business Rules:
    1. Exposure limits adjusted for concentration and duration
    2. Mixture hazards use proprietary algorithms
    3. Incompatibility matrix based on incident data
    4. PPE requirements based on exposure scenario

    Args:
        compound_id: Internal compound identifier
        chemical_formula: Chemical formula or CAS
        concentration: Concentration percentage
        exposure_route: Route of exposure
        exposure_duration: Duration category
        mixing_compounds: Other compounds in mixture

    Returns:
        Safety assessment with classifications and requirements
    """
    hazard_db = load_chemical_hazards()

    # Look up compound data
    compound_data = hazard_db["compounds"].get(
        chemical_formula,
        hazard_db["compounds"]["default"]
    )

    # Duration factors
    duration_factors = {
        "acute": 1.0,
        "short-term": 0.8,
        "chronic": 0.5
    }
    duration_factor = duration_factors.get(exposure_duration, 1.0)

    # Calculate exposure limits
    base_oel = compound_data["exposure_limits"]["oel_ppm"]
    exposure_limits = {
        "oel_ppm": calculate_exposure_limit(base_oel, concentration, duration_factor),
        "pel_ppm": compound_data["exposure_limits"]["pel_ppm"],
        "tlv_ppm": compound_data["exposure_limits"]["tlv_ppm"],
        "stel_ppm": compound_data["exposure_limits"].get("stel_ppm"),
        "idlh_ppm": compound_data["exposure_limits"].get("idlh_ppm")
    }

    # Get hazard classifications
    hazard_classification = {
        "flammability": compound_data["ghs_classification"]["flammable_liquid"],
        "acute_toxicity": compound_data["ghs_classification"]["acute_toxicity"],
        "skin_corrosion": compound_data["ghs_classification"].get("skin_corrosion"),
        "eye_damage": compound_data["ghs_classification"].get("eye_damage"),
        "skin_sensitization": compound_data["ghs_classification"].get("skin_sensitization"),
        "carcinogenicity": compound_data["ghs_classification"].get("carcinogenicity"),
        "signal_word": compound_data["ghs_classification"]["signal_word"]
    }

    # Check incompatibilities
    incompatibilities = check_incompatibility(
        chemical_formula,
        mixing_compounds,
        hazard_db["incompatibility_matrix"]
    )

    # Determine PPE requirements
    ppe_requirements = determine_ppe(
        hazard_classification,
        exposure_route,
        concentration
    )

    # Generate handling instructions
    handling_instructions = compound_data.get("handling_instructions", [])
    if incompatibilities:
        handling_instructions.append("DO NOT mix with incompatible materials")
    if hazard_classification["flammability"] and hazard_classification["flammability"] <= 2:
        handling_instructions.append("Keep away from heat, sparks, and open flames")
        handling_instructions.append("Ground and bond containers during transfer")

    # Storage requirements
    storage_requirements = compound_data.get("storage", {})

    return {
        "compound_id": compound_id,
        "chemical_formula": chemical_formula,
        "concentration": concentration,
        "hazard_classification": hazard_classification,
        "exposure_limits": exposure_limits,
        "ppe_requirements": ppe_requirements,
        "handling_instructions": handling_instructions,
        "incompatibilities": incompatibilities,
        "storage_requirements": storage_requirements,
        "exposure_route": exposure_route,
        "exposure_duration": exposure_duration,
        "ghs_pictograms": compound_data.get("ghs_pictograms", [])
    }


if __name__ == "__main__":
    import json
    result = analyze_safety(
        compound_id="CHEM-2024-001",
        chemical_formula="CH3OH",
        concentration=99.5,
        exposure_route="inhalation",
        exposure_duration="short-term",
        mixing_compounds=["H2O", "HCl"]
    )
    print(json.dumps(result, indent=2))
