# Project: Elastic Agent Builder MCP Tools

## Context

This PRD defines the implementation of Elastic Agent Builder tools using the Model Context Protocol (MCP) interface. The goal is to convert existing MCP tool definitions into Elastic Agent Builder tools powered by ES|QL queries, enabling Claude agents to search and retrieve agent skills directly through Kibana's Agent Builder API.

## Architecture

* **Language:** Python 3.10+
* **Package Manager:** `uv` (modern Python package installer)
* **Query Language:** ES|QL (Elasticsearch Query Language)
* **API Endpoint:** Kibana Agent Builder API (`/api/agent_builder/tools`)
* **Authentication:** API Key (via `Authorization: ApiKey` header)
* **Environment Variables:**
    * `KIBANA_URL` - Base Kibana URL
    * `ELASTIC_MCP_URL` - Full Agent Builder MCP endpoint URL
    * `ELASTIC_API_KEY` - API key for authentication
* **Index:** `agent_skills`

## Tool Definitions

The following tools from `/mcp/tools.json` will be converted to Agent Builder tools with ES|QL queries:

### 1. search_skills
**Purpose:** Semantic search for agent skills using natural language queries

**ES|QL Query Strategy:**
- Use `FROM agent_skills` to query the index
- Filter using semantic text matching on the `semantic_content` field
- Apply optional domain filtering
- Sort by relevance score (descending)
- Limit results based on user preference

**Parameters:**
- `query` (string, required): Search query string
- `limit` (integer, optional, default: 5): Maximum results to return

### 2. get_skill_by_id
**Purpose:** Retrieve a specific skill document by its unique identifier

**ES|QL Query Strategy:**
- Use `FROM agent_skills` to query the index
- Filter with `WHERE skill_id == ?skill_id` for exact match
- Return all fields for the matched document

**Parameters:**
- `skill_id` (string, required): Unique skill identifier

### 3. list_skills_by_domain
**Purpose:** List all skills within a specific domain category

**ES|QL Query Strategy:**
- Use `FROM agent_skills` to query the index
- Filter with `WHERE domain == ?domain` for exact domain match
- Return key fields: skill_id, name, domain, short_description, tags
- Sort by usage_count or rating (if available)

**Parameters:**
- `domain` (string, required): Domain category (finance, insurance, life_sciences)

### 4. get_skill_metadata
**Purpose:** Retrieve metadata for a skill without full content

**ES|QL Query Strategy:**
- Use `FROM agent_skills` to query the index
- Filter with `WHERE skill_id == ?skill_id`
- Use `KEEP` to select only metadata fields: skill_id, name, domain, tags, author, version, usage_count, rating, updated_at
- Exclude large fields like skill_markdown and description

**Parameters:**
- `skill_id` (string, required): Unique skill identifier

### 5. search_skills_by_tags
**Purpose:** Search for skills matching specific tags

**ES|QL Query Strategy:**
- Use `FROM agent_skills` to query the index
- Filter using tag matching logic:
  - If `match_all=true`: Check if all provided tags are present in the tags array
  - If `match_all=false`: Check if any provided tag is present
- Return matching skills with key fields

**Parameters:**
- `tags` (array[string], required): Array of tags to search for
- `match_all` (boolean, optional, default: false): Require all tags vs any tag

---

## Phase 1: ES|QL Query Development

**Goal:** Create and validate ES|QL queries for each tool using ES|QL console in Kibana.

- [ ] **Task 1.1: Create search_skills Query**
    - Write ES|QL query for semantic text search
    - Use MATCH or text search operators on `semantic_content` field
    - Implement dynamic limit parameter: `?limit`
    - Test with sample queries: "expense policy", "storm claim", "sample viability"
    - **Validation:** Query returns relevant results with scores

- [ ] **Task 1.2: Create get_skill_by_id Query**
    - Write ES|QL query with exact skill_id matching
    - Use parameterized query: `WHERE skill_id == ?skill_id`
    - Test with known skill IDs: "verify-expense-policy", "adjudicate-storm-claim"
    - **Validation:** Query returns single matching document

