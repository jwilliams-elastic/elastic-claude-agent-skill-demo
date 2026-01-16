# Project: Elastic Agent Skills Repository

## Context

This PRD documents the complete development of a demo showcasing Elasticsearch as a backend for Claude agent skills. The project was built in two major phases:

1. **Initial Build**: Python scripts, JSON configurations, and sample skills with proprietary business logic
2. **E2E Testing & Semantic Search Migration**: Migration from dense_vector embeddings to semantic_text with automatic inference, plus comprehensive end-to-end testing framework

## Architecture

* **Language:** Python 3.10+
* **Package Manager:** `uv` (modern Python package installer)
* **Search:** Elasticsearch Serverless (semantic_text with Jina embeddings)
* **Testing Framework:** pytest
* **Configuration:** `.env` file with `ELASTIC_SEARCH_URL` and `ELASTIC_API_KEY`
* **Structure:**
    * `/config`: JSON mappings and settings with semantic_text
    * `/scripts`: Ingestion, validation, and functional search tests
    * `/tests`: End-to-end test suite for all demo scenarios
    * `/sample_skills`: Domain-specific skills with proprietary business logic
    * `/mcp`: Tool definitions for Agent Builder

---

## Phase 1: Infrastructure & Configuration

**Goal:** Initialize the project using `uv` and create schemas.

- [x] **Task 1.1: Project Scaffold (uv)**
    - Initialize a new python project using `uv init`
    - Add dependencies using `uv add elasticsearch python-dotenv`
    - Create directories: `config`, `scripts`, `sample_skills`, `mcp`
    - **Validation:** Verify `pyproject.toml` exists and contains dependencies

- [x] **Task 1.2: Index Mappings**
    - Create `config/index_mappings.json` with semantic_text field for semantic_content
    - Add copy_to directives on: skill_id, name, description, short_description, domain, tags, author
    - Set inference_id to `.jina-embeddings-v3`
    - Create `config/index_settings.json`
    - **Validation:** Verify files contain valid JSON using `python -m json.tool`

- [x] **Task 1.3: MCP Tool Definitions**
    - Create `mcp/tools.json` containing tool definitions (search_skills, get_skill_by_id, etc.)
    - **Validation:** Verify file contains valid JSON

## Phase 2: Core Logic (Python)

**Goal:** Implement the ingestion and search scripts.

- [x] **Task 2.1: Ingestion Script**
    - Create `scripts/ingest_skills.py` with automatic semantic_text inference
    - Remove all embedding generation logic (relies on Elasticsearch inference)
    - Parse SKILL.md files and extract metadata
    - Ensure it reads from `ELASTIC_SEARCH_URL` and `ELASTIC_API_KEY` env vars
    - **Validation:** Run `uv run scripts/ingest_skills.py` and verify documents are indexed

- [x] **Task 2.2: Functional Search Script**
    - Create `scripts/search_test.py` that connects to Elasticsearch
    - Implement semantic search using `match` query on `semantic_content` field
    - Support command-line args: --query, --domain, --limit
    - Add domain filtering using `term` query
    - Print formatted results with skill_id, name, domain, description, relevance score
    - **Validation:** Run searches for each domain and verify results are relevant

## Phase 3: Sample Data Generation (Business Rules)

**Goal:** Populate the repository with 3 domain-specific skills with proprietary logic that an LLM cannot guess without context.

- [x] **Task 3.1: Finance Skill (Proprietary Expense Policy)**
    - Create `sample_skills/verify-expense-policy`
    - **Business Rules:**
        - Expenses > $500 require VP_APPROVAL
        - "Team_Dinner" category capped at $75/head
        - "Software" category requires pre-existing Procurement_Ticket_ID
    - **Files:** `SKILL.md`, `policy_check.py`, `allowance_table.json`
    - **Validation:** Verify policy_check.py implements all rules correctly

