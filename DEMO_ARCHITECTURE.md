# Elastic Agent Skills Architecture Specification

> **Purpose:** Technical architecture documentation for the Elastic Agent Skills Demo
> **Audience:** CTOs, Senior Architects, Account Executives, Business Analysts
> **Last Updated:** January 2026

-----

## Executive Summary

This solution demonstrates **AI-powered business automation** using Elasticsearch as a dynamic skill repository. Any MCP or A2A-capable AI agent (Claude, ChatGPT, Gemini) discovers, retrieves, and executes proprietary business logic stored in Elasticsearch—enabling real-time updates to business rules without retraining or redeploying the AI.

**Key Innovation:** Skills are "hot-loaded" at runtime, allowing organizations to:
- Update business rules instantly (no AI retraining)
- Keep proprietary logic private (stored in your Elasticsearch, not in AI training data)
- Scale to thousands of domain-specific skills across multiple business units

**The Secret Sauce:** Skills are *authored* using frontier LLMs (Claude, Gemini) via single-shot prompts. Domain experts describe their business logic, policies, and proprietary knowledge in natural language—the LLM generates production-ready skill code. This democratizes skill creation: no developer required to codify expertise.

---

## Architecture Breakdown 1: High Level (CTO View)

This view shows the major system components and their relationships—suitable for executive presentations and strategic discussions.

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                              PRESENTATION LAYER                                 │
│                                                                                 │
│    ┌─────────────────────────────────────────────────────────────────────┐      │
│    │                                                                     │      │
│    │   OPTION A: Elastic Agent Builder (Native Kibana Experience)        │      │
│    │   ─────────────────────────────────────────────────────────────     │      │
│    │   • Built-in Kibana UI for agent interactions                       │      │ 
│    │   • Pre-configured MCP server with Elasticsearch tools              │      │
│    │   • Enterprise SSO and RBAC integration                             │      │
│    │                                                                     │      │
│    │   OPTION B: Any MCP/A2A-Capable Interface                           │      │
│    │   ─────────────────────────────────────────────────────────────     │      │
│    │   • Claude (Anthropic) — Claude Code, Claude Desktop, API           │      │
│    │   • ChatGPT (OpenAI) — via MCP bridge or A2A protocol               │      │
│    │   • Gemini (Google) — via MCP bridge or A2A protocol                │      │
│    │   • Custom agents — any MCP-compatible client                       │      │
│    │                                                                     │      │
│    └─────────────────────────────────────────────────────────────────────┘      │
│                                      │                                          │
│                   Model Context Protocol (MCP) / Agent-to-Agent (A2A)           │
│                                      │                                          │
└──────────────────────────────────────┼──────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                            INTEGRATION LAYER                                    │
│                                                                                 │
│    ┌─────────────────────────────────────────────────────────────────────┐      │
│    │                     Kibana Agent Builder                            │      │
│    │              (MCP Server + Tool Orchestration)                      │      │
│    │                                                                     │      │
│    │   • Exposes skill search/retrieval tools to any MCP client          │      │
│    │   • Manages authentication & access control                         │      │
│    │   • Executes ES|QL queries against Elasticsearch                    │      │
│    └─────────────────────────────────────────────────────────────────────┘      │
│                                                                                 │
│    ┌─────────────────────────────────────────────────────────────────────┐      │
│    │                     Elastic Workflows                               │      │
│    │              (Automation & Orchestration)                           │      │
│    │                                                                     │      │
│    │   • Skill setup/teardown operations                                 │      │
│    │   • Async job management with polling                               │      │
│    │   • CI/CD for skill updates                                         │      │
│    └─────────────────────────────────────────────────────────────────────┘      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                    ELASTIC SKILL REPOSITORY (Data Layer)                        │
│                                                                                 │
│    ┌─────────────────────────────────────────────────────────────────────┐      │
│    │                 Elasticsearch Serverless                            │      │
│    │                                                                     │      │
│    │   ┌───────────────────────────────────────────────────────────────┐ │      │
│    │   │                    SEARCH CAPABILITIES                        │ │      │
│    │   │                                                               │ │      │
│    │   │  ┌─────────────────┐  ┌─────────────────┐  ┌────────────────┐ │ │      │
│    │   │  │ KEYWORD SEARCH  │  │ METADATA FILTER │  │ SEMANTIC SEARCH│ │ │      │
│    │   │  │ ─────────────── │  │ ─────────────── │  │ ────────────── │ │ │      │
│    │   │  │ • Full-text     │  │ • Domain        │  │ • Jina v3      │ │ │      │
│    │   │  │   matching      │  │ • Tags          │  │   Embeddings   │ │ │      │
│    │   │  │ • BM25 ranking  │  │ • Author        │  │ • Vector       │ │ │      │
│    │   │  │ • Phrase search │  │ • Version       │  │   similarity   │ │ │      │
│    │   │  │                 │  │ • Rating        │  │ • Meaning-     │ │ │      │
│    │   │  │                 │  │ • Date ranges   │  │   based        │ │ │      │
│    │   │  └─────────────────┘  └─────────────────┘  └────────────────┘ │ │      │
│    │   │                                                               │ │      │
│    │   │         Hybrid Search: Combine all three for best results     │ │      │
│    │   └───────────────────────────────────────────────────────────────┘ │      │
│    │                                                                     │      │
│    │   ┌───────────────────────┐    ┌───────────────────────┐            │      │
│    │   │   agent_skills        │    │  agent_skill_files    │            │      │
│    │   │                       │    │                       │            │      │
│    │   │  • Skill metadata     │    │  • Python code        │            │      │
│    │   │  • Jina v3 embeddings │    │  • JSON configs       │            │      │ 
│    │   │  • Domain/tag indexes │    │  • CSV data files     │            │      │
│    │   │  • Usage analytics    │    │  • Business rules     │            │      │
│    │   └───────────────────────┘    └───────────────────────┘            │      │
│    │                                                                     │      │
│    └─────────────────────────────────────────────────────────────────────┘      │ 
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                      SKILL AUTHORING (The Secret Sauce)                         │
│                                                                                 │
│    ┌─────────────────────────────────────────────────────────────────────┐      │
│    │                                                                     │      │
│    │   Domain Expert + Frontier LLM = Production-Ready Skill             │      │
│    │                                                                     │      │
│    │   ┌─────────────┐      ┌─────────────────┐      ┌───────────────┐   │      │
│    │   │   DOMAIN    │      │   SINGLE-SHOT   │      │   INDEXED     │   │      │
│    │   │   EXPERT    │ ───> │   LLM PROMPT    │ ───> │   SKILL       │   │      │
│    │   │             │      │                 │      │               │   │      │
│    │   │ "Our expense│      │ Claude / Gemini │      │ Python code   │   │      │
│    │   │  policy is..│      │ generates:      │      │ JSON config   │   │      │
│    │   │  VP approval│      │ • Logic code    │      │ Business rules│   │      │
│    │   │  over $500" │      │ • Validations   │      │ Test cases    │   │      │
│    │   │             │      │ • Edge cases    │      │               │   │      │
│    │   └─────────────┘      └─────────────────┘      └───────────────┘   │      │
│    │                                                                     │      │
│    │   No developer required • Natural language input • Instant output   │      │
│    │                                                                     │      │
│    └─────────────────────────────────────────────────────────────────────┘      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
                                       │
                                       ▼
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                            SKILL LIBRARY                                        │
│                                                                                 │
│    ┌───────────────┐  ┌───────────────┐  ┌───────────────┐  ┌───────────────┐   │
│    │    Finance    │  │   Insurance   │  │ Life Sciences │  │   Technology  │   │
│    │               │  │               │  │               │  │               │   │
│    │ Expense Policy│  │ Storm Claims  │  │ Sample Viab.  │  │ Digital Trans.│   │
│    │ ROI Calc      │  │ Lease Eval    │  │ Lab Protocol  │  │ Tesla Q&A     │   │
│    │ Risk Analysis │  │ Coverage Adj. │  │ Quality Check │  │ IT Assessment │   │
│    └───────────────┘  └───────────────┘  └───────────────┘  └───────────────┘   │
│                                                                                 │
│                         100+ Pre-built Skills (Extensible)                      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Component Summary

