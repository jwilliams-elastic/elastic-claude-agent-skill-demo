"""
M&A Technology Synergy Evaluation Module

Evaluates technology synergy potential in M&A transactions by analyzing
platform consolidation, tech stack compatibility, talent retention,
and integration complexity for deal teams and operating partners.
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


# Platform compatibility matrix
PLATFORM_COMPATIBILITY = {
    ("SAP S/4HANA", "SAP S/4HANA"): {"compatibility": "high", "migration_cost_factor": 0.1},
    ("SAP S/4HANA", "SAP ECC"): {"compatibility": "medium", "migration_cost_factor": 0.4},
    ("SAP S/4HANA", "Oracle EBS"): {"compatibility": "low", "migration_cost_factor": 0.8},
    ("SAP S/4HANA", "Oracle Cloud"): {"compatibility": "low", "migration_cost_factor": 0.7},
    ("SAP S/4HANA", "Microsoft Dynamics"): {"compatibility": "low", "migration_cost_factor": 0.75},
    ("Oracle EBS", "Oracle EBS"): {"compatibility": "high", "migration_cost_factor": 0.1},
    ("Oracle EBS", "Oracle Cloud"): {"compatibility": "medium", "migration_cost_factor": 0.5},
    ("Oracle Cloud", "Oracle Cloud"): {"compatibility": "high", "migration_cost_factor": 0.15},
    ("Microsoft Dynamics", "Microsoft Dynamics"): {"compatibility": "high", "migration_cost_factor": 0.1},
    ("Workday", "Workday"): {"compatibility": "high", "migration_cost_factor": 0.1},
    ("Salesforce", "Salesforce"): {"compatibility": "high", "migration_cost_factor": 0.15},
}

# Cloud provider compatibility
CLOUD_COMPATIBILITY = {
    ("aws", "aws"): {"compatibility": "high", "migration_effort": 0.1},
    ("azure", "azure"): {"compatibility": "high", "migration_effort": 0.1},
    ("gcp", "gcp"): {"compatibility": "high", "migration_effort": 0.1},
    ("aws", "azure"): {"compatibility": "medium", "migration_effort": 0.5},
    ("aws", "gcp"): {"compatibility": "medium", "migration_effort": 0.5},
    ("azure", "gcp"): {"compatibility": "medium", "migration_effort": 0.5},
    ("on_prem", "aws"): {"compatibility": "low", "migration_effort": 0.8},
    ("on_prem", "azure"): {"compatibility": "low", "migration_effort": 0.8},
    ("on_prem", "gcp"): {"compatibility": "low", "migration_effort": 0.8},
    ("on_prem", "on_prem"): {"compatibility": "medium", "migration_effort": 0.3},
}

# Tech debt impact factors
TECH_DEBT_FACTORS = {
    "low": {"integration_overhead": 0.05, "timeline_extension": 0},
    "medium": {"integration_overhead": 0.15, "timeline_extension": 3},
    "high": {"integration_overhead": 0.30, "timeline_extension": 6},
    "critical": {"integration_overhead": 0.50, "timeline_extension": 12}
}

# Integration strategy characteristics
INTEGRATION_STRATEGIES = {
    "absorption": {
        "description": "Full integration into acquirer's platform",
        "synergy_realization": 0.85,
        "risk_level": "medium",
        "timeline_months": 18
    },
    "best_of_breed": {
        "description": "Select best platform from either company",
        "synergy_realization": 0.70,
        "risk_level": "high",
        "timeline_months": 24
    },
    "transformation": {
        "description": "Move both to new platform",
        "synergy_realization": 0.90,
        "risk_level": "very_high",
        "timeline_months": 36
    },
    "preservation": {
        "description": "Maintain separate platforms",
        "synergy_realization": 0.30,
        "risk_level": "low",
        "timeline_months": 6
    }
}


def calculate_platform_synergy(
    acquirer_tech_spend: float,
    target_tech_spend: float,
    acquirer_erp: str,
    target_erp: str,
    integration_strategy: str
) -> Dict[str, Any]:
    """Calculate platform consolidation synergies."""
    # Get platform compatibility
    compat_key = (acquirer_erp, target_erp)
    reverse_key = (target_erp, acquirer_erp)

    compatibility = PLATFORM_COMPATIBILITY.get(
        compat_key,
        PLATFORM_COMPATIBILITY.get(reverse_key, {"compatibility": "low", "migration_cost_factor": 0.7})
    )

    # Base synergy from platform consolidation (40-60% per business rules)
    if compatibility["compatibility"] == "high":
        synergy_pct = 0.55
    elif compatibility["compatibility"] == "medium":
        synergy_pct = 0.45
    else:
        synergy_pct = 0.35

    # Adjust for integration strategy
    strategy_factor = INTEGRATION_STRATEGIES[integration_strategy]["synergy_realization"]
    adjusted_synergy_pct = synergy_pct * strategy_factor

    # Calculate dollar synergy (on smaller tech spend)
    smaller_spend = min(acquirer_tech_spend, target_tech_spend)
    annual_synergy = smaller_spend * adjusted_synergy_pct

    # Migration cost
    migration_cost = smaller_spend * compatibility["migration_cost_factor"]

    return {
        "annual_synergy": round(annual_synergy, 2),
        "compatibility": compatibility["compatibility"],
        "migration_cost": round(migration_cost, 2),
        "synergy_pct_achieved": round(adjusted_synergy_pct * 100, 1)
    }


def calculate_infrastructure_synergy(
    target_tech_spend: float,
    acquirer_cloud: str,
    target_cloud: str
) -> Dict[str, Any]:
    """Calculate infrastructure rationalization synergies."""
    # Get cloud compatibility
    compat_key = (acquirer_cloud, target_cloud)
    reverse_key = (target_cloud, acquirer_cloud)

    compatibility = CLOUD_COMPATIBILITY.get(
        compat_key,
        CLOUD_COMPATIBILITY.get(reverse_key, {"compatibility": "low", "migration_effort": 0.7})
    )

    # Infrastructure portion of tech spend (typically 30-40%)
    infra_spend = target_tech_spend * 0.35

    # Base synergy (25-35% per business rules)
    if compatibility["compatibility"] == "high":
        synergy_pct = 0.35
    elif compatibility["compatibility"] == "medium":
        synergy_pct = 0.30
    else:
        synergy_pct = 0.25

    annual_synergy = infra_spend * synergy_pct
    migration_cost = infra_spend * compatibility["migration_effort"]

    return {
        "annual_synergy": round(annual_synergy, 2),
        "cloud_compatibility": compatibility["compatibility"],
        "migration_cost": round(migration_cost, 2)
    }


def calculate_application_synergy(
    acquirer_app_count: int,
    target_app_count: int,
    overlap_pct: float
) -> Dict[str, Any]:
    """Calculate application portfolio rationalization synergies."""
    # Calculate overlapping applications
    overlap_apps = int(min(acquirer_app_count, target_app_count) * (overlap_pct / 100))

    # Per-application savings ($150K-$500K per business rules, use midpoint)
    per_app_savings = 325000  # $325K average

    # Year 1: 30% of apps retired, Year 2: 60%, Year 3: remaining
    year1_retirements = int(overlap_apps * 0.30)
    year2_retirements = int(overlap_apps * 0.30)
    year3_retirements = overlap_apps - year1_retirements - year2_retirements

    year1_synergy = year1_retirements * per_app_savings * 0.5  # Half year benefit
    year2_synergy = (year1_retirements + year2_retirements) * per_app_savings
    year3_synergy = overlap_apps * per_app_savings

    return {
        "redundant_applications": overlap_apps,
        "year1_synergy": round(year1_synergy / 1_000_000, 2),  # In $M
        "year2_synergy": round(year2_synergy / 1_000_000, 2),
        "year3_synergy": round(year3_synergy / 1_000_000, 2),
        "per_app_savings": per_app_savings
    }


def calculate_talent_retention_cost(
    target_tech_headcount: int,
    critical_talent_count: int,
    avg_tech_salary: float = 150000
) -> Dict[str, Any]:
    """Calculate tech talent retention costs."""
    # Retention premium 15-25% per business rules
    retention_premium_pct = 0.20  # Use midpoint

    # Critical talent retention packages
    critical_retention = critical_talent_count * avg_tech_salary * retention_premium_pct * 1.5  # 18 months

    # Broader retention programs
    general_retention = (target_tech_headcount - critical_talent_count) * avg_tech_salary * 0.10

    # Attrition risk (typically 15-25% in first year post-merger)
    expected_attrition_pct = 0.20
    attrition_replacement_cost = int(target_tech_headcount * expected_attrition_pct) * avg_tech_salary * 0.5

    total_retention_cost = critical_retention + general_retention + attrition_replacement_cost

    return {
        "critical_talent_retention": round(critical_retention / 1_000_000, 2),
        "general_retention": round(general_retention / 1_000_000, 2),
        "attrition_replacement": round(attrition_replacement_cost / 1_000_000, 2),
        "total_retention_cost": round(total_retention_cost / 1_000_000, 2),
        "expected_attrition_pct": expected_attrition_pct * 100
    }


def calculate_integration_complexity(
    acquirer_app_count: int,
    target_app_count: int,
    acquirer_cloud: str,
    target_cloud: str,
    tech_debt_rating: str,
    integration_strategy: str
) -> Dict[str, Any]:
    """Calculate integration complexity score (1-10)."""
    score = 5  # Start at midpoint

    # Application portfolio size impact
    total_apps = acquirer_app_count + target_app_count
    if total_apps > 300:
        score += 2
    elif total_apps > 150:
        score += 1
    elif total_apps < 50:
        score -= 1

    # Cloud compatibility impact
    compat_key = (acquirer_cloud, target_cloud)
    cloud_compat = CLOUD_COMPATIBILITY.get(compat_key, {"compatibility": "low"})
    if cloud_compat["compatibility"] == "low":
        score += 2
    elif cloud_compat["compatibility"] == "medium":
        score += 1

    # Tech debt impact
    if tech_debt_rating == "critical":
        score += 2
    elif tech_debt_rating == "high":
        score += 1
    elif tech_debt_rating == "low":
        score -= 1

    # Integration strategy impact
    if integration_strategy == "transformation":
        score += 2
    elif integration_strategy == "best_of_breed":
        score += 1
    elif integration_strategy == "preservation":
        score -= 2

    score = max(1, min(10, score))

    complexity_label = "Low" if score <= 3 else "Medium" if score <= 6 else "High" if score <= 8 else "Very High"

    return {
        "score": score,
        "label": complexity_label,
        "factors": {
            "application_portfolio": total_apps,
            "cloud_heterogeneity": cloud_compat["compatibility"] != "high",
            "tech_debt": tech_debt_rating,
            "strategy_complexity": integration_strategy
        }
    }


def identify_risk_factors(
    complexity_score: int,
    tech_debt_rating: str,
    critical_talent_count: int,
    integration_strategy: str,
    deal_timeline_months: int
) -> List[Dict[str, Any]]:
    """Identify key integration risk factors."""
    risks = []

    if complexity_score >= 8:
        risks.append({
            "risk": "High integration complexity",
            "likelihood": "high",
            "impact": "high",
            "mitigation": "Engage experienced integration PMO; consider phased approach"
        })

    if tech_debt_rating in ["high", "critical"]:
        risks.append({
            "risk": "Technical debt compounds integration challenges",
            "likelihood": "high",
            "impact": "medium",
            "mitigation": "Budget for remediation; prioritize critical systems"
        })

    if critical_talent_count > 20:
        risks.append({
            "risk": "Key person dependency",
            "likelihood": "medium",
            "impact": "high",
            "mitigation": "Accelerate knowledge transfer; implement retention packages Day 1"
        })

    if integration_strategy == "transformation":
        risks.append({
            "risk": "Transformation scope creep",
            "likelihood": "high",
            "impact": "high",
            "mitigation": "Define clear scope boundaries; implement change control"
        })

    if deal_timeline_months < 6:
        risks.append({
            "risk": "Compressed timeline",
            "likelihood": "high",
            "impact": "medium",
            "mitigation": "Focus on critical path items; defer non-essential integration"
        })

    risks.append({
        "risk": "Business disruption during cutover",
        "likelihood": "medium",
        "impact": "high",
        "mitigation": "Implement robust rollback plans; schedule during low-activity periods"
    })

    return risks


def identify_deal_breakers(
    complexity_score: int,
    tech_debt_rating: str,
    synergy_confidence: str,
    integration_cost_ratio: float
) -> List[Dict[str, str]]:
    """Identify critical issues that could derail integration."""
    deal_breakers = []

    if tech_debt_rating == "critical" and complexity_score >= 8:
        deal_breakers.append({
            "issue": "Unsustainable technical debt combined with high complexity",
            "severity": "critical",
            "recommendation": "Require remediation escrow or price adjustment"
        })

    if integration_cost_ratio > 0.5:
        deal_breakers.append({
            "issue": "Integration costs exceed 50% of expected synergies",
            "severity": "high",
            "recommendation": "Re-evaluate deal economics or integration approach"
        })

    if synergy_confidence == "low":
        deal_breakers.append({
            "issue": "Low confidence in synergy realization",
            "severity": "medium",
            "recommendation": "Conduct deeper technical due diligence"
        })

    return deal_breakers


def generate_quick_wins(
    acquirer_cloud: str,
    target_cloud: str,
    overlap_pct: float
) -> List[Dict[str, str]]:
    """Identify Day 1-100 synergy opportunities."""
    quick_wins = []

    quick_wins.append({
        "initiative": "Vendor contract consolidation",
        "timeline": "Day 1-30",
        "estimated_value": "5-10% of combined software spend",
        "complexity": "Low"
    })

    quick_wins.append({
        "initiative": "Eliminate duplicate SaaS subscriptions",
        "timeline": "Day 1-60",
        "estimated_value": "$500K-$2M annually",
        "complexity": "Low"
    })

    if acquirer_cloud == target_cloud:
        quick_wins.append({
            "initiative": "Cloud reserved instance optimization",
            "timeline": "Day 30-60",
            "estimated_value": "15-20% cloud cost reduction",
            "complexity": "Low"
        })

    if overlap_pct > 30:
        quick_wins.append({
            "initiative": "Redundant tool consolidation (monitoring, CI/CD)",
            "timeline": "Day 60-100",
            "estimated_value": "$200K-$1M annually",
            "complexity": "Medium"
        })

    quick_wins.append({
        "initiative": "Security tool consolidation",
        "timeline": "Day 30-90",
        "estimated_value": "$300K-$800K annually",
        "complexity": "Medium"
    })

    return quick_wins


def generate_integration_approach(
    integration_strategy: str,
    complexity_score: int,
    deal_timeline_months: int
) -> Dict[str, Any]:
    """Generate recommended integration approach."""
    strategy_details = INTEGRATION_STRATEGIES[integration_strategy]

    # Phase definitions
    phases = [
        {
            "phase": 1,
            "name": "Stabilization",
            "duration": "Day 1-90",
            "focus": "Maintain business continuity, implement quick wins",
            "key_activities": [
                "Establish integration governance",
                "Execute talent retention plans",
                "Consolidate vendor contracts",
                "Implement interim connectivity"
            ]
        },
        {
            "phase": 2,
            "name": "Foundation",
            "duration": "Month 3-9",
            "focus": "Build integration infrastructure",
            "key_activities": [
                "Deploy integration middleware",
                "Migrate non-critical applications",
                "Consolidate infrastructure",
                "Harmonize data models"
            ]
        },
        {
            "phase": 3,
            "name": "Transformation",
            "duration": "Month 9-18",
            "focus": "Platform consolidation",
            "key_activities": [
                "Migrate core platforms",
                "Retire redundant applications",
                "Complete data migration",
                "Achieve target state architecture"
            ]
        },
        {
            "phase": 4,
            "name": "Optimization",
            "duration": "Month 18-24",
            "focus": "Realize full synergies",
            "key_activities": [
                "Optimize combined platform",
                "Implement advanced capabilities",
                "Complete FTE optimization",
                "Measure synergy realization"
            ]
        }
    ]

    return {
        "strategy": integration_strategy,
        "strategy_description": strategy_details["description"],
        "expected_timeline_months": strategy_details["timeline_months"],
        "risk_level": strategy_details["risk_level"],
        "phases": phases
    }


def evaluate_synergy(
    deal_name: str,
    acquirer_name: str,
    target_name: str,
    acquirer_tech_spend: float,
    target_tech_spend: float,
    acquirer_erp: str,
    target_erp: str,
    acquirer_cloud_provider: str,
    target_cloud_provider: str,
    acquirer_app_count: int,
    target_app_count: int,
    estimated_app_overlap_pct: float,
    target_tech_headcount: int,
    critical_tech_talent_count: int,
    target_tech_debt_rating: str,
    integration_strategy: str,
    deal_timeline_months: int
) -> Dict[str, Any]:
    """
    Evaluate technology synergy potential for M&A transaction.

    Returns comprehensive synergy analysis with estimates, risks,
    integration approach, and recommendations.
    """
    # Calculate synergies
    platform_synergy = calculate_platform_synergy(
        acquirer_tech_spend, target_tech_spend,
        acquirer_erp, target_erp, integration_strategy
    )

    infra_synergy = calculate_infrastructure_synergy(
        target_tech_spend, acquirer_cloud_provider, target_cloud_provider
    )

    app_synergy = calculate_application_synergy(
        acquirer_app_count, target_app_count, estimated_app_overlap_pct
    )

    talent_costs = calculate_talent_retention_cost(
        target_tech_headcount, critical_tech_talent_count
    )

    # Calculate integration complexity
    complexity = calculate_integration_complexity(
        acquirer_app_count, target_app_count,
        acquirer_cloud_provider, target_cloud_provider,
        target_tech_debt_rating, integration_strategy
    )

    # Aggregate synergies by year
    tech_debt_factors = TECH_DEBT_FACTORS[target_tech_debt_rating]

    # Year 1: Infrastructure savings begin, partial platform
    year1_synergy = (
        infra_synergy["annual_synergy"] * 0.5 +
        app_synergy["year1_synergy"]
    ) * (1 - tech_debt_factors["integration_overhead"])

    # Year 2: Full infrastructure + platform + applications
    year2_synergy = (
        infra_synergy["annual_synergy"] +
        platform_synergy["annual_synergy"] * 0.6 +
        app_synergy["year2_synergy"]
    ) * (1 - tech_debt_factors["integration_overhead"] * 0.5)

    # Year 3: Run-rate
    year3_synergy = (
        infra_synergy["annual_synergy"] +
        platform_synergy["annual_synergy"] +
        app_synergy["year3_synergy"]
    )

    run_rate_synergy = year3_synergy

    # Calculate integration costs
    one_time_costs = (
        platform_synergy["migration_cost"] +
        infra_synergy["migration_cost"] +
        talent_costs["total_retention_cost"]
    )

    # Synergy confidence
    if complexity["score"] <= 4 and platform_synergy["compatibility"] == "high":
        synergy_confidence = "high"
    elif complexity["score"] <= 6:
        synergy_confidence = "medium"
    else:
        synergy_confidence = "low"

    # Calculate payback
    total_3yr_synergy = year1_synergy + year2_synergy + year3_synergy
    if total_3yr_synergy > 0:
        payback_months = int((one_time_costs / (total_3yr_synergy / 3)) * 12)
    else:
        payback_months = 999

    # Get risk factors and deal breakers
    risks = identify_risk_factors(
        complexity["score"], target_tech_debt_rating,
        critical_tech_talent_count, integration_strategy, deal_timeline_months
    )

    integration_cost_ratio = one_time_costs / total_3yr_synergy if total_3yr_synergy > 0 else 1
    deal_breakers = identify_deal_breakers(
        complexity["score"], target_tech_debt_rating,
        synergy_confidence, integration_cost_ratio
    )

    # Get quick wins and integration approach
    quick_wins = generate_quick_wins(
        acquirer_cloud_provider, target_cloud_provider, estimated_app_overlap_pct
    )

    integration_approach = generate_integration_approach(
        integration_strategy, complexity["score"], deal_timeline_months
    )

    return {
        "deal_name": deal_name,
        "acquirer": acquirer_name,
        "target": target_name,
        "total_synergy_estimate": {
            "year1": round(year1_synergy, 2),
            "year2": round(year2_synergy, 2),
            "year3": round(year3_synergy, 2),
            "run_rate": round(run_rate_synergy, 2)
        },
        "synergy_confidence": synergy_confidence,
        "synergy_breakdown": {
            "platform": platform_synergy,
            "infrastructure": infra_synergy,
            "applications": app_synergy
        },
        "integration_complexity_score": complexity["score"],
        "integration_complexity_label": complexity["label"],
        "integration_risk_factors": risks,
        "talent_retention_cost": talent_costs["total_retention_cost"],
        "one_time_integration_cost": round(one_time_costs, 2),
        "payback_months": payback_months,
        "recommended_integration_approach": integration_approach,
        "quick_wins": quick_wins,
        "deal_breakers": deal_breakers
    }


def main():
    """Example usage."""
    result = evaluate_synergy(
        deal_name="Project Atlas",
        acquirer_name="TechCorp",
        target_name="DataCo",
        acquirer_tech_spend=250,
        target_tech_spend=80,
        acquirer_erp="SAP S/4HANA",
        target_erp="Oracle EBS",
        acquirer_cloud_provider="aws",
        target_cloud_provider="azure",
        acquirer_app_count=200,
        target_app_count=75,
        estimated_app_overlap_pct=35,
        target_tech_headcount=150,
        critical_tech_talent_count=25,
        target_tech_debt_rating="medium",
        integration_strategy="absorption",
        deal_timeline_months=6
    )

    print(f"Deal: {result['deal_name']}")
    print(f"Run-Rate Synergy: ${result['total_synergy_estimate']['run_rate']}M")
    print(f"Integration Complexity: {result['integration_complexity_score']}/10")
    print(f"Synergy Confidence: {result['synergy_confidence']}")
    print(f"Payback: {result['payback_months']} months")
    print(f"Deal Breakers: {len(result['deal_breakers'])}")


if __name__ == "__main__":
    main()
