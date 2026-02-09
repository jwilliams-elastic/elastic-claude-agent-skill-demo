# Skill: Analyze ESG Score

## Domain
private_equity

## Description
Analyzes Environmental, Social, and Governance (ESG) factors to calculate composite ESG scores for investment screening and reporting.

## Tags
ESG, sustainability, investing, governance, social, environmental

## Use Cases
- ESG screening for investments
- Portfolio ESG analysis
- Regulatory ESG reporting
- Stakeholder disclosure

## Proprietary Business Rules

### Rule 1: Environmental Metrics
Carbon footprint, resource usage, and environmental impact scoring.

### Rule 2: Social Assessment
Labor practices, community impact, and diversity metrics.

### Rule 3: Governance Evaluation
Board composition, ethics policies, and transparency.

### Rule 4: Materiality Weighting
Industry-specific factor materiality application.

## Input Parameters
- `entity_id` (string): Entity identifier
- `environmental_data` (dict): Environmental metrics
- `social_data` (dict): Social metrics
- `governance_data` (dict): Governance metrics
- `industry` (string): Industry classification
- `peer_data` (list): Peer comparison data

## Output
- `esg_score` (float): Composite ESG score
- `pillar_scores` (dict): E, S, G individual scores
- `materiality_assessment` (dict): Material factor analysis
- `peer_comparison` (dict): Relative peer ranking
- `improvement_areas` (list): Areas for ESG improvement

## Implementation
The analysis logic is implemented in `esg_analyzer.py` and references data from CSV files:
- `pillar_weights.csv` - Reference data
- `environmental_benchmarks.csv` - Reference data
- `social_benchmarks.csv` - Reference data
- `governance_requirements.csv` - Reference data
- `scoring_thresholds.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from esg_analyzer import analyze_esg

result = analyze_esg(
    entity_id="COMP-001",
    environmental_data={"carbon_intensity": 150, "renewable_pct": 0.35, "waste_recycled": 0.6},
    social_data={"diversity_pct": 0.40, "safety_incidents": 2, "turnover_rate": 0.12},
    governance_data={"board_independence": 0.7, "ethics_policy": True, "audit_committee": True},
    industry="manufacturing",
    peer_data=[{"id": "PEER-001", "esg_score": 65}]
)

print(f"ESG Score: {result['esg_score']}")
```

## Test Execution
```python
from esg_analyzer import analyze_esg

result = analyze_esg(
    entity_id=input_data.get('entity_id'),
    environmental_data=input_data.get('environmental_data', {}),
    social_data=input_data.get('social_data', {}),
    governance_data=input_data.get('governance_data', {}),
    industry=input_data.get('industry'),
    peer_data=input_data.get('peer_data', [])
)
```
