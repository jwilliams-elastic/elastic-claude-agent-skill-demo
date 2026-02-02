# Skill: AI Product Quick TCO Calculator

## Domain
finance

## Description
Calculate the Total Cost of Ownership (TCO) and Return on Investment for AI products and tools. This skill evaluates the financial impact of AI adoption by comparing productivity gains against costs and security risks. Use this for AI tool evaluation, budget planning, ROI analysis, cost-benefit analysis, and technology investment decisions.

## Tags
TCO, ROI, AI, cost-analysis, productivity, security-risk, investment

## Input Parameters
- `total_users` (int): Total number of potential users for the AI product
- `cost_per_user_month` (float): Monthly cost per user license in dollars
- `user_adoption_pct` (float): Expected user adoption rate as decimal (0.0-1.0)
- `security_rating_pct` (float): Security rating/compliance score as decimal (0.0-1.0)
- `productivity_boost_pct` (float): Expected productivity improvement as decimal (0.0-1.0)

## Output
- `total_cost_year` (float): Annual cost based on adoption and licensing
- `productivity_value_year` (float): Annual value from productivity improvements
- `security_cost` (float): Risk-adjusted cost based on security rating
- `total_benefit` (float): Net benefit (productivity value minus security cost)
- `security_risk_ratio` (float): Risk multiplier based on security rating

## Implementation
Calculations in `ai_quick_tco_calculator.py` using reference data from:
- `reference_data.csv` - Contains yearly salary assumption and security risk thresholds

## Formulas
- **Total Cost/Year**: `total_users * user_adoption_pct * cost_per_user_month * months_per_year`
- **Productivity Value/Year**: `(productivity_boost_pct * yearly_salary) * (total_users * user_adoption_pct)`
- **Security Risk Ratio**: Tiered multiplier based on security rating:
  - Rating > 89%: 1.15x (low risk)
  - Rating > 69%: 2.0x (moderate risk)
  - Rating > 49%: 10.0x (high risk)
  - Rating > 0%: 20.0x (critical risk)
- **Security Cost**: `total_cost_year * security_risk_ratio`
- **Total Benefit**: `productivity_value_year - security_cost`
