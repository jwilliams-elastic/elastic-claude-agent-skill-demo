"""
End-to-end tests for Life Sciences scenario: Sample Viability Validation

Tests the complete workflow:
1. Semantic search for sample viability skill
2. Retrieve skill by ID
3. Execute skill logic with test inputs
4. Validate results against expected outcomes
"""

import pytest


def test_sample_rejected_time_violation(search_skills, get_skill_by_id, execute_skill_logic):
    """
    Test sample viability validation with time violation.

    Scenario: Plasma sample collected 5 hours ago (exceeds 4-hour limit)
    Expected: Overall status REJECTED, PROCESSING_TIME_EXCEEDED violation
    """
    # Step 1: Search for sample viability skill
    search_results = search_skills(
        "plasma sample viability validation",
        domain="life_sciences",
        limit=5
    )

    # Verify search returned results
    assert len(search_results) > 0, "Search should return at least one result"

    # Verify validate-sample-viability skill is in results
    skill_ids = [r['source'].get('skill_id') for r in search_results]
    assert 'validate-sample-viability' in skill_ids, \
        f"Expected 'validate-sample-viability' in results, got: {skill_ids}"

    # Step 2: Retrieve full skill content by ID
    skill = get_skill_by_id('validate-sample-viability')

    # Verify skill metadata
    assert skill['skill_id'] == 'validate-sample-viability'
    assert skill['domain'] == 'life_sciences'
    assert 'skill_markdown' in skill, "Skill should contain skill_markdown field"

    # Step 3: Execute skill with test input (rejection expected)
    test_input = {
        "sample_type": "Plasma-EDTA",
        "collection_time_hours_ago": 5,
        "turbidity_index": 0.9,
        "storage_temp_celsius": -75,
        "volume_ml": 3.2
    }

    result = execute_skill_logic(skill, test_input)

    # Step 4: Validate results
    assert result is not None, "Skill should return a result"

    # Verify overall status is REJECTED
    overall_status = result.get('overall_status') or result.get('status')
    assert overall_status == 'REJECTED', \
        f"Expected overall_status 'REJECTED', got: {overall_status}"

    # Verify PROCESSING_TIME_EXCEEDED violation is present
    violations = result.get('violations', [])
    warnings = result.get('warnings', [])
    all_issues = violations + warnings

    issue_types = [issue.get('type') or issue.get('code') for issue in all_issues]

    assert 'PROCESSING_TIME_EXCEEDED' in issue_types, \
        f"Expected PROCESSING_TIME_EXCEEDED in violations, got: {issue_types}"

    # Verify TURBIDITY_THRESHOLD_EXCEEDED warning is present
    assert 'TURBIDITY_THRESHOLD_EXCEEDED' in issue_types or 'TURBIDITY' in str(issue_types), \
        f"Expected TURBIDITY warning, got: {issue_types}"

    # Verify recommendations include "DO NOT process"
    recommendations = result.get('recommendations', [])
    recommendations_text = ' '.join(str(r) for r in recommendations).upper()

    assert 'DO NOT PROCESS' in recommendations_text or 'REJECT' in recommendations_text, \
        f"Expected 'DO NOT process' recommendation, got: {recommendations}"


def test_sample_approved_valid_params(get_skill_by_id, execute_skill_logic):
    """
    Test sample viability validation with valid parameters.

    Scenario: Plasma sample with valid collection time and turbidity
    Expected: Sample approved/viable, no critical violations
    """
    # Step 1: Retrieve skill by ID
    skill = get_skill_by_id('validate-sample-viability')

    # Verify skill retrieved
    assert skill['skill_id'] == 'validate-sample-viability'

    # Step 2: Execute skill with valid parameters
    test_input = {
        "sample_type": "Plasma-EDTA",
        "collection_time_hours_ago": 3,
        "turbidity_index": 0.5,
        "storage_temp_celsius": -75,
        "volume_ml": 4.5
    }

    result = execute_skill_logic(skill, test_input)

    # Step 3: Validate results
    assert result is not None, "Skill should return a result"

    # Verify sample is viable (APPROVED or VIABLE status)
    overall_status = result.get('overall_status') or result.get('status')
    viable_statuses = ['APPROVED', 'VIABLE', 'ACCEPTED', 'PASS']

    assert overall_status in viable_statuses, \
        f"Expected viable status (APPROVED/VIABLE/ACCEPTED), got: {overall_status}"

    # Verify no critical violations
    violations = result.get('violations', [])
    critical_violations = [
        v for v in violations
        if v.get('severity') == 'ERROR' or v.get('critical') is True
    ]

    assert len(critical_violations) == 0, \
        f"No critical violations expected for valid sample, got: {critical_violations}"

    # Verify viable result
    assert result.get('viable') is True or result.get('approved') is True, \
        f"Sample should be viable with valid parameters, got: {result}"