| Layer | Component | Purpose |
|-------|-----------|---------|
| **Presentation** | Elastic Agent Builder (Option A) | Native Kibana UI for agent interactions |
| **Presentation** | MCP/A2A Clients (Option B) | Claude, ChatGPT, Gemini, or custom agents |
| **Integration** | Kibana Agent Builder MCP Server | Exposes Elasticsearch tools to any MCP client |
| **Integration** | Elastic Workflows | Orchestrates skill lifecycle (setup/update/teardown) |
| **Data** | Elasticsearch Skill Repository | Keyword search + Metadata filters + Semantic search (Jina v3) |
| **Authoring** | Frontier LLMs (Claude/Gemini) | Single-shot skill generation from natural language |
| **Library** | Skill Files | Proprietary business logic (Python, JSON, CSV) |

### Key Value Propositions

1. **Real-Time Skill Updates** — Add or modify business rules without AI retraining
2. **Proprietary Logic Stays Private** — Skills live in your Elasticsearch, not AI provider's models
3. **Triple-Mode Discovery** — Keyword search, metadata filters, AND semantic search (Jina v3)
4. **LLM-Powered Authoring** — Domain experts create skills via natural language prompts
5. **Multi-Model Support** — Works with Claude, ChatGPT, Gemini, or any MCP/A2A client
6. **Auditable Decisions** — Every decision traces back to specific business rules

---

## Architecture Breakdown 2: Detailed (Architect View)

This view provides technical depth for implementation planning, security reviews, and integration design.

### Detailed Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│                                   CLIENT LAYER                                           │
│                                                                                          │
│   ┌────────────────────────────────────────────────────────────────────────────────┐    │
│   │                        OPTION A: Elastic Agent Builder                          │    │
│   │                                                                                │    │
│   │   • Native Kibana UI — no external client needed                               │    │
│   │   • Pre-configured MCP tools for skill search/retrieval                        │    │
│   │   • Enterprise SSO integration (SAML, OIDC)                                    │    │
│   │   • Built-in conversation history and analytics                                 │    │
│   └────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│   ┌────────────────────────────────────────────────────────────────────────────────┐    │
│   │                   OPTION B: Any MCP/A2A-Capable Client                          │    │
│   │                                                                                │    │
│   │  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐              │    │
│   │  │ Claude (Anthropic)│  │ ChatGPT (OpenAI) │  │ Gemini (Google)  │              │    │
│   │  │ ────────────────  │  │ ────────────────  │  │ ────────────────  │              │    │
│   │  │ • Claude Code CLI │  │ • MCP Bridge     │  │ • MCP Bridge     │              │    │
│   │  │ • Claude Desktop  │  │ • A2A Protocol   │  │ • A2A Protocol   │              │    │
│   │  │ • Claude API      │  │ • Custom wrapper │  │ • Custom wrapper │              │    │
│   │  └──────────────────┘  └──────────────────┘  └──────────────────┘              │    │
│   │                                                                                │    │
│   │  Configuration: .mcp.json (or equivalent for each client)                      │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ mcpServers.elastic:                                                       │ │    │
│   │  │   type: "http"                                                            │ │    │
│   │  │   url: "${ELASTIC_MCP_URL}"  →  Kibana Agent Builder endpoint             │ │    │
│   │  │   headers: Authorization: ApiKey ${ELASTIC_API_KEY}                       │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   │                                                                                │    │
│   │  Agent Behavior (regardless of client):                                        │    │
│   │  • Startup: Checks if agent_skills index exists (via search_skills)           │    │
│   │  • Discovery: Keyword + metadata + semantic search for relevant skills         │    │
│   │  • Retrieval: Fetches full skill files (Python/JSON/CSV)                       │    │
│   │  • Execution: Interprets and applies business logic from skill files           │    │
│   │  • Response: Formats results in markdown with actionable recommendations       │    │
│   └────────────────────────────────────────────────────────────────────────────────┘    │
│                                           │                                              │
│                         MCP Protocol (HTTP) or A2A Protocol                              │
│                              Authorization: ApiKey ...                                   │
│                                           │                                              │
└───────────────────────────────────────────┼──────────────────────────────────────────────┘
                                            │
                                            ▼
