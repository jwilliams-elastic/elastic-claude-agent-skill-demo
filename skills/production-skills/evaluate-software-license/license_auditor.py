"""
Software License Compliance Evaluation Module

Implements license metric calculations and compliance assessment
across different software vendors and licensing models.
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


def load_licensing_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    vendors_data = load_csv_as_dict("vendors.csv")
    params = load_parameters()
    return {
        "vendors": vendors_data,
        **params
    }


def calculate_processor_licenses(
    deployments: List[Dict],
    core_factor: float,
    virtualization_rules: Dict,
    virtualization_info: Dict
) -> Dict[str, Any]:
    """Calculate processor license requirements."""
    total_licenses_required = 0
    deployment_details = []

    for deploy in deployments:
        cores = deploy.get("cores", 0)
        environment = deploy.get("environment", "production")

        # Apply virtualization rules
        platform = virtualization_info.get("platform", "physical")
        soft_partition = virtualization_info.get("soft_partition", False)

        if platform in virtualization_rules.get("full_host_platforms", []):
            if not soft_partition:
                # Must license full host
                host_cores = deploy.get("host_cores", cores * 2)
                effective_cores = host_cores
            else:
                effective_cores = cores
        else:
            effective_cores = cores

        # Apply core factor
        licenses_needed = effective_cores * core_factor
        licenses_needed = max(2, licenses_needed)  # Minimum 2 processor licenses

        # Round up to whole numbers
        licenses_needed = int(licenses_needed + 0.5)

        total_licenses_required += licenses_needed

        deployment_details.append({
            "server": deploy.get("server"),
            "cores": cores,
            "effective_cores": effective_cores,
            "licenses_required": licenses_needed,
            "environment": environment
        })

    return {
        "total_required": total_licenses_required,
        "deployment_details": deployment_details
    }


def check_feature_edition(
    features_in_use: List[str],
    edition_features: Dict,
    current_edition: str
) -> Dict[str, Any]:
    """Check if features require higher edition."""
    required_edition = current_edition
    unlicensed_features = []

    edition_hierarchy = ["standard", "enterprise", "platinum"]

    current_level = edition_hierarchy.index(current_edition.lower()) if current_edition.lower() in edition_hierarchy else 0

    for feature in features_in_use:
        for edition, features_list in edition_features.items():
            if feature.lower() in [f.lower() for f in features_list]:
                feature_level = edition_hierarchy.index(edition.lower()) if edition.lower() in edition_hierarchy else 0

                if feature_level > current_level:
                    unlicensed_features.append({
                        "feature": feature,
                        "requires_edition": edition,
                        "current_edition": current_edition
                    })

                    if edition_hierarchy.index(edition.lower()) > edition_hierarchy.index(required_edition.lower()):
                        required_edition = edition

    return {
        "required_edition": required_edition,
        "edition_upgrade_needed": required_edition.lower() != current_edition.lower(),
        "unlicensed_features": unlicensed_features
    }


def calculate_true_up_cost(
    license_gap: int,
    unit_price: float,
    edition_upgrade: bool,
    edition_upgrade_cost: float
) -> Dict[str, Any]:
    """Calculate true-up cost estimate."""
    license_cost = max(0, license_gap) * unit_price
    upgrade_cost = edition_upgrade_cost if edition_upgrade else 0

    return {
        "license_cost": license_cost,
        "edition_upgrade_cost": upgrade_cost,
        "total_true_up": license_cost + upgrade_cost,
        "annual_maintenance_impact": (license_cost + upgrade_cost) * 0.22
    }


def identify_optimization_opportunities(
    deployments: List[Dict],
    usage_data: Dict,
    entitlements: Dict
) -> List[Dict]:
    """Identify license optimization opportunities."""
    opportunities = []

    # Check for non-production environments
    non_prod_deploys = [d for d in deployments if d.get("environment") != "production"]
    if non_prod_deploys:
        opportunities.append({
            "type": "non_production_licensing",
            "description": "Consider non-production licensing options for dev/test environments",
            "potential_savings_pct": 75
        })

    # Check for over-licensing
    if entitlements.get("processor_licenses", 0) > len(deployments) * 4:
        opportunities.append({
            "type": "over_licensing",
            "description": "Potential excess licenses - consider downsizing or redeployment",
            "potential_savings_pct": 20
        })

    # Check usage patterns
    peak_users = usage_data.get("peak_users", 0)
    avg_concurrent = usage_data.get("avg_concurrent", 0)

    if peak_users > 0 and avg_concurrent / peak_users < 0.3:
        opportunities.append({
            "type": "named_to_concurrent",
            "description": "Low concurrent usage ratio - consider named user to concurrent model",
            "potential_savings_pct": 40
        })

    return opportunities


def evaluate_compliance(
    software_product: str,
    vendor: str,
    deployments: List[Dict],
    entitlements: Dict,
    usage_data: Dict,
    virtualization_info: Dict,
    features_in_use: List[str]
) -> Dict[str, Any]:
    """
    Evaluate software license compliance.

    Business Rules:
    1. License metric calculation by type
    2. Virtualization licensing rules
    3. Feature-to-edition mapping
    4. Maintenance coverage validation

    Args:
        software_product: Product name
        vendor: Software vendor
        deployments: Deployment details
        entitlements: Purchased licenses
        usage_data: Usage metrics
        virtualization_info: Virtual environment info
        features_in_use: Active features

    Returns:
        Compliance assessment results
    """
    rules = load_licensing_rules()

    vendor_rules = rules["vendors"].get(vendor, rules["vendors"]["default"])
    product_rules = vendor_rules["products"].get(software_product, vendor_rules["products"]["default"])

    risks = []

    # Calculate processor licenses
    processor_calc = calculate_processor_licenses(
        deployments,
        product_rules["core_factor"],
        vendor_rules["virtualization"],
        virtualization_info
    )

    # License position
    processor_entitled = entitlements.get("processor_licenses", 0)
    processor_required = processor_calc["total_required"]
    processor_gap = processor_required - processor_entitled

    # Check edition requirements
    edition_check = check_feature_edition(
        features_in_use,
        product_rules["edition_features"],
        entitlements.get("edition", "standard")
    )

    # Determine compliance status
    if processor_gap > 0:
        compliance_status = "NON_COMPLIANT"
        risks.append({
            "type": "license_shortfall",
            "severity": "high",
            "description": f"Under-licensed by {processor_gap} processor licenses"
        })
    elif edition_check["edition_upgrade_needed"]:
        compliance_status = "NON_COMPLIANT"
        risks.append({
            "type": "edition_mismatch",
            "severity": "high",
            "description": f"Features require {edition_check['required_edition']} edition"
        })
    elif processor_gap < -4:
        compliance_status = "OVER_LICENSED"
        risks.append({
            "type": "over_licensing",
            "severity": "low",
            "description": f"Over-licensed by {abs(processor_gap)} processor licenses"
        })
    else:
        compliance_status = "COMPLIANT"

    # Calculate true-up cost
    true_up = calculate_true_up_cost(
        processor_gap,
        product_rules["list_price_per_processor"],
        edition_check["edition_upgrade_needed"],
        product_rules.get("edition_upgrade_cost", 50000)
    )

    # Identify optimization opportunities
    optimization_opportunities = identify_optimization_opportunities(
        deployments,
        usage_data,
        entitlements
    )

    return {
        "software_product": software_product,
        "vendor": vendor,
        "compliance_status": compliance_status,
        "license_position": {
            "entitled": processor_entitled,
            "required": processor_required,
            "gap": processor_gap,
            "deployment_details": processor_calc["deployment_details"]
        },
        "edition_analysis": edition_check,
        "true_up_cost": true_up["total_true_up"],
        "true_up_details": true_up,
        "optimization_opportunities": optimization_opportunities,
        "risk_assessment": {
            "risks": risks,
            "audit_exposure": true_up["total_true_up"] * 1.5 if compliance_status == "NON_COMPLIANT" else 0
        }
    }


if __name__ == "__main__":
    import json
    result = evaluate_compliance(
        software_product="Enterprise Database",
        vendor="Oracle",
        deployments=[
            {"server": "db-prod-01", "cores": 16, "environment": "production"},
            {"server": "db-prod-02", "cores": 16, "environment": "production"},
            {"server": "db-dev-01", "cores": 8, "environment": "development"}
        ],
        entitlements={"processor_licenses": 8, "edition": "enterprise"},
        usage_data={"peak_users": 150, "avg_concurrent": 45},
        virtualization_info={"platform": "vmware", "soft_partition": True},
        features_in_use=["partitioning", "advanced_compression", "real_application_clusters"]
    )
    print(json.dumps(result, indent=2))
