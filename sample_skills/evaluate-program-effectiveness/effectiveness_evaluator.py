"""
Program Effectiveness Evaluation Module

Implements program effectiveness assessment including
outcome measurement, ROI calculation, and performance rating.
"""

import csv
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
            # Convert numeric values
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
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Convert numeric values
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


def load_effectiveness_metrics() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    evaluation_dimensions_data = load_csv_as_dict("evaluation_dimensions.csv")
    scoring_thresholds_data = load_csv_as_dict("scoring_thresholds.csv")
    program_types_data = load_csv_as_dict("program_types.csv")
    roi_thresholds_data = load_csv_as_dict("roi_thresholds.csv")
    outcome_categories_data = load_csv_as_dict("outcome_categories.csv")
    evaluation_timing_data = load_csv_as_dict("evaluation_timing.csv")
    params = load_parameters()
    return {
        "evaluation_dimensions": evaluation_dimensions_data,
        "scoring_thresholds": scoring_thresholds_data,
        "program_types": program_types_data,
        "roi_thresholds": roi_thresholds_data,
        "outcome_categories": outcome_categories_data,
        "evaluation_timing": evaluation_timing_data,
        **params
    }


def calculate_dimension_score(
    dimension_data: Dict,
    dimension_config: Dict
) -> Dict[str, Any]:
    """Calculate score for a single evaluation dimension."""
    metrics = dimension_config.get("metrics", [])
    total_score = 0
    metric_count = 0

    metric_scores = []
    for metric in metrics:
        if metric in dimension_data:
            score = dimension_data[metric]
            total_score += score
            metric_count += 1
            metric_scores.append({
                "metric": metric,
                "score": score
            })

    avg_score = total_score / metric_count if metric_count > 0 else 0

    return {
        "dimension_score": round(avg_score, 2),
        "weight": dimension_config.get("weight", 0),
        "weighted_score": round(avg_score * dimension_config.get("weight", 0), 3),
        "metrics_evaluated": metric_count,
        "metric_scores": metric_scores
    }


def calculate_overall_effectiveness(
    dimension_scores: Dict[str, Dict]
) -> Dict[str, Any]:
    """Calculate overall effectiveness score."""
    total_weighted = sum(
        d["weighted_score"] for d in dimension_scores.values()
    )
    total_weight = sum(
        d["weight"] for d in dimension_scores.values()
    )

    overall_score = total_weighted / total_weight if total_weight > 0 else 0

    return {
        "overall_score": round(overall_score * 100, 1),
        "total_weighted_score": round(total_weighted, 3),
        "dimensions_evaluated": len(dimension_scores)
    }


