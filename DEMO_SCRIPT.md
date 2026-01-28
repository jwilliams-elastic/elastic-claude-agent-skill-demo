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

## Scenario 4: Automotive - Tesla Company Profile Q&A

### User Request
> "What is Tesla's mission and what makes their business model different from traditional automakers?"

### Agent Response

**[Agent searches for relevant skills]**

```
Using tool: search_skills
Query: "tesla company information business model automotive"
Domain: automotive
```

**[Agent receives search results]**

```json
{
  "skill_id": "tesla-company-qa",
  "name": "Tesla Company Profile Q&A",
  "domain": "automotive",
  "description": "Answers questions about Tesla's business model, operations, customer journey, manufacturing, and strategy with citations from the Bain & Company Tesla Company Profile document",
  "tags": ["automotive", "tesla", "electric-vehicles", "business-model", "question-answering"]
}
```

**[Agent retrieves and executes the skill]**

```
Using tool: execute_skill
ID: tesla-company-qa
Input: {
  "question": "What is Tesla's mission and what makes their business model different from traditional automakers?"
}
```

**[Skill execution results]**

```json
{
  "answer": "Tesla's mission is to accelerate the world's transition to sustainable energy by bringing compelling mass market electric cars to market. Tesla is taking a fundamentally different approach to its business model: products are a 'computer on wheels' with over-the-air updates, simplified SKUs, vertically integrated supply chain, highly automated manufacturing, charging network and best-in-class battery technology. Tesla has reinvented customer experience: showrooms in high-traffic areas, rejected dealership model for direct-to-consumer sales, multiple delivery options including contactless.",
  "citations": [
    {
      "source": "TeslaCompanyProfile.pdf",
      "pages": [1, 2, 10]
    }
  ],
  "confidence": "high"
}
```

### Agent Final Response

Based on the Tesla Company Profile document:

**Tesla's Mission:**
Tesla's mission is to accelerate the world's transition to sustainable energy by bringing compelling mass market electric cars to market.

**Key Business Model Differentiators:**

1. **Product as Software Platform**: Tesla vehicles are described as "computers on wheels" that continuously evolve features and functionality through over-the-air (OTA) updates

2. **Vertical Integration**: Tesla has a vertically integrated supply chain with highly automated manufacturing, unlike traditional OEMs that rely heavily on suppliers

3. **Direct-to-Consumer Sales**: Tesla rejected the dealership model entirely, selling exclusively online with no negotiations - estimated to increase gross margin by ~3.5%

4. **Simplified SKUs**: Model 3 has only ~120 possible configurations versus Toyota Corolla's 5 million and Mercedes A-Class's 480 million

5. **Charging Infrastructure**: Tesla invested heavily in its Supercharger network (1,870+ stations) and best-in-class battery technology

**[Citation: TeslaCompanyProfile.pdf, Pages 1, 2, 10]**

Would you like me to elaborate on any specific aspect of Tesla's business model?

---

## Scenario 5: Technology - Digital Transformation Readiness (Interactive)

### User Request
> "I'd like to assess our company's digital transformation readiness."

### Agent Response

**[Agent searches for relevant skills]**

```
Using tool: search_skills
Query: "digital transformation readiness assessment"
Domain: technology
```

**[Agent receives search results]**

```json
{
  "skill_id": "assess-digital-transformation-readiness",
  "name": "Assess Digital Transformation Readiness",
  "domain": "technology",
  "description": "Evaluates organizational readiness for digital transformation across six critical dimensions with interactive data collection",
  "tags": ["technology", "digital-transformation", "cio", "enterprise", "strategy"]
}
```

**[Agent retrieves skill and sees it requires interactive data collection]**

```
Using tool: get_skill_by_id
ID: assess-digital-transformation-readiness
```

I found our Digital Transformation Readiness Assessment skill. This assessment evaluates your organization across six dimensions and compares you to industry benchmarks. I'll need to gather some information from you in three steps.

