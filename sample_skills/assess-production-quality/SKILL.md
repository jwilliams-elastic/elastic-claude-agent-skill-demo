# Skill: Assess Production Line Quality

## Domain
advanced_manufacturing

## Description
Evaluates production line output quality against proprietary manufacturing standards, identifying defects, process deviations, and recommending corrective actions based on statistical process control metrics.

## Tags
manufacturing, quality-control, six-sigma, process-optimization, defect-detection

## Use Cases
- Real-time production quality monitoring
- Defect root cause analysis
- Process capability assessment
- Supplier quality evaluation

## Proprietary Business Rules

### Rule 1: Control Limit Enforcement
Parts must fall within ±3 sigma control limits based on historical process capability data specific to each product line.

### Rule 2: Consecutive Deviation Detection
Three consecutive measurements trending in the same direction (even within limits) triggers a process drift alert.

### Rule 3: Critical Dimension Tolerance
Critical dimensions (marked in specs) have zero tolerance for out-of-spec readings - immediate line stop required.

### Rule 4: Material Lot Correlation
Defects must be correlated with material lot numbers to identify supplier quality issues.

## Input Parameters
- `part_number` (string): Unique identifier for the part being inspected
- `measurements` (list): Array of measurement readings
- `dimension_type` (string): Type of dimension (critical, major, minor)
- `material_lot` (string): Material lot identifier
- `production_line` (string): Production line identifier
- `operator_id` (string): Operator performing the measurement

## Output
- `quality_status` (string): PASS, FAIL, or ALERT
- `defects_found` (list): List of identified defects
- `process_capability` (float): Cpk value for this measurement set
- `recommendations` (list): Corrective actions if needed
- `lot_correlation` (dict): Material lot quality correlation data

## Implementation
The quality logic is implemented in `quality_assessor.py` and references tolerance data from CSV files:
- `parts.csv` - Reference data
- `cpk_thresholds.csv` - Reference data
- `lot_quality_history.csv` - Reference data
- `production_lines.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from quality_assessor import assess_quality

result = assess_quality(
    part_number="MFG-2024-001",
    measurements=[10.02, 10.01, 10.03, 9.98, 10.00],
    dimension_type="critical",
    material_lot="LOT-A-2024-0156",
    production_line="LINE-07",
    operator_id="OP-445"
)

print(f"Status: {result['quality_status']}")
print(f"Cpk: {result['process_capability']}")
```

## Test Execution
```python
from quality_assessor import assess_quality

result = assess_quality(
    part_number=input_data.get('part_number'),
    measurements=input_data.get('measurements', []),
    dimension_type=input_data.get('dimension_type', 'major'),
    material_lot=input_data.get('material_lot'),
    production_line=input_data.get('production_line'),
    operator_id=input_data.get('operator_id')
)
```
