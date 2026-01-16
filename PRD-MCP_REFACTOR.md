# PRD: MCP Skill Index Refactor - Separate Metadata and File Storage

## Executive Summary

This PRD outlines the refactoring of the MCP (Model Context Protocol) skill storage system to split skill metadata and skill file contents into two separate Elasticsearch indexes. Currently, only the `SKILL.md` content is stored in the `skill_markdown` field; all other skill files (Python scripts, JSON configs, CSV data files) are **not** being stored in Elasticsearch. This refactor ensures all skill resources are persisted and retrievable.

---

## Problem Statement

### Current State
1. **Single Index Architecture**: All skill data resides in `agent_skills` index
2. **Incomplete File Storage**: Only `SKILL.md` content is stored in `skill_markdown` field
3. **Missing Resources**: Python implementation files (`policy_check.py`, `adjudicator.py`, etc.), configuration files (`allowance_table.json`, `biomarker_constraints.json`), and data files (`risk_matrix.csv`) are **NOT** stored in Elasticsearch
4. **Local File Dependency**: Tests currently rely on local filesystem access to execute skill logic (see `tests/conftest.py:267-275`)

### Evidence of the Problem
From `scripts/ingest_skills.py`:
- Lines 79-87: File metadata is collected but content is never read
- Line 121: Only `skill_markdown` (SKILL.md content) is stored
- The `resources` nested field in the mapping exists but is never populated

### Files Per Skill (excluding `__pycache__`)
| Skill | Files |
|-------|-------|
| `verify-expense-policy` | SKILL.md, policy_check.py, allowance_table.json |
| `adjudicate-storm-claim` | SKILL.md, adjudicator.py, risk_matrix.csv |
| `validate-sample-viability` | SKILL.md, viability_check.py, biomarker_constraints.json |

---

## Proposed Solution

### Architecture Change: Two-Index Design

#### Index 1: `agent_skills` (Metadata Index) - MODIFY EXISTING
Contains skill metadata for discovery and filtering. Remove `skill_markdown` field (will be stored in files index).

**Key Fields** (unchanged):
- `skill_id` (keyword) - Primary identifier
- `name`, `description`, `short_description` (text)
- `domain`, `tags`, `author` (keyword)
- `semantic_content` (semantic_text) - For vector search
- `rating`, `usage_count`, `success_rate` - Analytics

**Removed Fields**:
- `skill_markdown` - Moved to files index
- `resources` (nested) - Replaced by files index

#### Index 2: `agent_skill_files` (Files Index) - NEW
Contains all file contents for each skill.

**Schema**:
```json
{
  "mappings": {
    "properties": {
      "skill_id": {
        "type": "keyword"
      },
      "file_name": {
        "type": "keyword"
      },
      "file_path": {
        "type": "keyword"
      },
      "file_type": {
        "type": "keyword"
      },
      "file_content": {
        "type": "text",
        "index": false
      },
      "file_size_bytes": {
        "type": "long"
      },
      "created_at": {
        "type": "date"
      }
    }
  }
}
```

**Document ID Strategy**: `{skill_id}_{file_name}` (e.g., `verify-expense-policy_policy_check.py`)

---

## Implementation Requirements

### 1. Configuration Changes (`/config`)

#### 1.1 Create New File: `config/skill_files_mappings.json`
- Define schema for `agent_skill_files` index
- Fields: `skill_id`, `file_name`, `file_path`, `file_type`, `file_content`, `file_size_bytes`, `created_at`

#### 1.2 Modify: `config/index_mappings.json`
- Remove `skill_markdown` field (content moves to files index)
- Remove `resources` nested field (replaced by files index)
- Keep all other metadata fields intact

---

### 2. Script Changes (`/scripts`)

#### 2.1 Modify: `scripts/ingest_skills.py`

**Current Behavior**:
- Parses `SKILL.md` only
- Stores content in `skill_markdown` field
- Ignores other files