---

### Step 1: Company Profile

**Agent asks:**

> Let's start with your company profile. Please provide:
> 1. **Company name**: Your organization's name
> 2. **Industry**: Select one of: financial_services, healthcare, retail, manufacturing, technology, telecommunications, or energy

**User responds:**
> "We're Meridian Healthcare Systems. We're in the healthcare industry."

**Agent confirms:**
> Got it - Meridian Healthcare Systems in the healthcare sector. I'll use healthcare industry benchmarks for comparison.

---

### Step 2: Technology Infrastructure

**Agent asks:**

> Now let's assess your technology infrastructure:
> 1. **Legacy system percentage**: What percentage of your IT systems are older than 10 years? (0-100)
> 2. **Cloud adoption percentage**: What percentage of your workloads run in the cloud? (0-100)
> 3. **Analytics maturity**: What level best describes your analytics capability?
>    - `descriptive` - Basic reporting and dashboards
>    - `diagnostic` - Root cause analysis and drill-downs
>    - `predictive` - Forecasting and predictive models
>    - `prescriptive` - AI-driven recommendations and automation

**User responds:**
> "About 55% of our systems are legacy, we're at 30% cloud adoption, and I'd say we're at the diagnostic level for analytics."

**Agent confirms:**
> Understood - 55% legacy systems, 30% cloud adoption, and diagnostic-level analytics. Let me get the organizational information next.

---

### Step 3: Organizational Readiness

**Agent asks:**

> Finally, let's evaluate your organizational readiness:
> 1. **Digital talent percentage**: What percentage of your workforce has digital/tech skills? (0-100)
> 2. **Agile team percentage**: What percentage of your teams use agile methodologies? (0-100)
> 3. **Process automation rate**: What percentage of your business processes have automation? (0-100)

**User responds:**
> "I'd estimate 20% have strong digital skills, about 35% of teams are agile, and we've automated maybe 25% of our processes."

**Agent confirms:**
> Perfect. I now have all the information needed to run the assessment.

---

### Assessment Execution

**[Agent executes the skill with collected data]**

```
Using tool: execute_skill
ID: assess-digital-transformation-readiness
Input: {
  "company_name": "Meridian Healthcare Systems",
  "industry": "healthcare",
  "legacy_system_percentage": 55,
  "cloud_adoption_percentage": 30,
  "data_governance_score": 3,
  "analytics_maturity": "diagnostic",
  "digital_talent_percentage": 20,
  "agile_team_percentage": 35,
  "process_automation_rate": 25,
  "digital_revenue_percentage": 15,
  "annual_rd_digital_percentage": 12
}
```

**[Skill execution results]**

```json
{
  "company_name": "Meridian Healthcare Systems",
  "industry": "healthcare",
  "overall_score": 32.8,
  "readiness_tier": "At Risk",
  "dimension_scores": {
    "technology_infrastructure": 15.5,
    "data_maturity": 43.0,
    "talent_culture": 26.0,
    "process_automation": 25.0,
    "customer_experience": 22.5,
    "innovation_capacity": 24.0
  },
  "industry_benchmark": {
    "overall": 48,
    "comparison": "below",
    "gap": -15.2
  },
  "critical_gaps": [
    {
      "dimension": "technology_infrastructure",
      "current_score": 15.5,
      "benchmark": 45,
      "gap": 29.5
    },
    {
      "dimension": "talent_culture",
      "current_score": 26.0,
      "benchmark": 42,
      "gap": 16.0
    },
    {
      "dimension": "process_automation",
      "current_score": 25.0,
      "benchmark": 40,
      "gap": 15.0
    }
  ],
  "recommendations": [
    "Prioritize legacy modernization - consider cloud-native re-platforming for top 5 critical systems",
    "Accelerate cloud migration with a 'cloud-first' policy for all new workloads",
    "Invest in predictive analytics capabilities and ML platform infrastructure",
    "Launch digital skills academy and aggressive tech talent acquisition program",
    "Deploy intelligent automation CoE to identify and prioritize RPA/AI automation opportunities"
  ],
  "estimated_timeline_months": 63
}
```