- [x] **Task 3.2: Insurance Skill (Claim Adjudication)**
    - Create `sample_skills/adjudicate-storm-claim`
    - **Business Rules:**
        - Storm category 3+ waives deductible
        - Wood shake roofs in coastal regions denied unless retrofit_year > 2020
        - Material/region risk matrix applies coverage multipliers
    - **Files:** `SKILL.md`, `adjudicator.py`, `risk_matrix.csv`
    - **Validation:** Verify adjudicator.py implements all rules correctly

- [x] **Task 3.3: Life Sciences Skill (Lab Sample Accessioning)**
    - Create `sample_skills/validate-sample-viability`
    - **Business Rules:**
        - Plasma-EDTA samples must be processed within 4 hours
        - Turbidity_index > 0.8 requires ultracentrifugation
        - Storage_temp must be between -80°C and -70°C (strict)
        - Minimum volume requirements per sample type
    - **Files:** `SKILL.md`, `viability_check.py`, `biomarker_constraints.json`
    - **Validation:** Verify viability_check.py implements all rules correctly

## Phase 4: Initial Documentation

**Goal:** Create instructions for the human operator.

- [x] **Task 4.1: README Generation**
    - Create `README.md` summarizing how to use these artifacts
    - Mention use of `uv sync` and `uv run`
    - Include implementation plan steps
    - **Validation:** Check file existence and completeness

- [x] **Task 4.2: Demo Script**
    - Create `DEMO_SCRIPT.md` with hot-loading skill execution flow
    - Include all three domain scenarios with complete dialogues
    - **Validation:** Check file existence

## Phase 5: End-to-End Test Suite

**Goal:** Create runtime tests for all three demo scenarios with semantic search validation.

- [x] **Task 5.1: Test Infrastructure**
    - Add `pytest` and `pytest-json-report` to project dependencies
    - Create `tests/` directory structure
    - Create `tests/conftest.py` with fixtures for:
        - Elasticsearch client initialization
        - Skill search and retrieval helpers
        - Skill execution helpers with module import support
    - Create `tests/__init__.py` and `tests/helpers.py`
    - **Validation:** Run `uv run pytest --collect-only` to verify test discovery

- [x] **Task 5.2: Finance Scenario Tests**
    - Create `tests/test_expense_policy.py`
    - Test cases:
        - `test_expense_policy_violations()`: Verify VP approval and category limit violations
        - `test_expense_policy_valid()`: Verify compliant expenses are approved
        - `test_expense_policy_search_relevance()`: Verify semantic search finds correct skill
        - `test_expense_policy_edge_cases()`: Test boundary conditions
    - **Validation:** Run `uv run pytest tests/test_expense_policy.py -v` - all tests pass

- [x] **Task 5.3: Insurance Scenario Tests**
    - Create `tests/test_storm_claim.py`
    - Test cases:
        - `test_storm_claim_approved_with_waiver()`: Verify deductible waiver for Category 4 storm
        - `test_storm_claim_denied_old_retrofit()`: Verify denial for old retrofit
        - `test_storm_claim_search_relevance()`: Verify semantic search finds correct skill
        - `test_storm_claim_edge_cases()`: Test various storm categories and materials
        - `test_storm_claim_different_materials()`: Test different roof material types
    - **Validation:** Run `uv run pytest tests/test_storm_claim.py -v` - all tests pass

- [x] **Task 5.4: Life Sciences Scenario Tests**
    - Create `tests/test_sample_viability.py`
    - Test cases:
        - `test_sample_rejected_time_violation()`: Verify rejection for 5-hour processing time
        - `test_sample_approved_valid_params()`: Verify viable samples are approved
        - `test_sample_viability_search_relevance()`: Verify semantic search finds correct skill
        - `test_sample_viability_edge_cases()`: Test edge cases for all rules
        - `test_sample_viability_different_types()`: Test different sample types
        - `test_sample_viability_temperature_variations()`: Test temperature boundaries
    - **Validation:** Run `uv run pytest tests/test_sample_viability.py -v` - all tests pass

## Phase 6: Test Execution & Reporting

