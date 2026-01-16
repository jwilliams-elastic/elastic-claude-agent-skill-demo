"""
End-to-end tests for Insurance scenario: Storm Claim Adjudication

Tests the complete workflow:
1. Semantic search for storm claim skill
2. Retrieve skill by ID
3. Execute skill logic with test inputs
4. Validate results against expected outcomes
"""

import pytest


def test_storm_claim_approved_with_waiver(search_skills, get_skill_by_id, execute_skill_logic):
    """
    Test storm claim adjudication with approved claim and deductible waiver.

    Scenario: Category 4 hurricane with recent retrofit (2021)
    Expected: Claim approved, deductible waived, coverage eligible
    """
    # Step 1: Search for storm claim skill
    search_results = search_skills(
        "storm damage claim adjudication hurricane",
        domain="insurance",
        limit=5
    )

    # Verify search returned results
    assert len(search_results) > 0, "Search should return at least one result"

    # Verify adjudicate-storm-claim skill is in results
    skill_ids = [r['source'].get('skill_id') for r in search_results]
    assert 'adjudicate-storm-claim' in skill_ids, \
        f"Expected 'adjudicate-storm-claim' in results, got: {skill_ids}"

    # Step 2: Retrieve full skill content by ID
    skill = get_skill_by_id('adjudicate-storm-claim')

    # Verify skill metadata
    assert skill['skill_id'] == 'adjudicate-storm-claim'
    assert skill['domain'] == 'insurance'
    assert 'skill_markdown' in skill, "Skill should contain skill_markdown field"

    # Step 3: Execute skill with test input (approval expected)
    test_input = {
        "storm_category": 4,
        "roof_material": "wood_shake",
        "region": "coastal",
        "retrofit_year": 2021,
        "claim_amount": 45000,
        "deductible": 2500
    }

    result = execute_skill_logic(skill, test_input)

    # Step 4: Validate results
    assert result is not None, "Skill should return a result"

    # Verify claim status is APPROVED
    assert result.get('claim_status') == 'APPROVED', \
        f"Expected claim_status 'APPROVED', got: {result.get('claim_status')}"

    # Verify deductible is waived (adjusted_deductible should be 0)
    assert result.get('adjusted_deductible') == 0, \
        f"Expected deductible waiver (0), got: {result.get('adjusted_deductible')}"

    # Verify coverage eligibility (retrofit_year > 2020)
    assert result.get('coverage_eligible') is True, \
        f"Expected coverage_eligible True for retrofit_year 2021, got: {result.get('coverage_eligible')}"

    # Verify reasoning is provided
    assert 'reasoning' in result or 'explanation' in result or 'details' in result, \
        "Result should contain reasoning or explanation"


def test_storm_claim_denied_old_retrofit(get_skill_by_id, execute_skill_logic):
    """
    Test storm claim adjudication with denied claim due to old retrofit.

    Scenario: Storm claim with retrofit year 2019 (before cutoff)
    Expected: Coverage denied or claim rejected
    """
    # Step 1: Retrieve skill by ID
    skill = get_skill_by_id('adjudicate-storm-claim')

    # Verify skill retrieved
    assert skill['skill_id'] == 'adjudicate-storm-claim'

    # Step 2: Execute skill with old retrofit year
    test_input = {
        "storm_category": 4,
        "roof_material": "wood_shake",
        "region": "coastal",
        "retrofit_year": 2019,
        "claim_amount": 45000,
        "deductible": 2500
    }

    result = execute_skill_logic(skill, test_input)

    # Step 3: Validate results
    assert result is not None, "Skill should return a result"

    # Verify coverage is denied for old retrofit
    # Could be coverage_eligible=False OR claim_status contains DENIED/REJECTED
    coverage_denied = (
        result.get('coverage_eligible') is False or
        'DENIED' in str(result.get('claim_status', '')).upper() or
        'REJECTED' in str(result.get('claim_status', '')).upper() or
        result.get('approved') is False
    )

    assert coverage_denied, \
        f"Expected coverage denial for retrofit_year 2019, got: {result}"


def test_storm_claim_search_relevance(search_skills):
    """
    Test that semantic search returns relevant storm claim skill.

    Validates that semantic_content field enables accurate skill discovery.
    """
    # Test various storm/insurance-related queries
    queries = [
        "storm damage claim adjudication hurricane",
        "hurricane insurance coverage",
        "catastrophic weather claim processing"
    ]

    for query in queries:
        results = search_skills(query, domain="insurance", limit=3)

        # Verify results returned
        assert len(results) > 0, f"Query '{query}' should return results"

        # At least one insurance-related skill should be returned
        insurance_skills = [
            r for r in results
            if r['source'].get('domain') == 'insurance'
        ]
        assert len(insurance_skills) > 0, \
            f"Query '{query}' should return insurance skills"


def test_storm_claim_edge_cases(get_skill_by_id, execute_skill_logic):
    """
    Test storm claim with edge cases and boundary conditions.
    """
    skill = get_skill_by_id('adjudicate-storm-claim')

    # Edge case 1: Minimal storm category (Category 1)
    result = execute_skill_logic(skill, {
        "storm_category": 1,
        "roof_material": "metal",
        "region": "inland",
        "retrofit_year": 2022,
        "claim_amount": 5000,
        "deductible": 1000
    })
    assert result is not None, "Skill should handle Category 1 storm"

    # Edge case 2: Maximum storm category (Category 5)
    result = execute_skill_logic(skill, {
        "storm_category": 5,
        "roof_material": "wood_shake",
        "region": "coastal",
        "retrofit_year": 2023,
        "claim_amount": 100000,
        "deductible": 5000
    })
    assert result is not None, "Skill should handle Category 5 storm"

    # Edge case 3: Boundary year (retrofit_year = 2020, at cutoff)
    result = execute_skill_logic(skill, {
        "storm_category": 3,
        "roof_material": "asphalt",
        "region": "coastal",
        "retrofit_year": 2020,
        "claim_amount": 30000,
        "deductible": 2000
    })
    assert result is not None, "Skill should handle boundary retrofit_year 2020"


def test_storm_claim_different_materials(get_skill_by_id, execute_skill_logic):
    """
    Test storm claim with different roof materials.

    Verifies that skill handles various roof material types.
    """
    skill = get_skill_by_id('adjudicate-storm-claim')

    roof_materials = ["wood_shake", "metal", "asphalt", "tile"]

    for material in roof_materials:
        result = execute_skill_logic(skill, {
            "storm_category": 3,
            "roof_material": material,
            "region": "coastal",
            "retrofit_year": 2022,
            "claim_amount": 25000,
            "deductible": 2000
        })

        assert result is not None, \
            f"Skill should handle roof material: {material}"
        assert 'claim_status' in result or 'approved' in result, \
            f"Result should contain claim decision for material: {material}"
