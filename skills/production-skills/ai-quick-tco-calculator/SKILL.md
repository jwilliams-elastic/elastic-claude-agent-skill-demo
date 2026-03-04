# Skill: AI Quick TCO Calculator

## Domain
finance

## Description
Calculate the Total Cost of Ownership for AI products and SaaS tools. Evaluates annual licensing costs against productivity gains and security risk exposure. Computes net benefit by comparing productivity value from user adoption against total cost adjusted for security risk. Useful for AI procurement decisions, SaaS vendor evaluation, cost-benefit analysis, and IT budget planning.

## Tags
tco, roi, ai, cost-benefit, saas, procurement

## Input Parameters
- `total_users` (int): Number of users who will have access to the AI product
- `cost_per_user_month` (float): Monthly license cost per user in dollars
- `user_adoption_pct` (float): Expected user adoption rate (0.0 to 1.0)
- `security_rating_pct` (float): Vendor security rating (0.0 to 1.0, higher is better)
- `productivity_boost_pct` (float): Expected productivity improvement (0.0 to 1.0)

## Output
- `total_cost_year` (float): Annual licensing cost based on active users
- `productivity_value_year` (float): Annual dollar value of productivity gains
- `security_risk_ratio` (float): Cost multiplier based on security rating
- `security_cost` (float): Total cost adjusted for security risk
- `total_benefit` (float): Net benefit (productivity value minus security cost)

## Implementation
Calculations in `ai_quick_tco_calculator.py` using reference data from:
- `reference_data.csv` - Yearly salary per user, months per year, and security risk thresholds

## Formulas
- **Total Cost / Year** = total_users * user_adoption_pct * cost_per_user_month * months_per_year
- **Productivity Value / Year** = productivity_boost_pct * yearly_salary * total_users * user_adoption_pct
- **Security Risk Ratio** = tiered lookup based on security_rating_pct thresholds
- **Security Cost** = total_cost_year * security_risk_ratio
- **Total Benefit** = productivity_value_year - security_cost
