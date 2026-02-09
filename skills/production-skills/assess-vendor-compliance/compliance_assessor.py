"""
Vendor Compliance Assessment Module

Implements vendor compliance evaluation against
quality, security, financial, and regulatory standards.
"""

import csv
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


def load_compliance_standards() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    compliance_categories_data = load_csv_as_dict("compliance_categories.csv")
    certification_requirements_data = load_csv_as_dict("certification_requirements.csv")
    risk_thresholds_data = load_csv_as_dict("risk_thresholds.csv")
    audit_criteria_data = load_key_value_csv("audit_criteria.csv")
    params = load_parameters()
    return {
        "compliance_categories": compliance_categories_data,
        "certification_requirements": certification_requirements_data,
        "risk_thresholds": risk_thresholds_data,
        "audit_criteria": audit_criteria_data,
        **params
    }


def assess_category_compliance(
    category: str,
    vendor_data: Dict,
    requirements: List[str]
) -> Dict[str, Any]:
    """Assess compliance for a specific category."""
    met_requirements = []
    gaps = []

    for requirement in requirements:
        if vendor_data.get(requirement, False):
            met_requirements.append(requirement)
        else:
            gaps.append(requirement)

    score = (len(met_requirements) / len(requirements) * 100) if requirements else 0

    return {
        "category": category,
        "score": round(score, 1),
        "met_requirements": met_requirements,
        "gaps": gaps,
        "compliance_rate": f"{len(met_requirements)}/{len(requirements)}"
    }


def validate_certifications(
    certifications: List[Dict],
    cert_requirements: Dict
) -> Dict[str, Any]:
    """Validate vendor certifications."""
    valid_certs = []
    expired_certs = []
    missing_certs = []

    current_date = datetime.now()
    vendor_cert_names = {c.get("name") for c in certifications}

    for cert in certifications:
        cert_name = cert.get("name", "")
        expiry_date = cert.get("expiry_date", "")

        if expiry_date:
            try:
                expiry = datetime.strptime(expiry_date, "%Y-%m-%d")
                if expiry > current_date:
                    valid_certs.append({
                        "name": cert_name,
                        "expiry": expiry_date,
                        "days_remaining": (expiry - current_date).days
                    })
                else:
                    expired_certs.append({
                        "name": cert_name,
                        "expired_on": expiry_date
                    })
            except ValueError:
                expired_certs.append({"name": cert_name, "error": "invalid_date"})

    # Check for missing required certifications
    for req_cert in cert_requirements:
        if req_cert not in vendor_cert_names:
            missing_certs.append(req_cert)

    return {
        "valid_certifications": valid_certs,
        "expired_certifications": expired_certs,
        "missing_certifications": missing_certs,
        "certification_score": round(len(valid_certs) / max(len(cert_requirements), 1) * 100, 1)
    }


def assess_financial_stability(
    financial_data: Dict
) -> Dict[str, Any]:
    """Assess vendor financial stability."""
    score = 100
    findings = []

    # Check revenue trend
    revenue_growth = financial_data.get("revenue_growth_pct", 0)
    if revenue_growth < -10:
        score -= 25
        findings.append("Significant revenue decline")
    elif revenue_growth < 0:
        score -= 10
        findings.append("Revenue decline")

    # Check profitability
    profit_margin = financial_data.get("profit_margin_pct", 0)
    if profit_margin < 0:
        score -= 20
        findings.append("Operating at a loss")
    elif profit_margin < 5:
        score -= 10
        findings.append("Low profit margins")

    # Check debt ratio
    debt_ratio = financial_data.get("debt_to_equity", 0)
    if debt_ratio > 3:
        score -= 20
        findings.append("High debt levels")
    elif debt_ratio > 2:
        score -= 10
        findings.append("Elevated debt levels")

    # Check payment history
    payment_delays = financial_data.get("payment_delays_90_days", 0)
    if payment_delays > 0:
        score -= 15
        findings.append("History of payment delays")

    return {
        "financial_stability_score": max(0, score),
        "findings": findings,
        "risk_level": "high" if score < 60 else "medium" if score < 80 else "low"
    }


def evaluate_performance_metrics(
    performance_data: Dict
) -> Dict[str, Any]:
    """Evaluate vendor performance metrics."""
    scores = {}

    # On-time delivery
    otd = performance_data.get("on_time_delivery_pct", 0)
    if otd >= 98:
        scores["delivery"] = 100
    elif otd >= 95:
        scores["delivery"] = 80
    elif otd >= 90:
        scores["delivery"] = 60
    else:
        scores["delivery"] = 40

    # Quality rate
    quality = performance_data.get("quality_acceptance_pct", 0)
    if quality >= 99:
        scores["quality"] = 100
    elif quality >= 97:
        scores["quality"] = 80
    elif quality >= 95:
        scores["quality"] = 60
    else:
        scores["quality"] = 40

    # Response time
    response_hours = performance_data.get("avg_response_hours", 24)
    if response_hours <= 4:
        scores["responsiveness"] = 100
    elif response_hours <= 8:
        scores["responsiveness"] = 80
    elif response_hours <= 24:
        scores["responsiveness"] = 60
    else:
        scores["responsiveness"] = 40

    avg_score = sum(scores.values()) / len(scores) if scores else 0

    return {
        "performance_score": round(avg_score, 1),
        "component_scores": scores
    }