┌──────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                          │
│                            KIBANA AGENT BUILDER LAYER                                    │
│                                                                                          │
│   Endpoint: /api/agent_builder/mcp                                                       │
│                                                                                          │
│   ┌────────────────────────────────────────────────────────────────────────────────┐    │
│   │                              MCP TOOLS (5 Tools)                                │    │
│   │                                                                                │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ search_skills                                                             │ │    │
│   │  │ Query: FROM agent_skills METADATA _score                                  │ │    │
│   │  │        WHERE name:?q OR description:?q OR semantic_content:?q             │ │    │
│   │  │        SORT _score DESC LIMIT ?limit                                      │ │    │
│   │  │ Purpose: Semantic + full-text search across all skills                    │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   │                                                                                │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ get_skill_files                                                           │ │    │
│   │  │ Query: FROM agent_skill_files WHERE skill_id == ?skill_id                 │ │    │
│   │  │ Purpose: Retrieve Python code, JSON configs, CSV data for execution       │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   │                                                                                │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ list_skills_by_domain                                                     │ │    │
│   │  │ Query: FROM agent_skills WHERE domain == ?domain SORT rating DESC         │ │    │
│   │  │ Purpose: List all skills in a domain (finance, insurance, etc.)           │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   │                                                                                │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ get_skill_metadata                                                        │ │    │
│   │  │ Query: FROM agent_skills WHERE skill_id == ?skill_id (lightweight)        │ │    │
│   │  │ Purpose: Quick metadata lookup without full content                        │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   │                                                                                │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ search_skills_by_tags                                                     │ │    │
│   │  │ Query: FROM agent_skills WHERE tags_str RLIKE ?tag                        │ │    │
│   │  │ Purpose: Regex pattern matching on skill tags                              │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   │                                                                                │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ consultant_skills_operator (Workflow Tool)                                │ │    │
│   │  │ Operations: setup | teardown | update-skills                              │ │    │
│   │  │ Purpose: Lifecycle management for skill indexes                           │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   └────────────────────────────────────────────────────────────────────────────────┘    │
│                                                                                          │
│   ┌────────────────────────────────────────────────────────────────────────────────┐    │
│   │                       ELASTIC WORKFLOWS ENGINE                                  │    │
│   │                                                                                │    │
│   │  Workflow: consultant_skills_operator                                          │    │
│   │  ┌──────────────────────────────────────────────────────────────────────────┐ │    │
│   │  │ Step 1: POST to Data Operations API (start async job)                    │ │    │
│   │  │         /api/v1/ops/{operation}  →  Returns job_id                       │ │    │
│   │  │                                                                          │ │    │
│   │  │ Step 2: Poll Loop (max 30 iterations, 10s interval)                      │ │    │
│   │  │         GET /api/v1/jobs/{job_id}                                        │ │    │
│   │  │         Continue while status == "IN_PROGRESS"                           │ │    │
│   │  │                                                                          │ │    │
│   │  │ Step 3: Return final result                                              │ │    │
│   │  │         COMPLETED: indexes created/deleted, skills count                 │ │    │
│   │  │         FAILED: error details                                            │ │    │
│   │  └──────────────────────────────────────────────────────────────────────────┘ │    │
│   └────────────────────────────────────────────────────────────────────────────────┘    │
│                                           │                                              │
└───────────────────────────────────────────┼──────────────────────────────────────────────┘
                                            │
              ┌─────────────────────────────┼─────────────────────────────┐
              │                             │                             │
              ▼                             ▼                             ▼
┌───────────────────────────────────────────────────────────────────────────────────────────┐
│                         ELASTIC SKILL REPOSITORY (Elasticsearch Serverless)               │
│                                                                                           │
│   ┌─────────────────────────────────────────────────────────────────────────────────────┐│
│   │                          THREE-MODE SEARCH ARCHITECTURE                              ││
│   │                                                                                      ││
│   │  ┌─────────────────────┐  ┌─────────────────────┐  ┌─────────────────────────────┐ ││
│   │  │   KEYWORD SEARCH    │  │   METADATA FILTERS  │  │     SEMANTIC SEARCH         │ ││
│   │  │   ─────────────────  │  │   ─────────────────  │  │     ───────────────────     │ ││
│   │  │                     │  │                     │  │                             │ ││
│   │  │  • Full-text match  │  │  • domain == ?      │  │  Jina Embeddings v3         │ ││
│   │  │  • BM25 scoring     │  │  • tags CONTAINS ?  │  │  ─────────────────────────  │ ││
│   │  │  • Phrase queries   │  │  • author == ?      │  │  • 1024-dim dense vectors  │ ││
│   │  │  • Wildcards        │  │  • version == ?     │  │  • Multilingual support    │ ││
│   │  │  • Fuzzy matching   │  │  • rating >= ?      │  │  • semantic_text field     │ ││
│   │  │                     │  │  • created_at range │  │  • Cosine similarity       │ ││
│   │  │  ES|QL: name:?q     │  │                     │  │  • Meaning-based ranking   │ ││
│   │  │  description:?q     │  │  ES|QL: WHERE       │  │                             │ ││
│   │  │                     │  │  domain == ?domain  │  │  ES|QL: semantic_content:?q│ ││
│   │  └─────────────────────┘  └─────────────────────┘  └─────────────────────────────┘ ││
│   │                                                                                      ││
│   │  Hybrid Query: Combine all three for optimal relevance scoring                       ││
│   └─────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                           │
│   ┌───────────────────────────┐    ┌───────────────────────────┐                         │
│   │   agent_skills Index      │    │   agent_skill_files Index │                         │
│   │   ───────────────────     │    │   ───────────────────────  │                         │
│   │   skill_id (keyword)      │    │   skill_id (keyword)      │                         │
│   │   name (text+keyword)     │    │   file_name (keyword)     │                         │
│   │   description (text)      │    │   file_path (keyword)     │                         │
│   │   domain (keyword)        │    │   file_type (keyword)     │                         │
│   │   tags (keyword[])        │    │   file_content (text)     │                         │
│   │   semantic_content        │    │   file_size_bytes (long)  │                         │
│   │     (semantic_text)       │    │                           │                         │
│   │   rating (float)          │    │   Stores: Python code,    │                         │
│   │   usage_count (long)      │    │   JSON configs, CSV data  │                         │
│   │   success_rate (float)    │    │                           │                         │
│   └───────────────────────────┘    └───────────────────────────┘                         │
│                                                                                           │
└───────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────────────────────────────────┐
│                              SKILL AUTHORING LAYER (Secret Sauce)                           │
│                                                                                             │
│   ┌───────────────────────────────────────────────────────────────────────────────────────┐│
│   │                        SINGLE-SHOT LLM SKILL GENERATION                               ││
│   │                                                                                       ││
│   │   ┌───────────────────┐         ┌───────────────────┐         ┌───────────────────┐  ││
│   │   │   DOMAIN EXPERT   │         │   FRONTIER LLM    │         │  PRODUCTION SKILL │  ││
│   │   │   ───────────────  │  ────>  │   ────────────── │  ────>  │  ────────────────  │  ││
│   │   │                   │         │                   │         │                   │  ││
│   │   │ Natural language  │         │ Claude Opus/Sonnet│         │ SKILL.md          │  ││
│   │   │ description of:   │         │ Gemini Pro/Ultra  │         │ policy_check.py   │  ││
│   │   │                   │         │                   │         │ config.json       │  ││
│   │   │ • Business rules  │         │ Generates:        │         │ thresholds.csv    │  ││
│   │   │ • Edge cases      │         │ • Logic code      │         │ test_cases.py     │  ││
│   │   │ • Approval flows  │         │ • Validations     │         │                   │  ││
│   │   │ • Thresholds      │         │ • Error handling  │         │ Ready to index    │  ││
│   │   │ • Exceptions      │         │ • Test coverage   │         │ in Elasticsearch  │  ││
│   │   └───────────────────┘         └───────────────────┘         └───────────────────┘  ││
│   │                                                                                       ││
│   │   Example Prompt:                                                                     ││
│   │   "Create a skill that validates expense reports. VP approval required over $500.    ││
│   │    Team dinners capped at $75/head. Software purchases need procurement ticket."     ││
│   │                                                                                       ││
│   │   → LLM outputs complete, tested, production-ready skill in seconds                  ││
│   │                                                                                       ││
│   └───────────────────────────────────────────────────────────────────────────────────────┘│
│                                                                                             │
└─────────────────────────────────────────────────────────────────────────────────────────────┘

