# Skill: Calculate Insurance Premium

## Domain
insurance

## Description
Calculates insurance premiums using actuarial rating factors, risk classifications, and underwriting guidelines for various insurance products.

## Tags
insurance, premium-calculation, underwriting, actuarial, risk-pricing

## Use Cases
- New business quoting
- Renewal pricing
- Rate adequacy analysis
- Competitive positioning

## Proprietary Business Rules

### Rule 1: Base Rate Application
Territory and class-specific base rates with proprietary loss cost data.

### Rule 2: Rating Factor Application
Multiplicative factor application with interaction effects.

### Rule 3: Experience Modification
Loss history adjustments using credibility-weighted experience.

### Rule 4: Minimum Premium Enforcement
Product-specific minimum premium floors.

## Input Parameters
- `policy_type` (string): Insurance product type
- `coverage_limits` (dict): Coverage limits and deductibles
- `risk_characteristics` (dict): Risk profile data
- `territory` (string): Rating territory
- `effective_date` (string): Policy effective date
- `loss_history` (list): Prior loss experience

## Output
- `total_premium` (float): Final premium amount
- `premium_breakdown` (dict): Component premium detail
- `rating_factors` (dict): Applied rating factors
- `experience_mod` (float): Experience modification factor
- `tier_placement` (string): Risk tier assignment

## Implementation
The premium calculation logic is implemented in `premium_calculator.py` and references rates from CSV files:
- `products.csv` - Reference data
- `tier_rules.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from premium_calculator import calculate_premium

result = calculate_premium(
    policy_type="commercial_property",
    coverage_limits={"building": 1000000, "contents": 500000, "deductible": 5000},
    risk_characteristics={"construction": "fire_resistive", "occupancy": "office", "protection_class": 3},
    territory="NY-001",
    effective_date="2026-03-01",
    loss_history=[{"year": 2024, "losses": 15000}, {"year": 2025, "losses": 0}]
)

print(f"Premium: ${result['total_premium']}")
```

## Test Execution
```python
from premium_calculator import calculate_premium

result = calculate_premium(
    policy_type=input_data.get('policy_type'),
    coverage_limits=input_data.get('coverage_limits', {}),
    risk_characteristics=input_data.get('risk_characteristics', {}),
    territory=input_data.get('territory'),
    effective_date=input_data.get('effective_date'),
    loss_history=input_data.get('loss_history', [])
)
```
