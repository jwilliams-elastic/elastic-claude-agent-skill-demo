"""
Digital Transformation Readiness Assessment Module

Evaluates organizational readiness for digital transformation across six dimensions:
technology infrastructure, data maturity, talent & culture, process automation,
customer experience, and innovation capacity.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional


def load_csv_as_dict(filename: str, key_column: str = 'key') -> Dict[str, Dict[str, Any]]:
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


def load_csv_as_list(filename: str) -> List[Dict[str, Any]]:
    """Load a CSV file and return as list of dictionaries."""
    csv_path = Path(__file__).parent / filename
    result = []
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
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
            result.append(row)
    return result


def calculate_technology_score(legacy_pct: float, cloud_pct: float) -> float:
    """Calculate technology infrastructure dimension score."""
    legacy_penalty = max(0, (legacy_pct - 20) * 1.5)
    cloud_bonus = cloud_pct * 0.6
    base_score = 50 + cloud_bonus - legacy_penalty
    return max(0, min(100, base_score))


def calculate_data_score(governance_score: int, analytics_maturity: str) -> float:
    """Calculate data maturity dimension score."""
    analytics_scores = {
        "descriptive": 25,
        "diagnostic": 50,
        "predictive": 75,
        "prescriptive": 100
    }
    governance_component = governance_score * 12
    analytics_component = analytics_scores.get(analytics_maturity, 25)
    return (governance_component + analytics_component) / 2


def calculate_talent_score(digital_talent_pct: float, agile_pct: float) -> float:
    """Calculate talent & culture dimension score."""
    talent_component = digital_talent_pct * 0.6
    agile_component = agile_pct * 0.4
    return talent_component + agile_component


def calculate_automation_score(automation_rate: float) -> float:
    """Calculate process automation dimension score."""
    return automation_rate


def calculate_cx_score(digital_revenue_pct: float) -> float:
    """Calculate customer experience dimension score."""
    return min(100, digital_revenue_pct * 1.5)


def calculate_innovation_score(rd_digital_pct: float) -> float:
    """Calculate innovation capacity dimension score."""
    return min(100, rd_digital_pct * 2)


def determine_tier(score: float) -> str:
    """Determine readiness tier based on overall score."""
    if score >= 75:
        return "Leader"
    elif score >= 55:
        return "Fast Follower"
    elif score >= 35:
        return "Cautious Adopter"
    else:
        return "At Risk"


def get_industry_benchmark(industry: str) -> Dict[str, float]:
    """Get industry benchmark scores."""
    benchmarks = {
        "financial_services": {"overall": 62, "technology": 68, "data": 70, "talent": 55, "automation": 58, "cx": 65, "innovation": 50},
        "healthcare": {"overall": 48, "technology": 45, "data": 55, "talent": 42, "automation": 40, "cx": 52, "innovation": 55},
        "retail": {"overall": 55, "technology": 52, "data": 58, "talent": 48, "automation": 52, "cx": 72, "innovation": 45},
        "manufacturing": {"overall": 45, "technology": 42, "data": 48, "talent": 38, "automation": 55, "cx": 35, "innovation": 52},
        "technology": {"overall": 78, "technology": 85, "data": 82, "talent": 75, "automation": 70, "cx": 78, "innovation": 80},
        "default": {"overall": 50, "technology": 50, "data": 50, "talent": 50, "automation": 50, "cx": 50, "innovation": 50}
    }
    return benchmarks.get(industry, benchmarks["default"])


def assess_readiness(
    company_name: str,
    industry: str,
    legacy_system_percentage: float,
    cloud_adoption_percentage: float,
    data_governance_score: int,
    analytics_maturity: str,
    digital_talent_percentage: float,
    agile_team_percentage: float,
    process_automation_rate: float,
    digital_revenue_percentage: float,
    annual_rd_digital_percentage: float
) -> Dict[str, Any]:
    """
    Assess digital transformation readiness.

    Returns comprehensive readiness assessment with scores, benchmarks,
    gaps, and recommendations.
    """
    # Calculate dimension scores
    tech_score = calculate_technology_score(legacy_system_percentage, cloud_adoption_percentage)
    data_score = calculate_data_score(data_governance_score, analytics_maturity)
    talent_score = calculate_talent_score(digital_talent_percentage, agile_team_percentage)
    automation_score = calculate_automation_score(process_automation_rate)
    cx_score = calculate_cx_score(digital_revenue_percentage)
    innovation_score = calculate_innovation_score(annual_rd_digital_percentage)

    dimension_scores = {
        "technology_infrastructure": round(tech_score, 1),
        "data_maturity": round(data_score, 1),
        "talent_culture": round(talent_score, 1),
        "process_automation": round(automation_score, 1),
        "customer_experience": round(cx_score, 1),
        "innovation_capacity": round(innovation_score, 1)
    }

    # Weighted overall score
    weights = {"technology_infrastructure": 0.20, "data_maturity": 0.20, "talent_culture": 0.15,
               "process_automation": 0.15, "customer_experience": 0.15, "innovation_capacity": 0.15}
    overall_score = sum(dimension_scores[dim] * weights[dim] for dim in dimension_scores)

    # Get benchmarks
    benchmark = get_industry_benchmark(industry)

    # Identify gaps
    critical_gaps = []
    for dim, score in dimension_scores.items():
        benchmark_key = dim.split('_')[0] if dim != "talent_culture" else "talent"
        if dim == "customer_experience":
            benchmark_key = "cx"
        if dim == "technology_infrastructure":
            benchmark_key = "technology"
        if dim == "process_automation":
            benchmark_key = "automation"
        if dim == "innovation_capacity":
            benchmark_key = "innovation"
        if dim == "data_maturity":
            benchmark_key = "data"

        bench_score = benchmark.get(benchmark_key, 50)
        if score < bench_score - 10:
            critical_gaps.append({
                "dimension": dim,
                "current_score": score,
                "benchmark": bench_score,
                "gap": round(bench_score - score, 1)
            })

    # Sort gaps by severity
    critical_gaps.sort(key=lambda x: x["gap"], reverse=True)

    # Generate recommendations
    recommendations = []
    if legacy_system_percentage > 40:
        recommendations.append("Prioritize legacy modernization - consider cloud-native re-platforming for top 5 critical systems")
    if cloud_adoption_percentage < 50:
        recommendations.append("Accelerate cloud migration with a 'cloud-first' policy for all new workloads")
    if data_governance_score < 3:
        recommendations.append("Establish enterprise data governance framework with dedicated data stewardship roles")
    if analytics_maturity in ["descriptive", "diagnostic"]:
        recommendations.append("Invest in predictive analytics capabilities and ML platform infrastructure")
    if digital_talent_percentage < 30:
        recommendations.append("Launch digital skills academy and aggressive tech talent acquisition program")
    if agile_team_percentage < 50:
        recommendations.append("Scale agile transformation beyond IT into business operations")
    if process_automation_rate < 40:
        recommendations.append("Deploy intelligent automation CoE to identify and prioritize RPA/AI automation opportunities")
    if digital_revenue_percentage < 30:
        recommendations.append("Develop digital-first customer channels and e-commerce capabilities")

    # Estimate timeline to Leader tier
    gap_to_leader = max(0, 75 - overall_score)
    estimated_months = int(gap_to_leader * 1.5) if gap_to_leader > 0 else 0

    return {
        "company_name": company_name,
        "industry": industry,
        "overall_score": round(overall_score, 1),
        "readiness_tier": determine_tier(overall_score),
        "dimension_scores": dimension_scores,
        "industry_benchmark": {
            "overall": benchmark["overall"],
            "comparison": "above" if overall_score > benchmark["overall"] else "below",
            "gap": round(overall_score - benchmark["overall"], 1)
        },
        "critical_gaps": critical_gaps[:3],
        "recommendations": recommendations[:5],
        "estimated_timeline_months": estimated_months
    }


def main():
    """Example usage."""
    result = assess_readiness(
        company_name="Acme Corp",
        industry="financial_services",
        legacy_system_percentage=45,
        cloud_adoption_percentage=35,
        data_governance_score=3,
        analytics_maturity="diagnostic",
        digital_talent_percentage=25,
        agile_team_percentage=40,
        process_automation_rate=30,
        digital_revenue_percentage=20,
        annual_rd_digital_percentage=15
    )

    print(f"Company: {result['company_name']}")
    print(f"Overall Score: {result['overall_score']}")
    print(f"Readiness Tier: {result['readiness_tier']}")
    print(f"Industry Benchmark Gap: {result['industry_benchmark']['gap']}")
    print(f"Critical Gaps: {len(result['critical_gaps'])}")
    print(f"Estimated months to Leader: {result['estimated_timeline_months']}")


if __name__ == "__main__":
    main()