- [ ] **Task 1.3: Create list_skills_by_domain Query**
    - Write ES|QL query for domain filtering
    - Use parameterized query: `WHERE domain == ?domain`
    - Add KEEP clause to select relevant fields
    - Test with domains: "finance", "insurance", "life_sciences"
    - **Validation:** Query returns all skills in specified domain

- [ ] **Task 1.4: Create get_skill_metadata Query**
    - Write ES|QL query with skill_id filter and field selection
    - Use KEEP clause to include only metadata fields
    - Test that skill_markdown and description are excluded
    - **Validation:** Query returns lightweight metadata only

- [ ] **Task 1.5: Create search_skills_by_tags Query**
    - Write ES|QL query for tag matching
    - Implement conditional logic for match_all parameter
    - Test with single tag and multiple tags
    - **Validation:** Query returns skills matching tag criteria

## Phase 2: Agent Builder Tool Registration

**Goal:** Create tool definition JSON payloads and register them via Kibana API.

- [ ] **Task 2.1: Create Tool Definition Templates**
    - Create `agent_builder/tools/` directory
    - For each tool, create JSON file with Agent Builder format:
        - `id`: Tool identifier (e.g., "search_skills")
        - `type`: "esql"
        - `description`: Human-readable description
        - `tags`: ["agent-skills", "mcp"]
        - `configuration.query`: ES|QL query with parameter placeholders
        - `configuration.params`: Parameter definitions with types
    - **Validation:** Verify JSON structure matches Kibana API schema

- [ ] **Task 2.2: Create search_skills Tool Definition**
    - Create `agent_builder/tools/search_skills.json`
    - Map query parameter to ES|QL placeholder: `?query`
    - Map limit parameter to ES|QL placeholder: `?limit`
    - Define parameter types: query (keyword), limit (integer)
    - **Validation:** Validate JSON syntax

- [ ] **Task 2.3: Create get_skill_by_id Tool Definition**
    - Create `agent_builder/tools/get_skill_by_id.json`
    - Map skill_id parameter to ES|QL placeholder: `?skill_id`
    - Define parameter type: skill_id (keyword)
    - **Validation:** Validate JSON syntax

- [ ] **Task 2.4: Create list_skills_by_domain Tool Definition**
    - Create `agent_builder/tools/list_skills_by_domain.json`
    - Map domain parameter to ES|QL placeholder: `?domain`
    - Define parameter type: domain (keyword)
    - **Validation:** Validate JSON syntax

- [ ] **Task 2.5: Create get_skill_metadata Tool Definition**
    - Create `agent_builder/tools/get_skill_metadata.json`
    - Map skill_id parameter to ES|QL placeholder: `?skill_id`
    - Define parameter type: skill_id (keyword)
    - **Validation:** Validate JSON syntax

- [ ] **Task 2.6: Create search_skills_by_tags Tool Definition**
    - Create `agent_builder/tools/search_skills_by_tags.json`
    - Map tags parameter to ES|QL array handling
    - Map match_all parameter to conditional logic
    - Define parameter types: tags (array), match_all (boolean)
    - **Validation:** Validate JSON syntax

## Phase 3: Registration Script Development

**Goal:** Create a Python script to POST tool definitions to Kibana Agent Builder API.

- [ ] **Task 3.1: Create Registration Script**
    - Create `scripts/register_agent_builder_tools.py`
    - Load environment variables: KIBANA_URL, ELASTIC_API_KEY
    - Implement function: `register_tool(tool_definition_path)`
        - Read JSON tool definition from file
        - Construct POST request to `{KIBANA_URL}/api/agent_builder/tools`
        - Set headers:
            - `Authorization: ApiKey {ELASTIC_API_KEY}`
            - `kbn-xsrf: true`
            - `Content-Type: application/json`
        - Send POST request with tool definition as body
        - Handle response (success: 200/201, errors: 400/401/500)
    - **Validation:** Script runs without syntax errors

