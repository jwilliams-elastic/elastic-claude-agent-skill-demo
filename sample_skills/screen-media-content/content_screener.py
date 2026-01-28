"""
Media Content Screening Module

Implements content policy compliance and distribution eligibility
checking for media content across platforms and territories.
"""

import csv
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional



def load_csv_as_dict(filename: str, key_column: str = 'id') -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column, row.get('key', ''))
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result[key] = row
    return result


def load_csv_as_list(filename: str) -> List[Dict[str, Any]]:
    """Load a CSV file and return as list of dictionaries."""
    csv_path = Path(__file__).parent / filename
    result = []
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert values
            for k, v in list(row.items()):
                if v == '' or v is None:
                    continue
                # Try to parse as Python literal (dict, list, etc.)
                if str(v).startswith(('{', '[')):
                    try:
                        row[k] = ast.literal_eval(v)
                        continue
                    except (ValueError, SyntaxError):
                        pass
                # Try numeric conversion
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result.append(row)
    return result


def load_parameters(filename: str = 'parameters.csv') -> Dict[str, Any]:
    """Load parameters CSV as key-value dictionary."""
    csv_path = Path(__file__).parent / filename
    if not csv_path.exists():
        return {}
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('key', '')
            value = row.get('value', '')
            try:
                if '.' in str(value):
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except (ValueError, TypeError):
                if value.lower() == 'true':
                    result[key] = True
                elif value.lower() == 'false':
                    result[key] = False
                else:
                    result[key] = value
    return result