┌─────────────────────────┐  ┌─────────────────────────┐
│   DATA OPERATIONS API   │  │     SKILL SOURCES       │
│                         │  │                         │
│  FastAPI + Uvicorn      │  │  /sample_skills/        │
│                         │  │  ├── verify-expense-    │
│  Endpoints:             │  │  │   policy/            │
│  POST /ops/setup        │  │  │   ├── SKILL.md       │
│  POST /ops/teardown     │  │  │   ├── policy_check.py│
│  POST /ops/update-skills│  │  │   └── *.json/*.csv   │
│  GET  /jobs             │  │  ├── adjudicate-storm-  │
│  GET  /jobs/{id}        │  │  │   claim/             │
│  GET  /health           │  │  ├── validate-sample-   │
│                         │  │  │   viability/         │
│  Auth: X-API-Key header │  │  └── 97+ more skills... │
│                         │  │                         │
│  Job System:            │  │  /new_skills/           │
│  • Async background     │  │  └── tesla/             │
│    execution            │  │      ├── SKILL.md       │
│  • In-memory tracking   │  │      └── company_qa.py  │
│  • Thread-safe locks    │  │                         │
│  • Status polling       │  │  Ingestion:             │
│                         │  │  scripts/ingest_skills  │
│  Ingestion Process:     │  │    .py                  │
│  1. Parse SKILL.md      │  │                         │
│  2. Extract metadata    │  │  Per-Skill Structure:   │
│  3. Collect all files   │  │  • SKILL.md (metadata)  │
│  4. Bulk index to ES    │  │  • *.py (logic)         │
│                         │  │  • *.json (config)      │
│                         │  │  • *.csv (data)         │
│                         │  │                         │
└─────────────────────────┘  └─────────────────────────┘
```

### Data Flow Sequence

```
┌─────────┐     ┌─────────────┐     ┌───────────────────┐     ┌───────────────────┐
│  User   │     │ AI Client   │     │ Kibana Agent      │     │ Elastic Skill     │
│         │     │ (Any MCP/   │     │ Builder (MCP)     │     │ Repository        │
│         │     │  A2A Client)│     │                   │     │                   │
└────┬────┘     └──────┬──────┘     └─────────┬─────────┘     └─────────┬─────────┘
     │                 │                      │                         │
     │  "Check if my   │                      │                         │
     │   $850 expense  │                      │                         │
     │   is allowed"   │                      │                         │
     │ ───────────────>│                      │                         │
     │                 │                      │                         │
     │  Client can be: │                      │                         │
     │  • Agent Builder│                      │                         │
     │  • Claude       │                      │                         │
     │  • ChatGPT      │                      │                         │
     │  • Gemini       │                      │                         │
     │                 │                      │                         │
     │                 │  search_skills       │                         │
     │                 │  query: "expense     │                         │
     │                 │   policy approval"   │                         │
     │                 │ ────────────────────>│                         │
     │                 │                      │                         │
     │                 │                      │  TRIPLE-MODE SEARCH:    │
     │                 │                      │  ──────────────────────│
     │                 │                      │  1. Keyword: name:?q   │
     │                 │                      │  2. Metadata: domain=? │
     │                 │                      │  3. Semantic: Jina v3  │
     │                 │                      │     semantic_content:?q│
     │                 │                      │ ───────────────────────>│
     │                 │                      │                         │
     │                 │                      │  [skill_id: verify-     │
     │                 │                      │   expense-policy,       │
     │                 │                      │   score: 0.92]          │
     │                 │                      │ <───────────────────────│
     │                 │                      │                         │
     │                 │  Results: verify-    │                         │
     │                 │  expense-policy      │                         │
     │                 │ <────────────────────│                         │
     │                 │                      │                         │
     │                 │  get_skill_files     │                         │
     │                 │  skill_id: verify-   │                         │
     │                 │  expense-policy      │                         │
     │                 │ ────────────────────>│                         │
     │                 │                      │                         │
     │                 │                      │  ES|QL: FROM agent_     │
     │                 │                      │  skill_files WHERE      │
     │                 │                      │  skill_id == ?          │
     │                 │                      │ ───────────────────────>│
     │                 │                      │                         │
     │                 │                      │  [policy_check.py,      │
     │                 │                      │   allowance_table.json, │
     │                 │                      │   category_limits.csv]  │
     │                 │                      │ <───────────────────────│
     │                 │                      │                         │
     │                 │  Files: Python code  │                         │
     │                 │  + configs + data    │                         │
     │                 │ <────────────────────│                         │
     │                 │                      │                         │
     │                 │ ┌──────────────────┐ │                         │
     │                 │ │ AI interprets    │ │                         │
     │                 │ │ business rules:  │ │                         │
     │                 │ │ • VP approval    │ │                         │
     │                 │ │   >$500          │ │                         │
     │                 │ │ • Team dinner    │ │                         │
     │                 │ │   $75/head cap   │ │                         │
     │                 │ └──────────────────┘ │                         │
     │                 │                      │                         │
     │  "Not compliant:│                      │                         │
     │   VP approval   │                      │                         │
     │   required for  │                      │                         │
     │   amounts >$500"│                      │                         │
     │ <───────────────│                      │                         │
     │                 │                      │                         │
```

### Index Mapping Details

#### agent_skills Index

```json
{
  "mappings": {
    "properties": {
      "skill_id": { "type": "keyword" },
      "name": {
        "type": "text",
        "fields": { "keyword": { "type": "keyword" } },
        "copy_to": "semantic_content"
      },
      "description": {
        "type": "text",
        "analyzer": "english",
        "copy_to": "semantic_content"
      },
      "short_description": {
        "type": "text",
        "copy_to": "semantic_content"
      },
      "domain": { "type": "keyword" },
      "tags": { "type": "keyword" },
      "author": { "type": "keyword" },
      "version": { "type": "keyword" },
      "rating": { "type": "float" },
      "semantic_content": {
        "type": "semantic_text",
        "inference_id": "jina-embeddings-v3"
      },
      "execution_mode": { "type": "keyword" },
      "requires_elasticsearch": { "type": "boolean" },
      "usage_count": { "type": "long" },
      "success_rate": { "type": "float" },
      "avg_execution_time_ms": { "type": "long" },
      "created_at": { "type": "date" },
      "updated_at": { "type": "date" }
    }
  }
}
```

#### agent_skill_files Index

```json
{
  "mappings": {
    "properties": {
      "skill_id": { "type": "keyword" },
      "file_name": { "type": "keyword" },
      "file_path": { "type": "keyword" },
      "file_type": { "type": "keyword" },
      "file_content": { "type": "text", "index": false },
      "file_size_bytes": { "type": "long" },
      "created_at": { "type": "date" }
    }
  }
}
```

### Security Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                          ENTERPRISE SECURITY ARCHITECTURE                               │
│                                                                                         │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │                         DEFENSE IN DEPTH (7 LAYERS)                               │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  Layer 1: NETWORK SECURITY                                                              │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  • TLS 1.3 encryption for all data in transit                                     │  │
│  │  • IP allowlisting for API access                                                 │  │
│  │  • DDoS protection via Elastic Cloud infrastructure                               │  │
│  │  • WAF integration for web-based access                                           │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  Layer 2: IDENTITY & ACCESS MANAGEMENT                                                  │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  • Enterprise SSO integration (SAML 2.0, OIDC)                                    │  │
│  │  • Multi-factor authentication (MFA) enforcement                                  │  │
│  │  • API key authentication with scoped permissions                                 │  │
│  │  • Service account isolation for programmatic access                              │  │
│  │  • Session management with configurable timeouts                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  Layer 3: AUTHORIZATION & ACCESS CONTROL                                                │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  • Role-Based Access Control (RBAC) at index and field level                      │  │
│  │  • Document-level security (DLS) for skill isolation by domain                    │  │
│  │  • Field-level security (FLS) to mask sensitive skill content                     │  │
│  │  • Attribute-Based Access Control (ABAC) via custom roles                         │  │
│  │  • Principle of least privilege enforced                                          │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  Layer 4: DATA PROTECTION                                                               │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  • AES-256 encryption at rest (customer-managed keys available)                   │  │
│  │  • TLS 1.3 encryption in transit (no plaintext transmission)                      │  │ 
│  │  • Secrets management via environment variables (never in code/logs)              │  │
│  │  • PII detection and redaction capabilities                                       │  │
│  │  • Data classification tagging for sensitive skills                               │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  Layer 5: APPLICATION SECURITY                                                          │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  • ES|QL parameterized queries (prevents injection attacks)                       │  │
│  │  • Input validation and sanitization on all API endpoints                         │  │
│  │  • Type-safe parameter binding (no raw query construction)                        │  │
│  │  • Content Security Policy (CSP) headers                                          │  │
│  │  • Rate limiting and throttling on API endpoints                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  Layer 6: AUDIT & MONITORING                                                            │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  • Comprehensive audit logging (who, what, when, where)                           │  │
│  │  • Real-time security monitoring via Elastic Security                             │  │
│  │  • Anomaly detection for unusual access patterns                                  │  │
│  │  • SIEM integration for centralized security operations                           │  │
│  │  • Immutable audit trail for compliance evidence                                  │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
│  Layer 7: DATA SOVEREIGNTY & COMPLIANCE                                                 │
│  ┌───────────────────────────────────────────────────────────────────────────────────┐  │
│  │  • Data residency controls (choose deployment region)                             │  │
│  │  • Skills and business logic remain in YOUR Elasticsearch                         │  │
│  │  • No training data sent to AI providers (hot-loading only)                       │  │
│  │  • Data retention policies with automated lifecycle management                    │  │
│  │  • Cross-border data transfer controls                                            │  │
│  └───────────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Security Controls Summary

| Control Area | Implementation | Elastic Capability |
|--------------|----------------|-------------------|
| **Authentication** | API Keys, SAML, OIDC, MFA | Native + SSO integration |
| **Authorization** | RBAC, DLS, FLS, ABAC | Elasticsearch Security |
| **Encryption (Transit)** | TLS 1.3 | Enforced by default |
| **Encryption (Rest)** | AES-256 | Customer-managed keys available |
| **Audit Logging** | All access logged | Elastic audit logs |
| **Injection Prevention** | Parameterized ES|QL | Built into query layer |
| **Secret Management** | Env vars, Kibana Secure Settings | No secrets in code |
| **Data Residency** | Region selection | 30+ global regions |
| **Monitoring** | Real-time alerting | Elastic Security SIEM |

### Compliance Considerations

| Framework | Relevant Controls | Notes |
|-----------|-------------------|-------|
| **SOC 2 Type II** | Access control, encryption, audit logs | Elastic Cloud certified |
| **GDPR** | Data residency, right to erasure, DPAs | EU regions available |
| **HIPAA** | Encryption, audit trails, BAA | Healthcare BAA available |
| **FedRAMP** | Authorized at Moderate level | Government deployments |
| **ISO 27001** | Information security management | Elastic Cloud certified |
| **PCI DSS** | Encryption, access control, monitoring | For financial data |

### Data Flow Security

```
┌─────────────────────────────────────────────────────────────────────────────────────────┐
│                                                                                         │
│                            SECURE DATA FLOW                                             │
│                                                                                         │
│   ┌─────────────┐     TLS 1.3      ┌─────────────┐    Internal     ┌─────────────────┐ │
│   │             │  ──────────────> │             │  ────────────>  │                 │ │
│   │  AI Client  │   API Key Auth   │   Kibana    │   RBAC + DLS    │  Elasticsearch  │ │
│   │             │  <────────────── │   (MCP)     │  <────────────  │                 │ │
│   └─────────────┘     Encrypted    └─────────────┘    Encrypted    └─────────────────┘ │
│         │                                │                                │             │
│         │                                │                                │             │
│         ▼                                ▼                                ▼             │
│   ┌─────────────┐                 ┌─────────────┐                 ┌─────────────────┐ │
│   │ Audit Log   │                 │ Audit Log   │                 │ Audit Log       │ │
│   │ (Client)    │                 │ (Kibana)    │                 │ (ES)            │ │
│   └─────────────┘                 └─────────────┘                 └─────────────────┘ │
│                                                                                         │
│   KEY SECURITY PROPERTIES:                                                              │
│   ✓ No plaintext credentials in transit                                                │
│   ✓ No skill content sent to AI training                                               │
│   ✓ All access logged with user attribution                                            │
│   ✓ Skills isolated by domain via document-level security                             │
│   ✓ API keys scoped to minimum required permissions                                    │
│                                                                                         │
└─────────────────────────────────────────────────────────────────────────────────────────┘
```

### Environment Configuration

```bash
# Required Environment Variables (stored securely, never committed to code)
ELASTIC_SEARCH_URL=https://<deployment>.es.us-east-1.aws.elastic.cloud
ELASTIC_API_KEY=<base64-encoded-api-key>          # Scoped to agent_skills* indices only
KIBANA_URL=https://<deployment>.kb.us-east-1.aws.elastic.cloud
ELASTIC_MCP_URL=https://<deployment>.kb.us-east-1.aws.elastic.cloud/api/agent_builder/mcp
API_SERVICE_KEY=<service-key-for-data-ops-api>    # Rotated regularly

# Security Best Practices:
# • Store secrets in vault (HashiCorp Vault, AWS Secrets Manager, etc.)
# • Rotate API keys on regular schedule (90 days recommended)
# • Use separate API keys for development, staging, production
# • Enable MFA for all human users accessing Kibana
# • Configure IP allowlists for production API access
```

---

## Demo for Dummies (Business View)

This simplified view is designed for Account Executives and Business Analysts who need to explain the value proposition without technical complexity.

### The Simple Story

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│                         "SMART AI THAT KNOWS YOUR RULES"                        │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │     👤 Business User                                                    │   │
│  │        "Is my $850 expense report compliant?"                          │   │
│  │                                                                         │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │     🤖 Any AI Assistant (Claude, ChatGPT, Gemini, etc.)                │   │
│  │        "Let me check your company's expense policy..."                 │   │
│  │                                                                         │   │
│  │     Access via:                                                         │   │
│  │     • Elastic Agent Builder (built into Kibana)                        │   │
│  │     • Claude Desktop / Claude Code                                      │   │
│  │     • ChatGPT with MCP plugin                                           │   │
│  │     • Gemini with MCP bridge                                            │   │
│  │                                                                         │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│                           🔍 Triple-Mode Search                                 │
│                              (Keywords + Filters + AI Understanding)            │
│                                   │                                             │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │     📚 ELASTIC SKILL REPOSITORY                                        │   │
│  │                                                                         │   │
│  │     ┌───────────────────────────────────────────────────────────────┐  │   │
│  │     │              THREE WAYS TO FIND SKILLS                        │  │   │
│  │     │                                                               │  │   │
│  │     │  🔤 KEYWORDS     🏷️ FILTERS      🧠 SEMANTIC (Jina v3)       │  │   │
│  │     │  "expense"      domain=finance  "check if my dinner         │  │   │
│  │     │  "policy"       tags=approval    bill is allowed"           │  │   │
│  │     │  "VP approval"  author=CFO                                   │  │   │
│  │     └───────────────────────────────────────────────────────────────┘  │   │
│  │                                                                         │   │
│  │     ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐ │   │
│  │     │  FINANCE    │  │  INSURANCE  │  │   LEGAL     │  │     HR      │ │   │
│  │     │  ─────────  │  │  ─────────  │  │  ────────   │  │  ────────   │ │   │
│  │     │ ✓ Expenses  │  │ ✓ Claims    │  │ ✓ Contracts │  │ ✓ Policies  │ │   │
│  │     │ ✓ Budgets   │  │ ✓ Coverage  │  │ ✓ Compliance│  │ ✓ Benefits  │ │   │
│  │     │ ✓ Approvals │  │ ✓ Risk      │  │ ✓ Reviews   │  │ ✓ Onboarding│ │   │
│  │     └─────────────┘  └─────────────┘  └─────────────┘  └─────────────┘ │   │
│  │                                                                         │   │
│  └────────────────────────────────────────────────────────────────────────┘   │
│                                   │                                             │
│                           📄 Finds & loads                                      │
│                              expense rules                                      │
│                                   │                                             │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │     ✅ AI Response                                                      │   │
│  │                                                                         │   │
│  │     "Your expense needs VP approval because:                           │   │
│  │      • Amount ($850) exceeds $500 threshold                            │   │
│  │      • Team dinners capped at $75/person                               │   │
│  │                                                                         │   │
│  │      Recommendation: Get VP sign-off before submitting"                │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### The Secret Sauce: How Skills Get Created

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│              SINGLE-SHOT SKILL GENERATION (No Developer Required)               │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │   👩‍💼 Domain Expert (CFO, Policy Owner, Subject Matter Expert)          │   │
│  │                                                                         │   │
│  │   "Our expense policy works like this:                                 │   │
│  │    - Any expense over $500 needs VP approval                           │   │
│  │    - Team dinners are capped at $75 per person                         │   │
│  │    - Software purchases require a procurement ticket                   │   │
│  │    - Travel needs pre-approval from manager"                           │   │
│  │                                                                         │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │   🧠 Frontier LLM (Claude or Gemini)                                   │   │
│  │                                                                         │   │
│  │   Takes the natural language description and generates:                │   │
│  │   ✓ Working Python code with all business logic                       │   │
│  │   ✓ Configuration files with thresholds                               │   │
│  │   ✓ Validation rules and error messages                               │   │
│  │   ✓ Edge case handling                                                 │   │
│  │   ✓ Test cases to verify correctness                                   │   │
│  │                                                                         │   │
│  └────────────────────────────────┬────────────────────────────────────────┘   │
│                                   │                                             │
│                                   ▼                                             │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │   📦 Production-Ready Skill (Indexed in Elasticsearch)                 │   │
│  │                                                                         │   │
│  │   verify-expense-policy/                                               │   │
│  │   ├── SKILL.md          (metadata, instructions)                       │   │
│  │   ├── policy_check.py   (business logic)                               │   │
│  │   ├── thresholds.json   (configurable limits)                          │   │
│  │   └── test_policy.py    (validation tests)                             │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│   💡 Key Insight: Domain experts codify their knowledge WITHOUT writing code   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Why This Matters: 4 Key Benefits

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  1️⃣  YOUR RULES, YOUR CONTROL                                           │   │
│  │                                                                         │   │
│  │      ❌ Old Way: AI trained on generic data, doesn't know YOUR policies │   │
│  │      ✅ New Way: AI reads YOUR business rules stored in Elasticsearch   │   │
│  │                                                                         │   │
│  │      "The AI knows that OUR expense limit is $500,                     │   │
│  │       not some generic industry standard"                              │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  2️⃣  INSTANT UPDATES                                                    │   │
│  │                                                                         │   │
│  │      ❌ Old Way: Retrain AI model (weeks/months, expensive)             │   │
│  │      ✅ New Way: Update Elasticsearch document (minutes, free)         │   │
│  │                                                                         │   │
│  │      "Changed our policy last week? The AI knows immediately"          │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  3️⃣  NO DEVELOPER REQUIRED (Secret Sauce!)                              │   │
│  │                                                                         │   │
│  │      ❌ Old Way: Developers translate business rules into code          │   │
│  │      ✅ New Way: Domain experts describe rules → LLM generates code    │   │
│  │                                                                         │   │
│  │      "The CFO describes the policy, Claude writes the skill"          │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │  4️⃣  FULLY AUDITABLE                                                    │   │
│  │                                                                         │   │
│  │      ❌ Old Way: AI "black box" - can't explain decisions               │   │
│  │      ✅ New Way: Every decision traces to specific rules in Elasticsearch│   │
│  │                                                                         │   │
│  │      "Auditors can see exactly which rule triggered the denial"        │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### Demo Happy Path (What You'll See)

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│  STEP 1: "What skills do you have?"                                            │
│  ────────────────────────────────────────────────────────────────────          │
│  AI discovers available skills in the library                                   │
│                                                                                 │
│                                    ▼                                            │
│                                                                                 │
│  STEP 2: "Run setup from the workflow"                                         │
│  ────────────────────────────────────────────────────────────────────          │
│  System loads 100+ business skills into Elasticsearch                          │
│                                                                                 │
│                                    ▼                                            │
│                                                                                 │
│  STEP 3: "Do you have a Tesla skill?"                                          │
│  ────────────────────────────────────────────────────────────────────          │
│  AI: "No, but I can update my skills..."                                       │
│                                                                                 │
│                                    ▼                                            │
│                                                                                 │
│  STEP 4: "Update your skills"                                                  │
│  ────────────────────────────────────────────────────────────────────          │
│  🔄 System hot-loads new Tesla skill in real-time                              │
│                                                                                 │
│                                    ▼                                            │
│                                                                                 │
│  STEP 5: "Compare Tesla vs Ford digital transformation"                        │
│  ────────────────────────────────────────────────────────────────────          │
│  AI uses MULTIPLE skills together:                                             │
│  • Tesla company profile skill (for Tesla data)                                │
│  • Digital transformation assessment skill (for comparison)                    │
│                                                                                 │
│                                    ▼                                            │
│                                                                                 │
│  RESULT: Comprehensive comparison with actionable insights                     │
│  ────────────────────────────────────────────────────────────────────          │
│  "Tesla scores 78/100, Ford scores 52/100. Here's a roadmap for Ford..."      │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

### One-Slide Summary

```
┌─────────────────────────────────────────────────────────────────────────────────┐
│                                                                                 │
│         ELASTIC + ANY AI: INTELLIGENCE THAT KNOWS YOUR BUSINESS                │
│                                                                                 │
│  ┌─────────────────────────────────────────────────────────────────────────┐   │
│  │                                                                         │   │
│  │                          THE ARCHITECTURE                               │   │
│  │                                                                         │   │
│  │  ┌───────────────────┐                        ┌───────────────────┐    │   │
│  │  │    SKILL          │                        │   ELASTIC SKILL   │    │   │
│  │  │    AUTHORING      │                        │   REPOSITORY      │    │   │
│  │  │                   │                        │                   │    │   │
│  │  │  Domain Expert    │                        │  Keyword Search   │    │   │
│  │  │       +           │  ─── indexes ───────>  │  Metadata Filters │    │   │
│  │  │  Claude/Gemini    │                        │  Semantic (Jina)  │    │   │
│  │  │                   │                        │                   │    │   │
│  │  └───────────────────┘                        └─────────┬─────────┘    │   │
│  │                                                         │              │   │
│  │  ┌───────────────────┐                                  │              │   │
│  │  │  USER ASKS        │                                  │              │   │
│  │  │  ────────────     │                    ┌─────────────┘              │   │
│  │  │  "Is my expense   │                    │                            │   │
│  │  │   compliant?"     │                    ▼                            │   │
│  │  └─────────┬─────────┘          ┌───────────────────┐                  │   │
│  │            │                    │   AI FINDS &      │                  │   │
│  │            └──────────────────> │   EXECUTES SKILL  │                  │   │
│  │                                 │                   │                  │   │
│  │      Any MCP/A2A Client:        │  Agent Builder    │                  │   │
│  │      Claude, ChatGPT, Gemini    │  Claude, ChatGPT  │                  │   │
│  │                                 │  Gemini, etc.     │                  │   │
│  │                                 └─────────┬─────────┘                  │   │
│  │                                           │                            │   │
│  │                                           ▼                            │   │
│  │                                 ┌───────────────────┐                  │   │
│  │                                 │  ANSWERS WITH     │                  │   │
│  │                                 │  YOUR RULES       │                  │   │
│  │                                 └───────────────────┘                  │   │
│  │                                                                         │   │
│  └─────────────────────────────────────────────────────────────────────────┘   │
│                                                                                 │
│  KEY DIFFERENTIATORS:                                                          │
│                                                                                 │
│  ✓ Domain experts create skills via single-shot LLM prompts (no dev needed)   │
│  ✓ Triple search: Keywords + Metadata filters + Semantic (Jina v3 vectors)    │
│  ✓ Works with ANY AI: Claude, ChatGPT, Gemini via MCP/A2A protocols           │
│  ✓ 100+ pre-built skills across Finance, Insurance, Life Sciences             │
│  ✓ Update rules in minutes (no AI retraining)                                  │
│  ✓ Full audit trail for compliance                                             │
│                                                                                 │
└─────────────────────────────────────────────────────────────────────────────────┘
```

---

## Technical Reference

### Component Inventory

| Component | Technology | Location | Purpose |
|-----------|------------|----------|---------|
| **Presentation Layer** | | | |
| Elastic Agent Builder | Kibana Native UI | Elastic Cloud | Built-in agent interface (Option A) |
| MCP/A2A Clients | Claude, ChatGPT, Gemini | External | Any compatible AI client (Option B) |
| **Integration Layer** | | | |
| MCP Server | Kibana Agent Builder API | Elastic Cloud | Tool orchestration & auth |
| Elastic Workflows | YAML-based automation | Kibana | Lifecycle management |
| **Data Layer (Skill Repository)** | | | |
| Keyword Search | BM25 full-text | Elasticsearch | Traditional text matching |
| Metadata Filters | ES|QL WHERE clauses | Elasticsearch | Domain, tags, author, rating filters |
| Semantic Search | Jina v3 Embeddings | Elasticsearch | Meaning-based vector similarity |
| Skill Storage | agent_skills index | Elasticsearch | Skill metadata + embeddings |
| File Storage | agent_skill_files index | Elasticsearch | Python/JSON/CSV code |
| **Authoring Layer** | | | |
| Skill Generator | Claude/Gemini LLM | External | Single-shot skill creation |
| **Operations** | | | |
| Data Ops API | FastAPI + Uvicorn | Customer-hosted | Skill ingestion |
| Skill Sources | Python files | Git repository | Business logic |

### Search Architecture

| Search Mode | Technology | Use Case | Example Query |
|-------------|------------|----------|---------------|
| **Keyword** | BM25 full-text | Exact term matching | `name:expense OR description:approval` |
| **Metadata** | ES|QL filters | Category/attribute filtering | `WHERE domain == "finance" AND rating >= 4.0` |
| **Semantic** | Jina v3 (1024-dim) | Meaning-based discovery | `semantic_content:"check if dinner bill is allowed"` |
| **Hybrid** | All three combined | Best overall relevance | Combines all modes with score fusion |

### Skill Authoring Pipeline

| Step | Actor | Input | Output |
|------|-------|-------|--------|
| 1. Describe | Domain Expert | Natural language rules | Prompt text |
| 2. Generate | Claude/Gemini | Prompt text | Skill files (Python, JSON, CSV) |
| 3. Review | Domain Expert | Generated code | Approved skill |
| 4. Index | Ingestion Script | Skill directory | Elasticsearch documents |
| 5. Deploy | Elastic Workflows | Index operation | Live skill available |

### Domain Coverage

| Domain | Example Skills | Use Cases |
|--------|----------------|-----------|
| Finance | verify-expense-policy, calculate-roi | Expense compliance, financial analysis |
| Insurance | adjudicate-storm-claim, evaluate-lease | Claims processing, risk assessment |
| Life Sciences | validate-sample-viability | Lab protocols, quality control |
| Technology | assess-digital-transformation | IT strategy, readiness assessments |
| Automotive | tesla-company-qa | Company research, competitor analysis |

### Key Metrics (Demo Stats)

- **Pre-built Skills:** 100+
- **Supported Domains:** 5+
- **Skill Discovery:** Keyword + Metadata + Semantic (Jina v3)
- **Vector Dimensions:** 1024 (Jina embeddings v3)
- **Update Latency:** Real-time (no AI retraining)
- **Query Language:** ES|QL (parameterized, type-safe)
- **Supported Clients:** Claude, ChatGPT, Gemini, any MCP/A2A client
- **Skill Authoring:** Single-shot LLM generation (Claude/Gemini)

---

## Appendix: File Structure

```
elastic-claude-agent-skill-demo/
├── .mcp.json                          # MCP server configuration
├── .env                               # Environment variables (not committed)
├── DEMO_SCRIPT.md                     # Demo walkthrough with scenarios
├── DEMO_ARCHITECTURE.md               # This file
├── README.md                          # Setup instructions
│
├── api/                               # Data Operations API
│   ├── main.py                        # FastAPI application
│   ├── auth.py                        # Authentication middleware
│   └── routes/
│       ├── jobs.py                    # Job status endpoints
│       └── operations.py              # Setup/teardown endpoints
│
├── agent_builder/                     # Kibana Agent Builder configs
│   ├── agents/
│   │   └── consultant_skills_agent.json
│   ├── tools/
│   │   ├── search_skills.json
│   │   ├── get_skill_files.json
│   │   ├── list_skills_by_domain.json
│   │   ├── get_skill_metadata.json
│   │   └── search_skills_by_tags.json
│   └── workflows/
│       └── agent_skills_operator.yaml
│
├── config/                            # Elasticsearch configurations
│   ├── index_mappings.json
│   ├── index_settings.json
│   └── skill_files_mappings.json
│
├── sample_skills/                     # 100+ pre-built skills
│   ├── verify-expense-policy/
│   ├── adjudicate-storm-claim/
│   ├── validate-sample-viability/
│   └── ...
│
├── new_skills/                        # Skills for incremental updates
│   └── tesla/
│
├── scripts/                           # Utility scripts
│   ├── ingest_skills.py
│   ├── search_test.py
│   └── init.sh
│
└── tests/                             # Test suite
    ├── test_expense_policy.py
    ├── test_storm_claim.py
    └── test_sample_viability.py
```

---

---

## Quick Reference Card

### For the CTO

> "Elasticsearch becomes your AI skill repository. Domain experts describe business rules in plain English, Claude or Gemini generates production code, and any AI client can discover and execute those skills using Elastic's triple-mode search (keywords, metadata, semantic vectors with Jina v3)."

### For Senior Architects

> "MCP/A2A protocol connects any AI (Claude, ChatGPT, Gemini) to Kibana Agent Builder. Skills are indexed with Jina v3 embeddings for semantic search, plus traditional keyword and metadata filtering. Single-shot LLM prompts generate Python skills from natural language—no developer bottleneck."

### For Account Executives

> "Show them the Happy Path demo. Domain expert + Claude = instant skill. Any AI can use those skills. Elastic provides the searchable skill repository. Update rules in minutes, not months. Full audit trail."

---

*Document generated for Bain & Company CTO demo, January 2026*
