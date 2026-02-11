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


def calculate(inputs: dict) -> dict:
    """
    Calculate TCO and ROI for AI product investment.

    Args:
        inputs: Dictionary with keys:
            - total_users: Total number of potential users
            - cost_per_user_month: Monthly cost per user in dollars
            - adoption_rate: User adoption rate (0.0 to 1.0)
            - security_rating: Security rating score (0.0 to 1.0)
            - productivity_boost: Productivity improvement rate (0.0 to 1.0)

    Returns:
        Dictionary with calculated TCO metrics
    """
    ref = load_reference_data()

    # Extract inputs
    total_users = inputs['total_users']
    cost_per_user_month = inputs['cost_per_user_month']
    adoption_rate = inputs['adoption_rate']
    security_rating = inputs['security_rating']
    productivity_boost = inputs['productivity_boost']

    # Calculate total cost per year
    total_cost_year = (
        total_users *
        adoption_rate *
        cost_per_user_month *
        ref['months_per_year']
    )

    # Calculate productivity value per year
    productivity_value_year = (
        productivity_boost *
        ref['yearly_salary_per_user'] *
        total_users *
        adoption_rate
    )

    # Determine security risk ratio using tiered thresholds
    if security_rating > ref['security_tier_1_threshold']:
        security_risk_ratio = ref['security_tier_1_multiplier']
    elif security_rating > ref['security_tier_2_threshold']:
        security_risk_ratio = ref['security_tier_2_multiplier']
    elif security_rating > ref['security_tier_3_threshold']:
        security_risk_ratio = ref['security_tier_3_multiplier']
    else:
        security_risk_ratio = ref['security_tier_4_multiplier']

    # Calculate security cost
    security_cost = total_cost_year * security_risk_ratio

    # Calculate total benefit
    total_benefit = productivity_value_year - security_cost

    return {
        'total_cost_year': round(total_cost_year, 2),
        'productivity_value_year': round(productivity_value_year, 2),
        'security_cost': round(security_cost, 2),
        'total_benefit': round(total_benefit, 2),
        'security_risk_ratio': security_risk_ratio,
        'inputs': inputs  # Echo for verification
    }


if __name__ == "__main__":
    # Test with spreadsheet default values
    test_inputs = {
        'total_users': 100,
        'cost_per_user_month': 99.0,
        'adoption_rate': 0.3,
        'security_rating': 0.9,
        'productivity_boost': 0.2
    }

    result = calculate(test_inputs)

    print("AI Product Quick TCO Calculator - Test Results")
    print("=" * 50)
    print(f"Total Cost/Year:         ${result['total_cost_year']:,.2f}")
    print(f"Productivity Value/Year: ${result['productivity_value_year']:,.2f}")
    print(f"Security Cost:           ${result['security_cost']:,.2f}")
    print(f"Security Risk Ratio:     {result['security_risk_ratio']}x")
    print(f"Total Benefit:           ${result['total_benefit']:,.2f}")
