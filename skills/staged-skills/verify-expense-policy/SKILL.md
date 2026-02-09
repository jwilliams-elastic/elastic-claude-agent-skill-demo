# Skill: Verify Expense Policy Compliance

## Domain
finance

## Description
Validates expense requests against company policy rules including amount thresholds, category-specific limits, and required approvals.

## Business Rules
This skill enforces proprietary expense policies that require specific knowledge of internal business rules:

1. **Amount Threshold Rule**: Any expense over threshold requires VP_APPROVAL
2. **Team Dinner Cap**: Expenses categorized as "Team_Dinner" are capped per head
3. **Software Procurement**: Expenses in the "Software" category require a pre-existing Procurement_Ticket_ID

**IMPORTANT**: Actual threshold values and limits are defined in CSV configuration files. Do NOT use hardcoded values from this documentation.

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

## Execution
**ALWAYS delegate to `policy_check.py`** - do not implement logic inline.

The `verify_expense()` function in `policy_check.py` handles all validation logic and reads current thresholds from CSV files.

## Configuration Files (Source of Truth)
- `category_limits.csv` - Category-specific spending limits
- `approval_thresholds.csv` - Amount thresholds requiring approvals
- `special_rules.csv` - Category-specific special requirements
- `metadata.csv` - Skill metadata
- `parameters.csv` - General parameters

## Tags
finance, compliance, expense-management, policy-enforcement
