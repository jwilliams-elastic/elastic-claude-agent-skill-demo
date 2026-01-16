# Demo Script: Hot-Loading Skill Execution Flow

This demo script showcases how a Claude agent can discover, retrieve, and execute proprietary business logic stored in Elasticsearch. The agent uses MCP tools to search for relevant skills and hot-loads them to solve domain-specific problems.

---

## Scenario 1: Finance - Expense Policy Verification

### User Request
> "I need to submit an expense report for a team dinner that cost $850 for 10 people. Can you check if this meets our company policy?"

### Agent Response

**[Agent searches for relevant skills]**

```
Using tool: search_skills
Query: "expense policy approval rules"
Domain: finance
```

**[Agent receives search results]**

```json
{
  "skill_id": "verify-expense-policy",
  "name": "Verify Expense Policy",
  "domain": "finance",
  "description": "Validates expense submissions against company policy rules including approval requirements, category limits, and documentation needs",
  "tags": ["finance", "expense", "policy", "approval", "compliance"]
}
```

**[Agent retrieves full skill content]**

```
Using tool: get_skill_by_id
ID: verify-expense-policy
```

**[Agent reads skill instructions and business rules]**

Found the expense policy verification skill. Let me execute it with your expense details.

**[Agent hot-loads and executes the skill]**

```
Using tool: execute_skill
ID: verify-expense-policy
Input: {
  "amount": 850,
  "category": "Team_Dinner",
  "attendees": 10,
  "has_vp_approval": false
}
```

**[Skill execution results]**

```json
{
  "approved": false,
  "violations": [
    {
      "rule": "VP_APPROVAL_REQUIRED",
      "message": "Expenses over $500 require VP approval"
    },
    {
      "rule": "CATEGORY_LIMIT_EXCEEDED",
      "message": "Team_Dinner is capped at $75/head. Your cost: $85/head (10 attendees, $850 total)"
    }
  ],
  "recommendations": [
    "Obtain VP approval before submission",
    "Consider reducing the per-person cost to $75 or below",
    "Split into multiple smaller team events if possible"
  ]
}
```

### Agent Final Response

Your expense report does not currently meet company policy for two reasons:

1. **VP Approval Required**: Any expense over $500 requires VP approval before submission
2. **Per-Person Limit Exceeded**: Team dinners are capped at $75 per person, but your expense is $85 per person ($850 ÷ 10 attendees)

**Recommendations:**
- Obtain VP approval before submitting
- Reduce the total cost to $750 (10 people × $75/head) or fewer attendees
- Consider splitting this into smaller team events

Would you like me to help you draft an approval request for your VP?

---

## Scenario 2: Insurance - Storm Damage Claim

### User Request
> "I need to process a homeowner's claim for a Category 4 hurricane. The roof is wood shake, coastal property in Florida, but they had it retrofitted in 2021. Claim amount is $45,000."

### Agent Response

**[Agent searches for relevant skills]**

```
Using tool: search_skills
Query: "storm damage claim adjudication hurricane coverage"
Domain: insurance
```

**[Agent receives search results]**

```json
{
  "skill_id": "adjudicate-storm-claim",
  "name": "Adjudicate Storm Claim",
  "domain": "insurance",
  "description": "Evaluates storm damage claims based on storm severity, property characteristics, and risk factors to determine coverage eligibility and deductible requirements",
  "tags": ["insurance", "claims", "storm", "hurricane", "property", "adjudication"]
}
```

**[Agent retrieves and executes the skill]**

```
Using tool: execute_skill
ID: adjudicate-storm-claim
Input: {
  "storm_category": 4,
  "roof_material": "wood_shake",
  "region": "coastal",
  "retrofit_year": 2021,
  "claim_amount": 45000,
  "deductible": 2500
}
```

**[Skill execution results]**

```json
{
  "claim_status": "APPROVED",
  "coverage_decision": {
    "eligible": true,
    "reason": "Wood shake roof in coastal region APPROVED: retrofit_year (2021) > 2020 threshold"
  },
  "deductible_decision": {
    "waived": true,
    "reason": "Storm category 4 meets threshold (≥3) for deductible waiver",
    "original_deductible": 2500,
    "adjusted_deductible": 0
  },
  "risk_adjustment": {
    "material_region_multiplier": 1.15,
    "explanation": "Wood shake roof in coastal region carries elevated risk (15% multiplier)"
  },
  "payout_calculation": {
    "claim_amount": 45000,
    "deductible": 0,
    "net_payout": 45000,
    "notes": "Full claim amount approved due to deductible waiver"
  }
}
```

### Agent Final Response

Great news - this claim is **APPROVED** for full payout.

**Coverage Decision:**
- ✅ **Eligible**: While wood shake roofs in coastal regions are typically high-risk, the 2021 retrofit meets our requirement (must be after 2020)

**Deductible Decision:**
- ✅ **Waived**: Category 4 hurricanes automatically waive the standard $2,500 deductible (policy applies to Category 3+)

**Payout:**
- Claim Amount: $45,000
- Deductible: $0 (waived)
- **Net Payout: $45,000**

**Risk Notes:**
- The wood shake roof in a coastal region carries a 1.15x risk multiplier for future premium calculations
- Recommend discussing upgraded roofing materials (impact-resistant shingles) at next renewal

Would you like me to generate the approval documentation?

---

## Scenario 3: Life Sciences - Lab Sample Processing

### User Request
> "We just received a Plasma-EDTA sample that was collected 5 hours ago. Turbidity index is 0.9, stored at -75°C, volume is 3.2mL. Can we process this for the biomarker panel?"

