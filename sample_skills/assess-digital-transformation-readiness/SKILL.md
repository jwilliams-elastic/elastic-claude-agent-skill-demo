# Skill: Assess Digital Transformation Readiness

## Domain
technology

## Description
Evaluates an organization's readiness for digital transformation across six critical dimensions: technology infrastructure, data maturity, talent & culture, process automation, customer experience, and innovation capacity. Produces a comprehensive readiness score with actionable recommendations for CIOs and transformation leaders.

**This skill uses interactive data collection** - it prompts the user for required information through a guided 3-step assessment process.

## Business Rules
This skill implements a proprietary digital transformation readiness framework based on Bain's methodology:

1. **Technology Infrastructure Score**: Legacy system burden, cloud adoption rate, API-first architecture, cybersecurity posture
2. **Data Maturity Score**: Data governance, analytics capabilities, real-time data access, data quality metrics
3. **Talent & Culture Score**: Digital skills inventory, change readiness, agile adoption, leadership alignment
4. **Process Automation Score**: RPA penetration, workflow digitization, straight-through processing rates
5. **Customer Experience Score**: Digital channel adoption, personalization capability, omnichannel integration
6. **Innovation Capacity Score**: R&D digital investment, time-to-market, experimentation culture, ecosystem partnerships

## Interactive Data Collection

This skill requires user input collected through 3 sequential prompts:

### Prompt 1: Company Profile
The agent will ask:
> "Please provide your company information for the digital transformation assessment:"
- **company_name** (string): Company or organization name
- **industry** (enum): Industry sector - one of: financial_services, healthcare, retail, manufacturing, technology, telecommunications, energy

### Prompt 2: Technology Infrastructure
The agent will ask:
> "Now let's assess your technology infrastructure. Please provide:"
- **legacy_system_percentage** (number 0-100): Percentage of IT systems older than 10 years
- **cloud_adoption_percentage** (number 0-100): Percentage of workloads running in cloud
- **analytics_maturity** (enum): Current analytics level - one of: descriptive, diagnostic, predictive, prescriptive

### Prompt 3: Organizational Readiness
The agent will ask:
> "Finally, let's evaluate your organizational readiness:"
- **digital_talent_percentage** (number 0-100): Percentage of workforce with digital/tech skills
- **agile_team_percentage** (number 0-100): Percentage of teams using agile methodologies
- **process_automation_rate** (number 0-100): Percentage of business processes with automation

## Input Parameters
- `company_name` (string): Name of the organization being assessed
- `industry` (string): Industry sector for benchmark comparison
- `legacy_system_percentage` (float): Percentage of systems older than 10 years (0-100)
- `cloud_adoption_percentage` (float): Percentage of workloads in cloud (0-100)
- `data_governance_score` (int): Self-assessed data governance maturity (1-5)
- `analytics_maturity` (string): "descriptive", "diagnostic", "predictive", or "prescriptive"
- `digital_talent_percentage` (float): Percentage of workforce with digital skills (0-100)
- `agile_team_percentage` (float): Percentage of teams using agile methodologies (0-100)
- `process_automation_rate` (float): Percentage of processes with automation (0-100)
- `digital_revenue_percentage` (float): Percentage of revenue from digital channels (0-100)
- `annual_rd_digital_percentage` (float): Percentage of R&D budget for digital initiatives (0-100)

## Output
Returns a transformation readiness assessment with:
- `overall_score` (float): Composite readiness score (0-100)
- `readiness_tier` (string): "Leader", "Fast Follower", "Cautious Adopter", or "At Risk"
- `dimension_scores` (dict): Individual scores for each of the 6 dimensions
- `industry_benchmark` (dict): Comparison to industry peers
- `critical_gaps` (list): Top areas requiring immediate attention
- `recommendations` (list): Prioritized transformation recommendations
- `estimated_timeline_months` (int): Estimated months to reach "Leader" tier

## Usage Example
```python
from transformation_readiness import assess_readiness

result = assess_readiness(
    company_name="Acme Corp",
    industry="financial_services",
    legacy_system_percentage=45,
    cloud_adoption_percentage=35,
    data_governance_score=3,
    analytics_maturity="diagnostic",
    digital_talent_percentage=25,
    agile_team_percentage=40,
    process_automation_rate=30,
    digital_revenue_percentage=20,
    annual_rd_digital_percentage=15
)

print(f"Overall Score: {result['overall_score']}")
print(f"Readiness Tier: {result['readiness_tier']}")
```

## Tags
technology, digital-transformation, cio, enterprise, strategy, cloud, data, automation

## Implementation
The assessment logic is implemented in `transformation_readiness.py` and references:
- `required_inputs.csv` - Interactive prompt definitions for data collection
- `dimension_weights.csv` - Weighting factors for each dimension
- `industry_benchmarks.csv` - Industry-specific benchmark data
- `maturity_thresholds.csv` - Tier classification thresholds
