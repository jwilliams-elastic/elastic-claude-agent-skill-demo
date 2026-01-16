# Skill: Verify Expense Policy Compliance

## Domain
finance

## Description
Validates expense requests against company policy rules including amount thresholds, category-specific limits, and required approvals.

## Business Rules
This skill enforces proprietary expense policies that require specific knowledge of internal business rules:

1. **Amount Threshold Rule**: Any expense over $500 requires VP_APPROVAL
2. **Team Dinner Cap**: Expenses categorized as "Team_Dinner" are capped at $75 per head
3. **Software Procurement**: Expenses in the "Software" category require a pre-existing Procurement_Ticket_ID

## Input Parameters
- `amount` (float): The expense amount in USD
- `category` (string): Expense category (e.g., "Team_Dinner", "Software", "Travel", "Office_Supplies")
- `headcount` (int, optional): Number of people for Team_Dinner expenses
- `procurement_ticket_id` (string, optional): Required for Software category
- `approvals` (list, optional): List of approval types already obtained

## Output
Returns a validation result with:
- `compliant` (bool): Whether the expense meets policy requirements
- `violations` (list): List of policy violations if any
- `required_actions` (list): Actions needed to achieve compliance

## Usage Example
```python
from policy_check import verify_expense

result = verify_expense(
    amount=750.00,
    category="Software",
    procurement_ticket_id="PROC-12345",
    approvals=["MANAGER_APPROVAL"]
)

print(f"Compliant: {result['compliant']}")
print(f"Violations: {result['violations']}")
print(f"Required Actions: {result['required_actions']}")
```

## Tags
finance, compliance, expense-management, policy-enforcement

## Implementation
The actual policy logic is implemented in `policy_check.py` and references allowance data from `allowance_table.json`.

## Test Execution
```python
from policy_check import verify_expense

# Map test input parameters
headcount = input_data.get('attendees') or input_data.get('headcount')
approvals = []
if input_data.get('has_vp_approval'):
    approvals.append('VP_APPROVAL')
if input_data.get('has_manager_approval'):
    approvals.append('MANAGER_APPROVAL')

# Call the skill function
raw_result = verify_expense(
    amount=input_data.get('amount'),
    category=input_data.get('category'),
    headcount=headcount,
    procurement_ticket_id=input_data.get('procurement_ticket_id'),
    approvals=approvals
)

# Transform output to match test expectations
violations_list = []
for violation_str in raw_result.get('violations', []):
    if '$500 threshold' in violation_str or 'over $500' in violation_str:
        violations_list.append({'type': 'VP_APPROVAL_REQUIRED', 'message': violation_str})
    elif 'exceeds' in violation_str and 'head' in violation_str:
        violations_list.append({'type': 'CATEGORY_LIMIT_EXCEEDED', 'message': violation_str})
    elif 'Procurement_Ticket_ID' in violation_str:
        violations_list.append({'type': 'PROCUREMENT_TICKET_REQUIRED', 'message': violation_str})
    else:
        violations_list.append({'type': 'POLICY_VIOLATION', 'message': violation_str})

result = {
    'approved': raw_result.get('compliant', False),
    'violations': violations_list,
    'recommendations': raw_result.get('required_actions', []),
    'amount': raw_result.get('amount'),
    'category': raw_result.get('category')
}
```