### Agent Response

**[Agent searches for relevant skills]**

```
Using tool: search_skills
Query: "plasma sample viability validation biomarker processing"
Domain: life_sciences
```

**[Agent receives search results]**

```json
{
  "skill_id": "validate-sample-viability",
  "name": "Validate Sample Viability",
  "domain": "life_sciences",
  "description": "Validates lab sample viability against strict processing time windows, storage requirements, and quality thresholds to ensure research integrity",
  "tags": ["life_sciences", "laboratory", "sample", "viability", "quality_control"]
}
```

**[Agent retrieves and executes the skill]**

```
Using tool: execute_skill
ID: validate-sample-viability
Input: {
  "sample_type": "Plasma-EDTA",
  "collection_time_hours_ago": 5,
  "turbidity_index": 0.9,
  "storage_temp_celsius": -75,
  "volume_ml": 3.2
}
```

**[Skill execution results]**

```json
{
  "viable": false,
  "overall_status": "REJECTED",
  "violations": [
    {
      "rule": "PROCESSING_TIME_EXCEEDED",
      "severity": "CRITICAL",
      "message": "Plasma-EDTA samples must be processed within 4 hours. Current: 5 hours",
      "impact": "Sample integrity compromised - biomarker degradation likely"
    },
    {
      "rule": "TURBIDITY_THRESHOLD_EXCEEDED",
      "severity": "WARNING",
      "message": "Turbidity index 0.9 exceeds threshold of 0.8",
      "impact": "Requires ultracentrifugation before analysis"
    }
  ],
  "validations_passed": [
    {
      "rule": "STORAGE_TEMPERATURE",
      "status": "PASS",
      "message": "Storage temperature -75°C within acceptable range (-80°C to -70°C)"
    },
    {
      "rule": "MINIMUM_VOLUME",
      "status": "PASS",
      "message": "Volume 3.2mL meets minimum requirement of 2.5mL for Plasma-EDTA"
    }
  ],
  "recommendations": [
    "DO NOT process this sample for biomarker panel",
    "Sample must be flagged as 'Compromised' in LIMS",
    "Request new sample collection from patient",
    "Document time violation in quality incident report"
  ],
  "quality_metrics": {
    "processing_window_remaining": "EXPIRED (1 hour overdue)",
    "estimated_biomarker_degradation": "15-25%",
    "acceptable_for_research": false
  }
}
```

### Agent Final Response

⚠️ **SAMPLE REJECTED** - This sample cannot be processed for the biomarker panel.

**Critical Violations:**

1. **Processing Time Exceeded** (CRITICAL)
   - Plasma-EDTA samples must be processed within 4 hours
   - This sample was collected 5 hours ago (1 hour overdue)
   - Expected biomarker degradation: 15-25%

2. **High Turbidity** (WARNING)
   - Turbidity index of 0.9 exceeds the 0.8 threshold
   - Would require ultracentrifugation before analysis
   - However, time violation takes precedence

**Validations Passed:**
- ✅ Storage temperature (-75°C) is within acceptable range
- ✅ Volume (3.2mL) meets minimum requirements

**Required Actions:**
1. Flag sample as "Compromised" in the LIMS system
2. Document this time violation in a quality incident report
3. Request new sample collection from the patient
4. Do NOT proceed with biomarker panel analysis

**Note:** Even with ultracentrifugation to address turbidity, the time violation makes this sample unacceptable for research-grade biomarker analysis. Sample integrity is paramount for clinical accuracy.

Would you like me to generate the quality incident report?

---

## Key Demo Takeaways

This demonstration showcases several critical capabilities:

1. **Dynamic Skill Discovery**: The agent searches Elasticsearch to find relevant skills based on natural language queries, matching user needs to available business logic.

2. **Hot-Loading Execution**: Skills are retrieved and executed on-demand without being baked into the agent's training data. This allows:
   - Real-time updates to business rules
   - Proprietary logic that remains private
   - Domain-specific expertise across multiple industries

3. **Structured Decision-Making**: Each skill returns structured outputs (JSON) that the agent interprets to provide clear, actionable guidance to users.

4. **Compliance & Auditability**: All decisions are traceable back to specific rules and policies stored in the skill repository.

5. **Multi-Domain Support**: A single agent can handle finance, insurance, life sciences, and other domains by loading the appropriate skills from Elasticsearch.

## Technical Flow

```
User Query
    ↓
Agent (Claude)
    ↓
MCP Tool: search_skills → Elasticsearch (ES|QL query)
    ↓
Ranked skill results returned
    ↓
Agent selects most relevant skill
    ↓
MCP Tool: get_skill_by_id → Retrieve full skill content
    ↓
Agent reads instructions + business rules
    ↓
MCP Tool: execute_skill → Hot-load Python implementation
    ↓
Skill executes with user parameters
    ↓
Structured results returned to agent
    ↓
Agent interprets results and responds to user
```

## Next Steps

To implement this demo in your environment:

1. Follow the setup instructions in `README.md`
2. Configure your Elasticsearch credentials in `.env`
3. Run `uv run scripts/ingest_skills.py` to index the sample skills
4. Integrate the MCP tools from `mcp/tools.json` with your Claude agent
5. Start Claude with environment variables loaded:
   ```bash
   export $(cat .env | xargs) && claude
   ```
6. Try the example dialogues above or create your own scenarios

For more details on each skill's business logic, see the individual `SKILL.md` files in the `sample_skills/` directory.