- [ ] **Task 3.2: Add Batch Registration**
    - Implement function: `register_all_tools()`
    - Scan `agent_builder/tools/` directory for JSON files
    - Register each tool definition
    - Print registration status for each tool
    - Generate summary report: total, successful, failed
    - **Validation:** Script can process multiple tool files

- [ ] **Task 3.3: Add Update/Delete Functions**
    - Implement `update_tool(tool_id, tool_definition_path)` using PUT request
    - Implement `delete_tool(tool_id)` using DELETE request
    - Implement `list_tools()` using GET request
    - Add command-line interface:
        - `--register`: Register all tools
        - `--update <tool_id>`: Update specific tool
        - `--delete <tool_id>`: Delete specific tool
        - `--list`: List all registered tools
    - **Validation:** Script supports CRUD operations

- [ ] **Task 3.4: Add Validation Mode**
    - Implement `--dry-run` flag to validate without registering
    - Validate tool definition JSON schema
    - Check for required fields: id, type, configuration.query
    - Validate ES|QL query syntax (basic checks)
    - Print validation results without API calls
    - **Validation:** Dry-run mode provides helpful feedback

## Phase 4: Tool Testing & Validation

**Goal:** Test each registered tool through the Elastic MCP server.

- [ ] **Task 4.1: Create Test Script**
    - Create `scripts/test_agent_builder_tools.py`
    - Implement function: `test_tool(tool_id, test_params)`
        - Send POST request to `{ELASTIC_MCP_URL}/tools/{tool_id}/execute`
        - Include test parameters in request body
        - Validate response structure
        - Check for errors or empty results
        - Print formatted results
    - **Validation:** Script can invoke tools via MCP endpoint

- [ ] **Task 4.2: Test search_skills Tool**
    - Test case 1: Search for "expense policy" (expect: verify-expense-policy)
    - Test case 2: Search for "storm damage" (expect: adjudicate-storm-claim)
    - Test case 3: Search for "sample viability" (expect: validate-sample-viability)
    - Test case 4: Search with limit=1 (expect: single result)
    - **Validation:** All test cases return expected results

- [ ] **Task 4.3: Test get_skill_by_id Tool**
    - Test case 1: Get "verify-expense-policy" (expect: full document)
    - Test case 2: Get "adjudicate-storm-claim" (expect: full document)
    - Test case 3: Get "nonexistent-skill" (expect: empty/error)
    - **Validation:** Tool returns correct documents or handles missing IDs

- [ ] **Task 4.4: Test list_skills_by_domain Tool**
    - Test case 1: List finance skills (expect: verify-expense-policy)
    - Test case 2: List insurance skills (expect: adjudicate-storm-claim)
    - Test case 3: List life_sciences skills (expect: validate-sample-viability)
    - Test case 4: List nonexistent domain (expect: empty results)
    - **Validation:** Tool returns domain-filtered results

- [ ] **Task 4.5: Test get_skill_metadata Tool**
    - Test case 1: Get metadata for "verify-expense-policy"
    - Verify response includes: skill_id, name, domain, tags, author, version
    - Verify response excludes: skill_markdown, description (full text)
    - Test case 2: Get metadata for nonexistent skill (expect: empty/error)
    - **Validation:** Tool returns lightweight metadata only

- [ ] **Task 4.6: Test search_skills_by_tags Tool**
    - Test case 1: Search for tag "finance" (expect: finance skills)
    - Test case 2: Search for tag "insurance" (expect: insurance skills)
    - Test case 3: Search for tags ["compliance", "finance"] with match_all=true
    - Test case 4: Search for tags ["compliance", "finance"] with match_all=false
    - **Validation:** Tool returns tag-filtered results correctly

- [ ] **Task 4.7: Create Automated Test Suite**
    - Create `tests/test_agent_builder_mcp.py` using pytest
    - Implement test fixtures for MCP client and test data
    - Write test functions for each tool with multiple test cases
    - Assert expected results and handle errors
    - Generate test report showing pass/fail status
    - **Validation:** Run `uv run pytest tests/test_agent_builder_mcp.py -v`

