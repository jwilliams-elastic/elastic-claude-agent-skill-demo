# Skill: Validate Manufacturing Quality

## Domain
advanced_manufacturing

## Description
Validates manufacturing quality using statistical process control, defect analysis, and compliance verification against quality standards.

## Tags
manufacturing, quality, SPC, Six-Sigma, ISO, defects

## Use Cases
- Quality inspection
- SPC analysis
- Defect root cause
- Compliance verification

## Proprietary Business Rules

### Rule 1: SPC Control Chart Analysis
Statistical process control evaluation.

### Rule 2: Defect Classification
Defect type and severity categorization.

### Rule 3: Cpk/Ppk Calculation
Process capability indices.

### Rule 4: ISO Compliance Check
Quality standard compliance verification.

## Input Parameters
- `batch_id` (string): Production batch identifier
- `measurement_data` (list): Quality measurements
- `specifications` (dict): Product specifications
- `defect_records` (list): Defect observations
- `process_params` (dict): Process parameters
- `quality_standards` (list): Applicable standards

## Output
- `quality_score` (float): Overall quality rating
- `spc_analysis` (dict): SPC results
- `capability_indices` (dict): Cpk/Ppk values
- `defect_analysis` (dict): Defect summary
- `compliance_status` (dict): Standards compliance
- `recommendations` (list): Quality improvements

## Implementation
The validation logic is implemented in `quality_validator.py` and references data from CSV files:
- `quality_metrics.csv` - Reference data
- `inspection_types.csv` - Reference data
- `aql_tables.csv` - Reference data
- `defect_categories.csv` - Reference data
- `spc_rules.csv` - Reference data
- `corrective_action_thresholds.csv` - Reference data
- `certification_requirements.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from quality_validator import validate_quality

result = validate_quality(
    batch_id="BATCH-001",
    measurement_data=[{"param": "diameter", "value": 10.02, "unit": "mm"}],
    specifications={"diameter": {"target": 10.0, "usl": 10.1, "lsl": 9.9}},
    defect_records=[{"type": "surface_scratch", "count": 2}],
    process_params={"temperature": 180, "pressure": 50},
    quality_standards=["ISO9001", "AS9100"]
)

print(f"Quality Score: {result['quality_score']}")
```

## Test Execution
```python
from quality_validator import validate_quality

result = validate_quality(
    batch_id=input_data.get('batch_id'),
    measurement_data=input_data.get('measurement_data', []),
    specifications=input_data.get('specifications', {}),
    defect_records=input_data.get('defect_records', []),
    process_params=input_data.get('process_params', {}),
    quality_standards=input_data.get('quality_standards', [])
)
```
