# Skill: Evaluate M&A Technology Synergy

## Domain
private_equity

## Description
Evaluates technology synergy potential in M&A transactions by analyzing platform consolidation opportunities, tech stack compatibility, talent retention risks, and integration complexity. Provides quantified synergy estimates and integration risk assessment for deal teams and operating partners.

## Business Rules
This skill implements technology due diligence and synergy analysis for M&A:

1. **Platform Consolidation**: Overlapping enterprise platforms (ERP, CRM, HCM) yield 40-60% cost synergy in Year 2+
2. **Infrastructure Rationalization**: Data center/cloud consolidation typically achieves 25-35% savings
3. **Application Portfolio**: Each redundant application retirement saves $150K-$500K annually (maintenance, licensing)
4. **Tech Talent Premium**: Acquirer pays 15-25% retention premium for critical tech talent in first 18 months
5. **Integration Complexity Score**: Based on system count, API maturity, data architecture alignment
6. **Synergy Realization Timeline**: Infrastructure (6-12 months), Applications (12-24 months), Full integration (24-36 months)

## Input Parameters
- `deal_name` (string): Name/code for the transaction
- `acquirer_name` (string): Acquiring company name
- `target_name` (string): Target company name
- `acquirer_tech_spend` (float): Acquirer's annual IT spend ($M)
- `target_tech_spend` (float): Target's annual IT spend ($M)
- `acquirer_erp` (string): Acquirer's ERP system
- `target_erp` (string): Target's ERP system
- `acquirer_cloud_provider` (string): Primary cloud (aws, azure, gcp, on_prem)
- `target_cloud_provider` (string): Target's primary cloud
- `acquirer_app_count` (int): Number of applications in acquirer portfolio
- `target_app_count` (int): Number of applications in target portfolio
- `estimated_app_overlap_pct` (float): Estimated application overlap (0-100)
- `target_tech_headcount` (int): Target's IT/tech employee count
- `critical_tech_talent_count` (int): Number of key tech employees to retain
- `target_tech_debt_rating` (string): "low", "medium", "high", "critical"
- `integration_strategy` (string): "absorption", "best_of_breed", "transformation", "preservation"
- `deal_timeline_months` (int): Expected deal close to Day 1 timeline

## Output
Returns a technology synergy analysis with:
- `total_synergy_estimate` (dict): Year 1, Year 2, Year 3, Run-rate synergies ($M)
- `synergy_confidence` (string): "high", "medium", "low"
- `synergy_breakdown` (dict): Synergies by category (infrastructure, applications, labor, vendor)
- `integration_complexity_score` (int): 1-10 complexity rating
- `integration_risk_factors` (list): Key risks with likelihood and impact
- `talent_retention_cost` (float): Estimated retention package cost ($M)
- `one_time_integration_cost` (float): Total integration investment required ($M)
- `payback_months` (int): Months to synergy payback
- `recommended_integration_approach` (dict): Phased integration recommendations
- `quick_wins` (list): Day 1-100 synergy opportunities
- `deal_breakers` (list): Critical issues that could derail integration

## Usage Example
```python
from ma_tech_synergy import evaluate_synergy

result = evaluate_synergy(
    deal_name="Project Atlas",
    acquirer_name="TechCorp",
    target_name="DataCo",
    acquirer_tech_spend=250,
    target_tech_spend=80,
    acquirer_erp="SAP S/4HANA",
    target_erp="Oracle EBS",
    acquirer_cloud_provider="aws",
    target_cloud_provider="azure",
    acquirer_app_count=200,
    target_app_count=75,
    estimated_app_overlap_pct=35,
    target_tech_headcount=150,
    critical_tech_talent_count=25,
    target_tech_debt_rating="medium",
    integration_strategy="absorption",
    deal_timeline_months=6
)
```

## Tags
private-equity, ma, technology, synergy, due-diligence, integration, deal, portfolio-operations

## Implementation
The synergy analysis logic is implemented in `ma_tech_synergy.py` and references:
- `synergy_benchmarks.csv` - Industry synergy benchmarks by category
- `platform_compatibility.csv` - ERP/CRM compatibility and migration costs
- `integration_complexity_factors.csv` - Complexity scoring criteria
- `talent_retention_premiums.csv` - Retention cost factors by role type
