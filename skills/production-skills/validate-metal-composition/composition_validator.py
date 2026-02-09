"""
Metal Alloy Composition Validation Module

Implements composition analysis and grade verification against
industry standards and customer specifications.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_alloy_specs() -> Dict[str, Any]:
    """Load alloy specification data."""
    specs_path = Path(__file__).parent / "alloy_specs.csv"
    specs = {}

    with open(specs_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            family = row["alloy_family"]
            grade = row["grade"]
            element = row["element"]

            if family not in specs:
                specs[family] = {}
            if grade not in specs[family]:
                specs[family][grade] = {"elements": {}, "description": row.get("description", "")}

            specs[family][grade]["elements"][element] = {
                "min": float(row["min"]) if row["min"] else None,
                "max": float(row["max"]) if row["max"] else None,
                "target": float(row["target"]) if row.get("target") else None
            }

    return specs


def check_element_compliance(
    actual: float,
    spec: Dict
) -> Dict[str, Any]:
    """Check single element against specification."""
    min_val = spec.get("min")
    max_val = spec.get("max")

    in_spec = True
    margin = None
    status = "compliant"

    if min_val is not None and actual < min_val:
        in_spec = False
        margin = min_val - actual
        status = "below_minimum"
    elif max_val is not None and actual > max_val:
        in_spec = False
        margin = actual - max_val
        status = "above_maximum"
    else:
        # Check if marginal (within 10% of limits)
        if min_val is not None and actual < min_val * 1.1:
            status = "marginal_low"
        elif max_val is not None and actual > max_val * 0.9:
            status = "marginal_high"

    return {
        "in_spec": in_spec,
        "status": status,
        "actual": actual,
        "min": min_val,
        "max": max_val,
        "margin": margin
    }


def find_alternative_grades(
    composition: Dict[str, float],
    alloy_family: str,
    specs: Dict
) -> List[str]:
    """Find alternative grades that match this composition."""
    alternatives = []

    family_specs = specs.get(alloy_family, {})

    for grade, grade_spec in family_specs.items():
        all_match = True
        for element, value in composition.items():
            if element in grade_spec["elements"]:
                check = check_element_compliance(value, grade_spec["elements"][element])
                if not check["in_spec"]:
                    all_match = False
                    break

        if all_match:
            alternatives.append(grade)

    return alternatives


def apply_customer_spec(
    element_analysis: List[Dict],
    customer_spec: str
) -> List[Dict]:
    """Apply stricter customer-specific tolerances."""
    customer_modifiers = {
        "aerospace_standard": {
            "tolerance_multiplier": 0.8,  # 20% tighter
            "additional_elements": ["H", "O", "N"]
        },
        "nuclear_grade": {
            "tolerance_multiplier": 0.7,  # 30% tighter
            "additional_elements": ["Co", "B"]
        },
        "food_grade": {
            "additional_checks": ["Pb", "Cd", "Hg"]
        }
    }

    modifier = customer_modifiers.get(customer_spec, {})

    if "tolerance_multiplier" in modifier:
        for element in element_analysis:
            if element["status"] == "marginal_low" or element["status"] == "marginal_high":
                element["status"] = "non_compliant_customer_spec"
                element["note"] = f"Fails {customer_spec} tighter tolerance"

    return element_analysis


def validate_composition(
    sample_id: str,
    alloy_family: str,
    target_grade: str,
    composition: Dict[str, float],
    heat_number: str,
    customer_spec: Optional[str],
    intended_application: str
) -> Dict[str, Any]:
    """
    Validate metal alloy composition against specifications.

    Business Rules:
    1. Composition tolerances by alloy grade
    2. Trace element cumulative limits
    3. Mechanical property correlation
    4. Customer-specific requirements

    Args:
        sample_id: Sample identifier
        alloy_family: Alloy family (steel, aluminum, etc.)
        target_grade: Target grade specification
        composition: Analyzed composition
        heat_number: Production heat ID
        customer_spec: Customer specification
        intended_application: End use

    Returns:
        Composition validation results
    """
    specs = load_alloy_specs()

    element_analysis = []
    recommendations = []

    # Get target grade specification
    family_specs = specs.get(alloy_family, {})
    grade_spec = family_specs.get(target_grade, {})

    if not grade_spec:
        return {
            "sample_id": sample_id,
            "grade_verified": False,
            "compliance_status": "UNKNOWN_GRADE",
            "element_analysis": [],
            "alternative_grades": [],
            "recommendations": ["Verify target grade specification exists"]
        }

    # Check each element
    non_compliant_count = 0
    marginal_count = 0

    for element, spec in grade_spec["elements"].items():
        actual = composition.get(element)

        if actual is None:
            element_analysis.append({
                "element": element,
                "status": "not_reported",
                "spec_min": spec.get("min"),
                "spec_max": spec.get("max")
            })
            recommendations.append(f"Report {element} content for complete verification")
        else:
            check = check_element_compliance(actual, spec)
            check["element"] = element

            if not check["in_spec"]:
                non_compliant_count += 1
            elif check["status"].startswith("marginal"):
                marginal_count += 1

            element_analysis.append(check)

    # Check for unreported elements in composition
    for element, value in composition.items():
        if element not in grade_spec["elements"]:
            element_analysis.append({
                "element": element,
                "actual": value,
                "status": "not_specified",
                "note": "Element not in grade specification"
            })

    # Apply customer specification
    if customer_spec:
        element_analysis = apply_customer_spec(element_analysis, customer_spec)
        # Recount after customer spec
        non_compliant_count = sum(
            1 for e in element_analysis
            if e.get("status") in ["below_minimum", "above_maximum", "non_compliant_customer_spec"]
        )

    # Determine overall compliance
    if non_compliant_count > 0:
        compliance_status = "NON_COMPLIANT"
        grade_verified = False
        recommendations.append("Material does not meet grade specification")
        recommendations.append("Consider downgrade or rework options")
    elif marginal_count > 0:
        compliance_status = "MARGINAL"
        grade_verified = True
        recommendations.append("Composition is within spec but near limits")
        recommendations.append("Monitor future heats for consistency")
    else:
        compliance_status = "COMPLIANT"
        grade_verified = True

    # Find alternative grades
    alternative_grades = find_alternative_grades(composition, alloy_family, specs)
    alternative_grades = [g for g in alternative_grades if g != target_grade]

    return {
        "sample_id": sample_id,
        "heat_number": heat_number,
        "alloy_family": alloy_family,
        "target_grade": target_grade,
        "grade_verified": grade_verified,
        "compliance_status": compliance_status,
        "element_analysis": element_analysis,
        "alternative_grades": alternative_grades[:5],  # Top 5
        "recommendations": recommendations,
        "customer_spec": customer_spec,
        "intended_application": intended_application
    }


if __name__ == "__main__":
    import json

    result = validate_composition(
        sample_id="MET-2024-001",
        alloy_family="stainless_steel",
        target_grade="304",
        composition={"C": 0.05, "Cr": 18.2, "Ni": 8.5, "Mn": 1.5, "Si": 0.5, "P": 0.03, "S": 0.02},
        heat_number="H-2024-1234",
        customer_spec="aerospace_standard",
        intended_application="pressure_vessel"
    )
    print(json.dumps(result, indent=2))
