"""AI Product Quick TCO Calculator"""
import csv
from pathlib import Path


def load_reference_data():
    """Load all constants from CSV - no hardcoded values."""
    csv_path = Path(__file__).parent / "reference_data.csv"
    data = {}
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            val = row['value']
            try:
                data[row['variable']] = float(val) if '.' in val else int(val)
            except ValueError:
                data[row['variable']] = val
    return data


def get_security_risk_ratio(security_rating: float, ref: dict) -> float:
    """Calculate security risk ratio based on tiered thresholds."""
    if security_rating > ref['security_threshold_low']:
        return ref['security_multiplier_low']
    elif security_rating > ref['security_threshold_moderate']:
        return ref['security_multiplier_moderate']
    elif security_rating > ref['security_threshold_high']:
        return ref['security_multiplier_high']
    else:
        return ref['security_multiplier_critical']


def calculate(inputs: dict) -> dict:
    """
    Calculate AI product TCO and benefits.

    Args:
        inputs: Dictionary with keys:
            - total_users: Total number of potential users
            - cost_per_user_month: Monthly cost per user ($)
            - user_adoption_pct: Expected adoption rate (0.0-1.0)
            - security_rating_pct: Security/compliance score (0.0-1.0)
            - productivity_boost_pct: Expected productivity gain (0.0-1.0)

    Returns:
        Dictionary with calculated TCO metrics
    """
    ref = load_reference_data()

    # Extract inputs
    total_users = inputs['total_users']
    cost_per_user_month = inputs['cost_per_user_month']
    user_adoption_pct = inputs['user_adoption_pct']
    security_rating_pct = inputs['security_rating_pct']
    productivity_boost_pct = inputs['productivity_boost_pct']

    # Calculate active users
    active_users = total_users * user_adoption_pct

    # Total Cost / Year = users * adoption * cost_per_month * 12
    total_cost_year = active_users * cost_per_user_month * ref['months_per_year']

    # Productivity Value / Year = (productivity_boost * yearly_salary) * active_users
    productivity_value_year = (productivity_boost_pct * ref['yearly_salary']) * active_users

    # Security Risk Ratio based on tiered thresholds
    security_risk_ratio = get_security_risk_ratio(security_rating_pct, ref)

    # Security Cost = total_cost_year * security_risk_ratio
    security_cost = total_cost_year * security_risk_ratio

    # Total Benefit = productivity_value - security_cost
    total_benefit = productivity_value_year - security_cost

    return {
        'total_cost_year': round(total_cost_year, 2),
        'productivity_value_year': round(productivity_value_year, 2),
        'security_risk_ratio': security_risk_ratio,
        'security_cost': round(security_cost, 2),
        'total_benefit': round(total_benefit, 2),
        'inputs': inputs
    }


if __name__ == "__main__":
    # Test with spreadsheet default values
    result = calculate({
        'total_users': 100,
        'cost_per_user_month': 99,
        'user_adoption_pct': 0.3,
        'security_rating_pct': 0.9,
        'productivity_boost_pct': 0.2
    })

    print("AI Product Quick TCO Calculator - Verification")
    print("=" * 50)
    print(f"Inputs: {result['inputs']}")
    print(f"Total Cost/Year:        ${result['total_cost_year']:,.2f}")
    print(f"Productivity Value/Year: ${result['productivity_value_year']:,.2f}")
    print(f"Security Risk Ratio:    {result['security_risk_ratio']}")
    print(f"Security Cost:          ${result['security_cost']:,.2f}")
    print(f"Total Benefit:          ${result['total_benefit']:,.2f}")