---

### Agent Final Response

## Digital Transformation Readiness Assessment
### Meridian Healthcare Systems

---

**Overall Score: 32.8 / 100**
**Readiness Tier: ⚠️ At Risk**

Your organization is **15.2 points below** the healthcare industry benchmark of 48.

---

### Dimension Scores

| Dimension | Your Score | Industry Benchmark | Gap |
|-----------|------------|-------------------|-----|
| Technology Infrastructure | 15.5 | 45 | -29.5 🔴 |
| Data Maturity | 43.0 | 55 | -12.0 |
| Talent & Culture | 26.0 | 42 | -16.0 🔴 |
| Process Automation | 25.0 | 40 | -15.0 🔴 |
| Customer Experience | 22.5 | 52 | -29.5 |
| Innovation Capacity | 24.0 | 55 | -31.0 |

---

### Critical Gaps (Immediate Attention Required)

1. **Technology Infrastructure** (Gap: 29.5 points)
   - Your 55% legacy systems and 30% cloud adoption are significantly holding you back
   - Healthcare peers average 45% on this dimension

2. **Talent & Culture** (Gap: 16.0 points)
   - Only 20% digital talent and 35% agile adoption is below industry norms
   - Consider aggressive upskilling and hiring programs

3. **Process Automation** (Gap: 15.0 points)
   - 25% automation rate limits operational efficiency
   - Healthcare is rapidly adopting RPA for administrative tasks

---

### Recommended Actions

1. **Prioritize legacy modernization** - Start with cloud-native re-platforming for your top 5 critical clinical systems

2. **Accelerate cloud migration** - Implement a "cloud-first" policy for all new workloads

3. **Invest in predictive analytics** - Move beyond diagnostic to predictive capabilities, especially for patient outcomes

4. **Launch digital skills academy** - Aggressive tech talent acquisition and internal upskilling program

5. **Deploy intelligent automation CoE** - Establish a Center of Excellence to identify and prioritize RPA/AI automation opportunities

---

### Timeline to "Leader" Tier

Based on current gaps, achieving Leader status (75+ score) would take approximately **63 months** with consistent execution.

**Recommended approach:**
- **Phase 1 (0-12 months):** Technology infrastructure quick wins - cloud migration, legacy assessment
- **Phase 2 (12-24 months):** Talent transformation and automation CoE deployment
- **Phase 3 (24-36 months):** Advanced analytics and customer experience digitization

Would you like me to dive deeper into any specific dimension or create a detailed transformation roadmap?

---

## Key Demo Takeaways

This demonstration showcases several critical capabilities:

1. **Dynamic Skill Discovery**: The agent searches Elasticsearch to find relevant skills based on natural language queries, matching user needs to available business logic.

2. **Hot-Loading Execution**: Skills are retrieved and executed on-demand without being baked into the agent's training data. This allows:
   - Real-time updates to business rules
   - Proprietary logic that remains private
   - Domain-specific expertise across multiple industries

3. **Interactive Data Collection**: Skills can define required user inputs that the agent collects through guided prompts (see Scenario 5: Digital Transformation). This enables:
   - Multi-turn conversations to gather complex inputs
   - Validated data entry with field types and constraints
   - Structured assessment workflows

4. **Structured Decision-Making**: Each skill returns structured outputs (JSON) that the agent interprets to provide clear, actionable guidance to users.

5. **Compliance & Auditability**: All decisions are traceable back to specific rules and policies stored in the skill repository.

6. **Multi-Domain Support**: A single agent can handle finance, insurance, life sciences, healthcare, technology, and other domains by loading the appropriate skills from Elasticsearch.

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

---

## Quick Test Prompts

These prompts are designed to quickly test that the agent correctly retrieves and executes skill Python logic. Each prompt requires the proprietary business rules from the skill code to derive the correct answer.

