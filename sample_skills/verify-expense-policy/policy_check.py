"""
Expense Policy Verification Module

Implements proprietary business rules for expense validation that cannot be
inferred without access to company policy documentation.
"""

import csv
from pathlib import Path
from typing import Dict, List, Optional, Any



def load_csv_as_dict(filename: str, key_column: str = 'id') -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column, row.get('key', ''))
            # Convert numeric values
            for k, v in list(row.items()):
                if v == '':
                    continue
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result[key] = row
    return result


def load_csv_as_list(filename: str) -> List[Dict[str, Any]]:
    """Load a CSV file and return as list of dictionaries."""
    csv_path = Path(__file__).parent / filename
    result = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric values
            for k, v in list(row.items()):
                if v == '':
                    continue
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result.append(row)
    return result


def load_parameters(filename: str = 'parameters.csv') -> Dict[str, Any]:
    """Load parameters CSV as key-value dictionary."""
    csv_path = Path(__file__).parent / filename
    if not csv_path.exists():
        return {}
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('key', '')
            value = row.get('value', '')
            try:
                if '.' in str(value):
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except (ValueError, TypeError):
                if value.lower() == 'true':
                    result[key] = True
                elif value.lower() == 'false':
                    result[key] = False
                else:
                    result[key] = value
    return result

def load_key_value_csv(filename: str) -> Dict[str, Any]:
    """Load a key-value CSV file as a flat dictionary."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('key', row.get('id', ''))
            value = row.get('value', '')
            try:
                if '.' in str(value):
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except (ValueError, TypeError):
                if str(value).lower() == 'true':
                    result[key] = True
                elif str(value).lower() == 'false':
                    result[key] = False
                else:
                    result[key] = value
    return result


def load_allowance_table() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    category_limits_data = load_csv_as_dict("category_limits.csv")
    approval_thresholds_data = load_csv_as_dict("approval_thresholds.csv")
    special_rules_data = load_key_value_csv("special_rules.csv")
    metadata_data = load_key_value_csv("metadata.csv")
    params = load_parameters()
    return {
        "category_limits": category_limits_data,
        "approval_thresholds": approval_thresholds_data,
        "special_rules": special_rules_data,
        "metadata": metadata_data,
        **params
    }


def verify_expense(
    amount: float,
    category: str,
    headcount: Optional[int] = None,
    procurement_ticket_id: Optional[str] = None,
    approvals: Optional[List[str]] = None
) -> Dict[str, Any]:
    """
    Verify expense against company policy rules.

    Args:
        amount: Expense amount in USD
        category: Expense category
        headcount: Number of people (required for Team_Dinner)
        procurement_ticket_id: Procurement ticket ID (required for Software)
        approvals: List of approvals already obtained

    Returns:
        Dictionary containing:
        - compliant: bool indicating if expense meets all policies
        - violations: list of policy violations
        - required_actions: list of actions needed for compliance
    """
    if approvals is None:
        approvals = []

    violations = []
    required_actions = []
    allowance_table = load_allowance_table()

    # Rule 1: Amount Threshold - expenses > $500 require VP_APPROVAL
    if amount > 500.00:
        if "VP_APPROVAL" not in approvals:
            violations.append(f"Expense amount ${amount:.2f} exceeds $500 threshold")
            required_actions.append("Obtain VP_APPROVAL for expenses over $500")

    # Rule 2: Team Dinner Cap - $75/head limit
    if category == "Team_Dinner":
        if headcount is None or headcount <= 0:
            violations.append("Team_Dinner expenses require valid headcount")
            required_actions.append("Provide headcount for Team_Dinner expense")
        else:
            per_head_limit = allowance_table["category_limits"]["Team_Dinner"]["per_head_max"]
            per_head_amount = amount / headcount

            if per_head_amount > per_head_limit:
                violations.append(
                    f"Team_Dinner expense ${per_head_amount:.2f}/head exceeds "
                    f"${per_head_limit:.2f}/head limit"
                )
                required_actions.append(
                    f"Reduce per-head cost to ${per_head_limit:.2f} or obtain exception approval"
                )

    # Rule 3: Software Procurement - requires Procurement_Ticket_ID
    if category == "Software":
        if not procurement_ticket_id or procurement_ticket_id.strip() == "":
            violations.append("Software expenses require a Procurement_Ticket_ID")
            required_actions.append(
                "Create procurement ticket and provide Procurement_Ticket_ID"
            )
        else:
            # Validate ticket ID format (basic check)
            if not procurement_ticket_id.startswith("PROC-"):
                violations.append(
                    f"Invalid Procurement_Ticket_ID format: {procurement_ticket_id}"
                )
                required_actions.append(
                    "Procurement_Ticket_ID must follow format: PROC-XXXXX"
                )

    # Additional validation: Check category exists in allowance table
    valid_categories = allowance_table["valid_categories"]
    if category not in valid_categories:
        violations.append(f"Invalid expense category: {category}")
        required_actions.append(
            f"Use valid category from: {', '.join(valid_categories)}"
        )

    return {
        "compliant": len(violations) == 0,
        "violations": violations,
        "required_actions": required_actions,
        "amount": amount,
        "category": category
    }


def main():
    """Example usage of the expense verification system."""
    print("=" * 60)
    print("Expense Policy Verification Examples")
    print("=" * 60)

    # Example 1: High-value software purchase (should fail - needs VP approval and ticket)
    print("\n1. High-value software purchase ($750, no approvals):")
    result = verify_expense(
        amount=750.00,
        category="Software",
        procurement_ticket_id=None,
        approvals=[]
    )
    print(f"   Compliant: {result['compliant']}")
    if result['violations']:
        print(f"   Violations: {', '.join(result['violations'])}")
    if result['required_actions']:
        print(f"   Required Actions: {', '.join(result['required_actions'])}")

    # Example 2: Compliant software purchase
    print("\n2. Compliant software purchase ($750 with VP approval and ticket):")
    result = verify_expense(
        amount=750.00,
        category="Software",
        procurement_ticket_id="PROC-12345",
        approvals=["VP_APPROVAL", "MANAGER_APPROVAL"]
    )
    print(f"   Compliant: {result['compliant']}")

    # Example 3: Team dinner over per-head limit
    print("\n3. Team dinner over per-head limit ($500 for 5 people = $100/head):")
    result = verify_expense(
        amount=500.00,
        category="Team_Dinner",
        headcount=5,
        approvals=[]
    )
    print(f"   Compliant: {result['compliant']}")
    if result['violations']:
        print(f"   Violations: {', '.join(result['violations'])}")

    # Example 4: Compliant team dinner
    print("\n4. Compliant team dinner ($300 for 5 people = $60/head):")
    result = verify_expense(
        amount=300.00,
        category="Team_Dinner",
        headcount=5,
        approvals=[]
    )
    print(f"   Compliant: {result['compliant']}")

    # Example 5: Low-value office supplies (should pass)
    print("\n5. Low-value office supplies ($75):")
    result = verify_expense(
        amount=75.00,
        category="Office_Supplies",
        approvals=[]
    )
    print(f"   Compliant: {result['compliant']}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
