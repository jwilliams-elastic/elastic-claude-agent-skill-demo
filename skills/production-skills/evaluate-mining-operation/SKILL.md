# Skill: Evaluate Mining Operation Efficiency

## Domain
mining

## Description
Analyzes mining operation metrics to evaluate efficiency, safety compliance, and recommend optimization strategies based on operational benchmarks.

## Tags
mining, operations, efficiency, safety-compliance, resource-extraction

## Use Cases
- Operational efficiency assessment
- Equipment utilization analysis
- Safety compliance monitoring
- Production cost optimization

## Proprietary Business Rules

### Rule 1: Equipment Availability Targets
Minimum availability thresholds by equipment type with penalty calculations for downtime.

### Rule 2: Ore Grade Reconciliation
Variance limits between predicted and actual ore grades trigger investigation.

### Rule 3: Safety Incident Rate
Lost time injury frequency rate (LTIFR) thresholds by operation type.

### Rule 4: Energy Intensity Benchmarks
Energy consumption per tonne benchmarks by mining method.

## Input Parameters
- `operation_id` (string): Mining operation identifier
- `mining_method` (string): Open pit, underground, placer
- `production_data` (dict): Tonnes mined, ore grade, strip ratio
- `equipment_metrics` (list): Equipment availability and utilization
- `safety_data` (dict): Incidents, near misses, hours worked
- `energy_consumption` (dict): Fuel, electricity usage
- `labor_data` (dict): Workforce metrics

## Output
- `efficiency_score` (float): Overall efficiency rating
- `safety_rating` (string): Safety performance rating
- `bottlenecks` (list): Identified operational constraints
- `optimization_opportunities` (list): Improvement recommendations
- `benchmark_comparison` (dict): Performance vs benchmarks

## Implementation
The evaluation logic is implemented in `operation_evaluator.py` and references benchmarks from `mining_benchmarks.csv`.

## Usage Example
```python
from operation_evaluator import evaluate_operation

result = evaluate_operation(
    operation_id="MINE-001",
    mining_method="open_pit",
    production_data={"tonnes_mined": 500000, "ore_grade": 0.8, "strip_ratio": 3.5},
    equipment_metrics=[{"type": "haul_truck", "availability": 0.88, "utilization": 0.75}],
    safety_data={"lost_time_incidents": 1, "hours_worked": 250000},
    energy_consumption={"diesel_liters": 1500000, "electricity_kwh": 8000000},
    labor_data={"headcount": 350, "productivity_tonnes_per_person": 1428}
)

print(f"Efficiency Score: {result['efficiency_score']}")
```

## Test Execution
```python
from operation_evaluator import evaluate_operation

result = evaluate_operation(
    operation_id=input_data.get('operation_id'),
    mining_method=input_data.get('mining_method'),
    production_data=input_data.get('production_data', {}),
    equipment_metrics=input_data.get('equipment_metrics', []),
    safety_data=input_data.get('safety_data', {}),
    energy_consumption=input_data.get('energy_consumption', {}),
    labor_data=input_data.get('labor_data', {})
)
```
