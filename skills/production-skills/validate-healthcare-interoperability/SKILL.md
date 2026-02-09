# Skill: Validate Healthcare Interoperability

## Domain
healthcare

## Description
Validates healthcare data exchanges against interoperability standards including HL7 FHIR R4, C-CDA, X12 EDI, and CMS/ONC regulations. Ensures patient data can be safely and compliantly exchanged between EHR systems, payers, and healthcare applications.

## Business Rules
This skill implements healthcare interoperability validation per federal regulations and industry standards:

1. **FHIR R4 Compliance**: All patient-facing APIs must support FHIR R4 as per 21st Century Cures Act
2. **USCDI Requirement**: Data exchanges must include all USCDI v3 data classes for patient access
3. **Information Blocking**: Validate no information blocking practices per ONC rules (8 exceptions allowed)
4. **Security Standards**: SMART on FHIR required for third-party app authorization
5. **C-CDA Validation**: Clinical documents must pass C-CDA R2.1 schematron validation
6. **X12 EDI Compliance**: Claims and eligibility must use X12 5010 standard with HIPAA compliance

## Input Parameters
- `exchange_type` (string): "patient_access", "provider_to_provider", "payer_to_payer", "bulk_export"
- `data_format` (string): "fhir_r4", "ccda", "x12_837", "x12_835", "x12_270_271"
- `fhir_resources` (list, optional): FHIR resources being exchanged (e.g., ["Patient", "Condition", "Observation"])
- `uscdi_classes_included` (list): USCDI data classes present in exchange
- `smart_on_fhir_enabled` (bool): Whether SMART authorization is implemented
- `bulk_fhir_enabled` (bool): Whether Bulk FHIR export is supported
- `information_blocking_exceptions` (list, optional): Claimed exceptions if data withheld
- `encryption_at_rest` (bool): Whether data is encrypted at rest
- `encryption_in_transit` (bool): Whether TLS 1.2+ is used for transmission
- `audit_logging_enabled` (bool): Whether access audit logs are maintained
- `patient_consent_captured` (bool): Whether patient consent is documented
- `data_source_system` (string): Source EHR/system name
- `data_destination_system` (string): Destination system name

## Output
Returns an interoperability validation result with:
- `compliant` (bool): Overall compliance status
- `compliance_score` (float): Compliance percentage (0-100)
- `standard_validations` (dict): Pass/fail for each applicable standard
- `uscdi_coverage` (dict): Coverage of required USCDI data classes
- `information_blocking_risk` (string): "none", "low", "medium", "high"
- `security_assessment` (dict): Security control validation results
- `violations` (list): List of compliance violations with severity and remediation
- `regulatory_citations` (list): Applicable regulatory references
- `certification_gaps` (list): Gaps for ONC Health IT certification
- `recommended_actions` (list): Prioritized remediation steps

## Usage Example
```python
from interoperability_validator import validate_exchange

result = validate_exchange(
    exchange_type="patient_access",
    data_format="fhir_r4",
    fhir_resources=["Patient", "Condition", "MedicationRequest", "Observation"],
    uscdi_classes_included=["Patient Demographics", "Problems", "Medications", "Lab Results"],
    smart_on_fhir_enabled=True,
    bulk_fhir_enabled=True,
    encryption_at_rest=True,
    encryption_in_transit=True,
    audit_logging_enabled=True,
    patient_consent_captured=True,
    data_source_system="Epic",
    data_destination_system="Patient Mobile App"
)
```

## Tags
healthcare, interoperability, fhir, hl7, hipaa, ehr, compliance, patient-access, onc

## Implementation
The validation logic is implemented in `interoperability_validator.py` and references:
- `uscdi_data_classes.csv` - USCDI v3 required data classes
- `fhir_resources_required.csv` - Required FHIR resources by exchange type
- `information_blocking_exceptions.csv` - Valid information blocking exceptions
- `security_requirements.csv` - Security control requirements by regulation
