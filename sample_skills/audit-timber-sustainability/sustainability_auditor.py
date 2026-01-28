"""
Timber Sustainability Audit Module

Implements certification standard compliance checking for sustainable
forestry operations including FSC, PEFC, and SFI standards.
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


def load_certification_standards() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    certifications_data = load_csv_as_dict("certifications.csv")
    ecosystems_data = load_csv_as_dict("ecosystems.csv")
    scoring_weights_data = load_key_value_csv("scoring_weights.csv")
    severity_definitions_data = load_key_value_csv("severity_definitions.csv")
    params = load_parameters()
    return {
        "certifications": certifications_data,
        "ecosystems": ecosystems_data,
        "scoring_weights": scoring_weights_data,
        "severity_definitions": severity_definitions_data,
        **params
    }


def evaluate_species_diversity(
    species_composition: Dict[str, float],
    requirements: Dict
) -> Dict[str, Any]:
    """Evaluate species diversity against requirements."""
    species_count = len(species_composition)
    max_single_species = max(species_composition.values()) if species_composition else 1.0

    compliant = (
        species_count >= requirements["min_species"] and
        max_single_species <= requirements["max_single_species_pct"]
    )

    return {
        "compliant": compliant,
        "species_count": species_count,
        "dominant_species_pct": round(max_single_species * 100, 1),
        "required_min_species": requirements["min_species"],
        "required_max_dominant": requirements["max_single_species_pct"] * 100
    }


def evaluate_buffer_zones(
    buffer_zones: List[Dict],
    requirements: Dict
) -> Dict[str, Any]:
    """Evaluate buffer zone compliance."""
    findings = []
    all_compliant = True

    for buffer in buffer_zones:
        buffer_type = buffer.get("type")
        req = requirements.get(buffer_type)

        if req:
            if buffer.get("width_m", 0) < req["min_width_m"]:
                all_compliant = False
                findings.append({
                    "type": buffer_type,
                    "issue": f"Buffer width {buffer.get('width_m')}m below required {req['min_width_m']}m",
                    "severity": "major"
                })
            elif not buffer.get("compliant", True):
                all_compliant = False
                findings.append({
                    "type": buffer_type,
                    "issue": "Buffer zone disturbance detected",
                    "severity": "major"
                })

    return {
        "compliant": all_compliant,
        "findings": findings,
        "zones_evaluated": len(buffer_zones)
    }


def evaluate_regeneration(
    regeneration_data: Dict,
    requirements: Dict
) -> Dict[str, Any]:
    """Evaluate regeneration success against standards."""
    seedlings = regeneration_data.get("seedlings_per_ha", 0)
    survival = regeneration_data.get("survival_rate", 0)

    effective_stocking = seedlings * survival

    compliant = effective_stocking >= requirements["min_stocking_per_ha"]

    return {
        "compliant": compliant,
        "effective_stocking": round(effective_stocking, 0),
        "required_stocking": requirements["min_stocking_per_ha"],
        "survival_rate": survival,
        "assessment": "adequate" if compliant else "below_standard"
    }


def calculate_sustainability_score(
    species_eval: Dict,
    buffer_eval: Dict,
    regen_eval: Dict,
    weights: Dict
) -> float:
    """Calculate overall sustainability score."""
    score = 0

    # Species diversity component
    if species_eval["compliant"]:
        score += weights["species_diversity"]
    else:
        score += weights["species_diversity"] * (species_eval["species_count"] / 3)

    # Buffer zone component
    if buffer_eval["compliant"]:
        score += weights["buffer_zones"]
    else:
        non_compliant = len(buffer_eval["findings"])
        score += weights["buffer_zones"] * max(0, 1 - (non_compliant * 0.3))

    # Regeneration component
    if regen_eval["compliant"]:
        score += weights["regeneration"]
    else:
        ratio = regen_eval["effective_stocking"] / regen_eval["required_stocking"]
        score += weights["regeneration"] * min(ratio, 1)

    return round(score * 100, 1)


def audit_sustainability(
    harvest_unit_id: str,
    harvest_volume: float,
    species_composition: Dict[str, float],
    buffer_zones: List[Dict],
    regeneration_data: Dict,
    certification_type: str,
    ecosystem_type: str
) -> Dict[str, Any]:
    """
    Audit timber harvest sustainability compliance.

    Business Rules:
    1. AAC limits based on ecosystem growth models
    2. Buffer zones vary by ecosystem and feature type
    3. Species diversity requirements for biodiversity
    4. Regeneration success criteria by species

    Args:
        harvest_unit_id: Harvest unit identifier
        harvest_volume: Volume harvested
        species_composition: Species percentages
        buffer_zones: Buffer zone data
        regeneration_data: Regeneration survey data
        certification_type: Certification standard
        ecosystem_type: Forest ecosystem type

    Returns:
        Sustainability audit results
    """
    standards = load_certification_standards()

    findings = []
    corrective_actions = []

    # Get certification-specific requirements
    cert_standards = standards["certifications"].get(
        certification_type,
        standards["certifications"]["FSC"]
    )

    # Get ecosystem-specific parameters
    ecosystem_params = standards["ecosystems"].get(
        ecosystem_type,
        standards["ecosystems"]["default"]
    )

    # Evaluate species diversity
    species_eval = evaluate_species_diversity(
        species_composition,
        cert_standards["species_requirements"]
    )

    if not species_eval["compliant"]:
        findings.append({
            "code": "SD-001",
            "category": "species_diversity",
            "severity": "major",
            "description": f"Species diversity below standard: {species_eval['species_count']} species, {species_eval['dominant_species_pct']}% dominant"
        })
        corrective_actions.append("Increase species diversity in future harvests")

    # Evaluate buffer zones
    buffer_eval = evaluate_buffer_zones(
        buffer_zones,
        cert_standards["buffer_requirements"]
    )

    for finding in buffer_eval["findings"]:
        findings.append({
            "code": f"BZ-{len(findings)+1:03d}",
            "category": "buffer_zones",
            "severity": finding["severity"],
            "description": f"{finding['type']}: {finding['issue']}"
        })
        corrective_actions.append(f"Restore {finding['type']} buffer zone to required width")

    # Evaluate regeneration
    regen_eval = evaluate_regeneration(
        regeneration_data,
        cert_standards["regeneration_requirements"]
    )

    if not regen_eval["compliant"]:
        findings.append({
            "code": "RG-001",
            "category": "regeneration",
            "severity": "major",
            "description": f"Regeneration stocking {regen_eval['effective_stocking']}/ha below required {regen_eval['required_stocking']}/ha"
        })
        corrective_actions.append("Implement supplemental planting to achieve stocking targets")

    # Check harvest volume against AAC
    aac_limit = ecosystem_params["annual_allowable_cut_m3_per_ha"]
    # Assuming 100 ha unit for example
    if harvest_volume > aac_limit * 100:
        findings.append({
            "code": "AAC-001",
            "category": "harvest_volume",
            "severity": "critical",
            "description": f"Harvest volume exceeds annual allowable cut"
        })
        corrective_actions.append("Reduce harvest intensity in subsequent years")

    # Calculate sustainability score
    sustainability_score = calculate_sustainability_score(
        species_eval,
        buffer_eval,
        regen_eval,
        standards["scoring_weights"]
    )

    # Determine compliance status
    critical_findings = [f for f in findings if f["severity"] == "critical"]
    major_findings = [f for f in findings if f["severity"] == "major"]

    if critical_findings:
        compliance_status = "NON_COMPLIANT"
        certification_eligible = False
    elif len(major_findings) > 2:
        compliance_status = "NON_COMPLIANT"
        certification_eligible = False
    elif major_findings:
        compliance_status = "CONDITIONAL"
        certification_eligible = True
    else:
        compliance_status = "COMPLIANT"
        certification_eligible = True

    return {
        "harvest_unit_id": harvest_unit_id,
        "compliance_status": compliance_status,
        "certification_eligible": certification_eligible,
        "certification_type": certification_type,
        "sustainability_score": sustainability_score,
        "findings": findings,
        "corrective_actions": corrective_actions,
        "evaluations": {
            "species_diversity": species_eval,
            "buffer_zones": buffer_eval,
            "regeneration": regen_eval
        },
        "harvest_volume_m3": harvest_volume,
        "ecosystem_type": ecosystem_type
    }


if __name__ == "__main__":
    import json
    result = audit_sustainability(
        harvest_unit_id="HU-2024-001",
        harvest_volume=5000,
        species_composition={"douglas_fir": 0.6, "western_red_cedar": 0.3, "hemlock": 0.1},
        buffer_zones=[
            {"type": "riparian", "width_m": 30, "compliant": True},
            {"type": "wetland", "width_m": 25, "compliant": True}
        ],
        regeneration_data={"seedlings_per_ha": 1200, "survival_rate": 0.85},
        certification_type="FSC",
        ecosystem_type="temperate_rainforest"
    )
    print(json.dumps(result, indent=2))
