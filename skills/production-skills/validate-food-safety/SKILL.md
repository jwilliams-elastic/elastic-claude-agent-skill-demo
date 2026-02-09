# Skill: Validate Food Safety

## Domain
consumer_products

## Description
Validates food product safety compliance including ingredient verification, allergen labeling, and regulatory requirements for consumer protection.

## Tags
food-safety, FDA, allergens, labeling, compliance, HACCP

## Use Cases
- Ingredient safety verification
- Allergen label validation
- Regulatory compliance check
- Recall risk assessment

## Proprietary Business Rules

### Rule 1: Allergen Declaration
Verification of major allergen labeling requirements.

### Rule 2: Ingredient Limits
Validation against maximum permitted levels for additives.

### Rule 3: Cross-Contamination Risk
Assessment of manufacturing cross-contact risks.

### Rule 4: Label Compliance
FDA labeling regulation compliance verification.

## Input Parameters
- `product_id` (string): Product identifier
- `ingredients` (list): Ingredient list with quantities
- `allergen_info` (dict): Allergen declarations
- `manufacturing_info` (dict): Production facility details
- `label_claims` (list): Marketing claims on label
- `nutrition_facts` (dict): Nutritional information

## Output
- `compliance_status` (string): Overall compliance status
- `allergen_review` (dict): Allergen labeling assessment
- `ingredient_issues` (list): Ingredient-related findings
- `label_violations` (list): Labeling compliance issues
- `risk_level` (string): Food safety risk rating

## Implementation
The validation logic is implemented in `safety_validator.py` and references data from CSV files:
- `ingredient_limits.csv` - Reference data
- `facility_rules.csv` - Reference data
- `claim_rules.csv` - Reference data
- `nutrition_limits.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from safety_validator import validate_food_safety

result = validate_food_safety(
    product_id="PROD-001",
    ingredients=[{"name": "wheat flour", "percentage": 45}, {"name": "sugar", "percentage": 20}],
    allergen_info={"contains": ["wheat"], "may_contain": ["soy"]},
    manufacturing_info={"facility_type": "bakery", "haccp_certified": True},
    label_claims=["natural", "no artificial colors"],
    nutrition_facts={"calories": 150, "sodium_mg": 200}
)

print(f"Status: {result['compliance_status']}")
```

## Test Execution
```python
from safety_validator import validate_food_safety

result = validate_food_safety(
    product_id=input_data.get('product_id'),
    ingredients=input_data.get('ingredients', []),
    allergen_info=input_data.get('allergen_info', {}),
    manufacturing_info=input_data.get('manufacturing_info', {}),
    label_claims=input_data.get('label_claims', []),
    nutrition_facts=input_data.get('nutrition_facts', {})
)
```
