# Skill: Calculate Actuarial Reserve

## Domain
insurance

## Description
Calculates insurance policy reserves using actuarial methods including loss development, IBNR estimation, and statutory reserve requirements.

## Tags
actuarial, reserves, insurance, IBNR, loss-development, statutory

## Use Cases
- Loss reserve calculation
- IBNR estimation
- Reserve adequacy testing
- Statutory reporting

## Proprietary Business Rules

### Rule 1: Loss Development Factors
Application of historical loss development patterns.

### Rule 2: IBNR Calculation
Incurred but not reported claims estimation methods.

### Rule 3: Case Reserve Adequacy
Evaluation of individual case reserves.

### Rule 4: Statutory Compliance
Minimum reserve requirements by line of business.

## Input Parameters
- `valuation_date` (string): Reserve valuation date
- `loss_triangles` (dict): Historical loss data
- `case_reserves` (dict): Current case reserves
- `premium_data` (dict): Earned premium by period
- `line_of_business` (string): Insurance line
- `prior_estimates` (dict): Previous reserve estimates

## Output
- `total_reserve` (float): Total required reserve
- `ibnr_estimate` (float): IBNR component
- `development_factors` (dict): Selected factors
- `adequacy_assessment` (dict): Reserve adequacy analysis
- `statutory_minimum` (float): Minimum required reserve

## Implementation
The calculation logic is implemented in `reserve_calculator.py` and references data from CSV files:
- `method_weights.csv` - Reference data
- `statutory_factors.csv` - Reference data
- `adequacy_thresholds.csv` - Reference data
- `industry_ldfs.csv` - Reference data
- `expense_factors.csv` - Reference data
- `discount_factors.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from reserve_calculator import calculate_reserve

result = calculate_reserve(
    valuation_date="2025-12-31",
    loss_triangles={"paid": [[100, 150, 180], [120, 175]], "incurred": [[150, 190, 200], [180, 220]]},
    case_reserves={"open_claims": 500000, "claim_count": 150},
    premium_data={"earned_2024": 5000000, "earned_2025": 5500000},
    line_of_business="commercial_auto",
    prior_estimates={"total": 2000000, "ibnr": 800000}
)

print(f"Total Reserve: ${result['total_reserve']:,.0f}")
```

## Test Execution
```python
from reserve_calculator import calculate_reserve

result = calculate_reserve(
    valuation_date=input_data.get('valuation_date'),
    loss_triangles=input_data.get('loss_triangles', {}),
    case_reserves=input_data.get('case_reserves', {}),
    premium_data=input_data.get('premium_data', {}),
    line_of_business=input_data.get('line_of_business'),
    prior_estimates=input_data.get('prior_estimates', {})
)
```