## Phase 5: Documentation

**Goal:** Document the Agent Builder MCP tools implementation.

- [ ] **Task 5.1: Create Agent Builder Guide**
    - Create `AGENT_BUILDER.md` with comprehensive guide:
        - Overview of Agent Builder MCP architecture
        - ES|QL query patterns used
        - How to register/update/delete tools
        - How to test tools via MCP endpoint
        - Troubleshooting common issues
        - Examples of tool invocation from Claude agents
    - **Validation:** Review guide for completeness

- [ ] **Task 5.2: Update README**
    - Add "Agent Builder Integration" section to README.md
    - Document registration script usage:
        - `uv run scripts/register_agent_builder_tools.py --register`
        - `uv run scripts/register_agent_builder_tools.py --list`
    - Document test script usage:
        - `uv run scripts/test_agent_builder_tools.py --tool search_skills --query "expense"`
    - Include example MCP tool invocation
    - **Validation:** Commands work as documented

- [ ] **Task 5.3: Add Tool Definition Examples**
    - Document each tool definition JSON structure
    - Provide example ES|QL queries with explanations
    - Show parameter mapping patterns
    - Include troubleshooting tips for common ES|QL errors
    - **Validation:** Examples are accurate and helpful

## Success Criteria

- ✅ 5 Agent Builder tools registered in Kibana (search_skills, get_skill_by_id, list_skills_by_domain, get_skill_metadata, search_skills_by_tags)
- ✅ All tools use ES|QL queries with parameterized placeholders
- ✅ Registration script successfully POSTs tool definitions to Kibana API
- ✅ All tools tested via Elastic MCP endpoint with expected results
- ✅ Automated test suite validates tool functionality
- ✅ Documentation provides clear usage instructions
- ✅ Tools integrate seamlessly with existing agent_skills index

## Completion Rules

1. Do NOT mark a task as done until:
    - The code/query is written and tested
    - Tool definitions validate against API schema
    - Tools are registered and functional in Kibana
    - Test cases pass with expected results
2. All ES|QL queries must be tested in Kibana Dev Tools first
3. All API calls must use proper authentication headers
4. Use `uv run` for all Python script execution
5. Test both success and error cases for each tool

## Dependencies

- Elasticsearch Serverless instance running with agent_skills index
- Kibana instance accessible via KIBANA_URL
- Valid ELASTIC_API_KEY with Agent Builder permissions
- Skills must be ingested before testing tools
- Python packages: `requests`, `python-dotenv`, `pytest`

## Key Technical Decisions

### ES|QL vs REST API Queries
Agent Builder tools use ES|QL rather than REST API queries for several advantages:
- **Declarative syntax:** Easier to read and maintain
- **Piped operations:** Natural data transformation flow
- **Native Kibana support:** Built-in query validation and testing
- **Parameter safety:** Parameterized queries prevent injection attacks

### Semantic Search Implementation
The `search_skills` tool will use ES|QL's text matching capabilities on the `semantic_content` field:
- Leverages existing semantic_text field with Jina embeddings
- Maintains consistency with search_test.py script
- Returns relevance scores for ranking

### Tool Naming Convention
Tool IDs match existing MCP tool names for consistency:
- Enables easy migration from MCP tools.json to Agent Builder
- Maintains familiar API for Claude agents
- Simplifies testing and comparison

### Parameter Handling
ES|QL parameter placeholders use `?paramName` syntax:
- Type-safe parameter binding
- Clear parameter-to-query mapping
- Prevents SQL injection vulnerabilities

## Notes

- The `execute_skill` tool is intentionally excluded from this phase as it requires code execution capabilities beyond ES|QL queries
- Tool registration requires Agent Builder API access - verify API key permissions before starting
- ES|QL query syntax may differ from traditional SQL - reference Elastic documentation
- Test tools in Kibana Dev Tools console before registering as Agent Builder tools
- MCP endpoint URLs may vary by Elastic Cloud deployment - verify ELASTIC_MCP_URL is correct
