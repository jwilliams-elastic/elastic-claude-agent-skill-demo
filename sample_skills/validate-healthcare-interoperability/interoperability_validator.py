"""
Healthcare Interoperability Validation Module

Validates healthcare data exchanges against interoperability standards
including HL7 FHIR R4, C-CDA, X12 EDI, and CMS/ONC regulations.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_csv_as_dict(filename: str, key_column: str) -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column, row.get('id', ''))
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


# USCDI v3 Required Data Classes
USCDI_V3_DATA_CLASSES = [
    "Patient Demographics",
    "Allergies and Intolerances",
    "Assessment and Plan of Treatment",
    "Care Team Members",
    "Clinical Notes",
    "Goals",
    "Health Concerns",
    "Immunizations",
    "Lab Results",
    "Medications",
    "Problems",
    "Procedures",
    "Provenance",
    "Smoking Status",
    "Vital Signs",
    "Unique Device Identifiers",
    "Health Insurance Information",
    "Encounter Information",
    "Clinical Tests",
    "Diagnostic Imaging"
]

# Required FHIR resources by exchange type
FHIR_REQUIREMENTS = {
    "patient_access": [
        "Patient", "AllergyIntolerance", "CarePlan", "CareTeam", "Condition",
        "Device", "DiagnosticReport", "DocumentReference", "Encounter",
        "Goal", "Immunization", "Location", "Medication", "MedicationRequest",
        "Observation", "Organization", "Practitioner", "Procedure", "Provenance"
    ],
    "provider_to_provider": [
        "Patient", "Condition", "Observation", "MedicationRequest",
        "DiagnosticReport", "Procedure", "CarePlan", "Encounter"
    ],
    "payer_to_payer": [
        "Patient", "Coverage", "ExplanationOfBenefit", "Claim", "ClaimResponse"
    ],
    "bulk_export": [
        "Patient", "Group", "Observation", "Condition", "MedicationRequest"
    ]
}

# Valid information blocking exceptions (ONC)
VALID_IB_EXCEPTIONS = [
    "preventing_harm",
    "privacy",
    "security",
    "infeasibility",
    "health_it_performance",
    "content_and_manner",
    "fees",
    "licensing"
]


def validate_fhir_resources(
    exchange_type: str,
    fhir_resources: Optional[List[str]]
) -> Dict[str, Any]:
    """Validate FHIR resource coverage for exchange type."""
    required = FHIR_REQUIREMENTS.get(exchange_type, [])
    provided = fhir_resources or []

    missing = [r for r in required if r not in provided]
    extra = [r for r in provided if r not in required]

    coverage_pct = ((len(required) - len(missing)) / len(required) * 100) if required else 100

    return {
        "compliant": len(missing) == 0,
        "required_resources": required,
        "provided_resources": provided,
        "missing_resources": missing,
        "coverage_percentage": round(coverage_pct, 1)
    }


def validate_uscdi_coverage(uscdi_classes_included: List[str]) -> Dict[str, Any]:
    """Validate USCDI v3 data class coverage."""
    required = USCDI_V3_DATA_CLASSES
    provided = uscdi_classes_included or []

    missing = [c for c in required if c not in provided]
    coverage_pct = ((len(required) - len(missing)) / len(required) * 100) if required else 100

    # Critical classes that must be present
    critical_classes = ["Patient Demographics", "Medications", "Allergies and Intolerances", "Problems"]
    critical_missing = [c for c in critical_classes if c not in provided]

    return {
        "compliant": coverage_pct >= 80 and len(critical_missing) == 0,
        "total_required": len(required),
        "total_provided": len(provided),
        "missing_classes": missing[:10],  # Top 10 missing
        "critical_missing": critical_missing,
        "coverage_percentage": round(coverage_pct, 1)
    }


def validate_security_controls(
    encryption_at_rest: bool,
    encryption_in_transit: bool,
    audit_logging_enabled: bool,
    smart_on_fhir_enabled: bool,
    exchange_type: str
) -> Dict[str, Any]:
    """Validate security control requirements."""
    violations = []

    if not encryption_in_transit:
        violations.append({
            "control": "encryption_in_transit",
            "severity": "critical",
            "requirement": "TLS 1.2+ required for all PHI transmission"
        })

    if not encryption_at_rest:
        violations.append({
            "control": "encryption_at_rest",
            "severity": "high",
            "requirement": "AES-256 encryption required for PHI storage"
        })

    if not audit_logging_enabled:
        violations.append({
            "control": "audit_logging",
            "severity": "high",
            "requirement": "HIPAA requires audit logs for all PHI access"
        })

    if exchange_type == "patient_access" and not smart_on_fhir_enabled:
        violations.append({
            "control": "smart_on_fhir",
            "severity": "high",
            "requirement": "SMART on FHIR required for third-party app authorization"
        })

    return {
        "compliant": len(violations) == 0,
        "controls_validated": {
            "encryption_at_rest": encryption_at_rest,
            "encryption_in_transit": encryption_in_transit,
            "audit_logging": audit_logging_enabled,
            "smart_on_fhir": smart_on_fhir_enabled
        },
        "violations": violations
    }


def assess_information_blocking_risk(
    exchange_type: str,
    uscdi_coverage: float,
    fhir_compliant: bool,
    exceptions_claimed: Optional[List[str]]
) -> Dict[str, Any]:
    """Assess information blocking risk per ONC rules."""
    risk_factors = []

    if uscdi_coverage < 80:
        risk_factors.append("Incomplete USCDI data class coverage may constitute information blocking")

    if not fhir_compliant and exchange_type == "patient_access":
        risk_factors.append("Missing required FHIR resources for patient access API")

    # Validate claimed exceptions
    invalid_exceptions = []
    if exceptions_claimed:
        for exc in exceptions_claimed:
            if exc not in VALID_IB_EXCEPTIONS:
                invalid_exceptions.append(exc)

    if invalid_exceptions:
        risk_factors.append(f"Invalid information blocking exceptions claimed: {invalid_exceptions}")

    # Determine risk level
    if len(risk_factors) >= 2 or uscdi_coverage < 60:
        risk_level = "high"
    elif len(risk_factors) == 1 or uscdi_coverage < 80:
        risk_level = "medium"
    elif uscdi_coverage < 90:
        risk_level = "low"
    else:
        risk_level = "none"

    return {
        "risk_level": risk_level,
        "risk_factors": risk_factors,
        "valid_exceptions_claimed": [e for e in (exceptions_claimed or []) if e in VALID_IB_EXCEPTIONS],
        "invalid_exceptions": invalid_exceptions
    }


def get_regulatory_citations(
    exchange_type: str,
    data_format: str,
    violations: List[Dict]
) -> List[Dict[str, str]]:
    """Get applicable regulatory citations."""
    citations = []

    # 21st Century Cures Act
    citations.append({
        "regulation": "21st Century Cures Act",
        "section": "Section 4003",
        "requirement": "Prohibition on information blocking",
        "applies_to": "All covered actors"
    })

    # ONC Cures Act Final Rule
    if exchange_type == "patient_access":
        citations.append({
            "regulation": "ONC Cures Act Final Rule",
            "section": "45 CFR 170.315(g)(10)",
            "requirement": "Standardized API for patient and population services",
            "applies_to": "Certified Health IT"
        })

    # HIPAA
    citations.append({
        "regulation": "HIPAA Security Rule",
        "section": "45 CFR 164.312",
        "requirement": "Technical safeguards for PHI",
        "applies_to": "Covered entities and business associates"
    })

    # CMS Interoperability Rules
    if exchange_type in ["patient_access", "payer_to_payer"]:
        citations.append({
            "regulation": "CMS Interoperability and Patient Access Final Rule",
            "section": "CMS-9115-F",
            "requirement": "Patient access API and payer-to-payer exchange",
            "applies_to": "CMS-regulated payers"
        })

    return citations


def identify_certification_gaps(
    fhir_validation: Dict,
    security_validation: Dict,
    uscdi_validation: Dict,
    bulk_fhir_enabled: bool
) -> List[Dict[str, str]]:
    """Identify gaps for ONC Health IT certification."""
    gaps = []

    if not fhir_validation["compliant"]:
        gaps.append({
            "criterion": "170.315(g)(10)",
            "gap": "Standardized API - Missing required FHIR resources",
            "remediation": f"Implement missing resources: {fhir_validation['missing_resources'][:5]}"
        })

    if not security_validation["compliant"]:
        for violation in security_validation["violations"]:
            gaps.append({
                "criterion": "170.315(d)(12)/(13)",
                "gap": f"Security - {violation['control']}",
                "remediation": violation["requirement"]
            })

    if not uscdi_validation["compliant"]:
        gaps.append({
            "criterion": "170.315(b)(10)",
            "gap": "USCDI data class coverage below required threshold",
            "remediation": f"Add missing data classes: {uscdi_validation['critical_missing']}"
        })

    if not bulk_fhir_enabled:
        gaps.append({
            "criterion": "170.315(g)(10)",
            "gap": "Bulk FHIR export not supported",
            "remediation": "Implement Bulk FHIR IG for population-level data export"
        })

    return gaps


def generate_recommended_actions(
    violations: List[Dict],
    gaps: List[Dict],
    ib_risk: Dict
) -> List[Dict[str, str]]:
    """Generate prioritized remediation recommendations."""
    actions = []

    # Critical security issues first
    critical_violations = [v for v in violations if v.get("severity") == "critical"]
    for v in critical_violations:
        actions.append({
            "priority": "critical",
            "action": f"Address {v.get('area', 'issue')}: {v.get('description', '')}",
            "rationale": "Critical compliance violation"
        })

    # High-risk information blocking
    if ib_risk["risk_level"] == "high":
        actions.append({
            "priority": "critical",
            "action": "Address information blocking risk",
            "rationale": "High risk of ONC enforcement action"
        })

    # Certification gaps
    for gap in gaps[:3]:  # Top 3 gaps
        actions.append({
            "priority": "high",
            "action": gap["remediation"],
            "rationale": f"Required for ONC certification: {gap['criterion']}"
        })

    # High-severity security violations
    high_violations = [v for v in violations if v.get("severity") == "high"]
    for v in high_violations[:2]:
        actions.append({
            "priority": "high",
            "action": f"Address {v.get('area', 'issue')}: {v.get('description', '')}",
            "rationale": "High severity compliance violation"
        })

    return actions[:8]  # Return top 8 actions


def validate_exchange(
    exchange_type: str,
    data_format: str,
    fhir_resources: Optional[List[str]],
    uscdi_classes_included: List[str],
    smart_on_fhir_enabled: bool,
    bulk_fhir_enabled: bool,
    information_blocking_exceptions: Optional[List[str]],
    encryption_at_rest: bool,
    encryption_in_transit: bool,
    audit_logging_enabled: bool,
    patient_consent_captured: bool,
    data_source_system: str,
    data_destination_system: str
) -> Dict[str, Any]:
    """
    Validate healthcare data exchange against interoperability standards.

    Returns comprehensive validation result with compliance status,
    violations, regulatory citations, and remediation guidance.
    """
    # Validate FHIR resources
    fhir_validation = validate_fhir_resources(exchange_type, fhir_resources)

    # Validate USCDI coverage
    uscdi_validation = validate_uscdi_coverage(uscdi_classes_included)

    # Validate security controls
    security_validation = validate_security_controls(
        encryption_at_rest,
        encryption_in_transit,
        audit_logging_enabled,
        smart_on_fhir_enabled,
        exchange_type
    )

    # Assess information blocking risk
    ib_risk = assess_information_blocking_risk(
        exchange_type,
        uscdi_validation["coverage_percentage"],
        fhir_validation["compliant"],
        information_blocking_exceptions
    )

    # Compile all violations
    all_violations = []

    if not fhir_validation["compliant"]:
        all_violations.append({
            "area": "FHIR Resources",
            "severity": "high",
            "description": f"Missing required FHIR resources: {fhir_validation['missing_resources'][:5]}"
        })

    if uscdi_validation["critical_missing"]:
        all_violations.append({
            "area": "USCDI Coverage",
            "severity": "critical",
            "description": f"Missing critical USCDI classes: {uscdi_validation['critical_missing']}"
        })

    for v in security_validation["violations"]:
        all_violations.append({
            "area": "Security",
            "severity": v["severity"],
            "description": f"{v['control']}: {v['requirement']}"
        })

    if not patient_consent_captured and exchange_type == "patient_access":
        all_violations.append({
            "area": "Consent",
            "severity": "medium",
            "description": "Patient consent documentation required for third-party access"
        })

    # Calculate compliance score
    scores = [
        fhir_validation["coverage_percentage"] * 0.25,
        uscdi_validation["coverage_percentage"] * 0.25,
        (100 if security_validation["compliant"] else 50) * 0.30,
        (100 if ib_risk["risk_level"] == "none" else 70 if ib_risk["risk_level"] == "low" else 40) * 0.20
    ]
    compliance_score = sum(scores)

    # Overall compliance
    overall_compliant = (
        fhir_validation["compliant"] and
        security_validation["compliant"] and
        uscdi_validation["coverage_percentage"] >= 80 and
        ib_risk["risk_level"] in ["none", "low"]
    )

    # Get regulatory citations
    regulatory_citations = get_regulatory_citations(exchange_type, data_format, all_violations)

    # Identify certification gaps
    certification_gaps = identify_certification_gaps(
        fhir_validation,
        security_validation,
        uscdi_validation,
        bulk_fhir_enabled
    )

    # Generate recommendations
    recommended_actions = generate_recommended_actions(
        all_violations,
        certification_gaps,
        ib_risk
    )

    return {
        "exchange_type": exchange_type,
        "data_format": data_format,
        "source_system": data_source_system,
        "destination_system": data_destination_system,
        "compliant": overall_compliant,
        "compliance_score": round(compliance_score, 1),
        "standard_validations": {
            "fhir_r4": fhir_validation,
            "uscdi_v3": uscdi_validation,
            "security": security_validation
        },
        "uscdi_coverage": {
            "percentage": uscdi_validation["coverage_percentage"],
            "missing_critical": uscdi_validation["critical_missing"],
            "missing_count": len(uscdi_validation["missing_classes"])
        },
        "information_blocking_risk": ib_risk["risk_level"],
        "security_assessment": security_validation["controls_validated"],
        "violations": all_violations,
        "regulatory_citations": regulatory_citations,
        "certification_gaps": certification_gaps,
        "recommended_actions": recommended_actions
    }


def main():
    """Example usage."""
    result = validate_exchange(
        exchange_type="patient_access",
        data_format="fhir_r4",
        fhir_resources=["Patient", "Condition", "MedicationRequest", "Observation"],
        uscdi_classes_included=["Patient Demographics", "Problems", "Medications", "Lab Results"],
        smart_on_fhir_enabled=True,
        bulk_fhir_enabled=True,
        information_blocking_exceptions=None,
        encryption_at_rest=True,
        encryption_in_transit=True,
        audit_logging_enabled=True,
        patient_consent_captured=True,
        data_source_system="Epic",
        data_destination_system="Patient Mobile App"
    )

    print(f"Exchange: {result['source_system']} -> {result['destination_system']}")
    print(f"Compliant: {result['compliant']}")
    print(f"Compliance Score: {result['compliance_score']}")
    print(f"Information Blocking Risk: {result['information_blocking_risk']}")
    print(f"Violations: {len(result['violations'])}")


if __name__ == "__main__":
    main()