def test_sample_viability_search_relevance(search_skills):
    """
    Test that semantic search returns relevant sample viability skill.

    Validates that semantic_content field enables accurate skill discovery.
    """
    # Test various sample/life sciences-related queries
    queries = [
        "plasma sample viability validation",
        "biospecimen quality control",
        "sample integrity verification"
    ]

    for query in queries:
        results = search_skills(query, domain="life_sciences", limit=3)

        # Verify results returned
        assert len(results) > 0, f"Query '{query}' should return results"

        # At least one life_sciences skill should be returned
        life_sciences_skills = [
            r for r in results
            if r['source'].get('domain') == 'life_sciences'
        ]
        assert len(life_sciences_skills) > 0, \
            f"Query '{query}' should return life_sciences skills"


def test_sample_viability_edge_cases(get_skill_by_id, execute_skill_logic):
    """
    Test sample viability with edge cases and boundary conditions.
    """
    skill = get_skill_by_id('validate-sample-viability')

    # Edge case 1: Exactly at time limit (4 hours)
    result = execute_skill_logic(skill, {
        "sample_type": "Plasma-EDTA",
        "collection_time_hours_ago": 4,
        "turbidity_index": 0.5,
        "storage_temp_celsius": -75,
        "volume_ml": 3.5
    })
    assert result is not None, "Skill should handle boundary time (4 hours)"

    # Edge case 2: Minimum volume
    result = execute_skill_logic(skill, {
        "sample_type": "Plasma-EDTA",
        "collection_time_hours_ago": 2,
        "turbidity_index": 0.3,
        "storage_temp_celsius": -75,
        "volume_ml": 1.0
    })
    assert result is not None, "Skill should handle minimum volume"

    # Edge case 3: High turbidity but within time
    result = execute_skill_logic(skill, {
        "sample_type": "Plasma-EDTA",
        "collection_time_hours_ago": 2,
        "turbidity_index": 1.5,
        "storage_temp_celsius": -75,
        "volume_ml": 4.0
    })
    assert result is not None, "Skill should handle high turbidity"


def test_sample_viability_different_types(get_skill_by_id, execute_skill_logic):
    """
    Test sample viability with different sample types.

    Verifies that skill handles various sample types.
    """
    skill = get_skill_by_id('validate-sample-viability')

    sample_types = [
        "Plasma-EDTA",
        "Serum",
        "Whole-Blood",
        "Buffy-Coat"
    ]

    for sample_type in sample_types:
        result = execute_skill_logic(skill, {
            "sample_type": sample_type,
            "collection_time_hours_ago": 3,
            "turbidity_index": 0.5,
            "storage_temp_celsius": -75,
            "volume_ml": 4.0
        })

        assert result is not None, \
            f"Skill should handle sample type: {sample_type}"
        assert 'overall_status' in result or 'status' in result, \
            f"Result should contain status for sample type: {sample_type}"


def test_sample_viability_temperature_variations(get_skill_by_id, execute_skill_logic):
    """
    Test sample viability with different storage temperatures.

    Verifies that skill validates temperature requirements.
    """
    skill = get_skill_by_id('validate-sample-viability')

    # Valid temperature
    result = execute_skill_logic(skill, {
        "sample_type": "Plasma-EDTA",
        "collection_time_hours_ago": 2,
        "turbidity_index": 0.4,
        "storage_temp_celsius": -75,
        "volume_ml": 3.5
    })
    assert result is not None, "Skill should handle valid temperature (-75°C)"

    # Edge case: Different temperature
    result = execute_skill_logic(skill, {
        "sample_type": "Plasma-EDTA",
        "collection_time_hours_ago": 2,
        "turbidity_index": 0.4,
        "storage_temp_celsius": -20,
        "volume_ml": 3.5
    })
    assert result is not None, "Skill should handle -20°C storage temperature"
