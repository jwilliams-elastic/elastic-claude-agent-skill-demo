# Testing Guide

This document provides comprehensive guidance on the end-to-end testing framework for the Elastic Agent Skills Demo.

## Table of Contents

- [Overview](#overview)
- [Test Architecture](#test-architecture)
- [Running Tests](#running-tests)
- [Test Scenarios](#test-scenarios)
- [Adding New Tests](#adding-new-tests)
- [Troubleshooting](#troubleshooting)
- [Best Practices](#best-practices)

## Overview

The testing framework validates the complete workflow of semantic search, skill retrieval, and execution against a live Elasticsearch serverless instance. Tests are written using pytest and cover three domain-specific scenarios:

1. **Finance**: Expense policy verification
2. **Insurance**: Storm claim adjudication
3. **Life Sciences**: Sample viability validation

### Testing Approach

Tests validate two key aspects:

1. **Semantic Search**: Ensures the `semantic_text` field with Jina embeddings returns relevant skills
2. **Scenario Execution**: Validates end-to-end workflow from search to execution

## Test Architecture

```
tests/
├── __init__.py                    # Package initialization
├── conftest.py                    # Pytest fixtures and configuration
├── helpers.py                     # Utility functions
├── test_expense_policy.py         # Finance scenario tests
├── test_storm_claim.py            # Insurance scenario tests
└── test_sample_viability.py       # Life Sciences scenario tests

scripts/
├── search_test.py                 # Semantic search testing script
└── run_e2e_tests.py              # Test execution and reporting script
```

### Key Components

#### conftest.py - Pytest Fixtures

Session-scoped and function-scoped fixtures for test infrastructure:

- `es_credentials`: Loads credentials from .env file
- `es_client`: Creates Elasticsearch client (session-scoped for performance)
- `index_name`: Returns the index name "agent_skills"
- `search_skills`: Factory fixture for semantic search
- `get_skill_by_id`: Factory fixture for skill retrieval
- `execute_skill_logic`: Factory fixture for skill execution
- `format_test_results`: Factory fixture for result formatting

#### helpers.py - Utility Functions

Standalone helper functions that can be used independently of pytest:

- `search_skills()`: Execute semantic search queries
- `get_skill_by_id()`: Retrieve skill documents by ID
- `execute_skill_logic()`: Parse and execute skill Python code
- `format_test_results()`: Format results for reporting
- `validate_skill_structure()`: Validate skill document structure
- `extract_violations()`: Extract normalized violations from results
- `is_approval_status()`: Determine approval/acceptance status

## Running Tests

### Prerequisites

1. Elasticsearch serverless instance running and accessible
2. `.env` file with valid credentials:
   ```
   ELASTIC_SEARCH_URL=https://your-deployment.es.region.cloud.es.io
   ELASTIC_API_KEY=your_api_key_here
   ```
3. Skills ingested into the `agent_skills` index

### Search Testing

Test semantic search functionality without running full test suite:

```bash
# Basic search
uv run scripts/search_test.py --query "expense policy"

# With domain filter
uv run scripts/search_test.py --query "storm claim" --domain insurance

# Limit results
uv run scripts/search_test.py --query "sample viability" --limit 3

# Test multiple domains
uv run scripts/search_test.py --query "compliance" --domain finance
uv run scripts/search_test.py --query "compliance" --domain insurance
uv run scripts/search_test.py --query "compliance" --domain life_sciences
```

### Full Test Suite

Run all end-to-end tests and generate markdown report:

```bash
# Standard execution
uv run scripts/run_e2e_tests.py

# Verbose output
uv run scripts/run_e2e_tests.py --verbose

# Custom output path
uv run scripts/run_e2e_tests.py --output custom-results.md
```

### Individual Test Files

Run specific test scenarios using pytest:

```bash
# Finance scenario only
uv run pytest tests/test_expense_policy.py -v

# Insurance scenario only
uv run pytest tests/test_storm_claim.py -v

# Life Sciences scenario only
uv run pytest tests/test_sample_viability.py -v

# Run all tests with pytest
uv run pytest tests/ -v

# Run with specific markers or keywords
uv run pytest tests/ -k "search_relevance" -v
```

### Test Collection

Verify test discovery without running tests:

```bash
uv run pytest --collect-only tests/
```

## Test Scenarios

### Finance Scenario: Expense Policy Verification

**File:** `tests/test_expense_policy.py`

**Tests:**

1. `test_expense_policy_violations()`:
   - Searches for "expense policy approval rules" with domain filter "finance"
   - Verifies "verify-expense-policy" skill is returned
   - Executes skill with violating input (Team_Dinner $850, no VP approval)
   - Asserts violations: VP_APPROVAL_REQUIRED, CATEGORY_LIMIT_EXCEEDED
   - Confirms approval is denied

2. `test_expense_policy_valid()`:
   - Executes skill with compliant input (Office_Supplies $45)
   - Asserts approval is granted
   - Verifies no critical violations

3. `test_expense_policy_search_relevance()`:
   - Tests multiple expense-related queries
   - Validates semantic search returns finance skills

4. `test_expense_policy_edge_cases()`:
   - Tests zero amount, high amount with VP approval
   - Validates boundary conditions

**Example Input:**
```python
{
    "amount": 850,
    "category": "Team_Dinner",
    "attendees": 10,
    "has_vp_approval": False
}
```

**Expected Violations:**
- VP_APPROVAL_REQUIRED (amount > $500)
- CATEGORY_LIMIT_EXCEEDED ($75/head limit for Team_Dinner)

### Insurance Scenario: Storm Claim Adjudication

**File:** `tests/test_storm_claim.py`

**Tests:**

1. `test_storm_claim_approved_with_waiver()`:
   - Searches for "storm damage claim adjudication hurricane"
   - Verifies "adjudicate-storm-claim" skill is returned
   - Executes skill with Category 4 storm, recent retrofit (2021)
   - Asserts claim approved, deductible waived, coverage eligible

2. `test_storm_claim_denied_old_retrofit()`:
   - Executes skill with retrofit_year 2019 (before 2020 cutoff)
   - Asserts coverage is denied

3. `test_storm_claim_search_relevance()`:
   - Tests storm/insurance queries
   - Validates semantic search accuracy

4. `test_storm_claim_edge_cases()`:
   - Tests Category 1, Category 5 storms
   - Tests boundary year (2020)

5. `test_storm_claim_different_materials()`:
   - Tests various roof materials (wood_shake, metal, asphalt, tile)

**Example Input:**
```python
{
    "storm_category": 4,
    "roof_material": "wood_shake",
    "region": "coastal",
    "retrofit_year": 2021,
    "claim_amount": 45000,
    "deductible": 2500
}
```

**Expected Outcome:**
- Claim status: APPROVED
- Deductible: Waived (adjusted_deductible: 0)
- Coverage: Eligible (retrofit_year > 2020)

### Life Sciences Scenario: Sample Viability Validation

**File:** `tests/test_sample_viability.py`

**Tests:**

1. `test_sample_rejected_time_violation()`:
   - Searches for "plasma sample viability validation"
   - Verifies "validate-sample-viability" skill is returned
   - Executes skill with 5-hour collection time (exceeds 4-hour limit)
   - Asserts status REJECTED, PROCESSING_TIME_EXCEEDED violation

2. `test_sample_approved_valid_params()`:
   - Executes skill with valid parameters (3 hours, turbidity 0.5)
   - Asserts sample is viable
   - Verifies no critical violations

3. `test_sample_viability_search_relevance()`:
   - Tests life sciences queries
   - Validates semantic search accuracy

4. `test_sample_viability_edge_cases()`:
   - Tests boundary time (4 hours), minimum volume, high turbidity

5. `test_sample_viability_different_types()`:
   - Tests Plasma-EDTA, Serum, Whole-Blood, Buffy-Coat

6. `test_sample_viability_temperature_variations()`:
   - Tests different storage temperatures (-75°C, -20°C)

**Example Input:**
```python
{
    "sample_type": "Plasma-EDTA",
    "collection_time_hours_ago": 5,
    "turbidity_index": 0.9,
    "storage_temp_celsius": -75,
    "volume_ml": 3.2
}
```

**Expected Outcome:**
- Status: REJECTED
- Violations: PROCESSING_TIME_EXCEEDED (5 hours > 4 hour limit)
- Warnings: TURBIDITY_THRESHOLD_EXCEEDED (0.9 > 0.8)
- Recommendation: "DO NOT process this sample"

## Adding New Tests

### 1. Create Test File

Create a new test file in the `tests/` directory:

```python
# tests/test_new_scenario.py

def test_new_scenario_basic(search_skills, get_skill_by_id, execute_skill_logic):
    """Test basic scenario workflow."""

    # Step 1: Search for skill
    results = search_skills("your query", domain="your_domain")
    assert len(results) > 0

    # Step 2: Verify skill in results
    skill_ids = [r['source'].get('skill_id') for r in results]
    assert 'your-skill-id' in skill_ids

    # Step 3: Retrieve skill
    skill = get_skill_by_id('your-skill-id')
    assert skill['skill_id'] == 'your-skill-id'

    # Step 4: Execute skill
    result = execute_skill_logic(skill, {"param": "value"})

    # Step 5: Validate outcome
    assert result.get('status') == 'EXPECTED_STATUS'
```

### 2. Use Fixtures

Leverage pytest fixtures from `conftest.py`:

- `search_skills(query, domain, limit)`: Search for skills
- `get_skill_by_id(skill_id)`: Retrieve by ID
- `execute_skill_logic(skill, params)`: Execute skill code

### 3. Test Structure

Follow this pattern for scenario tests:

1. **Search**: Find skill using semantic search
2. **Verify**: Confirm skill is in results
3. **Retrieve**: Get full skill content
4. **Execute**: Run skill with test input
5. **Validate**: Assert expected outcomes

### 4. Assertions

Be specific with assertions:

```python
# Good: Specific assertion with helpful message
assert result.get('approved') is True, \
    f"Expected approval, got: {result}"

# Good: Check multiple outcomes
assert 'violations' in result
assert len(result['violations']) == 2

# Bad: Vague assertion
assert result
```

## Troubleshooting

### Connection Errors

**Error:** "Failed to connect to Elasticsearch"

**Solutions:**
1. Verify ELASTIC_SEARCH_URL is correct in .env
2. Check ELASTIC_API_KEY is valid
3. Test connection: `curl -H "Authorization: ApiKey $ELASTIC_API_KEY" $ELASTIC_SEARCH_URL`
4. Verify network connectivity

### Missing Credentials

**Error:** "ELASTIC_SEARCH_URL not found in .env file"

**Solutions:**
1. Create .env file in project root
2. Add required variables:
   ```
   ELASTIC_SEARCH_URL=https://your-deployment.es.region.cloud.es.io
   ELASTIC_API_KEY=your_api_key_here
   ```

### Skills Not Found

**Error:** "Skill not found: skill-id"

**Solutions:**
1. Verify skills are ingested: `uv run scripts/ingest_skills.py`
2. Check index exists and contains documents
3. Verify skill_id matches exactly (case-sensitive)

### Test Execution Failures

**Error:** Tests fail with assertion errors

**Solutions:**
1. Check skill output format matches test expectations
2. Verify skill Python code is correct
3. Review test input parameters
4. Check for changes in skill business logic

### Import Errors

**Error:** "ModuleNotFoundError: No module named 'pytest'"

**Solutions:**
1. Install dependencies: `uv sync`
2. Verify pytest is in pyproject.toml dependencies
3. Use `uv run` prefix for commands

## Best Practices

### Test Independence

- Tests should not depend on execution order
- Use fixtures for setup/teardown
- Don't share state between tests

### Clear Test Names

```python
# Good: Descriptive test name
def test_expense_policy_violations_with_high_amount():
    ...

# Bad: Vague test name
def test_expense_1():
    ...
```

### Helpful Assertions

Include context in assertion messages:

```python
assert result.get('status') == 'APPROVED', \
    f"Expected APPROVED status, got: {result.get('status')}"
```

### Test Documentation

Add docstrings to test functions:

```python
def test_scenario():
    """
    Test scenario description.

    Expected: What should happen
    """
    ...
```

### Edge Case Coverage

Test boundary conditions:

- Minimum/maximum values
- Null/empty inputs
- Boundary timestamps
- Special characters

### Performance Considerations

- Use session-scoped fixtures for expensive operations (ES client)
- Limit test data size
- Set reasonable timeouts

### Isolation

- Don't modify production data
- Use test-specific index if needed
- Clean up test artifacts

## Test Report

The test execution script generates a comprehensive markdown report:

```bash
uv run scripts/run_e2e_tests.py
```

**Report Sections:**

1. **Executive Summary**: Total tests, pass rate, duration
2. **Test Results by Scenario**: Finance, Insurance, Life Sciences
3. **Failed Tests Details**: Error messages and stack traces (if any)
4. **Search Performance Metrics**: Response times
5. **Environment Details**: Python version, platform, timestamp
6. **Assertions Verified**: Summary of validations

**Example Report:**

```markdown
# End-to-End Test Results

**Generated:** 2026-01-14 15:30:00
**Environment:** Python 3.10.12
**Platform:** darwin

## Executive Summary

- **Total Tests:** 13
- **Passed:** 13 ✅
- **Failed:** 0
- **Pass Rate:** 100.0%
- **Duration:** 4.52s

**Status:** ✅ All tests passed!
```

## Integration with CI/CD

The test framework can be integrated into CI/CD pipelines:

```yaml
# .github/workflows/e2e-tests.yml
name: E2E Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh

      - name: Install dependencies
        run: uv sync

      - name: Run E2E tests
        env:
          ELASTIC_SEARCH_URL: ${{ secrets.ELASTIC_SEARCH_URL }}
          ELASTIC_API_KEY: ${{ secrets.ELASTIC_API_KEY }}
        run: uv run scripts/run_e2e_tests.py

      - name: Upload test results
        uses: actions/upload-artifact@v3
        with:
          name: test-results
          path: e2e-test-results.md
```

## Summary

The testing framework provides comprehensive validation of:

- Semantic search accuracy with `semantic_text` field
- Domain filtering and query relevance
- Skill retrieval and execution
- Business logic and proprietary rules
- Edge cases and error handling

For questions or issues, refer to the main [README.md](README.md) or see [MIGRATION.md](MIGRATION.md) for details on the semantic_text migration.
