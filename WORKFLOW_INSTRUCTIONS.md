# Agent Skills Operator Workflow

## Overview

The `agent_skills_operator` workflow manages the agent skills environment by performing setup and teardown operations. It runs asynchronously with job polling to handle long-running operations.

## Workflow Name

```
agent_skills_operator
```

## Available Operations

| Operation | Description |
|-----------|-------------|
| `setup` | Creates Elasticsearch indexes and ingests all skills from `sample_skills/` |
| `teardown` | Deletes Elasticsearch indexes and removes all indexed skills |
| `update-skills` | Ingests all skills from `new_skills/` folder (for adding new skills incrementally) |

## Input Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `operation` | string | `setup` | Operation to perform: `setup` or `teardown` |
| `api_base_url` | string | (configured) | Base URL for the Data Operations API |
| `max_polls` | number | `30` | Maximum polling attempts (30 x 10s = 5 min timeout) |

## How to Invoke

### Setup Environment

To initialize the agent skills environment (create indexes, ingest skills, register tools):

```
Run the agent_skills_operator workflow with operation="setup"
```

**What it does:**
1. Creates `agent_skills` index (skill metadata)
2. Creates `agent_skill_files` index (skill file contents)
3. Bulk ingests all skills from the `sample_skills/` directory
4. Registers MCP tools for skill search and retrieval

### Teardown Environment

To clean up the agent skills environment (delete all data):

```
Run the agent_skills_operator workflow with operation="teardown"
```

**What it does:**
1. Enumerates existing skills for reporting
2. Deletes `agent_skills` index
3. Deletes `agent_skill_files` index
4. Unregisters MCP tools

### Update Skills (Add New Skills)

To add new skills incrementally without full setup:

```
Run the agent_skills_operator workflow with operation="update-skills"
```

**What it does:**
1. Scans the `new_skills/` folder for skill directories
2. Ingests each skill found (metadata + files)
3. Adds to existing indexes without deleting current data

**Workflow:**
1. Add skill folder(s) to `new_skills/` directory
2. Each skill folder must contain a `SKILL.md` file
3. Run the workflow with `operation="update-skills"`
4. Skills are indexed to `agent_skills` and files to `agent_skill_files`

## Expected Output

### Successful Setup

```
============================================
Job setup completed
============================================
Job ID: abc12345
Final Status: completed
Progress: Setup complete
Message: Environment setup complete. Indexes: ['agent_skills', 'agent_skill_files']. Skills ingested: 100.
Details:
  Indexes Created: agent_skills, agent_skill_files
  Indexes Deleted:
  Skills Created: 100
  Skills Deleted: 0
============================================
```

### Successful Teardown

```
============================================
Job teardown completed
============================================
Job ID: xyz67890
Final Status: completed
Progress: Teardown complete
Message: Environment teardown complete. Indexes deleted: ['agent_skills', 'agent_skill_files']. Skills deleted: 100.
Details:
  Indexes Created:
  Indexes Deleted: agent_skills, agent_skill_files
  Skills Created: 0
  Skills Deleted: 100
============================================
```

### Successful Update-Skills

```
============================================
Job update-skills completed
============================================
Job ID: def45678
Final Status: completed
Progress: Update complete
Message: Ingested 3 skill(s) from new_skills folder. Total files: 12.
Details:
  Indexes Created:
  Indexes Deleted:
  Skills Created: 3
  Skills Deleted: 0
============================================
```

## Timing

- **Setup**: ~30-60 seconds (depends on number of skills)
- **Teardown**: ~10-30 seconds
- **Update-skills**: ~5-15 seconds (depends on number of new skills)
- **Polling interval**: 10 seconds
- **Maximum wait**: 5 minutes (30 polls x 10s)

## Error Handling

If the job fails, the output will show:
- `Final Status: failed`
- `error` field with the failure reason

Common issues:
- Elasticsearch connection failure
- Missing environment variables (`ELASTIC_SEARCH_URL`, `ELASTIC_API_KEY`)
- API service not running or unreachable

## Prerequisites

Before running the workflow:

1. **API Service Running**: The Data Operations API must be running and accessible at the configured `api_base_url`
2. **Elasticsearch Access**: Valid credentials configured in the API's environment
3. **Network Access**: The workflow must be able to reach the API endpoint (may require tunnel for local development)