def load_key_value_csv(filename: str) -> Dict[str, Any]:
    """Load a key-value CSV file as a flat dictionary."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.get('key', row.get('id', ''))
            value = row.get('value', '')
            try:
                if '.' in str(value):
                    result[key] = float(value)
                else:
                    result[key] = int(value)
            except (ValueError, TypeError):
                if str(value).lower() == 'true':
                    result[key] = True
                elif str(value).lower() == 'false':
                    result[key] = False
                else:
                    result[key] = value
    return result


def load_content_policies() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    rating_systems_data = load_csv_as_dict("rating_systems.csv")
    platforms_data = load_csv_as_dict("platforms.csv")
    params = load_parameters()
    return {
        "rating_systems": rating_systems_data,
        "platforms": platforms_data,
        **params
    }


def determine_content_rating(
    content_descriptors: List[str],
    rating_rules: Dict
) -> Dict[str, str]:
    """Determine content rating by region based on descriptors."""
    ratings = {}

    for region, rules in rating_rules.items():
        max_rating_level = 0

        for descriptor in content_descriptors:
            for rating, criteria in rules["ratings"].items():
                if descriptor in criteria.get("triggers", []):
                    rating_level = criteria.get("level", 0)
                    max_rating_level = max(max_rating_level, rating_level)

        # Find rating for this level
        for rating, criteria in rules["ratings"].items():
            if criteria.get("level") == max_rating_level:
                ratings[region] = rating
                break

        if region not in ratings:
            ratings[region] = rules.get("default_rating", "G")

    return ratings


def check_platform_eligibility(
    content_type: str,
    content_descriptors: List[str],
    ratings: Dict[str, str],
    platforms: List[str],
    platform_policies: Dict
) -> Dict[str, Dict]:
    """Check content eligibility for each platform."""
    eligibility = {}

    for platform in platforms:
        policy = platform_policies.get(platform, platform_policies.get("default", {}))

        issues = []
        status = "approved"

        # Check content type
        if content_type not in policy.get("allowed_content_types", []):
            issues.append(f"Content type '{content_type}' not allowed")
            status = "blocked"

        # Check restricted content
        for descriptor in content_descriptors:
            if descriptor in policy.get("prohibited_content", []):
                issues.append(f"Prohibited content: {descriptor}")
                status = "blocked"
            elif descriptor in policy.get("restricted_content", []):
                issues.append(f"Restricted content: {descriptor}")
                if status != "blocked":
                    status = "restricted"

        # Check rating requirements
        max_rating = policy.get("max_rating_level", 5)
        for region, rating in ratings.items():
            # Would need rating level lookup
            pass

        eligibility[platform] = {
            "status": status,
            "issues": issues,
            "requirements_met": len(issues) == 0
        }

    return eligibility


def check_territory_rights(
    territories: List[str],
    rights_data: Dict
) -> Dict[str, Any]:
    """Verify distribution rights by territory."""
    territory_status = {}
    restrictions = []

    for territory in territories:
        rights = rights_data.get(territory.lower())

        if rights is None:
            territory_status[territory] = "no_rights"
            restrictions.append({
                "territory": territory,
                "reason": "No distribution rights for this territory"
            })
        elif rights == "expired":
            territory_status[territory] = "expired"
            restrictions.append({
                "territory": territory,
                "reason": "Distribution rights have expired"
            })
        else:
            territory_status[territory] = rights

    return {
        "status_by_territory": territory_status,
        "restrictions": restrictions
    }


def check_technical_specs(
    specs: Dict,
    platform_requirements: Dict
) -> Dict[str, Any]:
    """Verify technical specifications meet requirements."""
    issues = []

    resolution = specs.get("resolution", "HD")
    codec = specs.get("codec", "H.264")

    required_min_res = platform_requirements.get("min_resolution", "HD")
    allowed_codecs = platform_requirements.get("allowed_codecs", ["H.264", "H.265"])

    res_hierarchy = ["SD", "HD", "FHD", "4K", "8K"]
    current_idx = res_hierarchy.index(resolution) if resolution in res_hierarchy else 1
    required_idx = res_hierarchy.index(required_min_res) if required_min_res in res_hierarchy else 1

    if current_idx < required_idx:
        issues.append(f"Resolution {resolution} below minimum {required_min_res}")

    if codec not in allowed_codecs:
        issues.append(f"Codec {codec} not in allowed list: {allowed_codecs}")

    return {
        "meets_requirements": len(issues) == 0,
        "issues": issues,
        "specs_provided": specs
    }


def screen_content(
    content_id: str,
    content_type: str,
    content_descriptors: List[str],
    target_platforms: List[str],
    territories: List[str],
    rights_data: Dict,
    technical_specs: Dict
) -> Dict[str, Any]:
    """
    Screen media content for distribution eligibility.

    Business Rules:
    1. Rating classification by regional standards
    2. Platform policy compliance
    3. Territory rights verification
    4. Technical specification compliance

    Args:
        content_id: Content identifier
        content_type: Type of content
        content_descriptors: Content warning indicators
        target_platforms: Target distribution platforms
        territories: Target regions
        rights_data: Rights information
        technical_specs: Technical specifications

    Returns:
        Distribution screening results
    """
    policies = load_content_policies()

    required_edits = []

    # Determine ratings
    ratings = determine_content_rating(
        content_descriptors,
        policies["rating_systems"]
    )

    # Check platform eligibility
    platform_eligibility = check_platform_eligibility(
        content_type,
        content_descriptors,
        ratings,
        target_platforms,
        policies["platforms"]
    )

    # Check territory rights
    territory_check = check_territory_rights(territories, rights_data)

    # Check technical specs (using first platform as reference)
    first_platform = target_platforms[0] if target_platforms else "default"
    platform_tech_req = policies["platforms"].get(
        first_platform, {}
    ).get("technical_requirements", {})
    tech_check = check_technical_specs(technical_specs, platform_tech_req)

    # Determine overall status
    all_platforms_approved = all(
        p["status"] == "approved"
        for p in platform_eligibility.values()
    )
    has_rights_issues = len(territory_check["restrictions"]) > 0
    tech_compliant = tech_check["meets_requirements"]

    if not all_platforms_approved:
        blocked_platforms = [
            p for p, s in platform_eligibility.items()
            if s["status"] == "blocked"
        ]
        if blocked_platforms:
            distribution_status = "BLOCKED"
        else:
            distribution_status = "RESTRICTED"
    elif has_rights_issues:
        distribution_status = "RESTRICTED"
    elif not tech_compliant:
        distribution_status = "PENDING_TECHNICAL"
    else:
        distribution_status = "APPROVED"

    # Generate required edits
    for platform, status in platform_eligibility.items():
        for issue in status.get("issues", []):
            if "Restricted" in issue:
                descriptor = issue.split(": ")[-1]
                required_edits.append({
                    "platform": platform,
                    "edit_type": "content_removal",
                    "description": f"Remove or modify {descriptor} for {platform}"
                })

    if not tech_compliant:
        for issue in tech_check["issues"]:
            required_edits.append({
                "platform": "all",
                "edit_type": "technical",
                "description": issue
            })

    return {
        "content_id": content_id,
        "content_type": content_type,
        "distribution_status": distribution_status,
        "content_rating": ratings,
        "platform_eligibility": platform_eligibility,
        "territory_restrictions": territory_check["restrictions"],
        "territory_status": territory_check["status_by_territory"],
        "required_edits": required_edits,
        "technical_compliance": tech_check
    }


if __name__ == "__main__":
    import json
    result = screen_content(
        content_id="MOV-2024-001",
        content_type="movie",
        content_descriptors=["violence_moderate", "language_mild"],
        target_platforms=["streaming_premium", "broadcast_basic"],
        territories=["US", "UK", "DE"],
        rights_data={"us": "exclusive", "uk": "non-exclusive", "de": "exclusive"},
        technical_specs={"resolution": "4K", "hdr": True, "codec": "H.265"}
    )
    print(json.dumps(result, indent=2))
