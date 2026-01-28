"""
Vehicle Recall Risk Assessment Module

Implements proprietary risk assessment algorithms for identifying
potential recall situations based on field failure data and regulatory requirements.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from collections import Counter



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


def load_risk_thresholds() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    categories_data = load_csv_as_dict("categories.csv")
    risk_scoring_data = load_key_value_csv("risk_scoring.csv")
    geographic_regions_data = load_csv_as_dict("geographic_regions.csv")
    nhtsa_thresholds_data = load_key_value_csv("nhtsa_thresholds.csv")
    params = load_parameters()
    return {
        "categories": categories_data,
        "risk_scoring": risk_scoring_data,
        "geographic_regions": geographic_regions_data,
        "nhtsa_thresholds": nhtsa_thresholds_data,
        **params
    }


def calculate_failure_rate(failure_count: int, vehicles_in_field: int) -> float:
    """Calculate failures per thousand vehicles."""
    if vehicles_in_field == 0:
        return 0.0
    return (failure_count / vehicles_in_field) * 1000


def analyze_geographic_clustering(failure_reports: List[Dict]) -> Dict[str, Any]:
    """Analyze geographic distribution of failures."""
    if not failure_reports:
        return {"clustered": False, "dominant_region": None, "concentration": 0}

    regions = [r.get("region", "unknown") for r in failure_reports]
    region_counts = Counter(regions)

    if not region_counts:
        return {"clustered": False, "dominant_region": None, "concentration": 0}

    dominant_region, count = region_counts.most_common(1)[0]
    concentration = count / len(failure_reports)

    return {
        "clustered": concentration > 0.5,
        "dominant_region": dominant_region,
        "concentration": round(concentration, 2),
        "region_distribution": dict(region_counts)
    }


def analyze_mileage_pattern(failure_reports: List[Dict]) -> Dict[str, Any]:
    """Analyze mileage distribution of failures."""
    mileages = [r.get("mileage", 0) for r in failure_reports if r.get("mileage")]

    if not mileages:
        return {"pattern_detected": False, "average_mileage": 0}

    avg_mileage = sum(mileages) / len(mileages)
    early_failures = sum(1 for m in mileages if m < 30000)
    early_rate = early_failures / len(mileages)

    return {
        "pattern_detected": early_rate > 0.6,
        "average_mileage": round(avg_mileage, 0),
        "early_failure_rate": round(early_rate, 2),
        "indicates_design_issue": early_rate > 0.7
    }


def assess_recall_risk(
    component_id: str,
    failure_count: int,
    vehicles_in_field: int,
    failure_reports: List[Dict],
    component_category: str,
    affected_models: List[str],
    production_date_range: Dict[str, str]
) -> Dict[str, Any]:
    """
    Assess recall risk for a vehicle component.

    Business Rules:
    1. Failure rate thresholds vary by safety criticality
    2. Geographic clustering indicates environmental factors
    3. Mileage patterns identify design life issues
    4. Safety systems have accelerated timelines

    Args:
        component_id: Component part number
        failure_count: Number of failures reported
        vehicles_in_field: Total vehicles with component
        failure_reports: Detailed failure data
        component_category: Safety criticality category
        affected_models: Affected vehicle models
        production_date_range: Production date range

    Returns:
        Risk assessment with recommendations
    """
    thresholds = load_risk_thresholds()

    contributing_factors = []
    risk_score = 0

    # Get category-specific thresholds
    category_thresholds = thresholds["categories"].get(
        component_category,
        thresholds["categories"]["general"]
    )

    # Rule 1: Calculate and evaluate failure rate
    failure_rate = calculate_failure_rate(failure_count, vehicles_in_field)

    rate_threshold = category_thresholds["failure_rate_threshold"]
    if failure_rate >= rate_threshold * 2:
        risk_score += 40
        contributing_factors.append({
            "factor": "HIGH_FAILURE_RATE",
            "description": f"Failure rate {failure_rate:.2f}/1000 exceeds 2x threshold",
            "severity": "critical"
        })
    elif failure_rate >= rate_threshold:
        risk_score += 25
        contributing_factors.append({
            "factor": "ELEVATED_FAILURE_RATE",
            "description": f"Failure rate {failure_rate:.2f}/1000 exceeds threshold",
            "severity": "high"
        })

    # Rule 2: Geographic clustering analysis
    geo_analysis = analyze_geographic_clustering(failure_reports)
    if geo_analysis["clustered"]:
        risk_score += 15
        contributing_factors.append({
            "factor": "GEOGRAPHIC_CLUSTERING",
            "description": f"{geo_analysis['concentration']*100:.0f}% of failures in {geo_analysis['dominant_region']}",
            "severity": "medium"
        })

    # Rule 3: Mileage pattern analysis
    mileage_analysis = analyze_mileage_pattern(failure_reports)
    if mileage_analysis["indicates_design_issue"]:
        risk_score += 20
        contributing_factors.append({
            "factor": "EARLY_LIFE_FAILURES",
            "description": f"{mileage_analysis['early_failure_rate']*100:.0f}% failures under 30k miles",
            "severity": "high"
        })

    # Rule 4: Safety system prioritization
    if category_thresholds["safety_critical"]:
        risk_score += 15
        contributing_factors.append({
            "factor": "SAFETY_CRITICAL_SYSTEM",
            "description": f"Component category '{component_category}' is safety-critical",
            "severity": "high"
        })

    # Severity analysis from reports
    high_severity_count = sum(1 for r in failure_reports if r.get("severity") == "high")
    if high_severity_count > 0:
        severity_rate = high_severity_count / max(len(failure_reports), 1)
        if severity_rate > 0.3:
            risk_score += 15
            contributing_factors.append({
                "factor": "HIGH_SEVERITY_REPORTS",
                "description": f"{severity_rate*100:.0f}% of reports are high severity",
                "severity": "high"
            })

    # Determine risk level
    if risk_score >= 70:
        recall_risk_level = "CRITICAL"
        recommended_action = "Initiate recall evaluation immediately"
    elif risk_score >= 50:
        recall_risk_level = "HIGH"
        recommended_action = "Conduct formal safety investigation"
    elif risk_score >= 30:
        recall_risk_level = "MEDIUM"
        recommended_action = "Enhanced monitoring and root cause analysis"
    else:
        recall_risk_level = "LOW"
        recommended_action = "Continue standard monitoring"

    # NHTSA reporting timeline
    if category_thresholds["safety_critical"] and failure_count >= 5:
        reporting_deadline = "5 business days"
    else:
        reporting_deadline = "Quarterly EWR submission"

    regulatory_timeline = {
        "nhtsa_reporting": reporting_deadline,
        "investigation_required": recall_risk_level in ["CRITICAL", "HIGH"],
        "expedited_review": category_thresholds["safety_critical"]
    }

    return {
        "component_id": component_id,
        "recall_risk_level": recall_risk_level,
        "risk_score": round(risk_score, 1),
        "recommended_action": recommended_action,
        "failure_rate_per_1000": round(failure_rate, 2),
        "vehicles_affected": vehicles_in_field,
        "failure_count": failure_count,
        "contributing_factors": contributing_factors,
        "geographic_analysis": geo_analysis,
        "mileage_analysis": mileage_analysis,
        "regulatory_timeline": regulatory_timeline,
        "affected_models": affected_models
    }


if __name__ == "__main__":
    import json
    result = assess_recall_risk(
        component_id="BRK-2024-001",
        failure_count=45,
        vehicles_in_field=125000,
        failure_reports=[
            {"severity": "high", "region": "southwest", "mileage": 35000},
            {"severity": "high", "region": "southwest", "mileage": 28000},
            {"severity": "medium", "region": "southwest", "mileage": 42000},
            {"severity": "high", "region": "midwest", "mileage": 25000}
        ],
        component_category="brake_system",
        affected_models=["Sedan-X", "SUV-Y"],
        production_date_range={"start": "2023-01-01", "end": "2024-06-30"}
    )
    print(json.dumps(result, indent=2))