**New Behavior**:
```python
def ingest_skills(skills_dir, es_client):
    for skill_dir in skills_dir.iterdir():
        # 1. Parse metadata from SKILL.md
        metadata = parse_skill_metadata(skill_dir)

        # 2. Index metadata to agent_skills
        es_client.index(index="agent_skills", id=skill_id, document=metadata_doc)

        # 3. Index ALL files to agent_skill_files
        for file_path in skill_dir.rglob('*'):
            if file_path.is_file() and '__pycache__' not in str(file_path):
                file_doc = {
                    "skill_id": skill_id,
                    "file_name": file_path.name,
                    "file_path": str(file_path.relative_to(skill_dir)),
                    "file_type": file_path.suffix[1:] or "unknown",
                    "file_content": file_path.read_text(encoding='utf-8'),
                    "file_size_bytes": file_path.stat().st_size,
                    "created_at": datetime.utcnow().isoformat()
                }
                doc_id = f"{skill_id}_{file_path.name}"
                es_client.index(index="agent_skill_files", id=doc_id, document=file_doc)
```

**Key Changes**:
- Add `ensure_files_index()` function to create `agent_skill_files` index
- Read actual file content (not just metadata)
- Skip `__pycache__` directories and `.pyc` files
- Handle binary files appropriately (base64 encode if needed, or skip)

#### 2.2 Modify: `scripts/validate_indexing.py`
- Add validation for `agent_skill_files` index
- Verify file count matches expected files per skill
- Validate file content is not empty

---

### 3. Agent Builder Changes (`/agent_builder`)

#### 3.1 Modify: `agent_builder/queries/get_skill_by_id.esql`

**Current Query**:
```esql
FROM agent_skills
| WHERE skill_id == ?skill_id
```

**New Query** (metadata only):
```esql
FROM agent_skills
| WHERE skill_id == ?skill_id
```
(No change needed - this returns metadata)

#### 3.2 Create New: `agent_builder/queries/get_skill_files.esql`
```esql
FROM agent_skill_files
| WHERE skill_id == ?skill_id
| KEEP skill_id, file_name, file_path, file_type, file_content
```

#### 3.3 Modify: `agent_builder/tools/get_skill_by_id.json`

**Current Description**: Returns complete skill document

**New Implementation**: Must perform a JOIN lookup:
1. Query `agent_skills` for metadata
2. Query `agent_skill_files` for all files with matching `skill_id`
3. Return combined result

**Option A - Sequential ES|QL Queries** (Recommended for MCP):
The MCP tool handler will need to execute two queries and merge results programmatically.

**Option B - ES|QL LOOKUP** (If supported):
```esql
FROM agent_skills
| WHERE skill_id == ?skill_id
| LOOKUP agent_skill_files ON skill_id
```
Note: ES|QL LOOKUP has limitations; verify compatibility.

#### 3.4 Create New Tool: `agent_builder/tools/get_skill_files.json`
```json
{
  "id": "get_skill_files",
  "type": "esql",
  "description": "Retrieve all files for a specific skill by skill_id",
  "tags": ["agent-skills", "mcp", "files"],
  "configuration": {
    "query": "FROM agent_skill_files | WHERE skill_id == ?skill_id",
    "params": {
      "skill_id": {
        "type": "keyword",
        "description": "Skill identifier to retrieve files for"
      }
    }
  }
}
```

---

### 4. Test Changes (`/tests`)

#### 4.1 Modify: `tests/conftest.py`

**Current `get_skill_by_id` fixture** (lines 158-204):
- Only queries `agent_skills` index
- Returns metadata + skill_markdown

**New `get_skill_by_id` fixture**:
```python
@pytest.fixture
def get_skill_by_id(es_client, index_name):
    def _get(skill_id: str) -> Dict[str, Any]:
        # 1. Get metadata from agent_skills
        metadata_response = es_client.search(
            index="agent_skills",
            body={"query": {"term": {"skill_id": skill_id}}}
        )

        if metadata_response['hits']['total']['value'] == 0:
            raise Exception(f"Skill not found: {skill_id}")

        skill = metadata_response['hits']['hits'][0]['_source']

        # 2. Get all files from agent_skill_files
        files_response = es_client.search(
            index="agent_skill_files",
            body={
                "query": {"term": {"skill_id": skill_id}},
                "size": 100  # Get all files
            }
        )

        # 3. Merge files into skill document
        skill['files'] = {}
        for hit in files_response['hits']['hits']:
            file_doc = hit['_source']
            skill['files'][file_doc['file_name']] = file_doc['file_content']

        # 4. Set skill_markdown from SKILL.md file (for backward compatibility)
        if 'SKILL.md' in skill['files']:
            skill['skill_markdown'] = skill['files']['SKILL.md']

        return skill

    return _get
```