def determine_compliance_status(
    overall_score: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Determine overall compliance status."""
    for status, config in thresholds.items():
        if config["min_score"] <= overall_score < config["max_score"]:
            return {
                "status": status.upper(),
                "required_action": config["action"],
                "score_range": f"{config['min_score']}-{config['max_score']}"
            }

    return {"status": "LOW", "required_action": "monitor"}


def generate_remediation_plan(
    gaps: List[Dict]
) -> List[Dict]:
    """Generate remediation plan for compliance gaps."""
    plan = []

    priority_map = {
        "security": 1,
        "regulatory": 1,
        "quality": 2,
        "financial": 2,
        "operational": 3
    }

    for gap in gaps:
        category = gap.get("category", "operational")
        priority = priority_map.get(category, 3)

        for item in gap.get("gaps", []):
            plan.append({
                "gap": item,
                "category": category,
                "priority": priority,
                "recommended_timeline_days": 30 if priority == 1 else 60 if priority == 2 else 90
            })

    return sorted(plan, key=lambda x: x["priority"])


def assess_vendor_compliance(
    vendor_id: str,
    vendor_data: Dict,
    certifications: List[Dict],
    financial_data: Dict,
    performance_data: Dict,
    industry: str,
    assessment_date: str
) -> Dict[str, Any]:
    """
    Assess vendor compliance against standards.

    Business Rules:
    1. Multi-category compliance evaluation
    2. Certification validation and tracking
    3. Financial stability assessment
    4. Risk-based compliance status

    Args:
        vendor_id: Vendor identifier
        vendor_data: Vendor compliance data
        certifications: Vendor certifications
        financial_data: Financial information
        performance_data: Performance metrics
        industry: Industry classification
        assessment_date: Assessment date

    Returns:
        Vendor compliance assessment results
    """
    standards = load_compliance_standards()

    # Assess each compliance category
    category_results = []
    categories = standards.get("compliance_categories", {})

    for category, config in categories.items():
        result = assess_category_compliance(
            category,
            vendor_data,
            config.get("requirements", [])
        )
        result["weight"] = config.get("weight", 0.2)
        category_results.append(result)

    # Calculate weighted compliance score
    weighted_score = sum(
        r["score"] * r["weight"]
        for r in category_results
    )

    # Validate certifications
    industry_certs = standards.get("industry_requirements", {}).get(industry, [])
    cert_result = validate_certifications(
        certifications,
        industry_certs
    )

    # Assess financial stability
    financial_result = assess_financial_stability(financial_data)

    # Evaluate performance
    performance_result = evaluate_performance_metrics(performance_data)

    # Calculate overall score
    overall_score = (
        weighted_score * 0.40 +
        cert_result["certification_score"] * 0.25 +
        financial_result["financial_stability_score"] * 0.15 +
        performance_result["performance_score"] * 0.20
    )

    # Determine status
    status = determine_compliance_status(
        overall_score,
        standards.get("risk_thresholds", {})
    )

    # Generate remediation plan
    gaps = [r for r in category_results if r["gaps"]]
    remediation = generate_remediation_plan(gaps)

    return {
        "vendor_id": vendor_id,
        "assessment_date": assessment_date,
        "overall_compliance_score": round(overall_score, 1),
        "compliance_status": status,
        "category_assessments": category_results,
        "certification_status": cert_result,
        "financial_assessment": financial_result,
        "performance_assessment": performance_result,
        "remediation_plan": remediation[:10],
        "next_review_date": (
            datetime.strptime(assessment_date, "%Y-%m-%d") +
            timedelta(days=90)
        ).strftime("%Y-%m-%d")
    }


if __name__ == "__main__":
    import json
    result = assess_vendor_compliance(
        vendor_id="VND-001",
        vendor_data={
            "ISO_9001": True, "quality_manual": True, "inspection_records": True,
            "SOC2": True, "data_encryption": True, "access_controls": True,
            "financial_stability": True, "insurance_coverage": True
        },
        certifications=[
            {"name": "ISO_9001", "expiry_date": "2027-06-15"},
            {"name": "SOC2_Type2", "expiry_date": "2026-12-31"}
        ],
        financial_data={"revenue_growth_pct": 5, "profit_margin_pct": 12, "debt_to_equity": 1.2},
        performance_data={"on_time_delivery_pct": 97, "quality_acceptance_pct": 99, "avg_response_hours": 6},
        industry="financial",
        assessment_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
