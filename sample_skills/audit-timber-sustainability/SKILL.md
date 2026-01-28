# Skill: Audit Timber Sustainability

## Domain
forest_products

## Description
Evaluates timber harvesting operations against sustainability certification standards (FSC, PEFC) and environmental compliance requirements.

## Tags
forestry, sustainability, certification, environmental-compliance, supply-chain

## Use Cases
- Chain of custody verification
- Sustainable harvest certification
- Environmental impact assessment
- Supplier compliance auditing

## Proprietary Business Rules

### Rule 1: Harvest Rate Limits
Annual allowable cut (AAC) calculations based on growth models and sustainability targets.

### Rule 2: Buffer Zone Compliance
Protected area and riparian buffer requirements vary by region and ecosystem type.

### Rule 3: Species Mix Requirements
Biodiversity requirements mandate species diversity thresholds in harvest areas.

### Rule 4: Regeneration Standards
Post-harvest regeneration requirements with species-specific success criteria.

## Input Parameters
- `harvest_unit_id` (string): Harvest unit identifier
- `harvest_volume` (float): Volume harvested (m3)
- `species_composition` (dict): Species and percentages
- `buffer_zones` (list): Buffer zone compliance data
- `regeneration_data` (dict): Regeneration survey results
- `certification_type` (string): FSC, PEFC, or SFI
- `ecosystem_type` (string): Forest ecosystem classification

## Output
- `compliance_status` (string): Compliant, non-compliant, conditional
- `certification_eligible` (bool): Meets certification requirements
- `findings` (list): Audit findings
- `corrective_actions` (list): Required corrective actions
- `sustainability_score` (float): Overall sustainability rating

## Implementation
The audit logic is implemented in `sustainability_auditor.py` and references standards from CSV files:
- `certifications.csv` - Reference data
- `ecosystems.csv` - Reference data
- `scoring_weights.csv` - Reference data
- `severity_definitions.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from sustainability_auditor import audit_sustainability

result = audit_sustainability(
    harvest_unit_id="HU-2024-001",
    harvest_volume=5000,
    species_composition={"douglas_fir": 0.6, "western_red_cedar": 0.3, "hemlock": 0.1},
    buffer_zones=[{"type": "riparian", "width_m": 30, "compliant": True}],
    regeneration_data={"seedlings_per_ha": 1200, "survival_rate": 0.85},
    certification_type="FSC",
    ecosystem_type="temperate_rainforest"
)

print(f"Status: {result['compliance_status']}")
```

## Test Execution
```python
from sustainability_auditor import audit_sustainability

result = audit_sustainability(
    harvest_unit_id=input_data.get('harvest_unit_id'),
    harvest_volume=input_data.get('harvest_volume'),
    species_composition=input_data.get('species_composition', {}),
    buffer_zones=input_data.get('buffer_zones', []),
    regeneration_data=input_data.get('regeneration_data', {}),
    certification_type=input_data.get('certification_type', 'FSC'),
    ecosystem_type=input_data.get('ecosystem_type')
)
```
