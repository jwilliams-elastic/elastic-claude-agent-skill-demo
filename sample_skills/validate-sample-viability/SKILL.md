# Skill: Validate Sample Viability

## Domain
life_sciences

## Tags
lab_operations, sample_accessioning, quality_control, biospecimen_management

## Description
Validates laboratory sample viability based on proprietary accessioning rules for biospecimen processing. This skill enforces strict timing, quality, and storage requirements that are specific to each sample type and cannot be inferred without access to institutional protocols.

## Use Cases
- Accessioning incoming plasma samples for clinical trials
- Validating sample integrity before biomarker analysis
- Flagging samples requiring special processing steps
- Ensuring compliance with lab protocol requirements

## Input Parameters
- `sample_id` (string, required): Unique identifier for the laboratory sample
- `sample_type` (string, required): Type of biospecimen (e.g., "Plasma-EDTA", "Serum", "Whole-Blood")
- `collection_time` (ISO 8601 datetime, required): When the sample was collected
- `receipt_time` (ISO 8601 datetime, required): When the sample was received at the lab
- `turbidity_index` (float, required): Optical turbidity measurement (0.0-1.0 scale)
- `storage_temp` (float, required): Current storage temperature in Celsius
- `volume_ml` (float, required): Sample volume in milliliters

## Proprietary Business Rules

### Rule 1: Time-Sensitive Processing
Plasma-EDTA samples MUST be processed within 4 hours of collection. This is a hard constraint based on anticoagulant stability and cellular degradation kinetics specific to EDTA tubes.

### Rule 2: Turbidity Quality Control
Samples with turbidity_index > 0.8 indicate lipemia, hemolysis, or icterus and MUST be flagged for "Ultracentrifugation" pre-treatment before biomarker analysis. This threshold is calibrated to our specific nephelometer equipment.

### Rule 3: Ultra-Cold Storage Requirements
Storage temperature MUST be maintained between -80°C and -70°C (strict). Samples outside this range are considered compromised. This range is specific to our cryopreservation validation studies.

### Rule 4: Minimum Volume Requirements
Each sample type has minimum volume requirements loaded from CSV files (sample_types.csv, turbidity_thresholds.csv, quality_control_notes.csv, parameters.csv) based on the panel of assays to be performed.

## Output Format
```json
{
  "sample_id": "string",
  "viable": true/false,
  "flags": ["array of warning/processing flags"],
  "violations": ["array of rule violations"],
  "recommended_action": "string"
}
```

## Implementation
Execute using: `python viability_check.py`

## Notes
- These rules are based on validated laboratory protocols and cannot be approximated
- The biomarker constraints are institution-specific and updated quarterly
- Integration with LIMS (Laboratory Information Management System) planned for Phase 2

## Test Execution
```python
from viability_check import validate_sample_viability
from datetime import datetime, timedelta

# Convert test input format to function parameters
collection_time_hours_ago = input_data.get('collection_time_hours_ago', 0)
now = datetime.utcnow()
collection_time = (now - timedelta(hours=collection_time_hours_ago)).isoformat()
receipt_time = now.isoformat()

# Call the skill function
raw_result = validate_sample_viability(
    sample_id=input_data.get('sample_id', 'TEST-SAMPLE'),
    sample_type=input_data.get('sample_type'),
    collection_time=collection_time,
    receipt_time=receipt_time,
    turbidity_index=input_data.get('turbidity_index'),
    storage_temp=input_data.get('storage_temp_celsius', input_data.get('storage_temp', -75)),
    volume_ml=input_data.get('volume_ml')
)

# Transform output to match test expectations
violations_list = []
warnings_list = []

for violation_str in raw_result.get('violations', []):
    if 'processing time' in violation_str.lower() or '4h' in violation_str.lower() or '4 hours' in violation_str.lower():
        violations_list.append({'type': 'PROCESSING_TIME_EXCEEDED', 'message': violation_str})
    elif 'temperature' in violation_str.lower():
        violations_list.append({'type': 'TEMPERATURE_OUT_OF_RANGE', 'message': violation_str})
    elif 'volume' in violation_str.lower():
        violations_list.append({'type': 'INSUFFICIENT_VOLUME', 'message': violation_str})
    else:
        violations_list.append({'type': 'VIABILITY_VIOLATION', 'message': violation_str})

for flag_str in raw_result.get('flags', []):
    if 'HIGH_TURBIDITY' in flag_str or 'Ultracentrifugation' in flag_str:
        warnings_list.append({'type': 'TURBIDITY_THRESHOLD_EXCEEDED', 'message': flag_str})
    else:
        warnings_list.append({'type': 'SAMPLE_WARNING', 'message': flag_str})

overall_status = 'REJECTED' if not raw_result.get('viable') else 'ACCEPTED'

# Format recommendations as a list for test compatibility
recommended_action = raw_result.get('recommended_action', '')
recommendations = [recommended_action] if recommended_action else []

result = {
    'overall_status': overall_status,
    'status': overall_status,
    'violations': violations_list,
    'warnings': warnings_list,
    'recommended_action': recommended_action,
    'recommendations': recommendations,
    'sample_id': raw_result.get('sample_id'),
    'viable': raw_result.get('viable')
}
```
