"""
Compliance Controls Validation Module

Implements control testing and assessment including
effectiveness rating, deficiency identification, and remediation tracking.
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


def load_control_framework() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    control_categories_data = load_csv_as_dict("control_categories.csv")
    control_attributes_data = load_csv_as_dict("control_attributes.csv")
    assessment_ratings_data = load_csv_as_dict("assessment_ratings.csv")
    testing_methods_data = load_csv_as_dict("testing_methods.csv")
    deficiency_severity_data = load_csv_as_dict("deficiency_severity.csv")
    regulatory_frameworks_data = load_csv_as_dict("regulatory_frameworks.csv")
    risk_control_matrix_data = load_csv_as_dict("risk_control_matrix.csv")
    evidence_requirements_data = load_key_value_csv("evidence_requirements.csv")
    params = load_parameters()
    return {
        "control_categories": control_categories_data,
        "control_attributes": control_attributes_data,
        "assessment_ratings": assessment_ratings_data,
        "testing_methods": testing_methods_data,
        "deficiency_severity": deficiency_severity_data,
        "regulatory_frameworks": regulatory_frameworks_data,
        "risk_control_matrix": risk_control_matrix_data,
        "evidence_requirements": evidence_requirements_data,
        **params
    }


def calculate_control_score(
    test_results: Dict,
    control_attributes: Dict
) -> Dict[str, Any]:
    """Calculate control effectiveness score."""
    # Base score from test pass rate
    tests_passed = test_results.get("tests_passed", 0)
    total_tests = test_results.get("total_tests", 1)
    pass_rate = tests_passed / total_tests if total_tests > 0 else 0

    # Automation adjustment
    automation_level = test_results.get("automation_level", "manual")
    auto_config = control_attributes.get("automation_level", {}).get(automation_level, {})
    reliability_factor = auto_config.get("reliability", 0.70)

    # Frequency adjustment
    frequency = test_results.get("frequency", "monthly")
    freq_config = control_attributes.get("frequency", {}).get(frequency, {})
    frequency_multiplier = freq_config.get("effectiveness_multiplier", 1.0)

    # Calculate adjusted score
    raw_score = pass_rate * 100
    adjusted_score = raw_score * reliability_factor * frequency_multiplier

    return {
        "pass_rate": round(pass_rate * 100, 1),
        "automation_level": automation_level,
        "reliability_factor": reliability_factor,
        "frequency": frequency,
        "frequency_multiplier": frequency_multiplier,
        "raw_score": round(raw_score, 1),
        "adjusted_score": round(adjusted_score, 1)
    }


def rate_control_effectiveness(
    score: float,
    ratings: Dict
) -> Dict[str, Any]:
    """Rate control effectiveness based on score."""
    for rating_name, config in sorted(
        ratings.items(),
        key=lambda x: x[1].get("score_range", {}).get("min", 0),
        reverse=True
    ):
        score_range = config.get("score_range", {})
        if score >= score_range.get("min", 0):
            return {
                "rating": rating_name.upper().replace("_", " "),
                "score": score,
                "description": config.get("description", ""),
                "recommended_action": config.get("action", "")
            }

    return {
        "rating": "INEFFECTIVE",
        "score": score,
        "description": "Control not achieving objectives",
        "recommended_action": "redesign"
    }


def assess_testing_reliability(
    testing_method: str,
    sample_size: int,
    population_size: int,
    testing_methods: Dict
) -> Dict[str, Any]:
    """Assess reliability of testing approach."""
    method_config = testing_methods.get(testing_method, {})
    base_reliability = method_config.get("reliability", 0.70)

    # Adjust for sample coverage
    if population_size > 0:
        sample_coverage = sample_size / population_size
        coverage_factor = min(1.0, sample_coverage * 2)  # Max factor at 50% coverage
    else:
        coverage_factor = 1.0

    adjusted_reliability = base_reliability * coverage_factor

    return {
        "testing_method": testing_method,
        "method_description": method_config.get("description", ""),
        "base_reliability": base_reliability,
        "sample_size": sample_size,
        "population_size": population_size,
        "sample_coverage_pct": round(sample_size / population_size * 100, 1) if population_size > 0 else 100,
        "adjusted_reliability": round(adjusted_reliability, 3)
    }


def classify_deficiency(
    deficiency_data: Dict,
    severity_config: Dict
) -> Dict[str, Any]:
    """Classify deficiency severity."""
    impact = deficiency_data.get("potential_impact", "low")
    likelihood = deficiency_data.get("likelihood", "possible")
    compensating_controls = deficiency_data.get("compensating_controls", False)

    # Determine base severity
    if impact == "material" and likelihood == "likely":
        severity = "material_weakness"
    elif impact == "significant" or (impact == "material" and likelihood == "possible"):
        severity = "significant_deficiency"
    else:
        severity = "control_deficiency"

    # Reduce severity if compensating controls exist
    if compensating_controls and severity != "control_deficiency":
        severity_order = ["control_deficiency", "significant_deficiency", "material_weakness"]
        current_index = severity_order.index(severity)
        if current_index > 0:
            severity = severity_order[current_index - 1]

    config = severity_config.get(severity, {})

    return {
        "severity": severity.upper().replace("_", " "),
        "potential_impact": impact,
        "likelihood": likelihood,
        "compensating_controls_exist": compensating_controls,
        "reporting_required": config.get("reporting_required", False),
        "remediation_timeline_days": config.get("remediation_timeline_days", 365)
    }


def evaluate_control_category(
    category_name: str,
    category_config: Dict,
    controls: List[Dict]
) -> Dict[str, Any]:
    """Evaluate all controls in a category."""
    if not controls:
        return {
            "category": category_name,
            "controls_tested": 0,
            "error": "No controls to evaluate"
        }

    total_weighted_score = 0
    control_results = []

    for control in controls:
        control_id = control.get("control_id", "")
        score = control.get("effectiveness_score", 0)
        weight = 1 / len(controls)  # Equal weighting

        total_weighted_score += score * weight

        control_results.append({
            "control_id": control_id,
            "control_name": control.get("control_name", ""),
            "score": score,
            "rating": control.get("rating", "")
        })

    category_score = total_weighted_score
    effectiveness_weight = category_config.get("effectiveness_weight", 0.25)

    return {
        "category": category_name,
        "category_description": category_config.get("description", ""),
        "effectiveness_weight": effectiveness_weight,
        "controls_tested": len(controls),
        "category_score": round(category_score, 1),
        "weighted_contribution": round(category_score * effectiveness_weight, 2),
        "control_details": control_results
    }


def identify_gaps(
    control_results: List[Dict],
    risk_control_matrix: Dict
) -> List[Dict]:
    """Identify control gaps based on risk assessment."""
    gaps = []

    for control in control_results:
        risk_level = control.get("risk_level", "medium")
        control_count = control.get("active_controls", 0)
        rating = control.get("rating", "")

        risk_config = risk_control_matrix.get(risk_level, {})
        min_controls = risk_config.get("min_controls", 1)

        # Check for insufficient controls
        if control_count < min_controls:
            gaps.append({
                "gap_type": "INSUFFICIENT_CONTROLS",
                "risk_area": control.get("risk_area", ""),
                "risk_level": risk_level,
                "required_controls": min_controls,
                "actual_controls": control_count,
                "gap_description": f"Risk area has {control_count} controls, requires minimum {min_controls}"
            })

        # Check for ineffective controls
        if rating in ["INEFFECTIVE", "NEEDS IMPROVEMENT"]:
            gaps.append({
                "gap_type": "INEFFECTIVE_CONTROL",
                "risk_area": control.get("risk_area", ""),
                "risk_level": risk_level,
                "control_rating": rating,
                "gap_description": f"Control rated as {rating}, requires remediation"
            })

    return gaps


def generate_remediation_plan(
    deficiencies: List[Dict],
    gaps: List[Dict]
) -> List[Dict]:
    """Generate remediation plan for identified issues."""
    remediation_items = []
    priority_order = {"MATERIAL WEAKNESS": 0, "SIGNIFICANT DEFICIENCY": 1, "CONTROL DEFICIENCY": 2}

    # Add deficiency remediation
    for deficiency in deficiencies:
        severity = deficiency.get("severity", "CONTROL DEFICIENCY")
        timeline = deficiency.get("remediation_timeline_days", 365)

        remediation_items.append({
            "item_type": "DEFICIENCY",
            "severity": severity,
            "priority": priority_order.get(severity, 3),
            "description": deficiency.get("description", ""),
            "remediation_action": "Design and implement control enhancement",
            "timeline_days": timeline,
            "owner": "Control Owner TBD"
        })

    # Add gap remediation
    for gap in gaps:
        gap_type = gap.get("gap_type", "")
        risk_level = gap.get("risk_level", "medium")

        if gap_type == "INSUFFICIENT_CONTROLS":
            action = "Implement additional controls"
            timeline = 90 if risk_level == "high" else 180
        else:
            action = "Enhance existing control effectiveness"
            timeline = 60 if risk_level == "high" else 120

        remediation_items.append({
            "item_type": "GAP",
            "gap_type": gap_type,
            "risk_level": risk_level,
            "priority": 1 if risk_level == "high" else 2,
            "description": gap.get("gap_description", ""),
            "remediation_action": action,
            "timeline_days": timeline,
            "owner": "Control Owner TBD"
        })

    # Sort by priority
    remediation_items.sort(key=lambda x: x.get("priority", 3))

    return remediation_items


def validate_compliance_controls(
    assessment_id: str,
    entity_name: str,
    framework: str,
    control_tests: List[Dict],
    deficiency_data: List[Dict],
    risk_assessments: List[Dict],
    assessment_period: str,
    assessment_date: str
) -> Dict[str, Any]:
    """
    Validate compliance controls.

    Business Rules:
    1. Control effectiveness scoring
    2. Deficiency classification
    3. Gap identification
    4. Remediation planning

    Args:
        assessment_id: Assessment identifier
        entity_name: Entity being assessed
        framework: Regulatory framework (sox, coso, cobit)
        control_tests: Control test results
        deficiency_data: Identified deficiencies
        risk_assessments: Risk area assessments
        assessment_period: Period assessed
        assessment_date: Assessment date

    Returns:
        Compliance control validation results
    """
    config = load_control_framework()
    control_categories = config.get("control_categories", {})
    control_attributes = config.get("control_attributes", {})
    assessment_ratings = config.get("assessment_ratings", {})
    deficiency_severity = config.get("deficiency_severity", {})
    testing_methods = config.get("testing_methods", {})
    risk_control_matrix = config.get("risk_control_matrix", {})

    # Score each control
    scored_controls = []
    for test in control_tests:
        score_result = calculate_control_score(test, control_attributes)
        rating = rate_control_effectiveness(score_result["adjusted_score"], assessment_ratings)

        scored_controls.append({
            "control_id": test.get("control_id", ""),
            "control_name": test.get("control_name", ""),
            "category": test.get("category", ""),
            "effectiveness_score": score_result["adjusted_score"],
            "rating": rating["rating"],
            "recommended_action": rating["recommended_action"],
            "score_details": score_result
        })

    # Group by category
    category_results = []
    for cat_name, cat_config in control_categories.items():
        cat_controls = [c for c in scored_controls if c["category"] == cat_name]
        if cat_controls:
            cat_result = evaluate_control_category(cat_name, cat_config, cat_controls)
            category_results.append(cat_result)

    # Calculate overall score
    total_weighted = sum(c["weighted_contribution"] for c in category_results)
    overall_score = total_weighted / sum(c["effectiveness_weight"] for c in category_results) if category_results else 0

    overall_rating = rate_control_effectiveness(overall_score, assessment_ratings)

    # Classify deficiencies
    classified_deficiencies = []
    for deficiency in deficiency_data:
        classification = classify_deficiency(deficiency, deficiency_severity)
        classified_deficiencies.append({
            **deficiency,
            **classification
        })

    # Identify gaps
    gaps = identify_gaps(risk_assessments, risk_control_matrix)

    # Generate remediation plan
    remediation_plan = generate_remediation_plan(classified_deficiencies, gaps)

    # Summary counts
    deficiency_counts = {
        "material_weakness": sum(1 for d in classified_deficiencies if d["severity"] == "MATERIAL WEAKNESS"),
        "significant_deficiency": sum(1 for d in classified_deficiencies if d["severity"] == "SIGNIFICANT DEFICIENCY"),
        "control_deficiency": sum(1 for d in classified_deficiencies if d["severity"] == "CONTROL DEFICIENCY")
    }

    return {
        "assessment_id": assessment_id,
        "entity_name": entity_name,
        "framework": framework,
        "assessment_date": assessment_date,
        "assessment_period": assessment_period,
        "overall_assessment": {
            "score": round(overall_score, 1),
            "rating": overall_rating["rating"],
            "action_required": overall_rating["recommended_action"]
        },
        "category_results": category_results,
        "control_details": scored_controls,
        "deficiencies": {
            "counts": deficiency_counts,
            "details": classified_deficiencies
        },
        "control_gaps": gaps,
        "remediation_plan": {
            "total_items": len(remediation_plan),
            "high_priority": sum(1 for r in remediation_plan if r["priority"] <= 1),
            "items": remediation_plan
        },
        "assessment_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = validate_compliance_controls(
        assessment_id="CTRL-2026-001",
        entity_name="Corporate Finance Division",
        framework="sox",
        control_tests=[
            {
                "control_id": "CTRL-001",
                "control_name": "Journal Entry Approval",
                "category": "preventive",
                "tests_passed": 48,
                "total_tests": 50,
                "automation_level": "semi_automated",
                "frequency": "daily"
            },
            {
                "control_id": "CTRL-002",
                "control_name": "Bank Reconciliation",
                "category": "detective",
                "tests_passed": 11,
                "total_tests": 12,
                "automation_level": "manual",
                "frequency": "monthly"
            },
            {
                "control_id": "CTRL-003",
                "control_name": "Access Review",
                "category": "preventive",
                "tests_passed": 3,
                "total_tests": 4,
                "automation_level": "fully_automated",
                "frequency": "quarterly"
            }
        ],
        deficiency_data=[
            {
                "description": "Segregation of duties not enforced in AP system",
                "potential_impact": "significant",
                "likelihood": "possible",
                "compensating_controls": True
            }
        ],
        risk_assessments=[
            {
                "risk_area": "Financial Reporting",
                "risk_level": "high",
                "active_controls": 3,
                "rating": "EFFECTIVE"
            },
            {
                "risk_area": "Access Management",
                "risk_level": "medium",
                "active_controls": 1,
                "rating": "NEEDS IMPROVEMENT"
            }
        ],
        assessment_period="2025",
        assessment_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
