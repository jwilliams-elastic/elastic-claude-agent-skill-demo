# Skill: Calculate Depreciation Schedule

## Domain
financial_services

## Description
Calculates asset depreciation schedules using multiple methods including straight-line, declining balance, and MACRS for financial reporting.

## Tags
depreciation, accounting, assets, GAAP, tax, fixed-assets

## Use Cases
- Financial statement preparation
- Tax planning
- Asset lifecycle management
- Book-tax reconciliation

## Proprietary Business Rules

### Rule 1: Method Selection
Appropriate depreciation method determination.

### Rule 2: Useful Life Assignment
Asset class useful life standards.

### Rule 3: Book-Tax Differences
GAAP vs tax depreciation tracking.

### Rule 4: Impairment Assessment
Asset impairment trigger identification.

## Input Parameters
- `asset_id` (string): Asset identifier
- `asset_info` (dict): Asset details
- `acquisition_data` (dict): Purchase information
- `depreciation_method` (string): Method to apply
- `tax_elections` (dict): Tax treatment elections
- `reporting_period` (dict): Reporting dates

## Output
- `depreciation_schedule` (list): Period-by-period depreciation
- `accumulated_depreciation` (float): Total depreciation to date
- `book_value` (float): Current book value
- `tax_depreciation` (dict): Tax basis schedule
- `book_tax_difference` (float): Temporary difference

## Implementation
The calculation logic is implemented in `depreciation_calculator.py` and references data from `depreciation_tables.json`.

## Usage Example
```python
from depreciation_calculator import calculate_depreciation

result = calculate_depreciation(
    asset_id="AST-001",
    asset_info={"description": "Equipment", "category": "machinery"},
    acquisition_data={"cost": 100000, "date": "2025-01-15", "salvage": 10000},
    depreciation_method="straight_line",
    tax_elections={"section_179": False, "bonus_depreciation": True},
    reporting_period={"year": 2025, "period": "annual"}
)

print(f"Annual Depreciation: ${result['depreciation_schedule'][0]['amount']:,.0f}")
```

## Test Execution
```python
from depreciation_calculator import calculate_depreciation

result = calculate_depreciation(
    asset_id=input_data.get('asset_id'),
    asset_info=input_data.get('asset_info', {}),
    acquisition_data=input_data.get('acquisition_data', {}),
    depreciation_method=input_data.get('depreciation_method', 'straight_line'),
    tax_elections=input_data.get('tax_elections', {}),
    reporting_period=input_data.get('reporting_period', {})
)
```