**Goal:** Run all tests and generate comprehensive test results report.

- [x] **Task 6.1: Test Execution Script**
    - Create `scripts/run_e2e_tests.py` that:
        - Runs pytest with verbose output and JSON report
        - Captures test results, timing, and failures
        - Formats results for markdown output
    - Add command-line options: --verbose, --output
    - **Validation:** Run script and verify it executes all tests

- [x] **Task 6.2: Test Results Report**
    - Generate `e2e-test-results.md` with:
        - Test execution summary (total tests, passed, failed, duration)
        - Results for each scenario (Finance, Insurance, Life Sciences)
        - For each test: status, duration, assertions verified
        - Search query performance metrics
        - Environment details
    - Format with clear sections and markdown tables
    - Include pass/fail indicators (✅/❌)
    - **Validation:** Review generated report - all 15 tests passing

## Phase 7: Documentation

**Goal:** Document the testing framework and usage instructions.

- [x] **Task 7.1: Update README**
    - Add "End-to-End Testing" section
    - Document search test usage: `uv run scripts/search_test.py --query "expense policy"`
    - Document e2e test usage: `uv run scripts/run_e2e_tests.py`
    - Document specific test execution: `uv run pytest tests/test_expense_policy.py`
    - Include example output from test runs
    - **Validation:** Verify commands work as documented

- [x] **Task 7.2: Testing Guide**
    - Create `TESTING.md` with comprehensive guide:
        - Overview of testing approach (semantic search + scenario tests)
        - Test architecture
        - How to add new test scenarios
        - Troubleshooting common issues
        - Best practices for writing skill tests
    - **Validation:** Review guide for completeness

## Success Criteria

- ✅ All code uses semantic_text with automatic Jina embeddings inference
- ✅ Ingestion script successfully indexes skills without manual embedding generation
- ✅ Search test script can query Elasticsearch and return relevant results with domain filtering
- ✅ All three scenario tests (expense policy, storm claim, sample viability) pass
- ✅ 15/15 tests passing with 100% pass rate
- ✅ Test results report generated with detailed metrics
- ✅ Documentation updated with comprehensive testing instructions
- ✅ No breaking changes to existing skill functionality

## Completion Rules

1. Do NOT mark a task as done until:
    - The code is written and passes syntax checks
    - Tests are run and pass successfully
    - Generated files are validated
2. All tests must run against a live Elasticsearch serverless instance (not mocks)
3. Use `uv run` for all Python execution
4. The final `e2e-test-results.md` must be generated and show all tests passing
5. All three demo scenarios (Finance, Insurance, Life Sciences) must have passing tests

## Dependencies

- Elasticsearch serverless instance must be running and accessible
- `.env` file must contain valid `ELASTIC_SEARCH_URL` and `ELASTIC_API_KEY`
- Skills must be ingested before running e2e tests
- Python packages: `elasticsearch`, `python-dotenv`, `pytest`, `pytest-json-report`

## Key Technical Decisions

### Semantic Text Migration
- **From:** Manual dense_vector embedding generation (1536-dimensional mock vectors)
- **To:** Automatic semantic_text field with `.jina-embeddings-v3` inference
- **Benefits:** Simplified ingestion, no embedding generation code, automatic inference by Elasticsearch
- **Implementation:** copy_to directives from multiple fields into semantic_content field

### Test Execution Strategy
- Tests execute actual skill Python code by adding skill directories to sys.path
- SKILL.md files include "Test Execution" sections with adapter code to transform inputs/outputs
- Tests validate both semantic search accuracy and business logic correctness
- All tests run against live Elasticsearch instance (no mocking)

### Domain-Specific Business Rules
Each skill implements proprietary logic that cannot be guessed:
- **Finance:** Complex approval thresholds, per-head limits, procurement requirements
- **Insurance:** Storm category logic, material/region risk matrices, retrofit requirements
- **Life Sciences:** Time-sensitive processing rules, turbidity thresholds, strict temperature ranges
