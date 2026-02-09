# Skill: Screen Media Content for Distribution

## Domain
media_entertainment

## Description
Evaluates media content against distribution platform requirements, content policies, and regional regulations to determine distribution eligibility.

## Tags
media, content-screening, distribution, compliance, content-policy

## Use Cases
- Platform content approval
- Regional content adaptation
- Rating classification
- Rights clearance verification

## Proprietary Business Rules

### Rule 1: Content Rating Classification
Age rating determination based on content descriptors and regional standards.

### Rule 2: Platform Policy Compliance
Platform-specific content policy checks for restricted content types.

### Rule 3: Rights Territory Verification
Distribution rights validation by geographic territory.

### Rule 4: Technical Specification Compliance
Format and quality requirements by distribution channel.

## Input Parameters
- `content_id` (string): Content identifier
- `content_type` (string): Movie, series, short, documentary
- `content_descriptors` (list): Violence, language, nudity indicators
- `target_platforms` (list): Distribution platforms
- `territories` (list): Target distribution regions
- `rights_data` (dict): Licensing and rights information
- `technical_specs` (dict): Format, resolution, codec

## Output
- `distribution_status` (string): Approved, blocked, restricted
- `content_rating` (dict): Rating by region
- `platform_eligibility` (dict): Status by platform
- `required_edits` (list): Content modifications needed
- `territory_restrictions` (list): Geographic limitations

## Implementation
The screening logic is implemented in `content_screener.py` and references policies from CSV files:
- `rating_systems.csv` - Reference data
- `platforms.csv` - Reference data
- `parameters.csv` - Reference data.

## Usage Example
```python
from content_screener import screen_content

result = screen_content(
    content_id="MOV-2024-001",
    content_type="movie",
    content_descriptors=["violence_moderate", "language_mild"],
    target_platforms=["streaming_premium", "broadcast_basic"],
    territories=["US", "UK", "DE"],
    rights_data={"us": "exclusive", "uk": "non-exclusive"},
    technical_specs={"resolution": "4K", "hdr": True, "codec": "H.265"}
)

print(f"Status: {result['distribution_status']}")
```

## Test Execution
```python
from content_screener import screen_content

result = screen_content(
    content_id=input_data.get('content_id'),
    content_type=input_data.get('content_type'),
    content_descriptors=input_data.get('content_descriptors', []),
    target_platforms=input_data.get('target_platforms', []),
    territories=input_data.get('territories', []),
    rights_data=input_data.get('rights_data', {}),
    technical_specs=input_data.get('technical_specs', {})
)
```
