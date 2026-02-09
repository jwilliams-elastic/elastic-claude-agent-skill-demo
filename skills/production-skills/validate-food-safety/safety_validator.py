"""
Food Safety Validation Module

Implements food product safety compliance checking including
allergen verification and regulatory requirements.
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


def load_food_standards() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    ingredient_limits_data = load_csv_as_dict("ingredient_limits.csv")
    facility_rules_data = load_csv_as_dict("facility_rules.csv")
    claim_rules_data = load_csv_as_dict("claim_rules.csv")
    nutrition_limits_data = load_key_value_csv("nutrition_limits.csv")
    params = load_parameters()
    return {
        "ingredient_limits": ingredient_limits_data,
        "facility_rules": facility_rules_data,
        "claim_rules": claim_rules_data,
        "nutrition_limits": nutrition_limits_data,
        **params
    }


def check_allergen_labeling(
    ingredients: List[Dict],
    allergen_info: Dict,
    allergen_rules: Dict
) -> Dict[str, Any]:
    """Check allergen declaration compliance."""
    issues = []
    major_allergens = allergen_rules.get("major_allergens", [])

    declared_allergens = set(allergen_info.get("contains", []))
    may_contain = set(allergen_info.get("may_contain", []))

    # Check each ingredient for allergen content
    detected_allergens = set()
    for ingredient in ingredients:
        name = ingredient.get("name", "").lower()
        allergen_mapping = allergen_rules.get("ingredient_allergen_mapping", {})

        for allergen, keywords in allergen_mapping.items():
            if any(kw in name for kw in keywords):
                detected_allergens.add(allergen)

    # Verify all detected allergens are declared
    undeclared = detected_allergens - declared_allergens
    for allergen in undeclared:
        issues.append(f"Allergen '{allergen}' detected but not declared")

    # Check for over-declaration
    over_declared = declared_allergens - detected_allergens
    for allergen in over_declared:
        if allergen not in may_contain:
            issues.append(f"Allergen '{allergen}' declared but not found in ingredients")

    return {
        "compliant": len(issues) == 0,
        "detected_allergens": list(detected_allergens),
        "declared_allergens": list(declared_allergens),
        "issues": issues
    }


def validate_ingredient_limits(
    ingredients: List[Dict],
    limits: Dict
) -> Dict[str, Any]:
    """Validate ingredient quantities against regulatory limits."""
    violations = []
    warnings = []

    for ingredient in ingredients:
        name = ingredient.get("name", "").lower()
        percentage = ingredient.get("percentage", 0)
        ppm = ingredient.get("ppm")

        # Check against additive limits
        for additive, limit_info in limits.get("additives", {}).items():
            if additive in name:
                max_ppm = limit_info.get("max_ppm")
                if ppm and max_ppm and ppm > max_ppm:
                    violations.append({
                        "ingredient": name,
                        "limit_type": "max_ppm",
                        "actual": ppm,
                        "limit": max_ppm
                    })

        # Check preservative limits
        for preservative, max_pct in limits.get("preservatives", {}).items():
            if preservative in name and percentage > max_pct:
                violations.append({
                    "ingredient": name,
                    "limit_type": "max_percentage",
                    "actual": percentage,
                    "limit": max_pct
                })

    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "warnings": warnings
    }


def assess_cross_contamination(
    manufacturing_info: Dict,
    allergen_info: Dict,
    facility_rules: Dict
) -> Dict[str, Any]:
    """Assess cross-contamination risk from manufacturing."""
    risks = []
    risk_score = 0

    facility_type = manufacturing_info.get("facility_type", "unknown")
    shared_lines = manufacturing_info.get("shared_lines", False)
    haccp_certified = manufacturing_info.get("haccp_certified", False)

    # Check facility risks
    facility_risk = facility_rules.get("facility_types", {}).get(facility_type, {})
    common_cross_contact = facility_risk.get("common_cross_contact", [])

    may_contain = set(allergen_info.get("may_contain", []))

    # Identify undisclosed cross-contact risks
    for allergen in common_cross_contact:
        if allergen not in may_contain:
            risks.append({
                "type": "potential_cross_contact",
                "allergen": allergen,
                "source": facility_type,
                "severity": "medium"
            })
            risk_score += 20

    if shared_lines:
        risks.append({
            "type": "shared_production_lines",
            "severity": "high"
        })
        risk_score += 30

    if not haccp_certified:
        risks.append({
            "type": "no_haccp_certification",
            "severity": "high"
        })
        risk_score += 25

    return {
        "risk_score": min(100, risk_score),
        "risks": risks,
        "haccp_status": haccp_certified
    }


def validate_label_claims(
    label_claims: List[str],
    ingredients: List[Dict],
    claim_rules: Dict
) -> Dict[str, Any]:
    """Validate marketing claims on product label."""
    violations = []

    for claim in label_claims:
        claim_lower = claim.lower()
        claim_requirements = claim_rules.get(claim_lower, {})

        if not claim_requirements:
            continue

        # Check prohibited ingredients for this claim
        prohibited = claim_requirements.get("prohibited_ingredients", [])
        for ingredient in ingredients:
            name = ingredient.get("name", "").lower()
            for prohibited_item in prohibited:
                if prohibited_item in name:
                    violations.append({
                        "claim": claim,
                        "violation": f"Contains prohibited ingredient '{name}' for '{claim}' claim"
                    })

        # Check required certifications
        required_cert = claim_requirements.get("requires_certification")
        if required_cert:
            violations.append({
                "claim": claim,
                "warning": f"Claim '{claim}' may require {required_cert} certification"
            })

    return {
        "compliant": len([v for v in violations if "violation" in v]) == 0,
        "violations": violations
    }


def validate_food_safety(
    product_id: str,
    ingredients: List[Dict],
    allergen_info: Dict,
    manufacturing_info: Dict,
    label_claims: List[str],
    nutrition_facts: Dict
) -> Dict[str, Any]:
    """
    Validate food product safety compliance.

    Business Rules:
    1. Major allergen declaration verification
    2. Ingredient limit validation
    3. Cross-contamination risk assessment
    4. Label claim compliance

    Args:
        product_id: Product identifier
        ingredients: Ingredient list
        allergen_info: Allergen declarations
        manufacturing_info: Facility details
        label_claims: Marketing claims
        nutrition_facts: Nutritional information

    Returns:
        Food safety validation results
    """
    standards = load_food_standards()

    # Allergen review
    allergen_review = check_allergen_labeling(
        ingredients,
        allergen_info,
        standards.get("allergen_rules", {})
    )

    # Ingredient limits
    ingredient_result = validate_ingredient_limits(
        ingredients,
        standards.get("ingredient_limits", {})
    )

    # Cross-contamination
    contamination_result = assess_cross_contamination(
        manufacturing_info,
        allergen_info,
        standards.get("facility_rules", {})
    )

    # Label claims
    label_result = validate_label_claims(
        label_claims,
        ingredients,
        standards.get("claim_rules", {})
    )

    # Compile issues
    ingredient_issues = ingredient_result.get("violations", [])
    label_violations = label_result.get("violations", [])

    # Determine overall compliance
    all_compliant = (
        allergen_review["compliant"] and
        ingredient_result["compliant"] and
        label_result["compliant"]
    )

    if all_compliant and contamination_result["risk_score"] < 30:
        compliance_status = "COMPLIANT"
        risk_level = "low"
    elif all_compliant:
        compliance_status = "COMPLIANT_WITH_WARNINGS"
        risk_level = "medium"
    else:
        compliance_status = "NON_COMPLIANT"
        risk_level = "high"

    return {
        "product_id": product_id,
        "compliance_status": compliance_status,
        "allergen_review": allergen_review,
        "ingredient_issues": ingredient_issues,
        "label_violations": label_violations,
        "contamination_risk": contamination_result,
        "risk_level": risk_level
    }


if __name__ == "__main__":
    import json
    result = validate_food_safety(
        product_id="PROD-001",
        ingredients=[
            {"name": "wheat flour", "percentage": 45},
            {"name": "sugar", "percentage": 20},
            {"name": "butter", "percentage": 15},
            {"name": "eggs", "percentage": 10}
        ],
        allergen_info={"contains": ["wheat", "milk", "eggs"], "may_contain": ["soy"]},
        manufacturing_info={"facility_type": "bakery", "haccp_certified": True},
        label_claims=["natural", "no artificial colors"],
        nutrition_facts={"calories": 150, "sodium_mg": 200}
    )
    print(json.dumps(result, indent=2))
