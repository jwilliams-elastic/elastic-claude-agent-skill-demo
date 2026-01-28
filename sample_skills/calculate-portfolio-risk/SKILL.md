# Skill: Calculate Investment Portfolio Risk

## Domain
wealth_management

## Description
Analyzes investment portfolio composition to calculate risk metrics including VaR, volatility, and concentration risk based on proprietary risk models.

## Tags
wealth-management, portfolio-risk, var-calculation, investment-analysis, risk-metrics

## Use Cases
- Portfolio risk assessment
- Client suitability verification
- Rebalancing recommendations
- Regulatory reporting

## Proprietary Business Rules

### Rule 1: VaR Calculation Method
Proprietary VaR methodology using historical simulation with volatility scaling.

### Rule 2: Concentration Limits
Position and sector concentration limits based on client risk profile.

### Rule 3: Correlation Adjustments
Dynamic correlation estimates during stress periods.

### Rule 4: Liquidity Risk Scoring
Position liquidity assessment based on trading volume and market depth.

## Input Parameters
- `portfolio_id` (string): Portfolio identifier
- `positions` (list): Holdings with ticker, quantity, value
- `client_risk_profile` (string): Conservative, moderate, aggressive
- `time_horizon` (string): Short, medium, long term
- `benchmark` (string): Benchmark index
- `stress_scenario` (string): None, moderate, severe

## Output
- `var_95` (float): 95% Value at Risk
- `var_99` (float): 99% Value at Risk
- `volatility` (float): Annualized portfolio volatility
- `concentration_alerts` (list): Concentration limit breaches
- `risk_score` (int): Overall risk score 1-100

## Implementation
The risk calculation logic is implemented in `portfolio_risk_calculator.py` and references market data from CSV files:
- `securities.csv` - Reference data
- `risk_profiles.csv` - Reference data
- `stress_scenarios.csv` - Reference data
- `correlation_matrix.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from portfolio_risk_calculator import calculate_portfolio_risk

result = calculate_portfolio_risk(
    portfolio_id="PORT-12345",
    positions=[
        {"ticker": "AAPL", "quantity": 100, "value": 18500},
        {"ticker": "MSFT", "quantity": 50, "value": 19000}
    ],
    client_risk_profile="moderate",
    time_horizon="medium",
    benchmark="SPY",
    stress_scenario="none"
)

print(f"VaR 95%: ${result['var_95']}")
```

## Test Execution
```python
from portfolio_risk_calculator import calculate_portfolio_risk

result = calculate_portfolio_risk(
    portfolio_id=input_data.get('portfolio_id'),
    positions=input_data.get('positions', []),
    client_risk_profile=input_data.get('client_risk_profile', 'moderate'),
    time_horizon=input_data.get('time_horizon', 'medium'),
    benchmark=input_data.get('benchmark', 'SPY'),
    stress_scenario=input_data.get('stress_scenario', 'none')
)
```
