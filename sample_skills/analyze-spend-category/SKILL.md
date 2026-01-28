# Skill: Analyze Spend Category

## Domain
supply_chain

## Description
Analyzes procurement spend by category to identify savings opportunities, supplier consolidation, and contract optimization.

## Tags
procurement, spend, sourcing, savings, suppliers, analytics

## Use Cases
- Spend visibility
- Savings identification
- Supplier rationalization
- Contract optimization

## Proprietary Business Rules

### Rule 1: Spend Classification
Category taxonomy mapping and classification.

### Rule 2: Supplier Concentration Analysis
Supplier fragmentation and consolidation opportunities.

### Rule 3: Benchmark Comparison
Price benchmarking against market rates.

### Rule 4: Savings Opportunity Sizing
Potential savings quantification.

## Input Parameters
- `analysis_id` (string): Analysis identifier
- `spend_data` (list): Transaction-level spend
- `supplier_data` (dict): Supplier information
- `category_taxonomy` (dict): Category hierarchy
- `benchmark_data` (dict): Market benchmarks
- `contract_data` (list): Existing contracts

## Output
- `category_summary` (dict): Spend by category
- `supplier_analysis` (dict): Supplier concentration
- `savings_opportunities` (list): Identified savings
- `consolidation_recommendations` (list): Supplier rationalization
- `benchmark_comparison` (dict): Price analysis

## Implementation
The analysis logic is implemented in `spend_analyzer.py` and references data from CSV files:
- `category_taxonomy.csv` - Reference data
- `analysis_dimensions.csv` - Reference data
- `opportunity_levers.csv` - Reference data
- `compliance_requirements.csv` - Reference data
- `risk_indicators.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from spend_analyzer import analyze_spend

result = analyze_spend(
    analysis_id="SPN-001",
    spend_data=[{"supplier": "SUP-001", "amount": 100000, "category": "IT_hardware"}],
    supplier_data={"SUP-001": {"name": "Tech Corp", "tier": 1}},
    category_taxonomy={"IT_hardware": {"parent": "IT", "level": 2}},
    benchmark_data={"IT_hardware": {"market_rate": 0.95}},
    contract_data=[{"supplier": "SUP-001", "end_date": "2026-12-31"}]
)

print(f"Total Spend Analyzed: ${sum(result['category_summary'].values()):,.0f}")
```

## Test Execution
```python
from spend_analyzer import analyze_spend

result = analyze_spend(
    analysis_id=input_data.get('analysis_id'),
    spend_data=input_data.get('spend_data', []),
    supplier_data=input_data.get('supplier_data', {}),
    category_taxonomy=input_data.get('category_taxonomy', {}),
    benchmark_data=input_data.get('benchmark_data', {}),
    contract_data=input_data.get('contract_data', [])
)
```
