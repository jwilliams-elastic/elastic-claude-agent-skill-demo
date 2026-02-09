"""
Data Platform Maturity Assessment Module

Evaluates enterprise data platform maturity across data engineering, governance,
analytics, and ML operations dimensions based on DCAM and DAMA-DMBOK frameworks.
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


# Maturity level definitions
MATURITY_LEVELS = {
    1: {"label": "Initial", "description": "Ad-hoc processes, siloed data, minimal governance"},
    2: {"label": "Developing", "description": "Emerging standards, basic governance, reactive analytics"},
    3: {"label": "Defined", "description": "Documented processes, active governance, self-service BI"},
    4: {"label": "Managed", "description": "Measured and controlled, advanced analytics, ML in production"},
    5: {"label": "Optimizing", "description": "Continuous improvement, AI-driven, data mesh, full automation"}
}

# Industry benchmarks
INDUSTRY_BENCHMARKS = {
    "financial_services": {"avg_level": 3.4, "top_quartile": 4.2},
    "healthcare": {"avg_level": 2.8, "top_quartile": 3.6},
    "retail": {"avg_level": 3.1, "top_quartile": 3.9},
    "manufacturing": {"avg_level": 2.6, "top_quartile": 3.4},
    "technology": {"avg_level": 3.8, "top_quartile": 4.5},
    "telecommunications": {"avg_level": 3.2, "top_quartile": 4.0},
    "energy": {"avg_level": 2.5, "top_quartile": 3.3},
    "default": {"avg_level": 3.0, "top_quartile": 3.8}
}


def calculate_data_engineering_score(
    data_volume_tb: float,
    data_sources_count: int,
    real_time_pipelines: bool,
    cloud_platform: str
) -> Dict[str, Any]:
    """Calculate data engineering maturity dimension score."""
    score = 0
    findings = []

    # Volume handling capability
    if data_volume_tb > 1000:
        score += 25
        findings.append("Petabyte-scale data infrastructure")
    elif data_volume_tb > 100:
        score += 20
        findings.append("Enterprise-scale data volume")
    elif data_volume_tb > 10:
        score += 15
    else:
        score += 10
        findings.append("Limited data volume may indicate early maturity")

    # Data source integration
    if data_sources_count > 100:
        score += 25
        findings.append("Comprehensive data integration across enterprise")
    elif data_sources_count > 50:
        score += 20
    elif data_sources_count > 20:
        score += 15
    else:
        score += 10
        findings.append("Limited data source integration")

    # Real-time capability
    if real_time_pipelines:
        score += 25
        findings.append("Real-time/streaming data capabilities present")
    else:
        score += 10
        findings.append("Batch-only processing limits use cases")

    # Cloud platform maturity
    cloud_scores = {
        "databricks": 25,
        "snowflake": 25,
        "bigquery": 23,
        "azure_synapse": 20,
        "redshift": 18,
        "on_prem": 10
    }
    score += cloud_scores.get(cloud_platform, 15)

    return {
        "score": min(100, score),
        "findings": findings
    }


def calculate_data_governance_score(
    data_catalog_implemented: bool,
    data_lineage_automated: bool,
    data_quality_score: Optional[float]
) -> Dict[str, Any]:
    """Calculate data governance maturity dimension score."""
    score = 0
    findings = []

    # Data catalog
    if data_catalog_implemented:
        score += 35
        findings.append("Enterprise data catalog deployed")
    else:
        score += 10
        findings.append("Missing data catalog limits data discovery")

    # Data lineage
    if data_lineage_automated:
        score += 35
        findings.append("Automated lineage tracking enabled")
    else:
        score += 15
        findings.append("Manual/missing lineage creates compliance risk")

    # Data quality
    if data_quality_score is not None:
        if data_quality_score >= 90:
            score += 30
            findings.append("Excellent data quality metrics")
        elif data_quality_score >= 75:
            score += 25
        elif data_quality_score >= 60:
            score += 20
            findings.append("Data quality needs improvement")
        else:
            score += 10
            findings.append("Poor data quality undermines trust")
    else:
        score += 5
        findings.append("Data quality not measured")

    return {
        "score": min(100, score),
        "findings": findings
    }


def calculate_analytics_score(
    self_service_bi_adoption: float,
    data_quality_score: Optional[float]
) -> Dict[str, Any]:
    """Calculate analytics maturity dimension score."""
    score = 0
    findings = []

    # Self-service BI adoption
    if self_service_bi_adoption >= 70:
        score += 50
        findings.append("Strong self-service BI culture")
    elif self_service_bi_adoption >= 50:
        score += 40
        findings.append("Growing self-service adoption")
    elif self_service_bi_adoption >= 30:
        score += 30
        findings.append("Self-service BI adoption below industry norm")
    else:
        score += 15
        findings.append("Limited self-service analytics capability")

    # Analytics quality (based on data quality)
    if data_quality_score is not None:
        if data_quality_score >= 80:
            score += 50
        elif data_quality_score >= 60:
            score += 35
        else:
            score += 20
    else:
        score += 25

    return {
        "score": min(100, score),
        "findings": findings
    }


def calculate_mlops_score(
    ml_models_in_production: int,
    feature_store_implemented: bool,
    mlops_automation_level: str
) -> Dict[str, Any]:
    """Calculate MLOps maturity dimension score."""
    score = 0
    findings = []

    # Production ML models
    if ml_models_in_production >= 50:
        score += 35
        findings.append("Scaled ML deployment with 50+ production models")
    elif ml_models_in_production >= 20:
        score += 30
        findings.append("Growing ML portfolio")
    elif ml_models_in_production >= 5:
        score += 20
        findings.append("Early ML adoption")
    elif ml_models_in_production > 0:
        score += 10
        findings.append("Initial ML experimentation")
    else:
        score += 5
        findings.append("No ML models in production")

    # Feature store
    if feature_store_implemented:
        score += 30
        findings.append("Centralized feature store enables ML reuse")
    else:
        score += 10
        findings.append("Missing feature store limits ML scalability")

    # MLOps automation
    automation_scores = {
        "fully_automated": 35,
        "semi_automated": 25,
        "manual": 10
    }
    score += automation_scores.get(mlops_automation_level, 15)

    if mlops_automation_level == "manual":
        findings.append("Manual MLOps processes create deployment bottlenecks")
    elif mlops_automation_level == "fully_automated":
        findings.append("Automated ML pipelines enable rapid iteration")

    return {
        "score": min(100, score),
        "findings": findings
    }


def calculate_data_culture_score(
    data_literacy_program: bool,
    self_service_bi_adoption: float,
    data_mesh_adopted: bool
) -> Dict[str, Any]:
    """Calculate data culture maturity dimension score."""
    score = 0
    findings = []

    # Data literacy
    if data_literacy_program:
        score += 35
        findings.append("Formal data literacy program in place")
    else:
        score += 10
        findings.append("No formal data literacy training")

    # Democratization (self-service proxy)
    if self_service_bi_adoption >= 50:
        score += 30
        findings.append("Data democratization efforts succeeding")
    else:
        score += 15
        findings.append("Limited data democratization")

    # Data mesh / domain orientation
    if data_mesh_adopted:
        score += 35
        findings.append("Data mesh architecture enables domain ownership")
    else:
        score += 15

    return {
        "score": min(100, score),
        "findings": findings
    }


def calculate_overall_maturity(dimension_scores: Dict[str, float]) -> Dict[str, Any]:
    """Calculate overall maturity level from dimension scores."""
    weights = {
        "data_engineering": 0.25,
        "data_governance": 0.25,
        "analytics": 0.20,
        "mlops": 0.15,
        "data_culture": 0.15
    }

    weighted_score = sum(
        dimension_scores[dim] * weights[dim]
        for dim in weights
    )

    # Convert to 1-5 scale
    if weighted_score >= 85:
        level = 5
    elif weighted_score >= 70:
        level = 4
    elif weighted_score >= 50:
        level = 3
    elif weighted_score >= 30:
        level = 2
    else:
        level = 1

    return {
        "level": level,
        "label": MATURITY_LEVELS[level]["label"],
        "description": MATURITY_LEVELS[level]["description"],
        "weighted_score": round(weighted_score, 1)
    }


def calculate_industry_percentile(maturity_score: float, industry: str) -> int:
    """Calculate percentile ranking vs industry peers."""
    benchmark = INDUSTRY_BENCHMARKS.get(industry, INDUSTRY_BENCHMARKS["default"])

    # Convert score to 1-5 scale for comparison
    score_as_level = maturity_score / 20  # 0-100 to 0-5 scale

    if score_as_level >= benchmark["top_quartile"]:
        return 90
    elif score_as_level >= benchmark["avg_level"]:
        return 50 + int((score_as_level - benchmark["avg_level"]) /
                        (benchmark["top_quartile"] - benchmark["avg_level"]) * 40)
    else:
        return int((score_as_level / benchmark["avg_level"]) * 50)


def identify_capability_gaps(dimension_results: Dict[str, Dict]) -> List[Dict[str, Any]]:
    """Identify critical capability gaps."""
    gaps = []

    for dim, result in dimension_results.items():
        if result["score"] < 40:
            gaps.append({
                "dimension": dim,
                "severity": "critical",
                "score": result["score"],
                "findings": result["findings"]
            })
        elif result["score"] < 60:
            gaps.append({
                "dimension": dim,
                "severity": "significant",
                "score": result["score"],
                "findings": result["findings"]
            })

    return sorted(gaps, key=lambda x: x["score"])


def generate_quick_wins(dimension_results: Dict[str, Dict]) -> List[Dict[str, str]]:
    """Generate high-impact, low-effort improvement recommendations."""
    quick_wins = []

    if not dimension_results["data_governance"]["score"] >= 70:
        if "Missing data catalog" in str(dimension_results["data_governance"]["findings"]):
            quick_wins.append({
                "action": "Deploy cloud-native data catalog (e.g., AWS Glue, Azure Purview)",
                "impact": "High - Enables data discovery across organization",
                "effort": "Medium - 4-8 weeks with cloud-native tools"
            })

    if dimension_results["analytics"]["score"] < 60:
        quick_wins.append({
            "action": "Launch self-service BI enablement program with 5 pilot teams",
            "impact": "High - Democratizes data access",
            "effort": "Low - 4-6 weeks"
        })

    if dimension_results["data_culture"]["score"] < 50:
        quick_wins.append({
            "action": "Implement data literacy training curriculum",
            "impact": "Medium - Builds foundation for data-driven culture",
            "effort": "Low - Off-the-shelf programs available"
        })

    if dimension_results["mlops"]["score"] < 40:
        quick_wins.append({
            "action": "Standardize ML model deployment with managed MLOps platform",
            "impact": "High - Reduces ML deployment friction",
            "effort": "Medium - 6-10 weeks"
        })

    return quick_wins[:5]


def generate_strategic_investments(
    overall_maturity: Dict,
    dimension_results: Dict[str, Dict],
    cloud_platform: str
) -> List[Dict[str, str]]:
    """Generate major investment recommendations."""
    investments = []

    if overall_maturity["level"] < 3:
        investments.append({
            "initiative": "Modern Data Platform Foundation",
            "description": "Establish cloud-native data lakehouse architecture",
            "estimated_investment": "$2M-$5M",
            "timeline": "12-18 months",
            "expected_outcome": "Move from Level 1-2 to Level 3 maturity"
        })

    if dimension_results["data_governance"]["score"] < 50:
        investments.append({
            "initiative": "Enterprise Data Governance Program",
            "description": "Implement comprehensive data governance with catalog, lineage, and quality",
            "estimated_investment": "$1M-$3M",
            "timeline": "9-12 months",
            "expected_outcome": "Regulatory compliance, improved data trust"
        })

    if dimension_results["mlops"]["score"] < 50 and dimension_results["data_engineering"]["score"] >= 50:
        investments.append({
            "initiative": "ML Platform & Feature Store",
            "description": "Build enterprise ML platform with feature store and automated pipelines",
            "estimated_investment": "$1.5M-$4M",
            "timeline": "12-15 months",
            "expected_outcome": "10x ML model deployment velocity"
        })

    if cloud_platform == "on_prem":
        investments.append({
            "initiative": "Cloud Data Migration",
            "description": "Migrate on-premises data infrastructure to cloud",
            "estimated_investment": "$3M-$8M",
            "timeline": "18-24 months",
            "expected_outcome": "Cost reduction, scalability, modern capabilities"
        })

    return investments


def generate_roadmap(overall_maturity: Dict, gaps: List[Dict]) -> List[Dict[str, Any]]:
    """Generate phased improvement roadmap."""
    roadmap = []

    # Phase 1: Foundation (0-6 months)
    phase1_initiatives = []
    for gap in gaps:
        if gap["severity"] == "critical":
            phase1_initiatives.append(f"Address critical gap in {gap['dimension']}")

    roadmap.append({
        "phase": 1,
        "name": "Foundation",
        "duration": "0-6 months",
        "focus": "Address critical gaps and establish baseline capabilities",
        "initiatives": phase1_initiatives[:3] or ["Establish data governance framework"]
    })

    # Phase 2: Scale (6-12 months)
    roadmap.append({
        "phase": 2,
        "name": "Scale",
        "duration": "6-12 months",
        "focus": "Expand capabilities and drive adoption",
        "initiatives": [
            "Scale self-service analytics",
            "Expand data quality automation",
            "Launch ML platform pilot"
        ]
    })

    # Phase 3: Optimize (12-18 months)
    roadmap.append({
        "phase": 3,
        "name": "Optimize",
        "duration": "12-18 months",
        "focus": "Achieve operational excellence",
        "initiatives": [
            "Implement real-time analytics",
            "Scale ML operations",
            "Advance to data mesh architecture"
        ]
    })

    return roadmap


def assess_maturity(
    organization_name: str,
    industry: str,
    data_volume_tb: float,
    data_sources_count: int,
    real_time_pipelines: bool,
    data_catalog_implemented: bool,
    data_lineage_automated: bool,
    data_quality_score: Optional[float],
    self_service_bi_adoption: float,
    ml_models_in_production: int,
    feature_store_implemented: bool,
    mlops_automation_level: str,
    data_literacy_program: bool,
    data_mesh_adopted: bool,
    cloud_data_platform: str
) -> Dict[str, Any]:
    """
    Assess enterprise data platform maturity.

    Returns comprehensive maturity assessment with dimension scores,
    gaps, recommendations, and improvement roadmap.
    """
    # Calculate dimension scores
    data_eng = calculate_data_engineering_score(
        data_volume_tb, data_sources_count, real_time_pipelines, cloud_data_platform
    )
    data_gov = calculate_data_governance_score(
        data_catalog_implemented, data_lineage_automated, data_quality_score
    )
    analytics = calculate_analytics_score(self_service_bi_adoption, data_quality_score)
    mlops = calculate_mlops_score(
        ml_models_in_production, feature_store_implemented, mlops_automation_level
    )
    data_culture = calculate_data_culture_score(
        data_literacy_program, self_service_bi_adoption, data_mesh_adopted
    )

    dimension_results = {
        "data_engineering": data_eng,
        "data_governance": data_gov,
        "analytics": analytics,
        "mlops": mlops,
        "data_culture": data_culture
    }

    dimension_scores = {dim: result["score"] for dim, result in dimension_results.items()}

    # Calculate overall maturity
    overall_maturity = calculate_overall_maturity(dimension_scores)

    # Calculate industry percentile
    industry_percentile = calculate_industry_percentile(
        overall_maturity["weighted_score"], industry
    )

    # Identify gaps
    capability_gaps = identify_capability_gaps(dimension_results)

    # Generate recommendations
    quick_wins = generate_quick_wins(dimension_results)
    strategic_investments = generate_strategic_investments(
        overall_maturity, dimension_results, cloud_data_platform
    )

    # Generate roadmap
    roadmap = generate_roadmap(overall_maturity, capability_gaps)

    # Estimate investment ranges
    if overall_maturity["level"] <= 2:
        investment_range = {"low": "$3M", "high": "$10M", "timeline": "18-24 months"}
    elif overall_maturity["level"] == 3:
        investment_range = {"low": "$2M", "high": "$6M", "timeline": "12-18 months"}
    else:
        investment_range = {"low": "$1M", "high": "$3M", "timeline": "6-12 months"}

    return {
        "organization_name": organization_name,
        "industry": industry,
        "overall_maturity_level": overall_maturity["level"],
        "overall_maturity_label": overall_maturity["label"],
        "overall_maturity_description": overall_maturity["description"],
        "weighted_score": overall_maturity["weighted_score"],
        "dimension_scores": dimension_scores,
        "dimension_details": dimension_results,
        "industry_percentile": industry_percentile,
        "capability_gaps": capability_gaps,
        "quick_wins": quick_wins,
        "strategic_investments": strategic_investments,
        "roadmap_phases": roadmap,
        "estimated_investment": investment_range
    }


def main():
    """Example usage."""
    result = assess_maturity(
        organization_name="Acme Financial",
        industry="financial_services",
        data_volume_tb=500,
        data_sources_count=150,
        real_time_pipelines=True,
        data_catalog_implemented=True,
        data_lineage_automated=False,
        data_quality_score=72,
        self_service_bi_adoption=35,
        ml_models_in_production=12,
        feature_store_implemented=False,
        mlops_automation_level="semi_automated",
        data_literacy_program=True,
        data_mesh_adopted=False,
        cloud_data_platform="snowflake"
    )

    print(f"Organization: {result['organization_name']}")
    print(f"Maturity Level: {result['overall_maturity_level']} - {result['overall_maturity_label']}")
    print(f"Industry Percentile: {result['industry_percentile']}%")
    print(f"Capability Gaps: {len(result['capability_gaps'])}")
    print(f"Quick Wins: {len(result['quick_wins'])}")


if __name__ == "__main__":
    main()
