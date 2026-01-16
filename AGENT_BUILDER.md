# Agent Builder MCP Tools Guide

This guide provides comprehensive documentation for the Elastic Agent Builder MCP tools implementation. These tools enable Claude agents to search and retrieve agent skills directly through Kibana's Agent Builder API using ES|QL queries.

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tool Definitions](#tool-definitions)
- [ES|QL Query Patterns](#esql-query-patterns)
- [Registration Guide](#registration-guide)
- [Testing Guide](#testing-guide)
- [Troubleshooting](#troubleshooting)
- [Examples](#examples)

## Overview

The Agent Builder MCP tools provide a bridge between Claude agents and Elasticsearch-stored agent skills. Instead of traditional MCP server implementations, these tools leverage Kibana's Agent Builder API to execute ES|QL queries directly, offering:

- **Declarative queries**: ES|QL provides a clear, SQL-like syntax
- **Native Kibana integration**: Built-in query validation and testing
- **Type-safe parameters**: Parameterized queries prevent injection attacks
- **Scalability**: Direct Elasticsearch access for optimal performance

## Architecture

### Components

```
┌─────────────────┐
│  Claude Agent   │
└────────┬────────┘
         │
         │ MCP Protocol
         │
         v
┌─────────────────┐
│ Kibana Agent    │
│ Builder API     │
│ /api/agent_     │
│ builder/mcp     │
└────────┬────────┘
         │
         │ ES|QL Queries
         │
         v
┌─────────────────┐
│ Elasticsearch   │
│ agent_skills    │
│ index           │
└─────────────────┘
```

### Key Technologies

- **Language**: Python 3.10+
- **Query Language**: ES|QL (Elasticsearch Query Language)
- **API Endpoint**: `/api/agent_builder/tools` (registration), `/api/agent_builder/mcp` (execution)
- **Authentication**: API Key via `Authorization: ApiKey` header
- **Index**: `agent_skills` with semantic_text field

### Environment Variables

```bash
KIBANA_URL=https://your-kibana-instance.elastic.cloud
ELASTIC_API_KEY=your_api_key_here
ELASTIC_MCP_URL=https://your-kibana-instance.elastic.cloud/api/agent_builder/mcp
```

## Tool Definitions

### Available Tools

| Tool ID | Purpose | Parameters |
|---------|---------|------------|
| `search_skills` | Semantic search for agent skills | `query` (string), `limit` (int) |
| `get_skill_by_id` | Retrieve specific skill by ID | `skill_id` (string) |
| `list_skills_by_domain` | List skills in a domain | `domain` (string) |
| `get_skill_metadata` | Get lightweight skill metadata | `skill_id` (string) |
| `search_skills_by_tags` | Search skills by tags | `tag` (string, regex pattern) |

### Tool Definition Format

Each tool is defined in JSON format with the following structure:

```json
{
  "id": "tool_identifier",
  "type": "esql",
  "description": "Human-readable description of what the tool does",
  "tags": ["agent-skills", "mcp", "category"],
  "configuration": {
    "query": "ES|QL query with ?param placeholders",
    "params": {
      "param_name": {
        "type": "keyword|integer|boolean",
        "description": "Parameter description",
        "required": true|false,
        "default": "optional_default_value"
      }
    }
  }
}
```

## ES|QL Query Patterns

### 1. Basic Selection with Filter

```esql
FROM agent_skills
| WHERE skill_id == ?skill_id
```

**Use Case**: Exact match retrieval (e.g., `get_skill_by_id`)

### 2. Field Selection with KEEP

```esql
FROM agent_skills
| WHERE domain == ?domain
| KEEP skill_id, name, domain, short_description, tags, rating
| SORT rating DESC
```

**Use Case**: Listing with specific fields (e.g., `list_skills_by_domain`)

### 3. Multi-Value Field Handling

```esql
FROM agent_skills
| EVAL tags_str = MV_CONCAT(tags, ",")
| WHERE tags_str RLIKE ?tag
| KEEP skill_id, name, domain, tags, short_description
```

**Use Case**: Tag matching with regex patterns (e.g., `search_skills_by_tags`)

**Note**: ES|QL `RLIKE` requires literal string patterns, so the `?tag` parameter must be pre-formatted as a regex (e.g., ".*finance.*").

### 4. Metadata-Only Queries

```esql
FROM agent_skills
| WHERE skill_id == ?skill_id
| KEEP skill_id, name, domain, tags, author, version, rating, created_at
```

**Use Case**: Lightweight metadata retrieval without large fields (e.g., `get_skill_metadata`)

### Key ES|QL Operators

- `FROM`: Specify source index
- `WHERE`: Filter rows (supports ==, !=, <, >, <=, >=, RLIKE)
- `KEEP`: Select specific fields to return
- `DROP`: Exclude specific fields
- `SORT`: Order results (ASC/DESC)
- `LIMIT`: Limit number of results
- `EVAL`: Create computed fields
- `MV_CONCAT`: Concatenate multi-value fields

### Parameter Placeholders

Use `?param_name` syntax for parameterized queries:

```esql
WHERE domain == ?domain
WHERE skill_id == ?skill_id
LIMIT ?limit
```

Parameters are type-safe and prevent SQL injection vulnerabilities.

## Registration Guide

### Prerequisites

1. Kibana instance with Agent Builder API access
2. Valid API key with appropriate permissions
3. Environment variables configured in `.env` file

### Register All Tools

```bash
# Validate tool definitions without registering
uv run scripts/register_agent_builder_tools.py --dry-run

# Register all tools from agent_builder/tools/
uv run scripts/register_agent_builder_tools.py --register
```

### Update a Specific Tool

```bash
uv run scripts/register_agent_builder_tools.py --update search_skills
```

### Delete a Tool

```bash
uv run scripts/register_agent_builder_tools.py --delete search_skills
```

### List Registered Tools

```bash
uv run scripts/register_agent_builder_tools.py --list
```

### Registration Process

1. Script reads tool definition JSON files from `agent_builder/tools/`
2. Validates required fields: `id`, `type`, `configuration.query`
3. Constructs POST request to `{KIBANA_URL}/api/agent_builder/tools`
4. Sets authentication headers:
   - `Authorization: ApiKey {ELASTIC_API_KEY}`
   - `kbn-xsrf: true`
   - `Content-Type: application/json`
5. Sends tool definition as request body
6. Handles response codes:
   - 200/201: Success
   - 400: Bad request (validation error)
   - 401: Authentication error
   - 500: Server error

## Testing Guide

### Using the Test Script

#### Test a Specific Tool

```bash
uv run scripts/test_agent_builder_tools.py \
  --tool search_skills \
  --params '{"query": "expense policy", "limit": 5}'
```

#### Run Predefined Test Suite

```bash
# Test all search_skills test cases
uv run scripts/test_agent_builder_tools.py --test-suite search_skills

# Test with verbose output
uv run scripts/test_agent_builder_tools.py --test-suite get_skill_by_id --verbose
```

#### Run All Tests

```bash
uv run scripts/test_agent_builder_tools.py --all
```

### Using Pytest

```bash
# Run all Agent Builder MCP tests
uv run pytest tests/test_agent_builder_mcp.py -v

# Run specific test class
uv run pytest tests/test_agent_builder_mcp.py::TestSearchSkills -v

# Run specific test method
uv run pytest tests/test_agent_builder_mcp.py::TestSearchSkills::test_search_expense_policy -v

# Generate JSON report
uv run pytest tests/test_agent_builder_mcp.py --json-report --json-report-file=report.json
```

### Test Data Requirements

Tests expect the following skills to be ingested:

- **verify-expense-policy** (domain: finance)
- **adjudicate-storm-claim** (domain: insurance)
- **validate-sample-viability** (domain: life_sciences)

Run ingestion script before testing:

```bash
uv run scripts/ingest_skills.py
```

## Troubleshooting

### Common Issues

#### 1. Authentication Errors (401)

**Symptom**: `401 Unauthorized` response

**Solutions**:
- Verify `ELASTIC_API_KEY` is correct in `.env`
- Check API key has Agent Builder permissions
- Ensure API key format is correct (no extra whitespace)

```bash
# Test API key
curl -H "Authorization: ApiKey $ELASTIC_API_KEY" \
     -H "kbn-xsrf: true" \
     "$KIBANA_URL/api/agent_builder/tools"
```

#### 2. Tool Not Found (404)

**Symptom**: Tool execution returns 404

**Solutions**:
- Verify tool is registered: `uv run scripts/register_agent_builder_tools.py --list`
- Re-register the tool: `uv run scripts/register_agent_builder_tools.py --register`

#### 3. ES|QL Query Syntax Errors (400)

**Symptom**: Bad request with ES|QL syntax error

**Solutions**:
- Test query in Kibana Dev Tools → ES|QL console
- Check parameter placeholders use `?param_name` syntax
- Verify field names match index mapping

#### 4. Empty Results

**Symptom**: Tools return no results

**Solutions**:
- Verify skills are ingested: `uv run scripts/search_test.py`
- Check index name is correct: `agent_skills`
- Verify semantic search inference endpoint is configured

#### 5. Semantic Search Limitation

**Symptom**: `search_skills` doesn't use query parameter

**Known Issue**: ES|QL does not support semantic text search with MATCH operator in WHERE clauses.

**Current Workaround**: The tool uses `LIMIT` without semantic filtering. Agent Builder API may provide additional capabilities beyond raw ES|QL.

**Alternative**: Consider using Elasticsearch Query DSL for semantic search, or wait for ES|QL semantic search support.

### Debug Mode

Enable verbose output for detailed error information:

```bash
# Test script verbose mode
uv run scripts/test_agent_builder_tools.py --tool get_skill_by_id \
  --params '{"skill_id": "test"}' --verbose

# Pytest verbose mode
uv run pytest tests/test_agent_builder_mcp.py -v -s
```

### Validate Tool Definitions

```bash
# Dry-run validation
uv run scripts/register_agent_builder_tools.py --dry-run
```

Expected output:
```
Validating 5 tool(s)...

✓ get_skill_by_id.json: Valid tool definition for 'get_skill_by_id'
✓ get_skill_metadata.json: Valid tool definition for 'get_skill_metadata'
✓ list_skills_by_domain.json: Valid tool definition for 'list_skills_by_domain'
✓ search_skills.json: Valid tool definition for 'search_skills'
✓ search_skills_by_tags.json: Valid tool definition for 'search_skills_by_tags'

Validation Summary:
  Total: 5
  ✅ Successful: 5
  ❌ Failed: 0
```

## Examples

### Example 1: Search and Retrieve Skill

```python
from scripts.test_agent_builder_tools import MCPToolTester
import os

# Initialize tester
tester = MCPToolTester(
    mcp_url=os.getenv('ELASTIC_MCP_URL'),
    api_key=os.getenv('ELASTIC_API_KEY')
)

# Search for skills
results = tester.test_tool('search_skills', {
    'query': 'expense policy validation',
    'limit': 3
})

# Get first skill by ID
if results.get('results'):
    skill_id = results['results'][0]['skill_id']
    skill = tester.test_tool('get_skill_by_id', {
        'skill_id': skill_id
    })
    print(f"Retrieved skill: {skill}")
```

### Example 2: List Skills by Domain

```python
# List all finance skills
finance_skills = tester.test_tool('list_skills_by_domain', {
    'domain': 'finance'
})

for skill in finance_skills.get('results', []):
    print(f"{skill['skill_id']}: {skill['name']}")
```

### Example 3: Search by Tags

```python
# Find all compliance-related skills
compliance_skills = tester.test_tool('search_skills_by_tags', {
    'tag': '.*compliance.*'
})

for skill in compliance_skills.get('results', []):
    print(f"{skill['skill_id']}: {skill['tags']}")
```

### Example 4: Get Lightweight Metadata

```python
# Get metadata without full content
metadata = tester.test_tool('get_skill_metadata', {
    'skill_id': 'verify-expense-policy'
})

# Metadata includes: skill_id, name, domain, tags, author, version, rating
# Excludes large fields: skill_markdown, description
print(f"Skill: {metadata['results'][0]['name']}")
print(f"Domain: {metadata['results'][0]['domain']}")
print(f"Rating: {metadata['results'][0]['rating']}")
```

### Example 5: Claude Agent Usage

Claude agents can invoke these tools through the MCP protocol:

```
User: "Find me a skill for validating expense policies"

Claude: <uses search_skills tool>
        query: "expense policy validation"
        limit: 3

Result: Found "verify-expense-policy" skill

User: "Show me the full implementation"

Claude: <uses get_skill_by_id tool>
        skill_id: "verify-expense-policy"

Result: Returns complete skill with markdown content and Python code
```

## Best Practices

### Query Design

1. **Use KEEP for field selection**: Reduces payload size
2. **Add SORT for deterministic results**: Especially important for pagination
3. **Use parameterized queries**: Always use `?param` instead of string concatenation
4. **Test in Kibana Dev Tools first**: Validate ES|QL syntax before registration

### Error Handling

1. **Check for errors in response**: Always validate `"error" not in response`
2. **Handle empty results gracefully**: Skills may not exist or queries may match nothing
3. **Provide meaningful error messages**: Help users understand what went wrong

### Performance

1. **Use metadata queries when possible**: Avoid fetching large skill_markdown fields
2. **Set appropriate limits**: Don't fetch more results than needed
3. **Use domain filtering**: Narrow search scope when domain is known

### Security

1. **Never expose API keys**: Use environment variables
2. **Validate input parameters**: Especially for regex patterns in tag search
3. **Use parameterized queries**: Prevent injection attacks

## Additional Resources

- [ES|QL Documentation](https://www.elastic.co/guide/en/elasticsearch/reference/current/esql.html)
- [Kibana Agent Builder API](https://www.elastic.co/guide/en/kibana/current/agent-builder-api.html)
- [Elasticsearch Semantic Text](https://www.elastic.co/guide/en/elasticsearch/reference/current/semantic-text.html)
- [MCP Protocol Specification](https://modelcontextprotocol.io/)

## Support

For issues or questions:

1. Check the [Troubleshooting](#troubleshooting) section
2. Review test output for error details
3. Validate tool definitions with dry-run mode
4. Test ES|QL queries in Kibana Dev Tools console

## License

This implementation is part of the Elastic Agent Skills Demo repository.
