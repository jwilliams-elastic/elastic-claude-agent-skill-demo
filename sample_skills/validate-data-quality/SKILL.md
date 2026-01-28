# Skill: Validate Data Quality

## Domain
technology

## Description
Validates data quality across dimensions including completeness, accuracy, consistency, and timeliness for data governance.

## Tags
data-quality, governance, analytics, completeness, accuracy, validation

## Use Cases
- Data profiling
- Quality monitoring
- Issue detection
- Compliance reporting

## Proprietary Business Rules

### Rule 1: Completeness Check
Missing value and null detection.

### Rule 2: Accuracy Validation
Data correctness verification against rules.

### Rule 3: Consistency Analysis
Cross-dataset consistency checking.

### Rule 4: Timeliness Assessment
Data freshness evaluation.

## Input Parameters
- `dataset_id` (string): Dataset identifier
- `data_sample` (list): Data records to validate
- `quality_rules` (list): Validation rules
- `schema_definition` (dict): Expected schema
- `reference_data` (dict): Reference lookups
- `sla_requirements` (dict): Quality SLAs

## Output
- `quality_score` (float): Overall quality score
- `dimension_scores` (dict): Score by dimension
- `issues_detected` (list): Quality issues
- `rule_results` (dict): Rule-level outcomes
- `recommendations` (list): Improvement actions

## Implementation
The validation logic is implemented in `quality_validator.py` and references data from `quality_rules.json`.

## Usage Example
```python
from quality_validator import validate_data_quality

result = validate_data_quality(
    dataset_id="DS-001",
    data_sample=[{"id": "1", "name": "Test", "email": "test@example.com"}],
    quality_rules=[{"field": "email", "rule": "format", "pattern": "email"}],
    schema_definition={"id": "required", "name": "required", "email": "required"},
    reference_data={"valid_domains": ["example.com"]},
    sla_requirements={"completeness": 0.99, "accuracy": 0.98}
)

print(f"Data Quality Score: {result['quality_score']}")
```

## Test Execution
```python
from quality_validator import validate_data_quality

result = validate_data_quality(
    dataset_id=input_data.get('dataset_id'),
    data_sample=input_data.get('data_sample', []),
    quality_rules=input_data.get('quality_rules', []),
    schema_definition=input_data.get('schema_definition', {}),
    reference_data=input_data.get('reference_data', {}),
    sla_requirements=input_data.get('sla_requirements', {})
)
```
