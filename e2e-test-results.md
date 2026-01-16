# End-to-End Test Results

**Generated:** 2026-01-14 15:37:06
**Environment:** Python Unknown
**Platform:** Unknown

## Executive Summary

- **Total Tests:** 15
- **Passed:** 15 ✅
- **Failed:** 0 
- **Skipped:** 0
- **Pass Rate:** 100.0%
- **Duration:** 5.13s

**Status:** ✅ All tests passed!

## Test Results by Scenario

### Finance Scenario

| Test | Status | Duration | Details |
|------|--------|----------|---------|
| `test_expense_policy_violations` | ✅ PASSED | 0.376s |  |
| `test_expense_policy_valid` | ✅ PASSED | 0.083s |  |
| `test_expense_policy_search_relevance` | ✅ PASSED | 0.817s |  |
| `test_expense_policy_edge_cases` | ✅ PASSED | 0.078s |  |

### Insurance Scenario

| Test | Status | Duration | Details |
|------|--------|----------|---------|
| `test_storm_claim_approved_with_waiver` | ✅ PASSED | 0.438s |  |
| `test_storm_claim_denied_old_retrofit` | ✅ PASSED | 0.083s |  |
| `test_storm_claim_search_relevance` | ✅ PASSED | 0.625s |  |
| `test_storm_claim_edge_cases` | ✅ PASSED | 0.074s |  |
| `test_storm_claim_different_materials` | ✅ PASSED | 0.085s |  |

### Life Sciences Scenario

| Test | Status | Duration | Details |
|------|--------|----------|---------|
| `test_sample_rejected_time_violation` | ✅ PASSED | 0.277s |  |
| `test_sample_approved_valid_params` | ✅ PASSED | 0.163s |  |
| `test_sample_viability_search_relevance` | ✅ PASSED | 0.745s |  |
| `test_sample_viability_edge_cases` | ✅ PASSED | 0.082s |  |
| `test_sample_viability_different_types` | ✅ PASSED | 0.217s |  |
| `test_sample_viability_temperature_variations` | ✅ PASSED | 0.081s |  |

## Search Performance Metrics

- **Total Search Tests:** 3
- **Total Search Time:** 2.187s
- **Average Search Time:** 0.729s

## Environment Details

| Property | Value |
|----------|-------|

## Assertions Verified

- Estimated assertions verified: ~45 (avg 3 per test)
- All three demo scenarios tested: Finance, Insurance, Life Sciences
- Semantic search accuracy validated
- Skill retrieval by ID validated
- Skill execution logic validated
- Domain filtering validated
