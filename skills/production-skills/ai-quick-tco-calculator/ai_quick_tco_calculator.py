"""AI Quick TCO Calculator"""
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


def get_security_risk_ratio(security_rating_pct, ref):
    """Tiered security risk ratio based on vendor security rating."""
    if security_rating_pct > ref['security_threshold_high']:
        return ref['security_ratio_high']
    elif security_rating_pct > ref['security_threshold_medium']:
        return ref['security_ratio_medium']
    elif security_rating_pct > ref['security_threshold_low']:
        return ref['security_ratio_low']
    else:
        return ref['security_ratio_critical']


def calculate(inputs: dict) -> dict:
    """Main calculation function."""
    ref = load_reference_data()

    total_users = inputs['total_users']
    cost_per_user_month = inputs['cost_per_user_month']
    user_adoption_pct = inputs['user_adoption_pct']
    security_rating_pct = inputs['security_rating_pct']
    productivity_boost_pct = inputs['productivity_boost_pct']

    total_cost_year = total_users * user_adoption_pct * cost_per_user_month * ref['months_per_year']
    productivity_value_year = productivity_boost_pct * ref['yearly_salary'] * total_users * user_adoption_pct
    security_risk_ratio = get_security_risk_ratio(security_rating_pct, ref)
    security_cost = total_cost_year * security_risk_ratio
    total_benefit = productivity_value_year - security_cost

    return {
        'total_cost_year': total_cost_year,
        'productivity_value_year': productivity_value_year,
        'security_risk_ratio': security_risk_ratio,
        'security_cost': security_cost,
        'total_benefit': total_benefit,
        'inputs': inputs
    }


if __name__ == "__main__":
    result = calculate({
        'total_users': 100,
        'cost_per_user_month': 99,
        'user_adoption_pct': 0.3,
        'security_rating_pct': 0.9,
        'productivity_boost_pct': 0.2
    })
    for k, v in result.items():
        if k != 'inputs':
            print(f"  {k}: {v}")
