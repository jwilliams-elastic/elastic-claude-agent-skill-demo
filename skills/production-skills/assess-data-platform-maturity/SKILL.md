# Skill: Assess Data Platform Maturity

## Domain
technology

## Description
Evaluates enterprise data platform maturity across data engineering, governance, analytics, and ML operations dimensions. Provides a comprehensive assessment for CDOs and CIOs to benchmark capabilities, identify gaps, and prioritize data infrastructure investments.

## Business Rules
This skill implements a data platform maturity model based on industry frameworks (DCAM, DAMA-DMBOK):

1. **Data Engineering Maturity**: Batch vs. streaming, ELT pipelines, data lakehouse architecture, DataOps practices
2. **Data Governance Maturity**: Cataloging, lineage, quality rules, stewardship, privacy controls
3. **Analytics Maturity**: Self-service BI adoption, semantic layers, embedded analytics, decision intelligence
4. **ML Operations Maturity**: Feature stores, model registry, automated retraining, A/B testing infrastructure
5. **Data Culture Score**: Data literacy programs, data-driven decision metrics, democratization index

## Input Parameters
- `organization_name` (string): Name of the organization
- `industry` (string): Industry for benchmark comparison
- `data_volume_tb` (float): Total data volume in TB
- `data_sources_count` (int): Number of integrated data sources
- `real_time_pipelines` (bool): Whether real-time/streaming pipelines exist
- `data_catalog_implemented` (bool): Whether enterprise data catalog exists
- `data_lineage_automated` (bool): Whether lineage is automatically tracked
- `data_quality_score` (float): Current data quality score if measured (0-100)
- `self_service_bi_adoption` (float): Percentage of business users with BI access (0-100)
- `ml_models_in_production` (int): Number of ML models in production
- `feature_store_implemented` (bool): Whether centralized feature store exists
- `mlops_automation_level` (string): "manual", "semi_automated", "fully_automated"
- `data_literacy_program` (bool): Whether formal data literacy training exists
- `data_mesh_adopted` (bool): Whether data mesh/domain-oriented architecture is used
- `cloud_data_platform` (string): Primary platform ("snowflake", "databricks", "bigquery", "redshift", "azure_synapse", "on_prem")

## Output
Returns a maturity assessment with:
- `overall_maturity_level` (int): 1-5 maturity level
- `overall_maturity_label` (string): "Initial", "Developing", "Defined", "Managed", "Optimizing"
- `dimension_scores` (dict): Scores for each maturity dimension
- `industry_percentile` (int): Percentile ranking vs. industry peers
- `capability_gaps` (list): Critical capability gaps identified
- `quick_wins` (list): High-impact, low-effort improvements
- `strategic_investments` (list): Major investments recommended
- `target_architecture` (dict): Recommended target state architecture
- `roadmap_phases` (list): Phased improvement roadmap
- `estimated_investment` (dict): Investment ranges by phase
- `business_value_potential` (dict): Projected value from improvements

## Usage Example
```python
from data_platform_maturity import assess_maturity

result = assess_maturity(
    organization_name="Acme Financial",
    industry="financial_services",
    data_volume_tb=500,
    data_sources_count=150,
    real_time_pipelines=True,
    data_catalog_implemented=True,
    data_lineage_automated=False,
    data_quality_score=72,
    self_service_bi_adoption=35,
    ml_models_in_production=12,
    feature_store_implemented=False,
    mlops_automation_level="semi_automated",
    data_literacy_program=True,
    data_mesh_adopted=False,
    cloud_data_platform="snowflake"
)
```

## Tags
technology, data-platform, analytics, mlops, data-governance, cdo, data-engineering, lakehouse

## Implementation
The maturity assessment logic is implemented in `data_platform_maturity.py` and references:
- `maturity_criteria.csv` - Detailed criteria for each maturity level
- `industry_benchmarks.csv` - Industry-specific benchmark data
- `capability_weights.csv` - Weighting factors for capability scoring
- `investment_ranges.csv` - Typical investment ranges by improvement type