def rate_effectiveness(
    score: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Rate program effectiveness based on score."""
    score_decimal = score / 100

    if score_decimal >= thresholds["highly_effective"]["min"]:
        rating = "highly_effective"
    elif score_decimal >= thresholds["effective"]["min"]:
        rating = "effective"
    elif score_decimal >= thresholds["moderately_effective"]["min"]:
        rating = "moderately_effective"
    elif score_decimal >= thresholds["marginally_effective"]["min"]:
        rating = "marginally_effective"
    else:
        rating = "ineffective"

    rating_info = thresholds[rating]

    return {
        "rating": rating.upper().replace("_", " "),
        "grade": rating_info["rating"],
        "score": score,
        "threshold_met": round(rating_info["min"] * 100, 0)
    }


def calculate_program_roi(
    program_costs: float,
    program_benefits: float,
    roi_thresholds: Dict
) -> Dict[str, Any]:
    """Calculate program ROI and assess performance."""
    if program_costs <= 0:
        return {"error": "Invalid program costs"}

    roi = (program_benefits - program_costs) / program_costs
    roi_pct = roi * 100

    # Determine ROI rating
    if roi >= roi_thresholds["excellent"]["min"]:
        roi_rating = "EXCELLENT"
    elif roi >= roi_thresholds["good"]["min"]:
        roi_rating = "GOOD"
    elif roi >= roi_thresholds["acceptable"]["min"]:
        roi_rating = "ACCEPTABLE"
    elif roi >= roi_thresholds["marginal"]["min"]:
        roi_rating = "MARGINAL"
    else:
        roi_rating = "POOR"

    return {
        "program_costs": program_costs,
        "program_benefits": program_benefits,
        "net_benefit": round(program_benefits - program_costs, 2),
        "roi": round(roi, 2),
        "roi_pct": round(roi_pct, 1),
        "roi_rating": roi_rating
    }


def compare_to_benchmark(
    effectiveness_score: float,
    program_type: str,
    program_types: Dict
) -> Dict[str, Any]:
    """Compare program effectiveness to industry benchmarks."""
    type_config = program_types.get(program_type, {})
    benchmark = type_config.get("benchmark_effectiveness", 0.70)
    benchmark_pct = benchmark * 100

    score_decimal = effectiveness_score / 100
    vs_benchmark = score_decimal - benchmark
    vs_benchmark_pct = (vs_benchmark / benchmark) * 100 if benchmark > 0 else 0

    if vs_benchmark >= 0.10:
        performance = "SIGNIFICANTLY_ABOVE"
    elif vs_benchmark >= 0:
        performance = "ABOVE_BENCHMARK"
    elif vs_benchmark >= -0.10:
        performance = "BELOW_BENCHMARK"
    else:
        performance = "SIGNIFICANTLY_BELOW"

    return {
        "program_type": program_type,
        "effectiveness_score": effectiveness_score,
        "benchmark_score": benchmark_pct,
        "vs_benchmark_pct": round(vs_benchmark_pct, 1),
        "performance_vs_benchmark": performance,
        "key_metrics": type_config.get("key_metrics", [])
    }


def assess_outcome_achievement(
    planned_outcomes: List[Dict],
    actual_outcomes: List[Dict]
) -> Dict[str, Any]:
    """Assess achievement of program outcomes."""
    outcomes_assessment = []
    total_achievement = 0

    for planned in planned_outcomes:
        outcome_id = planned.get("outcome_id", "")
        target = planned.get("target", 0)

        # Find matching actual outcome
        actual = next(
            (a for a in actual_outcomes if a.get("outcome_id") == outcome_id),
            {}
        )
        actual_value = actual.get("actual", 0)

        achievement_pct = (actual_value / target * 100) if target > 0 else 0
        total_achievement += min(achievement_pct, 100)

        outcomes_assessment.append({
            "outcome_id": outcome_id,
            "description": planned.get("description", ""),
            "target": target,
            "actual": actual_value,
            "achievement_pct": round(achievement_pct, 1),
            "status": "ACHIEVED" if achievement_pct >= 100 else "PARTIAL" if achievement_pct >= 50 else "NOT_ACHIEVED"
        })

    avg_achievement = total_achievement / len(planned_outcomes) if planned_outcomes else 0

    return {
        "total_outcomes": len(planned_outcomes),
        "achieved_count": sum(1 for o in outcomes_assessment if o["status"] == "ACHIEVED"),
        "partial_count": sum(1 for o in outcomes_assessment if o["status"] == "PARTIAL"),
        "not_achieved_count": sum(1 for o in outcomes_assessment if o["status"] == "NOT_ACHIEVED"),
        "average_achievement_pct": round(avg_achievement, 1),
        "outcomes_detail": outcomes_assessment
    }


def generate_recommendations(
    effectiveness_rating: Dict,
    roi_analysis: Dict,
    benchmark_comparison: Dict,
    outcome_achievement: Dict
) -> List[Dict]:
    """Generate program improvement recommendations."""
    recommendations = []

    # Based on effectiveness rating
    if effectiveness_rating["grade"] in ["D", "F"]:
        recommendations.append({
            "priority": "HIGH",
            "area": "Program Design",
            "recommendation": "Conduct comprehensive program review and redesign",
            "expected_impact": "Significant improvement in effectiveness"
        })

    # Based on ROI
    if roi_analysis.get("roi_rating") in ["POOR", "MARGINAL"]:
        recommendations.append({
            "priority": "HIGH",
            "area": "Cost Efficiency",
            "recommendation": "Analyze cost structure and identify optimization opportunities",
            "expected_impact": "Improved return on investment"
        })

    # Based on benchmark comparison
    if benchmark_comparison.get("performance_vs_benchmark") in ["BELOW_BENCHMARK", "SIGNIFICANTLY_BELOW"]:
        recommendations.append({
            "priority": "MEDIUM",
            "area": "Best Practices",
            "recommendation": "Benchmark against high-performing programs and adopt best practices",
            "expected_impact": "Alignment with industry standards"
        })

    # Based on outcome achievement
    if outcome_achievement.get("average_achievement_pct", 0) < 70:
        recommendations.append({
            "priority": "HIGH",
            "area": "Outcome Delivery",
            "recommendation": "Review outcome targets and delivery mechanisms",
            "expected_impact": "Higher outcome achievement rates"
        })

    return sorted(recommendations, key=lambda x: {"HIGH": 0, "MEDIUM": 1, "LOW": 2}.get(x["priority"], 3))


def evaluate_program_effectiveness(
    program_id: str,
    program_name: str,
    program_type: str,
    dimension_scores: Dict[str, Dict],
    program_costs: float,
    program_benefits: float,
    planned_outcomes: List[Dict],
    actual_outcomes: List[Dict],
    evaluation_period: str,
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate program effectiveness.

    Business Rules:
    1. Multi-dimensional effectiveness scoring
    2. ROI calculation and assessment
    3. Benchmark comparison
    4. Outcome achievement analysis

    Args:
        program_id: Program identifier
        program_name: Program name
        program_type: Type of program
        dimension_scores: Scores for each evaluation dimension
        program_costs: Total program costs
        program_benefits: Quantified program benefits
        planned_outcomes: Planned program outcomes
        actual_outcomes: Actual achieved outcomes
        evaluation_period: Period being evaluated
        evaluation_date: Evaluation date

    Returns:
        Program effectiveness evaluation results
    """
    config = load_effectiveness_metrics()
    dimensions = config.get("evaluation_dimensions", {})
    thresholds = config.get("scoring_thresholds", {})
    roi_thresholds = config.get("roi_thresholds", {})
    program_types = config.get("program_types", {})

    # Calculate dimension scores
    calculated_dimensions = {}
    for dim_name, dim_data in dimension_scores.items():
        if dim_name in dimensions:
            calculated_dimensions[dim_name] = calculate_dimension_score(
                dim_data,
                dimensions[dim_name]
            )

    # Calculate overall effectiveness
    overall = calculate_overall_effectiveness(calculated_dimensions)

    # Rate effectiveness
    effectiveness_rating = rate_effectiveness(overall["overall_score"], thresholds)

    # Calculate ROI
    roi_analysis = calculate_program_roi(program_costs, program_benefits, roi_thresholds)

    # Benchmark comparison
    benchmark_comparison = compare_to_benchmark(
        overall["overall_score"],
        program_type,
        program_types
    )

    # Outcome achievement
    outcome_achievement = assess_outcome_achievement(planned_outcomes, actual_outcomes)

    # Generate recommendations
    recommendations = generate_recommendations(
        effectiveness_rating,
        roi_analysis,
        benchmark_comparison,
        outcome_achievement
    )

    return {
        "program_id": program_id,
        "program_name": program_name,
        "program_type": program_type,
        "evaluation_date": evaluation_date,
        "evaluation_period": evaluation_period,
        "effectiveness_summary": {
            "overall_score": overall["overall_score"],
            "rating": effectiveness_rating["rating"],
            "grade": effectiveness_rating["grade"]
        },
        "dimension_analysis": calculated_dimensions,
        "roi_analysis": roi_analysis,
        "benchmark_comparison": benchmark_comparison,
        "outcome_achievement": outcome_achievement,
        "recommendations": recommendations,
        "evaluation_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = evaluate_program_effectiveness(
        program_id="PROG-001",
        program_name="Leadership Development Program",
        program_type="training",
        dimension_scores={
            "outcome_achievement": {
                "goal_attainment": 0.82,
                "target_completion": 0.78,
                "milestone_achievement": 0.85
            },
            "efficiency": {
                "cost_per_outcome": 0.75,
                "resource_utilization": 0.80,
                "time_to_completion": 0.70
            },
            "quality": {
                "deliverable_quality": 0.88,
                "stakeholder_satisfaction": 0.85,
                "error_rate": 0.90
            },
            "impact": {
                "beneficiary_reach": 0.72,
                "behavior_change": 0.68,
                "sustainability": 0.75
            },
            "governance": {
                "compliance": 0.95,
                "reporting_accuracy": 0.92,
                "risk_management": 0.88
            }
        },
        program_costs=250000,
        program_benefits=425000,
        planned_outcomes=[
            {"outcome_id": "O1", "description": "Participants trained", "target": 100},
            {"outcome_id": "O2", "description": "Satisfaction score", "target": 4.5},
            {"outcome_id": "O3", "description": "Promotion rate", "target": 0.25}
        ],
        actual_outcomes=[
            {"outcome_id": "O1", "actual": 95},
            {"outcome_id": "O2", "actual": 4.3},
            {"outcome_id": "O3", "actual": 0.22}
        ],
        evaluation_period="2025",
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
