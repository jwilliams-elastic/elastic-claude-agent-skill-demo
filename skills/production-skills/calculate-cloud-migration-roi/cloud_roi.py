"""
Cloud Migration ROI Calculator Module

Calculates comprehensive ROI and TCO analysis for cloud migration initiatives,
comparing on-premises costs against public cloud scenarios.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_csv_as_dict(filename: str, key_column: str) -> Dict[str, Dict[str, Any]]:
    """Load a CSV file and return as dictionary keyed by specified column."""
    csv_path = Path(__file__).parent / filename
    result = {}
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = row.pop(key_column, row.get('id', ''))
            for k, v in list(row.items()):
                if v == '':
                    continue
                try:
                    if '.' in str(v):
                        row[k] = float(v)
                    else:
                        row[k] = int(v)
                except (ValueError, TypeError):
                    pass
            result[key] = row
    return result


def get_cloud_pricing(provider: str, architecture: str) -> Dict[str, float]:
    """Get cloud pricing factors by provider and architecture."""
    pricing = {
        "aws": {
            "iaas": {"compute_per_unit": 150, "storage_per_tb": 23, "network_per_tb": 90},
            "paas": {"compute_per_unit": 200, "storage_per_tb": 25, "network_per_tb": 90},
            "serverless": {"compute_per_unit": 100, "storage_per_tb": 23, "network_per_tb": 90},
            "saas": {"compute_per_unit": 0, "storage_per_tb": 0, "network_per_tb": 0}
        },
        "azure": {
            "iaas": {"compute_per_unit": 145, "storage_per_tb": 21, "network_per_tb": 87},
            "paas": {"compute_per_unit": 190, "storage_per_tb": 24, "network_per_tb": 87},
            "serverless": {"compute_per_unit": 95, "storage_per_tb": 21, "network_per_tb": 87},
            "saas": {"compute_per_unit": 0, "storage_per_tb": 0, "network_per_tb": 0}
        },
        "gcp": {
            "iaas": {"compute_per_unit": 140, "storage_per_tb": 20, "network_per_tb": 85},
            "paas": {"compute_per_unit": 185, "storage_per_tb": 22, "network_per_tb": 85},
            "serverless": {"compute_per_unit": 90, "storage_per_tb": 20, "network_per_tb": 85},
            "saas": {"compute_per_unit": 0, "storage_per_tb": 0, "network_per_tb": 0}
        }
    }

    return pricing.get(provider, pricing["aws"]).get(architecture, pricing["aws"]["iaas"])


def get_migration_cost_factors(strategy: str) -> Dict[str, float]:
    """Get migration cost factors by strategy."""
    factors = {
        "rehost": {"effort_multiplier": 1.0, "risk_contingency": 0.15, "timeline_factor": 1.0},
        "replatform": {"effort_multiplier": 1.5, "risk_contingency": 0.25, "timeline_factor": 1.3},
        "refactor": {"effort_multiplier": 2.5, "risk_contingency": 0.40, "timeline_factor": 2.0},
        "repurchase": {"effort_multiplier": 0.5, "risk_contingency": 0.20, "timeline_factor": 0.8},
        "retain": {"effort_multiplier": 0.1, "risk_contingency": 0.05, "timeline_factor": 0.2}
    }

    return factors.get(strategy, factors["replatform"])


def get_labor_factors(architecture: str) -> Dict[str, float]:
    """Get FTE adjustment factors by architecture."""
    factors = {
        "iaas": {"infra_reduction": 0.30, "cloud_eng_increase": 0.20},
        "paas": {"infra_reduction": 0.45, "cloud_eng_increase": 0.15},
        "serverless": {"infra_reduction": 0.50, "cloud_eng_increase": 0.25},
        "saas": {"infra_reduction": 0.60, "cloud_eng_increase": 0.10}
    }

    return factors.get(architecture, factors["paas"])


def calculate_current_tco(
    infra_cost: float,
    license_cost: float,
    fte_count: float,
    avg_fte_cost: float,
    years: int = 3
) -> Dict[str, float]:
    """Calculate current on-premises TCO."""
    annual_labor = fte_count * avg_fte_cost
    annual_total = infra_cost + license_cost + annual_labor

    # Apply 5% annual increase for on-prem costs
    total_3yr = sum(annual_total * (1.05 ** i) for i in range(years))

    return {
        "annual_infrastructure": infra_cost,
        "annual_licensing": license_cost,
        "annual_labor": annual_labor,
        "annual_total": annual_total,
        "total_3yr": round(total_3yr, 2)
    }


def calculate_cloud_tco(
    compute_units: int,
    storage_tb: float,
    data_transfer_tb: float,
    provider: str,
    architecture: str,
    current_license_cost: float,
    fte_count: float,
    avg_fte_cost: float,
    migration_strategy: str,
    years: int = 3
) -> Dict[str, Any]:
    """Calculate cloud TCO."""
    pricing = get_cloud_pricing(provider, architecture)
    labor_factors = get_labor_factors(architecture)

    # Annual cloud infrastructure costs
    compute_cost = compute_units * pricing["compute_per_unit"] * 12
    storage_cost = storage_tb * pricing["storage_per_tb"] * 12
    network_cost = data_transfer_tb * pricing["network_per_tb"] * 12

    annual_infra = compute_cost + storage_cost + network_cost

    # License cost adjustment (cloud-native often reduces licensing)
    license_reduction = 0.20 if architecture in ["paas", "serverless", "saas"] else 0.0
    annual_license = current_license_cost * (1 - license_reduction)

    # Labor cost adjustment
    infra_fte_reduction = fte_count * labor_factors["infra_reduction"]
    cloud_eng_increase = fte_count * labor_factors["cloud_eng_increase"]
    net_fte = fte_count - infra_fte_reduction + cloud_eng_increase
    annual_labor = net_fte * avg_fte_cost

    annual_total = annual_infra + annual_license + annual_labor

    # Apply 3% annual increase for cloud (lower than on-prem)
    total_3yr = sum(annual_total * (1.03 ** i) for i in range(years))

    return {
        "annual_compute": round(compute_cost, 2),
        "annual_storage": round(storage_cost, 2),
        "annual_network": round(network_cost, 2),
        "annual_infrastructure": round(annual_infra, 2),
        "annual_licensing": round(annual_license, 2),
        "annual_labor": round(annual_labor, 2),
        "annual_total": round(annual_total, 2),
        "total_3yr": round(total_3yr, 2),
        "fte_after_migration": round(net_fte, 1)
    }


def calculate_migration_costs(
    current_infra_cost: float,
    migration_strategy: str,
    timeline_months: int,
    avg_fte_cost: float
) -> Dict[str, float]:
    """Calculate one-time migration costs."""
    factors = get_migration_cost_factors(migration_strategy)

    # Base migration cost as percentage of annual infra
    base_migration = current_infra_cost * 0.30 * factors["effort_multiplier"]

    # Phase breakdown
    discovery = base_migration * 0.05
    planning = base_migration * 0.10
    migration = base_migration * 0.60
    optimization = base_migration * 0.25

    # Risk contingency
    contingency = base_migration * factors["risk_contingency"]

    # Training and change management
    training = avg_fte_cost * 0.10 * 5  # 5 FTEs worth of training

    total = base_migration + contingency + training

    return {
        "discovery": round(discovery, 2),
        "planning": round(planning, 2),
        "migration": round(migration, 2),
        "optimization": round(optimization, 2),
        "contingency": round(contingency, 2),
        "training": round(training, 2),
        "total": round(total, 2)
    }


def identify_risk_factors(
    migration_strategy: str,
    compliance_requirements: List[str],
    compute_units: int,
    storage_tb: float
) -> List[Dict[str, str]]:
    """Identify key risk factors for the migration."""
    risks = []

    if migration_strategy == "refactor":
        risks.append({
            "risk": "Application refactoring complexity",
            "likelihood": "high",
            "impact": "high",
            "mitigation": "Implement phased refactoring with feature flags"
        })

    if "HIPAA" in compliance_requirements:
        risks.append({
            "risk": "HIPAA compliance validation",
            "likelihood": "medium",
            "impact": "critical",
            "mitigation": "Engage compliance team early; use HIPAA-eligible services"
        })

    if "SOC2" in compliance_requirements:
        risks.append({
            "risk": "SOC2 audit scope change",
            "likelihood": "medium",
            "impact": "medium",
            "mitigation": "Update SOC2 scope documentation; plan for re-audit"
        })

    if compute_units > 100:
        risks.append({
            "risk": "Large-scale migration coordination",
            "likelihood": "high",
            "impact": "medium",
            "mitigation": "Use migration waves; implement robust rollback"
        })

    if storage_tb > 500:
        risks.append({
            "risk": "Data migration duration and integrity",
            "likelihood": "medium",
            "impact": "high",
            "mitigation": "Use incremental sync; validate checksums"
        })

    risks.append({
        "risk": "Vendor lock-in",
        "likelihood": "medium",
        "impact": "medium",
        "mitigation": "Use cloud-agnostic services where possible; containerization"
    })

    return risks


def identify_hidden_costs(architecture: str, compliance_requirements: List[str]) -> List[Dict[str, Any]]:
    """Identify often-overlooked costs to budget for."""
    hidden_costs = [
        {"category": "Data egress fees", "estimated_pct": 5, "description": "Outbound data transfer charges often underestimated"},
        {"category": "Premium support", "estimated_pct": 3, "description": "Enterprise support agreements for production workloads"},
        {"category": "Security tooling", "estimated_pct": 8, "description": "Cloud-native security, SIEM, and monitoring tools"},
        {"category": "Reserved instance management", "estimated_pct": 2, "description": "FinOps tooling and unused reservation waste"}
    ]

    if architecture == "serverless":
        hidden_costs.append({
            "category": "Cold start optimization",
            "estimated_pct": 3,
            "description": "Engineering effort to optimize serverless performance"
        })

    if compliance_requirements:
        hidden_costs.append({
            "category": "Compliance tooling",
            "estimated_pct": 5,
            "description": "Cloud compliance monitoring and audit tools"
        })

    return hidden_costs


def calculate_sensitivity_analysis(
    base_savings: float,
    migration_cost: float
) -> Dict[str, Dict[str, float]]:
    """Calculate ROI under different scenarios."""
    return {
        "optimistic": {
            "savings_multiplier": 1.20,
            "total_savings": round(base_savings * 1.20, 2),
            "roi_pct": round(((base_savings * 1.20) - migration_cost) / migration_cost * 100, 1)
        },
        "base": {
            "savings_multiplier": 1.0,
            "total_savings": round(base_savings, 2),
            "roi_pct": round((base_savings - migration_cost) / migration_cost * 100, 1) if migration_cost > 0 else 0
        },
        "pessimistic": {
            "savings_multiplier": 0.70,
            "total_savings": round(base_savings * 0.70, 2),
            "roi_pct": round(((base_savings * 0.70) - migration_cost) / migration_cost * 100, 1) if migration_cost > 0 else 0
        }
    }


def calculate_migration_roi(
    workload_name: str,
    migration_strategy: str,
    current_infra_annual_cost: float,
    current_license_annual_cost: float,
    current_fte_count: float,
    avg_fte_cost: float,
    compute_units: int,
    storage_tb: float,
    data_transfer_tb_monthly: float,
    cloud_provider: str,
    target_architecture: str,
    compliance_requirements: List[str],
    migration_timeline_months: int
) -> Dict[str, Any]:
    """
    Calculate comprehensive ROI for cloud migration.

    Returns detailed analysis with TCO comparison, cost breakdown,
    risks, and sensitivity analysis.
    """
    # Calculate current TCO
    current_tco = calculate_current_tco(
        current_infra_annual_cost,
        current_license_annual_cost,
        current_fte_count,
        avg_fte_cost
    )

    # Calculate cloud TCO
    cloud_tco = calculate_cloud_tco(
        compute_units,
        storage_tb,
        data_transfer_tb_monthly,
        cloud_provider,
        target_architecture,
        current_license_annual_cost,
        current_fte_count,
        avg_fte_cost,
        migration_strategy
    )

    # Calculate migration costs
    migration_costs = calculate_migration_costs(
        current_infra_annual_cost,
        migration_strategy,
        migration_timeline_months,
        avg_fte_cost
    )

    # Calculate savings and ROI
    total_3yr_savings = current_tco["total_3yr"] - cloud_tco["total_3yr"] - migration_costs["total"]

    if migration_costs["total"] > 0:
        roi_percentage = (total_3yr_savings / migration_costs["total"]) * 100
    else:
        roi_percentage = 0

    # Calculate payback period
    annual_savings = current_tco["annual_total"] - cloud_tco["annual_total"]
    if annual_savings > 0:
        payback_months = int((migration_costs["total"] / annual_savings) * 12)
    else:
        payback_months = 999

    # Determine recommendation
    if roi_percentage > 50 and payback_months <= 24:
        recommendation = "proceed"
    elif roi_percentage > 20 and payback_months <= 36:
        recommendation = "conditional"
    else:
        recommendation = "defer"

    # Get risk factors
    risk_factors = identify_risk_factors(
        migration_strategy,
        compliance_requirements,
        compute_units,
        storage_tb
    )

    # Get hidden costs
    hidden_costs = identify_hidden_costs(target_architecture, compliance_requirements)

    # Sensitivity analysis
    sensitivity = calculate_sensitivity_analysis(
        current_tco["total_3yr"] - cloud_tco["total_3yr"],
        migration_costs["total"]
    )

    return {
        "workload_name": workload_name,
        "recommendation": recommendation,
        "total_3yr_savings": round(total_3yr_savings, 2),
        "roi_percentage": round(roi_percentage, 1),
        "payback_months": payback_months,
        "tco_comparison": {
            "current_3yr_tco": current_tco["total_3yr"],
            "cloud_3yr_tco": cloud_tco["total_3yr"],
            "migration_investment": migration_costs["total"],
            "net_savings": round(total_3yr_savings, 2)
        },
        "cost_breakdown": {
            "current_annual": current_tco,
            "cloud_annual": cloud_tco,
            "migration_one_time": migration_costs
        },
        "risk_factors": risk_factors,
        "sensitivity_analysis": sensitivity,
        "hidden_costs": hidden_costs
    }


def main():
    """Example usage."""
    result = calculate_migration_roi(
        workload_name="ERP System",
        migration_strategy="replatform",
        current_infra_annual_cost=2500000,
        current_license_annual_cost=800000,
        current_fte_count=12,
        avg_fte_cost=150000,
        compute_units=50,
        storage_tb=100,
        data_transfer_tb_monthly=5,
        cloud_provider="azure",
        target_architecture="paas",
        compliance_requirements=["SOC2", "GDPR"],
        migration_timeline_months=18
    )

    print(f"Workload: {result['workload_name']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"3-Year Savings: ${result['total_3yr_savings']:,.2f}")
    print(f"ROI: {result['roi_percentage']}%")
    print(f"Payback: {result['payback_months']} months")


if __name__ == "__main__":
    main()