#### 4.2 Modify: `tests/conftest.py` - `execute_skill_logic` fixture

**Current Behavior** (lines 267-296):
- Reads files from local filesystem
- Adds skill directory to Python path

**New Behavior**:
- Extract files from Elasticsearch response
- Write files to temporary directory
- Execute from temp directory
- Clean up after execution

```python
@pytest.fixture
def execute_skill_logic():
    def _execute(skill_content: Dict[str, Any], input_params: Dict[str, Any]) -> Dict[str, Any]:
        import tempfile
        import os

        skill_id = skill_content.get('skill_id')
        files = skill_content.get('files', {})

        # Create temp directory with skill files
        with tempfile.TemporaryDirectory() as temp_dir:
            # Write all files to temp directory
            for file_name, file_content in files.items():
                file_path = os.path.join(temp_dir, file_name)
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(file_content)

            # Add temp directory to path
            sys.path.insert(0, temp_dir)

            try:
                # Extract and execute Python code from SKILL.md
                skill_markdown = files.get('SKILL.md', '')
                # ... (existing code extraction logic)

                exec_locals = {'input_data': input_params}
                exec(python_code, {}, exec_locals)

                return exec_locals.get('result')
            finally:
                sys.path.remove(temp_dir)

    return _execute
```

#### 4.3 Create New Test: `tests/test_skill_files.py`

```python
"""Tests for skill file storage and retrieval."""

def test_all_skill_files_indexed(es_client):
    """Verify all skill files are stored in Elasticsearch."""
    expected_files = {
        'verify-expense-policy': ['SKILL.md', 'policy_check.py', 'allowance_table.json'],
        'adjudicate-storm-claim': ['SKILL.md', 'adjudicator.py', 'risk_matrix.csv'],
        'validate-sample-viability': ['SKILL.md', 'viability_check.py', 'biomarker_constraints.json']
    }

    for skill_id, expected in expected_files.items():
        response = es_client.search(
            index="agent_skill_files",
            body={"query": {"term": {"skill_id": skill_id}}}
        )

        actual_files = [hit['_source']['file_name'] for hit in response['hits']['hits']]

        for file_name in expected:
            assert file_name in actual_files, f"Missing file: {skill_id}/{file_name}"


def test_file_content_not_empty(es_client):
    """Verify file content is properly stored."""
    response = es_client.search(
        index="agent_skill_files",
        body={"query": {"match_all": {}}, "size": 100}
    )

    for hit in response['hits']['hits']:
        file_doc = hit['_source']
        assert file_doc['file_content'], f"Empty content for {file_doc['skill_id']}/{file_doc['file_name']}"


def test_pycache_not_indexed(es_client):
    """Verify __pycache__ files are NOT indexed."""
    response = es_client.search(
        index="agent_skill_files",
        body={
            "query": {
                "wildcard": {"file_name": "*.pyc"}
            }
        }
    )

    assert response['hits']['total']['value'] == 0, "Found .pyc files in index"
```

---

### 5. MCP Server Changes (if applicable)

The MCP tool `get_skill_by_id` must be updated to:
1. Execute first query against `agent_skills`
2. Execute second query against `agent_skill_files`
3. Merge results into single response
4. Return combined skill document with all files

---

## Success Criteria

### Acceptance Tests
1. **All Files Indexed**: Every file from each skill directory (except `__pycache__`) is stored in `agent_skill_files` index
2. **File Count Validation**:
   - `verify-expense-policy`: 3 files
   - `adjudicate-storm-claim`: 3 files
   - `validate-sample-viability`: 3 files
   - Total: 9 files in `agent_skill_files` index
3. **get_skill_by_id Returns All Files**: API returns both metadata and all associated files
4. **Skill Execution Works**: Tests can execute skill logic using files retrieved from Elasticsearch (not local filesystem)
5. **Existing Tests Pass**: All tests in `test_expense_policy.py`, `test_storm_claim.py`, `test_sample_viability.py` continue to pass
6. **No __pycache__ Files**: Zero `.pyc` files or `__pycache__` directories indexed

### Performance Criteria
- File retrieval should complete in < 500ms for skills with up to 10 files
- Ingestion should handle files up to 1MB in size

---

