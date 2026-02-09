"""
Operational Risk Assessment Module

Implements operational risk assessment using
risk categories, control effectiveness, and KRI monitoring.
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


def load_risk_framework() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    risk_categories_data = load_csv_as_dict("risk_categories.csv")
    impact_scales_data = load_csv_as_dict("impact_scales.csv")
    likelihood_scales_data = load_csv_as_dict("likelihood_scales.csv")
    risk_appetite_data = load_csv_as_dict("risk_appetite.csv")
    control_effectiveness_data = load_csv_as_dict("control_effectiveness.csv")
    kri_thresholds_data = load_csv_as_dict("kri_thresholds.csv")
    basel_event_types_data = load_key_value_csv("basel_event_types.csv")
    params = load_parameters()
    return {
        "risk_categories": risk_categories_data,
        "impact_scales": impact_scales_data,
        "likelihood_scales": likelihood_scales_data,
        "risk_appetite": risk_appetite_data,
        "control_effectiveness": control_effectiveness_data,
        "kri_thresholds": kri_thresholds_data,
        "basel_event_types": basel_event_types_data,
        **params
    }


def calculate_inherent_risk(
    likelihood: int,
    impact: int
) -> Dict[str, Any]:
    """Calculate inherent risk score."""
    inherent_score = likelihood * impact

    if inherent_score <= 5:
        level = "LOW"
    elif inherent_score <= 10:
        level = "MEDIUM"
    elif inherent_score <= 15:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return {
        "likelihood": likelihood,
        "impact": impact,
        "inherent_score": inherent_score,
        "inherent_level": level
    }


def assess_control_effectiveness(
    controls: List[Dict],
    control_config: Dict
) -> Dict[str, Any]:
    """Assess effectiveness of risk controls."""
    if not controls:
        return {
            "overall_effectiveness": "ineffective",
            "residual_factor": 1.0,
            "control_count": 0
        }

    effectiveness_scores = []
    control_details = []

    for control in controls:
        effectiveness = control.get("effectiveness", "weak")
        config = control_config.get(effectiveness, {"rating": 3, "residual_factor": 0.75})

        effectiveness_scores.append(config["rating"])
        control_details.append({
            "control_id": control.get("id", "unknown"),
            "control_type": control.get("type", "detective"),
            "effectiveness": effectiveness,
            "rating": config["rating"]
        })

    avg_rating = sum(effectiveness_scores) / len(effectiveness_scores)

    if avg_rating <= 1.5:
        overall = "strong"
        residual_factor = 0.25
    elif avg_rating <= 2.5:
        overall = "adequate"
        residual_factor = 0.50
    elif avg_rating <= 3.5:
        overall = "weak"
        residual_factor = 0.75
    else:
        overall = "ineffective"
        residual_factor = 1.0

    return {
        "overall_effectiveness": overall,
        "residual_factor": residual_factor,
        "average_rating": round(avg_rating, 2),
        "control_count": len(controls),
        "control_details": control_details
    }


def calculate_residual_risk(
    inherent_score: int,
    residual_factor: float
) -> Dict[str, Any]:
    """Calculate residual risk after controls."""
    residual_score = inherent_score * residual_factor

    if residual_score <= 5:
        level = "LOW"
    elif residual_score <= 10:
        level = "MEDIUM"
    elif residual_score <= 15:
        level = "HIGH"
    else:
        level = "CRITICAL"

    return {
        "residual_score": round(residual_score, 1),
        "residual_level": level,
        "risk_reduction_pct": round((1 - residual_factor) * 100, 1)
    }


def evaluate_kris(
    kri_values: Dict[str, float],
    kri_thresholds: Dict
) -> Dict[str, Any]:
    """Evaluate Key Risk Indicators."""
    kri_status = []
    breach_count = 0
    warning_count = 0

    for kri_name, value in kri_values.items():
        thresholds = kri_thresholds.get(kri_name, {})
        green = thresholds.get("green", float('inf'))
        amber = thresholds.get("amber", float('inf'))
        red = thresholds.get("red", float('inf'))

        if value <= green:
            status = "GREEN"
        elif value <= amber:
            status = "AMBER"
            warning_count += 1
        else:
            status = "RED"
            breach_count += 1

        kri_status.append({
            "kri": kri_name,
            "value": value,
            "status": status,
            "thresholds": {"green": green, "amber": amber, "red": red}
        })

    return {
        "kri_assessments": kri_status,
        "breach_count": breach_count,
        "warning_count": warning_count,
        "overall_kri_status": "RED" if breach_count > 0 else "AMBER" if warning_count > 0 else "GREEN"
    }


def categorize_risk(
    risk_description: str,
    risk_categories: Dict
) -> Dict[str, Any]:
    """Categorize risk by type."""
    # Simple keyword-based categorization
    keywords = {
        "people": ["fraud", "employee", "staff", "unauthorized", "workplace"],
        "process": ["error", "transaction", "execution", "documentation"],
        "systems": ["system", "IT", "cyber", "data", "technology"],
        "external": ["vendor", "disaster", "regulatory", "third-party"]
    }

    description_lower = risk_description.lower()
    category_scores = {}

    for category, terms in keywords.items():
        score = sum(1 for term in terms if term in description_lower)
        if score > 0:
            category_scores[category] = score

    if category_scores:
        primary_category = max(category_scores, key=category_scores.get)
    else:
        primary_category = "process"

    return {
        "primary_category": primary_category,
        "weight": risk_categories.get(primary_category, {}).get("weight", 0.25)
    }


def determine_risk_response(
    residual_score: float,
    risk_appetite: Dict
) -> Dict[str, Any]:
    """Determine appropriate risk response."""
    for level, config in sorted(risk_appetite.items(), key=lambda x: x[1]["threshold"]):
        if residual_score <= config["threshold"]:
            return {
                "response_level": level,
                "recommended_action": config["action"],
                "threshold": config["threshold"]
            }

    return {
        "response_level": "critical",
        "recommended_action": "immediate_action",
        "threshold": 25
    }


def calculate_expected_loss(
    probability: float,
    impact_amount: float,
    residual_factor: float
) -> Dict[str, Any]:
    """Calculate expected loss from risk."""
    gross_expected_loss = probability * impact_amount
    net_expected_loss = gross_expected_loss * residual_factor

    return {
        "gross_expected_loss": round(gross_expected_loss, 2),
        "net_expected_loss": round(net_expected_loss, 2),
        "loss_reduction": round(gross_expected_loss - net_expected_loss, 2)
    }


def assess_operational_risk(
    risk_id: str,
    risk_description: str,
    likelihood: int,
    financial_impact: float,
    reputational_impact: int,
    controls: List[Dict],
    kri_values: Dict[str, float],
    business_unit: str,
    assessment_date: str
) -> Dict[str, Any]:
    """
    Assess operational risk.

    Business Rules:
    1. Inherent risk calculation (likelihood x impact)
    2. Control effectiveness evaluation
    3. Residual risk determination
    4. KRI monitoring and thresholds

    Args:
        risk_id: Risk identifier
        risk_description: Description of the risk
        likelihood: Likelihood score (1-5)
        financial_impact: Potential financial impact
        reputational_impact: Reputational impact score (1-5)
        controls: List of mitigating controls
        kri_values: Current KRI values
        business_unit: Business unit
        assessment_date: Assessment date

    Returns:
        Operational risk assessment results
    """
    framework = load_risk_framework()

    # Determine impact score from financial impact
    impact_scales = framework.get("impact_scales", {}).get("financial", {})
    impact_score = 1
    for score, config in impact_scales.items():
        range_vals = config.get("range", [0, 100000])
        if range_vals[1] is None or financial_impact < range_vals[1]:
            if financial_impact >= range_vals[0]:
                impact_score = int(score)
                break

    # Use higher of financial or reputational impact
    impact_score = max(impact_score, reputational_impact)

    # Calculate inherent risk
    inherent_risk = calculate_inherent_risk(likelihood, impact_score)

    # Assess controls
    control_assessment = assess_control_effectiveness(
        controls,
        framework.get("control_effectiveness", {})
    )

    # Calculate residual risk
    residual_risk = calculate_residual_risk(
        inherent_risk["inherent_score"],
        control_assessment["residual_factor"]
    )

    # Evaluate KRIs
    kri_assessment = evaluate_kris(
        kri_values,
        framework.get("kri_thresholds", {})
    )

    # Categorize risk
    risk_category = categorize_risk(
        risk_description,
        framework.get("risk_categories", {})
    )

    # Determine response
    risk_response = determine_risk_response(
        residual_risk["residual_score"],
        framework.get("risk_appetite", {})
    )

    # Calculate expected loss
    probability = likelihood / 5  # Convert to probability
    expected_loss = calculate_expected_loss(
        probability,
        financial_impact,
        control_assessment["residual_factor"]
    )

    return {
        "risk_id": risk_id,
        "assessment_date": assessment_date,
        "business_unit": business_unit,
        "risk_description": risk_description,
        "risk_category": risk_category,
        "inherent_risk": inherent_risk,
        "control_assessment": control_assessment,
        "residual_risk": residual_risk,
        "kri_assessment": kri_assessment,
        "risk_response": risk_response,
        "expected_loss": expected_loss,
        "overall_risk_rating": residual_risk["residual_level"]
    }


if __name__ == "__main__":
    import json
    result = assess_operational_risk(
        risk_id="OPR-001",
        risk_description="System failure causing transaction processing errors",
        likelihood=3,
        financial_impact=1500000,
        reputational_impact=2,
        controls=[
            {"id": "CTL-001", "type": "preventive", "effectiveness": "strong"},
            {"id": "CTL-002", "type": "detective", "effectiveness": "adequate"}
        ],
        kri_values={
            "system_downtime_hours": 6,
            "failed_transactions_pct": 0.3,
            "incident_count": 15
        },
        business_unit="Operations",
        assessment_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
