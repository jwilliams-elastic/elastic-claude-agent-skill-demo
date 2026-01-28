# Skill: Evaluate Real Estate Investment

## Domain
real_estate

## Description
Analyzes commercial real estate investment opportunities using proprietary valuation models, cap rate analysis, and risk-adjusted return calculations.

## Tags
real-estate, investment-analysis, valuation, cap-rate, property-assessment

## Use Cases
- Acquisition underwriting
- Portfolio performance review
- Disposition analysis
- Development feasibility

## Proprietary Business Rules

### Rule 1: Cap Rate Benchmarking
Property-type and market-specific cap rate comparisons against proprietary benchmarks.

### Rule 2: NOI Projection Methodology
Standardized NOI projection with market-specific vacancy and expense assumptions.

### Rule 3: Risk-Adjusted Returns
IRR calculations with property and market risk premiums.

### Rule 4: Debt Service Coverage
Minimum DSCR requirements by property type and lender profile.

## Input Parameters
- `property_id` (string): Property identifier
- `property_type` (string): Office, retail, industrial, multifamily
- `market` (string): MSA or market identifier
- `asking_price` (float): Purchase price
- `noi` (float): Current net operating income
- `square_feet` (int): Rentable square feet
- `occupancy` (float): Current occupancy rate
- `lease_terms` (dict): Lease structure details
- `capex_needed` (float): Capital expenditure requirements

## Output
- `investment_rating` (string): Buy, hold, pass
- `cap_rate` (float): Going-in cap rate
- `projected_irr` (float): Projected internal rate of return
- `risk_score` (int): Investment risk score
- `valuation_range` (dict): Value range estimate

## Implementation
The analysis logic is implemented in `investment_analyzer.py` and references market data from CSV files:
- `markets.csv` - Reference data
- `property_types.csv` - Reference data
- `financing_assumptions.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from investment_analyzer import evaluate_investment

result = evaluate_investment(
    property_id="PROP-2024-001",
    property_type="office",
    market="NYC",
    asking_price=50000000,
    noi=3000000,
    square_feet=100000,
    occupancy=0.92,
    lease_terms={"walt": 5.2, "escalations": 0.03},
    capex_needed=2000000
)

print(f"Rating: {result['investment_rating']}")
print(f"IRR: {result['projected_irr']:.1%}")
```

## Test Execution
```python
from investment_analyzer import evaluate_investment

result = evaluate_investment(
    property_id=input_data.get('property_id'),
    property_type=input_data.get('property_type'),
    market=input_data.get('market'),
    asking_price=input_data.get('asking_price'),
    noi=input_data.get('noi'),
    square_feet=input_data.get('square_feet'),
    occupancy=input_data.get('occupancy'),
    lease_terms=input_data.get('lease_terms', {}),
    capex_needed=input_data.get('capex_needed', 0)
)
```
