# Skill: Process Private Equity Deal Screening

## Domain
private_equity

## Description
Screens potential investment opportunities against fund investment criteria, performing preliminary due diligence scoring and deal qualification.

## Tags
private-equity, deal-screening, due-diligence, investment-criteria, portfolio

## Use Cases
- Deal flow screening
- Investment criteria matching
- Preliminary valuation assessment
- Portfolio fit analysis

## Proprietary Business Rules

### Rule 1: Investment Criteria Matching
Fund-specific investment parameters including sector, size, and geography.

### Rule 2: Value Creation Assessment
Scoring potential for operational improvement and growth initiatives.

### Rule 3: Risk Factor Evaluation
Proprietary risk scoring across market, operational, and financial dimensions.

### Rule 4: Portfolio Concentration Limits
Sector and geography concentration checks against fund constraints.

## Input Parameters
- `deal_id` (string): Deal identifier
- `company_profile` (dict): Target company details
- `financials` (dict): Key financial metrics
- `sector` (string): Industry sector
- `geography` (string): Primary geography
- `deal_size` (float): Enterprise value
- `fund_id` (string): Target fund
- `management_quality` (int): Management score 1-10

## Output
- `screening_status` (string): Pursue, pass, review
- `criteria_match_score` (float): Fit score 0-100
- `value_creation_potential` (dict): Value creation assessment
- `risk_assessment` (dict): Risk scoring
- `recommendation` (string): Investment recommendation

## Implementation
The screening logic is implemented in `deal_screener.py` and references criteria from CSV files:
- `funds.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from deal_screener import screen_deal

result = screen_deal(
    deal_id="DEAL-2024-001",
    company_profile={"name": "TechCo Inc", "employees": 500, "founded": 2015},
    financials={"revenue": 50000000, "ebitda": 8000000, "growth_rate": 0.25},
    sector="technology",
    geography="north_america",
    deal_size=100000000,
    fund_id="FUND-GROWTH-I",
    management_quality=8
)

print(f"Status: {result['screening_status']}")
```

## Test Execution
```python
from deal_screener import screen_deal

result = screen_deal(
    deal_id=input_data.get('deal_id'),
    company_profile=input_data.get('company_profile', {}),
    financials=input_data.get('financials', {}),
    sector=input_data.get('sector'),
    geography=input_data.get('geography'),
    deal_size=input_data.get('deal_size', 0),
    fund_id=input_data.get('fund_id'),
    management_quality=input_data.get('management_quality', 5)
)
```