**Important:** The expected outcomes listed here are for the demonstrator's reference only. The agent must retrieve the skill from Elasticsearch and execute the Python code to determine the correct answer.

### Finance: Expense Policy (verify-expense-policy)

| # | Prompt | Expected Outcome |
|---|--------|------------------|
| 1 | "I need to submit a $750 software purchase for a new IDE license. I have manager approval but not VP approval. The procurement ticket is PROC-2026-0042. Will this expense be approved?" | Not compliant - requires VP approval for amounts over $500 |
| 2 | "Our team of 8 people is planning a celebration dinner that will cost $680 total. Does this comply with our expense policy?" | Not compliant - $85/head exceeds the $75/head limit |
| 3 | "Can I expense $150 for office supplies without any special approvals?" | Compliant - under $500 threshold and valid category |
| 4 | "I want to expense a $200 software subscription. I don't have a procurement ticket yet. Is this allowed?" | Not compliant - Software category requires Procurement_Ticket_ID |

### Insurance: Storm Claims (adjudicate-storm-claim)

| # | Prompt | Expected Outcome |
|---|--------|------------------|
| 1 | "Process claim CLM-2026-001: A Category 4 hurricane caused $85,000 damage to a coastal property with an asphalt shingle roof. The roof was retrofitted in 2022. Should we approve this claim and waive the deductible?" | APPROVED with deductible waived (Category 3+ qualifies) |
| 2 | "We received claim CLM-2026-002 for a wood shake roof in a coastal area damaged by a Category 3 storm. The property was last retrofitted in 2019. Damage is estimated at $60,000. What's the decision?" | DENIED - Wood shake coastal requires retrofit after 2020 |
| 3 | "Adjudicate claim CLM-2026-003: Category 2 storm damage to an inland property with a tile roof. Damage estimate is $25,000. No recent retrofits." | APPROVED - Standard claim, no deductible waiver (Category < 3) |
| 4 | "Urgent: Claim CLM-2026-004 for Category 5 hurricane damage. Coastal property with metal roof, $200,000 in damages. Needs immediate decision." | REVIEW_REQUIRED - High-risk catastrophic event |

### Life Sciences: Sample Viability (validate-sample-viability)

| # | Prompt | Expected Outcome |
|---|--------|------------------|
| 1 | "Check viability for sample BIO-2026-001: It's a Plasma-EDTA sample that was collected 5 hours ago. Volume is 4ml, turbidity index is 0.3, and it's currently stored at -75C. Can we proceed with processing?" | REJECTED - Plasma-EDTA must be processed within 4 hours |
| 2 | "Validate sample BIO-2026-002: Serum sample, 3ml volume, collected 2 hours ago, turbidity index 0.85, storage temp -75C. Is this sample viable for biomarker analysis?" | ACCEPTED with flag - Requires ultracentrifugation (turbidity > 0.8) |
| 3 | "We have Whole-Blood sample BIO-2026-003 stored at -65C. Volume is 6ml, turbidity is 0.2, collected 1 hour ago. What's the viability status?" | REJECTED - Storage temp outside range (-80C to -70C) |
| 4 | "Sample BIO-2026-004 is a Plasma-EDTA sample: 2ml volume, collected 2 hours ago, turbidity 0.3, stored at -75C. Can we run the full assay panel?" | REJECTED - Volume below minimum (Plasma-EDTA requires 3.0ml) |
| 5 | "Validate sample BIO-2026-005: Serum, 4ml volume, collected 3 hours ago, turbidity 0.4, storage at -78C. Ready for processing?" | ACCEPTED - All criteria met |

### Automotive: Tesla Company Profile Q&A (tesla-company-qa)

