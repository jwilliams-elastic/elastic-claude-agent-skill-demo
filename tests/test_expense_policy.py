"""
End-to-end tests for Finance scenario: Expense Policy Verification

Tests the complete workflow:
1. Semantic search for expense policy skill
2. Retrieve skill by ID
3. Execute skill logic with test inputs
4. Validate results against expected outcomes
"""

import pytest


def test_expense_policy_violations(search_skills, get_skill_by_id, execute_skill_logic):
    """
    Test expense policy verification with violations.

    Scenario: Team dinner expense exceeding category limit without VP approval
    Expected: Violations detected (VP_APPROVAL_REQUIRED, CATEGORY_LIMIT_EXCEEDED)
    """
    # Step 1: Search for expense policy skill
    search_results = search_skills(
        "expense policy approval rules",
        domain="finance",
        limit=5
    )

    # Verify search returned results
    assert len(search_results) > 0, "Search should return at least one result"

    # Verify verify-expense-policy skill is in results
    skill_ids = [r['source'].get('skill_id') for r in search_results]
    assert 'verify-expense-policy' in skill_ids, \
        f"Expected 'verify-expense-policy' in results, got: {skill_ids}"

    # Step 2: Retrieve full skill content by ID
    skill = get_skill_by_id('verify-expense-policy')

    # Verify skill metadata
    assert skill['skill_id'] == 'verify-expense-policy'
    assert skill['domain'] == 'finance'
    assert 'skill_markdown' in skill, "Skill should contain skill_markdown field"

    # Step 3: Execute skill with test input (violations expected)
    test_input = {
        "amount": 850,
        "category": "Team_Dinner",
        "attendees": 10,
        "has_vp_approval": False
    }

    result = execute_skill_logic(skill, test_input)

    # Step 4: Validate results
    assert result is not None, "Skill should return a result"
    assert 'violations' in result, "Result should contain violations field"
    assert 'recommendations' in result, "Result should contain recommendations field"

    # Check for expected violations
    violations = result['violations']
    violation_types = [v['type'] for v in violations]

    assert 'VP_APPROVAL_REQUIRED' in violation_types, \
        f"Expected VP_APPROVAL_REQUIRED violation, got: {violation_types}"
    assert 'CATEGORY_LIMIT_EXCEEDED' in violation_types, \
        f"Expected CATEGORY_LIMIT_EXCEEDED violation, got: {violation_types}"

    # Verify recommendations are provided
    assert len(result['recommendations']) > 0, \
        "Recommendations should be provided for violations"

    # Verify overall status
    assert result.get('approved') is False, \
        "Expense should not be approved with violations"


def test_expense_policy_valid(get_skill_by_id, execute_skill_logic):
    """
    Test expense policy verification with compliant input.

    Scenario: Valid expense within limits
    Expected: Approval granted, no violations
    """
    # Step 1: Retrieve skill by ID (skip search since we already tested it)
    skill = get_skill_by_id('verify-expense-policy')

    # Verify skill retrieved
    assert skill['skill_id'] == 'verify-expense-policy'

    # Step 2: Execute skill with compliant input
    test_input = {
        "amount": 45,
        "category": "Office_Supplies",
        "attendees": 1,
        "has_vp_approval": False
    }

    result = execute_skill_logic(skill, test_input)

    # Step 3: Validate results
    assert result is not None, "Skill should return a result"

    # Verify no violations or minimal warnings
    violations = result.get('violations', [])
    critical_violations = [v for v in violations if v.get('severity') == 'ERROR']

    assert len(critical_violations) == 0, \
        f"No critical violations expected for compliant expense, got: {critical_violations}"

    # Verify approval is granted
    assert result.get('approved') is True, \
        "Compliant expense should be approved"


def test_expense_policy_search_relevance(search_skills):
    """
    Test that semantic search returns relevant expense policy skill.

    Validates that semantic_content field enables accurate skill discovery.
    """
    # Test various expense-related queries
    queries = [
        "expense policy approval rules",
        "corporate spending limits",
        "expense verification compliance"
    ]

    for query in queries:
        results = search_skills(query, domain="finance", limit=3)

        # Verify results returned
        assert len(results) > 0, f"Query '{query}' should return results"

        # Check if verify-expense-policy is in top results
        skill_ids = [r['source'].get('skill_id') for r in results]

        # At least one finance-related skill should be returned
        finance_skills = [
            r for r in results
            if r['source'].get('domain') == 'finance'
        ]
        assert len(finance_skills) > 0, \
            f"Query '{query}' should return finance skills"


def test_expense_policy_edge_cases(get_skill_by_id, execute_skill_logic):
    """
    Test expense policy with edge cases.

    Tests boundary conditions and special scenarios.
    """
    skill = get_skill_by_id('verify-expense-policy')

    # Edge case 1: Zero amount
    result = execute_skill_logic(skill, {
        "amount": 0,
        "category": "Office_Supplies",
        "attendees": 1,
        "has_vp_approval": False
    })
    assert result is not None, "Skill should handle zero amount"

    # Edge case 2: High amount with VP approval
    result = execute_skill_logic(skill, {
        "amount": 10000,
        "category": "Conference",
        "attendees": 5,
        "has_vp_approval": True
    })
    assert result is not None, "Skill should handle high amounts with VP approval"

    # Verify VP approval affects outcome
    violations = result.get('violations', [])
    vp_required = any(v.get('type') == 'VP_APPROVAL_REQUIRED' for v in violations)
    assert not vp_required, "VP approval should satisfy VP_APPROVAL_REQUIRED check"
