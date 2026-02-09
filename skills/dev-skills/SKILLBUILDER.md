# Spreadsheet to Skill Conversion Guide

Convert any spreadsheet into an agent skill that is searchable and executable.

----

## Prompt Template

```
Convert ./spreadsheets/<SPREADSHEET>.xlsx into a skill named "<skill-name>" in ./skills/dev-skills/

STEP 1: ANALYZE
- Read the spreadsheet and list all formulas with cell references
- Identify inputs (user-provided) vs constants (reference data)
- Identify the domain category and relevant tags for search

STEP 2: CREATE FILES
Create these files in ./skills/dev-skills/<skill-name>/:

1. SKILL.md - Metadata and documentation (see format below)
2. <skill_name>.py - Python with all calculations
3. reference_data.csv - All constants/thresholds (no hardcoded values in Python)

STEP 3: VERIFY
- Run Python with spreadsheet's default values
- Confirm outputs match spreadsheet exactly (diff < 0.01)
- Show verification table with expected vs actual

Show me the formula analysis, then create the files, then verify.
```

---

## SKILL.md Format (Required for Elasticsearch Ingestion)

The ingestion script parses these specific patterns. Use this exact format:

```markdown
# Skill: <Title>

## Domain
<single-word-category-lowercase>

## Description
<What this skill does. This text is indexed for semantic search.
Include key terms users might search for.>

## Tags
<tag1-lowercase>, <tag2-lowercase>, <tag3-lowercase>, <tag4-lowercase>

## Input Parameters
- `<param>` (<type>): <description>

## Output
- `<field>` (<type>): <description>

## Implementation
Calculations in `<filename>.py` using reference data from:
- `reference_data.csv` - <what it contains>

## Formulas
<Document each formula with variable names, not hardcoded numbers>
```

### Critical Parsing Rules

| Element | Format | Example |
|---------|--------|---------|
| Domain | `## Domain` heading, value on next line | `## Domain`<br>`finance` |
| Tags | `## Tags` heading, comma-separated on next line | `## Tags`<br>`roi, cost, analysis` |
| Description | `## Description` heading, text until next `##` | Full paragraphs OK |

**IMPORTANT:**
- **Domain values must be lowercase** (e.g., `finance`, not `Finance`)
- **Tag values must be lowercase** (e.g., `roi, tco, cost-benefit`, not `ROI, TCO, Cost-Benefit`)
- **DO NOT USE** markdown tables for metadata - they won't be parsed.

---

## File Structure

```
skills/dev-skills/
└── <skill-name>/              # kebab-case folder name
    ├── SKILL.md               # Required - metadata for search
    ├── <skill_name>.py        # snake_case Python module
    └── reference_data.csv     # All constants and thresholds
```

---

## reference_data.csv Format

```csv
variable,value,description
<variable_name>,<value>,<what it represents>
```

**Include ALL numeric constants:**
- Thresholds and boundaries
- Multipliers and ratios
- Default values
- Magic numbers (e.g., 12 for months/year)

---

## Python Module Structure

```python
"""<Skill Name>"""
import csv
from pathlib import Path

def load_reference_data():
    """Load all constants from CSV - no hardcoded values."""
    csv_path = Path(__file__).parent / "reference_data.csv"
    data = {}
    with open(csv_path) as f:
        for row in csv.DictReader(f):
            val = row['value']
            try:
                data[row['variable']] = float(val) if '.' in val else int(val)
            except ValueError:
                data[row['variable']] = val
    return data

def calculate(inputs: dict) -> dict:
    """Main calculation function."""
    ref = load_reference_data()

    # Use ref['variable_name'] for all constants
    # Example: total = inputs['users'] * ref['months_per_year']

    return {
        'result_field': value,
        'inputs': inputs  # Echo for verification
    }

if __name__ == "__main__":
    # Test with default values
    result = calculate({...})
    print(result)
```

---

## Verification Requirement

Before completion, verify Python matches spreadsheet:

```
| Field | Spreadsheet | Python | Status |
|-------|-------------|--------|--------|
| <output1> | <value> | <value> | ✓ PASS |
```

All outputs must match within 0.01.

---

## Domain Categories

Use consistent domain values for filtering:

| Domain | Use For |
|--------|---------|
| `finance` | ROI, TCO, budgets, costs |
| `operations` | Supply chain, logistics, capacity |
| `compliance` | Policy, regulations, audits |
| `risk` | Risk assessment, scoring |
| `hr` | Workforce, retention, scheduling |
| `sales` | Revenue, pricing, forecasting |
| `healthcare` | Clinical, patient, medical |
| `manufacturing` | Production, quality, maintenance |

---

## Quick Checklist

- [ ] SKILL.md uses `## Domain` and `## Tags` headings (not tables)
- [ ] Domain value is lowercase (e.g., `finance`, not `Finance`)
- [ ] All tag values are lowercase (e.g., `roi, tco`, not `ROI, TCO`)
- [ ] Description contains searchable keywords
- [ ] All numeric constants in reference_data.csv
- [ ] Python loads values from CSV, not hardcoded
- [ ] Verification shows Python matches spreadsheet

---

## Publishing Skills to Elastic

After creating skills in `./skills/dev-skills/`, publish them to Elasticsearch using the consultant workflow.

### Prompt Translation

When you ask to **"publish my new skills to elastic using SKILLBUILDER.md"**, this translates to:

```
Run the update-skills operation in the consultant_skills_operator workflow
```

### Command Format

```
Can you run the consultant workflow to update skills located in ./skills/dev-skills
```

**IMPORTANT**: The workflow requires an **absolute path**. When executing:

1. Resolve `./skills/dev-skills` to an absolute path using the primary working directory
2. Construct the full path: `<primary_working_directory>/skills/dev-skills`
3. Pass this absolute path to the tool

Example execution:
```python
# If primary working directory is /Users/username/project
# Then skills_path should be: /Users/username/project/skills/dev-skills
```

This executes the `consultant_skills_operator` tool with:
- **operation**: `update-skills`
- **skills_path**: `<absolute_path_to_dev_skills>` (resolved from working directory)

The workflow will:
1. Scan the skills directory
2. Parse SKILL.md files for metadata
3. Index skills in Elasticsearch for semantic search
4. Make skills discoverable and executable by agents
