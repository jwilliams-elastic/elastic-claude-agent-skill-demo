# Skill: AI Product Quick TCO Calculator

## Domain
finance

## Description
Calculate total cost of ownership (TCO) and return on investment (ROI) for AI products based on user count, monthly cost, adoption rate, security rating, and productivity impact. Determines productivity value and security risk costs to compute net benefit. Useful for evaluating AI tool purchases, comparing vendors, and justifying AI investments with financial analysis.

## Tags
tco, roi, cost-benefit, ai-product

## Input Parameters
- `total_users` (int): Total number of potential users in organization
- `cost_per_user_month` (float): Monthly cost per user license in dollars
- `adoption_rate` (float): Expected user adoption rate (0.0 to 1.0)
- `security_rating` (float): Security rating score (0.0 to 1.0, higher is better)
- `productivity_boost` (float): Expected productivity improvement rate (0.0 to 1.0)

## Output
- `total_cost_year` (float): Total annual cost in dollars
- `productivity_value_year` (float): Annual productivity value in dollars
- `security_cost` (float): Annual security risk cost in dollars
- `total_benefit` (float): Net annual benefit (productivity - security cost) in dollars
- `security_risk_ratio` (float): Security risk multiplier applied to costs
- `inputs` (dict): Echo of input parameters for verification

## Implementation
Calculations in `ai_quick_tco_calculator.py` using reference data from:
- `reference_data.csv` - Yearly salary, time constants, and security risk tier thresholds

## Formulas
1. **Total Cost per Year** = `total_users × adoption_rate × cost_per_user_month × months_per_year`
2. **Productivity Value per Year** = `productivity_boost × yearly_salary_per_user × total_users × adoption_rate`
3. **Security Risk Ratio** (tiered based on security_rating):
   - If security_rating > 0.89: 1.15×
   - Else if security_rating > 0.69: 2.0×
   - Else if security_rating > 0.49: 10.0×
   - Else: 20.0×
4. **Security Cost** = `total_cost_year × security_risk_ratio`
5. **Total Benefit** = `productivity_value_year - security_cost`