| # | Prompt | Expected Outcome |
|---|--------|------------------|
| 1 | "What is Tesla's mission statement and when was the company founded?" | Mission: accelerate world's transition to sustainable energy. Founded 2003 in Palo Alto, CA. [Pages 1, 4] |
| 2 | "How many employees does Tesla have and what was their 2019 automotive revenue?" | 48,000 FTE employees. 2019 Automotive Revenue: $20.8B. 2019 Gross Profit: $4.4B. [Page 4] |
| 3 | "What are Tesla's battery cost reduction strategies announced at Battery Day?" | 56% cost reduction to ~$55/kWh by 2025 via: larger cell design (14%), dry electrode process (18%), silicon anode (5%), diversified cathodes (12%), giga casting/structural batteries (7%). [Page 5] |
| 4 | "How does Tesla's direct-to-consumer sales model work and how many states ban it?" | Sells exclusively online with no negotiations, as few as 5 clicks to order with $100 non-refundable fee. 74.8% customer satisfaction. ~3.5% gross margin increase. 10 states have outright sales ban. [Pages 10, 46] |
| 5 | "What percentage of Tesla service issues can be diagnosed and fixed remotely?" | 90% of issues remotely diagnosed, 80% fixed remotely. SmartAlerts proactively diagnose. 80% of physical repairs via mobile service (~700 units worldwide). [Page 22] |

### Technology: Digital Transformation Readiness (assess-digital-transformation-readiness)

**Note:** This skill demonstrates interactive data collection. The agent will prompt for information in 3 steps before executing the assessment.

| # | Initial Prompt | User Inputs to Provide | Expected Outcome |
|---|----------------|------------------------|------------------|
| 1 | "Assess our digital transformation readiness" | Company: TechStart Inc, Industry: technology, Legacy: 15%, Cloud: 80%, Analytics: predictive, Digital Talent: 65%, Agile: 75%, Automation: 60% | Score ~70+, "Fast Follower" tier, above technology benchmark |
| 2 | "I want to evaluate how ready my company is for digital transformation" | Company: OldBank Corp, Industry: financial_services, Legacy: 70%, Cloud: 20%, Analytics: descriptive, Digital Talent: 15%, Agile: 20%, Automation: 15% | Score ~25-30, "At Risk" tier, significant gaps in all dimensions |
| 3 | "Can you run a digital readiness assessment for us?" | Company: MidCo Manufacturing, Industry: manufacturing, Legacy: 40%, Cloud: 45%, Analytics: diagnostic, Digital Talent: 30%, Agile: 45%, Automation: 50% | Score ~45-50, "Cautious Adopter" tier, automation strength, talent gap |
| 4 | "Help me understand our digital transformation gaps" | Company: RetailNow, Industry: retail, Legacy: 35%, Cloud: 55%, Analytics: predictive, Digital Talent: 40%, Agile: 60%, Automation: 45% | Score ~55-60, "Fast Follower" tier, near industry benchmark |

**Interactive Flow to Test:**
1. Agent should first ask for Company Profile (company name + industry)
2. Agent should then ask for Technology Infrastructure metrics (legacy %, cloud %, analytics maturity)
3. Agent should finally ask for Organizational Readiness metrics (digital talent %, agile %, automation %)
4. After collecting all data, agent executes assessment and presents detailed results

### Key Business Rules Reference

| Skill | Domain | Key Rules |
|-------|--------|-----------|
| verify-expense-policy | Finance | VP approval >$500, Team dinner $75/head cap, Software needs PROC ticket |
| adjudicate-storm-claim | Insurance | Cat 3+ deductible waiver, Wood shake coastal needs 2020+ retrofit |
| validate-sample-viability | Life Sciences | Plasma-EDTA 4hr limit, Turbidity >0.8 needs centrifuge, Storage -80 to -70C |
| tesla-company-qa | Automotive | PDF Q&A with citations, 46 pages covering business model, manufacturing, sales, battery tech |
| assess-digital-transformation-readiness | Technology | Interactive 3-step data collection, 6 dimensions, industry benchmarks, tier classification (Leader/Fast Follower/Cautious Adopter/At Risk) |
