# Skill: Analyze Chemical Compound Safety

## Domain
chemicals

## Description
Evaluates chemical compounds and mixtures for safety compliance, hazard classification, and handling requirements based on GHS standards and proprietary safety thresholds.

## Tags
chemicals, safety-compliance, ghs-classification, hazard-assessment, regulatory

## Use Cases
- New compound safety assessment
- SDS (Safety Data Sheet) generation support
- Chemical compatibility checking
- Transportation classification

## Proprietary Business Rules

### Rule 1: Exposure Limit Calculation
Proprietary exposure limits based on toxicological data and safety factors specific to industrial applications.

### Rule 2: Mixture Hazard Classification
Hazard classification for mixtures using proprietary algorithms beyond standard GHS calculations.

### Rule 3: Incompatibility Matrix
Chemical incompatibility rules based on internal incident data and reaction studies.

### Rule 4: PPE Requirements
Personal protective equipment requirements based on exposure scenario and compound properties.

## Input Parameters
- `compound_id` (string): Internal compound identifier
- `chemical_formula` (string): Chemical formula or CAS number
- `concentration` (float): Concentration percentage
- `exposure_route` (string): Inhalation, dermal, ingestion
- `exposure_duration` (string): Acute, short-term, chronic
- `mixing_compounds` (list): Other compounds in mixture

## Output
- `hazard_classification` (dict): GHS hazard categories
- `exposure_limits` (dict): OEL, PEL, TLV values
- `ppe_requirements` (list): Required protective equipment
- `handling_instructions` (list): Safe handling procedures
- `incompatibilities` (list): Incompatible materials

## Implementation
The safety analysis logic is implemented in `safety_analyzer.py` and references hazard data from CSV files:
- `compounds.csv` - Reference data
- `incompatibility_matrix.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from safety_analyzer import analyze_safety

result = analyze_safety(
    compound_id="CHEM-2024-001",
    chemical_formula="CH3OH",
    concentration=99.5,
    exposure_route="inhalation",
    exposure_duration="short-term",
    mixing_compounds=["H2O"]
)

print(f"Hazard Class: {result['hazard_classification']}")
```

## Test Execution
```python
from safety_analyzer import analyze_safety

result = analyze_safety(
    compound_id=input_data.get('compound_id'),
    chemical_formula=input_data.get('chemical_formula'),
    concentration=input_data.get('concentration', 100),
    exposure_route=input_data.get('exposure_route', 'inhalation'),
    exposure_duration=input_data.get('exposure_duration', 'acute'),
    mixing_compounds=input_data.get('mixing_compounds', [])
)
```
