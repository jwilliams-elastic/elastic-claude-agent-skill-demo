"""
Cybersecurity Risk Assessment Module

Implements cyber risk assessment using NIST framework,
vulnerability analysis, and threat modeling.
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


def load_security_frameworks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    required_controls_data = load_csv_as_dict("required_controls.csv")
    cvss_thresholds_data = load_key_value_csv("cvss_thresholds.csv")
    threat_landscape_data = load_csv_as_dict("threat_landscape.csv")
    impact_factors_data = load_csv_as_dict("impact_factors.csv")
    params = load_parameters()
    return {
        "required_controls": required_controls_data,
        "cvss_thresholds": cvss_thresholds_data,
        "threat_landscape": threat_landscape_data,
        "impact_factors": impact_factors_data,
        **params
    }


def assess_control_gaps(
    control_status: Dict,
    required_controls: Dict
) -> List[Dict]:
    """Identify security control gaps."""
    gaps = []

    for control_id, control_info in required_controls.items():
        status = control_status.get(control_id, False)
        required = control_info.get("required", True)

        if required and not status:
            gaps.append({
                "control_id": control_id,
                "control_name": control_info.get("name", control_id),
                "category": control_info.get("category", "general"),
                "severity": control_info.get("severity", "medium"),
                "recommendation": control_info.get("recommendation", f"Implement {control_id}")
            })
        elif status == "partial":
            gaps.append({
                "control_id": control_id,
                "control_name": control_info.get("name", control_id),
                "category": control_info.get("category", "general"),
                "severity": "low",
                "recommendation": f"Complete implementation of {control_id}"
            })

    return gaps


def prioritize_vulnerabilities(
    vulnerability_data: List[Dict],
    asset_inventory: List[Dict],
    cvss_thresholds: Dict
) -> List[Dict]:
    """Prioritize vulnerabilities by risk."""
    prioritized = []

    # Build asset criticality map
    asset_criticality = {}
    for asset in asset_inventory:
        asset_criticality[asset.get("id", "")] = asset.get("criticality", "medium")

    for vuln in vulnerability_data:
        cvss = vuln.get("cvss", 0)
        affected_assets = vuln.get("affected_assets", 0)
        cve = vuln.get("cve", "unknown")

        # Calculate adjusted risk score
        base_score = cvss * 10

        # Asset exposure adjustment
        if affected_assets > 10:
            base_score *= 1.3
        elif affected_assets > 5:
            base_score *= 1.15

        # Determine priority
        if cvss >= cvss_thresholds.get("critical", 9.0):
            priority = "critical"
            sla_hours = 24
        elif cvss >= cvss_thresholds.get("high", 7.0):
            priority = "high"
            sla_hours = 72
        elif cvss >= cvss_thresholds.get("medium", 4.0):
            priority = "medium"
            sla_hours = 168
        else:
            priority = "low"
            sla_hours = 720

        prioritized.append({
            "cve": cve,
            "cvss": cvss,
            "adjusted_score": round(base_score, 1),
            "priority": priority,
            "affected_assets": affected_assets,
            "remediation_sla_hours": sla_hours
        })

    # Sort by adjusted score
    prioritized.sort(key=lambda x: x["adjusted_score"], reverse=True)

    return prioritized


def assess_threats(
    threat_intel: Dict,
    business_context: Dict,
    threat_landscape: Dict
) -> Dict[str, Any]:
    """Assess threat landscape and likelihood."""
    industry = threat_intel.get("industry", "general")
    recent_campaigns = threat_intel.get("recent_campaigns", [])
    data_sensitivity = business_context.get("data_sensitivity", "medium")

    industry_threats = threat_landscape.get(industry, threat_landscape.get("general", {}))

    active_threats = []
    threat_score = 0

    for threat_type, threat_info in industry_threats.items():
        # Skip empty or non-dict threat info
        if not threat_info or not isinstance(threat_info, dict):
            continue
        base_likelihood = threat_info.get("base_likelihood", 0.3)

        # Adjust for recent campaigns
        if threat_type in recent_campaigns:
            adjusted_likelihood = min(1.0, base_likelihood * 1.5)
            active_threats.append({
                "threat_type": threat_type,
                "likelihood": adjusted_likelihood,
                "recent_activity": True,
                "impact": threat_info.get("impact", "high")
            })
            threat_score += adjusted_likelihood * 30
        else:
            threat_score += base_likelihood * 20

    # Data sensitivity adjustment
    sensitivity_multiplier = {"high": 1.3, "medium": 1.0, "low": 0.8}.get(data_sensitivity, 1.0)
    threat_score *= sensitivity_multiplier

    return {
        "overall_threat_level": "high" if threat_score > 50 else "medium" if threat_score > 25 else "low",
        "threat_score": round(threat_score, 1),
        "active_threats": active_threats,
        "industry_profile": industry
    }


def calculate_business_impact(
    business_context: Dict,
    impact_factors: Dict
) -> Dict[str, Any]:
    """Calculate potential business impact of breach."""
    data_sensitivity = business_context.get("data_sensitivity", "medium")
    regulatory = business_context.get("regulatory", [])

    # Base impact by data sensitivity
    sensitivity_impact = impact_factors.get("data_sensitivity", {}).get(data_sensitivity, 50)

    # Regulatory penalty exposure
    regulatory_impact = 0
    for reg in regulatory:
        penalty = impact_factors.get("regulatory_penalties", {}).get(reg, 0)
        regulatory_impact += penalty

    # Reputation impact estimate
    reputation_impact = impact_factors.get("reputation_base", 20)
    if data_sensitivity == "high":
        reputation_impact *= 1.5

    total_impact_score = sensitivity_impact + regulatory_impact + reputation_impact

    return {
        "total_impact_score": round(total_impact_score, 1),
        "data_sensitivity_impact": sensitivity_impact,
        "regulatory_exposure": regulatory_impact,
        "reputation_risk": round(reputation_impact, 1),
        "applicable_regulations": regulatory
    }


def generate_recommendations(
    control_gaps: List[Dict],
    critical_vulns: List[Dict],
    threat_assessment: Dict
) -> List[Dict]:
    """Generate prioritized security recommendations."""
    recommendations = []

    # High priority control gaps
    for gap in control_gaps:
        if gap.get("severity") in ["critical", "high"]:
            recommendations.append({
                "priority": "high",
                "category": "control_implementation",
                "action": gap.get("recommendation"),
                "rationale": f"Critical control gap: {gap.get('control_name')}"
            })

    # Critical vulnerabilities
    for vuln in critical_vulns[:5]:  # Top 5
        if vuln.get("priority") in ["critical", "high"]:
            recommendations.append({
                "priority": vuln.get("priority"),
                "category": "vulnerability_remediation",
                "action": f"Patch {vuln.get('cve')} on affected systems",
                "rationale": f"CVSS {vuln.get('cvss')} affecting {vuln.get('affected_assets')} assets"
            })

    # Threat-based recommendations
    for threat in threat_assessment.get("active_threats", []):
        recommendations.append({
            "priority": "medium",
            "category": "threat_mitigation",
            "action": f"Enhance defenses against {threat.get('threat_type')}",
            "rationale": f"Recent {threat.get('threat_type')} activity targeting industry"
        })

    return recommendations


def assess_cyber_risk(
    organization_id: str,
    asset_inventory: List[Dict],
    vulnerability_data: List[Dict],
    control_status: Dict,
    threat_intel: Dict,
    business_context: Dict
) -> Dict[str, Any]:
    """
    Assess cybersecurity risk.

    Business Rules:
    1. NIST framework control mapping
    2. CVSS-based vulnerability scoring
    3. Industry threat likelihood
    4. Business impact quantification

    Args:
        organization_id: Organization ID
        asset_inventory: IT asset details
        vulnerability_data: Vulnerability scan results
        control_status: Control implementation status
        threat_intel: Threat intelligence
        business_context: Business criticality

    Returns:
        Cyber risk assessment results
    """
    frameworks = load_security_frameworks()

    # Control gap analysis
    control_gaps = assess_control_gaps(
        control_status,
        frameworks.get("required_controls", {})
    )

    # Vulnerability prioritization
    critical_vulnerabilities = prioritize_vulnerabilities(
        vulnerability_data,
        asset_inventory,
        frameworks.get("cvss_thresholds", {})
    )

    # Threat assessment
    threat_assessment = assess_threats(
        threat_intel,
        business_context,
        frameworks.get("threat_landscape", {})
    )

    # Business impact
    impact_analysis = calculate_business_impact(
        business_context,
        frameworks.get("impact_factors", {})
    )

    # Calculate overall risk score
    control_gap_score = len([g for g in control_gaps if g.get("severity") in ["critical", "high"]]) * 15
    vuln_score = sum(v.get("adjusted_score", 0) for v in critical_vulnerabilities[:10]) / 10
    threat_score = threat_assessment.get("threat_score", 0)

    risk_score = min(100, (control_gap_score + vuln_score + threat_score) / 3)

    # Generate recommendations
    recommendations = generate_recommendations(
        control_gaps,
        critical_vulnerabilities,
        threat_assessment
    )

    return {
        "organization_id": organization_id,
        "risk_score": round(risk_score, 1),
        "risk_level": "critical" if risk_score > 75 else "high" if risk_score > 50 else "medium" if risk_score > 25 else "low",
        "control_gaps": control_gaps,
        "critical_vulnerabilities": critical_vulnerabilities[:10],
        "threat_assessment": threat_assessment,
        "business_impact": impact_analysis,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    import json
    result = assess_cyber_risk(
        organization_id="ORG-001",
        asset_inventory=[
            {"id": "SRV-001", "type": "server", "criticality": "high", "exposure": "internet"},
            {"id": "SRV-002", "type": "server", "criticality": "medium", "exposure": "internal"}
        ],
        vulnerability_data=[
            {"cve": "CVE-2025-1234", "cvss": 9.8, "affected_assets": 5},
            {"cve": "CVE-2025-5678", "cvss": 7.5, "affected_assets": 10}
        ],
        control_status={"mfa": True, "encryption": True, "patching": "partial", "backup": True},
        threat_intel={"industry": "financial", "recent_campaigns": ["ransomware"]},
        business_context={"data_sensitivity": "high", "regulatory": ["PCI", "SOX"]}
    )
    print(json.dumps(result, indent=2))