## Implementation Steps

### Phase 1: Configuration
1. Create `config/skill_files_mappings.json`
2. Create `config/skill_files_settings.json`
3. Update `config/index_mappings.json` (remove deprecated fields)

### Phase 2: Ingestion Script
1. Add `ensure_files_index()` function to `ingest_skills.py`
2. Modify `parse_skill_metadata()` to exclude file content
3. Add `index_skill_files()` function
4. Update main ingestion loop
5. Add `__pycache__` exclusion logic

### Phase 3: Agent Builder
1. Create `get_skill_files.esql` query
2. Create `get_skill_files.json` tool definition
3. Update tool registration script

### Phase 4: Tests
1. Modify `conftest.py` fixtures
2. Create `test_skill_files.py`
3. Update existing tests if needed

### Phase 5: Validation
1. Run `validate_indexing.py`
2. Run full test suite
3. Verify all 9 files are indexed
4. Verify skill execution works from ES data

---

## File Change Summary

| File | Action | Description |
|------|--------|-------------|
| `config/skill_files_mappings.json` | CREATE | New index mapping for files |
| `config/skill_files_settings.json` | CREATE | New index settings for files |
| `config/index_mappings.json` | MODIFY | Remove skill_markdown, resources fields |
| `scripts/ingest_skills.py` | MODIFY | Add file indexing logic |
| `scripts/validate_indexing.py` | MODIFY | Add files index validation |
| `agent_builder/queries/get_skill_files.esql` | CREATE | New query for files |
| `agent_builder/tools/get_skill_files.json` | CREATE | New tool definition |
| `tests/conftest.py` | MODIFY | Update fixtures for two-index lookup |
| `tests/test_skill_files.py` | CREATE | New tests for file storage |

---

## Risks and Mitigations

| Risk | Impact | Mitigation |
|------|--------|------------|
| Large file content exceeds ES limits | High | Implement file size check; warn/skip files > 1MB |
| Binary files cause encoding issues | Medium | Detect binary files and use base64 encoding |
| ES|QL LOOKUP not supported | Medium | Use programmatic join in MCP handler |
| Breaking change to existing API | High | Maintain backward compatibility by populating `skill_markdown` from SKILL.md file |

---

## Backward Compatibility

To ensure existing integrations continue to work:
1. The `skill_markdown` field will be populated from the `SKILL.md` file in the response
2. The `get_skill_by_id` response structure remains the same, with an added `files` object
3. Existing tests should pass without modification (once fixtures are updated)

---

## Appendix: Expected Index Documents

### agent_skills Document Example
```json
{
  "skill_id": "verify-expense-policy",
  "name": "Skill: Verify Expense Policy",
  "description": "Validates expense requests against company policy...",
  "short_description": "Validates expense requests...",
  "domain": "finance",
  "tags": ["expense", "policy", "compliance"],
  "author": "system",
  "version": "1.0",
  "rating": 5.0,
  "semantic_content": "...",
  "created_at": "2026-01-14T00:00:00Z"
}
```

### agent_skill_files Documents Example
```json
// Document 1: verify-expense-policy_SKILL.md
{
  "skill_id": "verify-expense-policy",
  "file_name": "SKILL.md",
  "file_path": "SKILL.md",
  "file_type": "md",
  "file_content": "# Skill: Verify Expense Policy\n\n## Domain\nfinance\n\n...",
  "file_size_bytes": 3456,
  "created_at": "2026-01-15T00:00:00Z"
}

// Document 2: verify-expense-policy_policy_check.py
{
  "skill_id": "verify-expense-policy",
  "file_name": "policy_check.py",
  "file_path": "policy_check.py",
  "file_type": "py",
  "file_content": "#!/usr/bin/env python3\n\ndef verify_expense(...):\n    ...",
  "file_size_bytes": 2345,
  "created_at": "2026-01-15T00:00:00Z"
}

// Document 3: verify-expense-policy_allowance_table.json
{
  "skill_id": "verify-expense-policy",
  "file_name": "allowance_table.json",
  "file_path": "allowance_table.json",
  "file_type": "json",
  "file_content": "{\"valid_categories\": [...], ...}",
  "file_size_bytes": 1234,
  "created_at": "2026-01-15T00:00:00Z"
}
```

---

## Version History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-01-15 | System | Initial PRD |
