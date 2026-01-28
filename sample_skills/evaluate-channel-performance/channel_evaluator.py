"""
Channel Performance Evaluation Module

Implements sales channel performance analysis including
profitability, efficiency metrics, and optimization recommendations.
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


def load_channel_metrics() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    channel_types_data = load_csv_as_dict("channel_types.csv")
    performance_metrics_data = load_csv_as_dict("performance_metrics.csv")
    profitability_analysis_data = load_key_value_csv("profitability_analysis.csv")
    performance_ratings_data = load_csv_as_dict("performance_ratings.csv")
    conflict_indicators_data = load_csv_as_dict("conflict_indicators.csv")
    incentive_structures_data = load_csv_as_dict("incentive_structures.csv")
    optimization_levers_data = load_csv_as_dict("optimization_levers.csv")
    params = load_parameters()
    return {
        "channel_types": channel_types_data,
        "performance_metrics": performance_metrics_data,
        "profitability_analysis": profitability_analysis_data,
        "performance_ratings": performance_ratings_data,
        "conflict_indicators": conflict_indicators_data,
        "incentive_structures": incentive_structures_data,
        "optimization_levers": optimization_levers_data,
        **params
    }


def calculate_channel_profitability(
    channel_data: Dict,
    channel_config: Dict
) -> Dict[str, Any]:
    """Calculate channel profitability metrics."""
    revenue = channel_data.get("revenue", 0)
    cogs = channel_data.get("cost_of_goods", 0)
    variable_costs = channel_data.get("variable_costs", 0)
    fixed_costs = channel_data.get("allocated_fixed_costs", 0)

    gross_profit = revenue - cogs
    gross_margin = gross_profit / revenue if revenue > 0 else 0

    contribution_margin = gross_profit - variable_costs
    contribution_margin_pct = contribution_margin / revenue if revenue > 0 else 0

    channel_profit = contribution_margin - fixed_costs
    channel_profit_pct = channel_profit / revenue if revenue > 0 else 0

    # Compare to typical margin
    typical_margin = channel_config.get("typical_margin_range", {})
    margin_min = typical_margin.get("min", 0)
    margin_max = typical_margin.get("max", 1)

    if gross_margin >= margin_max:
        margin_assessment = "ABOVE_EXPECTED"
    elif gross_margin >= margin_min:
        margin_assessment = "WITHIN_RANGE"
    else:
        margin_assessment = "BELOW_EXPECTED"

    return {
        "revenue": revenue,
        "cost_of_goods": cogs,
        "gross_profit": round(gross_profit, 2),
        "gross_margin_pct": round(gross_margin * 100, 1),
        "variable_costs": variable_costs,
        "contribution_margin": round(contribution_margin, 2),
        "contribution_margin_pct": round(contribution_margin_pct * 100, 1),
        "allocated_fixed_costs": fixed_costs,
        "channel_profit": round(channel_profit, 2),
        "channel_profit_pct": round(channel_profit_pct * 100, 1),
        "margin_assessment": margin_assessment,
        "expected_margin_range": f"{margin_min * 100:.0f}%-{margin_max * 100:.0f}%"
    }


def calculate_performance_metrics(
    channel_data: Dict,
    metric_benchmarks: Dict
) -> Dict[str, Any]:
    """Calculate channel performance metrics."""
    metrics_results = []
    total_weighted_score = 0
    total_weight = 0

    for metric_name, config in metric_benchmarks.items():
        weight = config.get("weight", 0)
        benchmarks = config.get("benchmarks", {})

        actual_value = channel_data.get(metric_name, 0)

        # Determine score based on benchmark achievement
        target = benchmarks.get("target", 0)
        minimum = benchmarks.get("minimum", benchmarks.get("maximum", 0))

        if target > 0:
            if "maximum" in benchmarks:
                # Lower is better (like CAC ratio)
                achievement = minimum / actual_value if actual_value > 0 else 0
            else:
                # Higher is better
                achievement = actual_value / target if target > 0 else 0

            score = min(achievement * 100, 100)
        else:
            score = 50  # Default if no benchmark

        weighted_score = score * weight
        total_weighted_score += weighted_score
        total_weight += weight

        metrics_results.append({
            "metric": metric_name,
            "actual": actual_value,
            "target": target,
            "score": round(score, 1),
            "weight": weight,
            "weighted_score": round(weighted_score, 2)
        })

    overall_score = total_weighted_score / total_weight if total_weight > 0 else 0

    return {
        "metrics": metrics_results,
        "overall_score": round(overall_score, 1)
    }


def rate_channel_performance(
    score: float,
    ratings: Dict
) -> Dict[str, Any]:
    """Rate channel performance based on score."""
    for rating_name, config in sorted(
        ratings.items(),
        key=lambda x: x[1].get("min_score", 0),
        reverse=True
    ):
        if score >= config.get("min_score", 0):
            return {
                "rating": rating_name.upper().replace("_", " "),
                "score": score,
                "recommended_action": config.get("action", "")
            }

    return {
        "rating": "FAILING",
        "score": score,
        "recommended_action": "exit_evaluation"
    }


def detect_channel_conflicts(
    channel_data: Dict,
    all_channels: List[Dict],
    conflict_indicators: Dict
) -> List[Dict]:
    """Detect channel conflicts."""
    conflicts = []
    channel_id = channel_data.get("channel_id", "")

    # Check price undercutting
    channel_avg_price = channel_data.get("average_selling_price", 0)
    for other in all_channels:
        if other.get("channel_id") == channel_id:
            continue

        other_price = other.get("average_selling_price", 0)
        if channel_avg_price > 0 and other_price > 0:
            price_diff = (channel_avg_price - other_price) / channel_avg_price

            threshold = conflict_indicators.get("price_undercutting", {}).get("threshold_pct", 0.10)
            if price_diff >= threshold:
                conflicts.append({
                    "conflict_type": "PRICE_UNDERCUTTING",
                    "severity": conflict_indicators.get("price_undercutting", {}).get("severity", "high"),
                    "conflicting_channel": other.get("channel_id", ""),
                    "details": f"Price difference of {price_diff * 100:.1f}%"
                })

    # Check territory overlap
    territories = set(channel_data.get("territories", []))
    for other in all_channels:
        if other.get("channel_id") == channel_id:
            continue

        other_territories = set(other.get("territories", []))
        overlap = territories.intersection(other_territories)

        if territories and len(overlap) / len(territories) >= conflict_indicators.get("territory_overlap", {}).get("threshold_pct", 0.25):
            conflicts.append({
                "conflict_type": "TERRITORY_OVERLAP",
                "severity": conflict_indicators.get("territory_overlap", {}).get("severity", "medium"),
                "conflicting_channel": other.get("channel_id", ""),
                "details": f"Overlapping territories: {', '.join(overlap)}"
            })

    return conflicts


def calculate_incentive_effectiveness(
    incentives_paid: Dict,
    performance_change: Dict,
    incentive_structures: Dict
) -> Dict[str, Any]:
    """Analyze incentive effectiveness."""
    incentive_analysis = []
    total_paid = 0
    total_impact = 0

    for incentive_type, amount in incentives_paid.items():
        if amount <= 0:
            continue

        total_paid += amount
        typical_range = incentive_structures.get(incentive_type, {}).get("typical_range", {})

        # Calculate ROI based on performance change
        performance_metric = f"{incentive_type}_impact"
        impact = performance_change.get(performance_metric, 0)
        total_impact += impact

        roi = (impact - amount) / amount if amount > 0 else 0

        incentive_analysis.append({
            "incentive_type": incentive_type,
            "amount_paid": amount,
            "performance_impact": impact,
            "roi": round(roi, 2),
            "typical_rate_range": f"{typical_range.get('min', 0) * 100:.1f}%-{typical_range.get('max', 0) * 100:.1f}%"
        })

    overall_roi = (total_impact - total_paid) / total_paid if total_paid > 0 else 0

    return {
        "total_incentives_paid": total_paid,
        "total_performance_impact": total_impact,
        "overall_roi": round(overall_roi, 2),
        "incentive_breakdown": incentive_analysis
    }


def identify_optimization_opportunities(
    profitability: Dict,
    performance: Dict,
    channel_type: str,
    optimization_levers: Dict
) -> List[Dict]:
    """Identify channel optimization opportunities."""
    opportunities = []

    # Check each optimization lever
    for lever, config in optimization_levers.items():
        potential_improvement = 0
        applicable = False

        if lever == "channel_mix_adjustment":
            if performance.get("overall_score", 0) < 70:
                applicable = True
                potential_improvement = config.get("potential_margin_improvement", 0)

        elif lever == "partner_tiering":
            if channel_type in ["distributor", "reseller"]:
                applicable = True
                potential_improvement = config.get("potential_efficiency_gain", 0)

        elif lever == "digital_transformation":
            if channel_type in ["direct_sales", "retail"]:
                applicable = True
                potential_improvement = config.get("potential_cost_reduction", 0)

        elif lever == "territory_optimization":
            applicable = True
            potential_improvement = config.get("potential_coverage_improvement", 0)

        if applicable:
            revenue = profitability.get("revenue", 0)
            estimated_value = revenue * potential_improvement

            opportunities.append({
                "lever": lever.replace("_", " ").title(),
                "potential_improvement_pct": round(potential_improvement * 100, 1),
                "estimated_value": round(estimated_value, 2),
                "applicable_to": channel_type
            })

    # Sort by estimated value
    opportunities.sort(key=lambda x: x["estimated_value"], reverse=True)

    return opportunities


def evaluate_channel_performance(
    evaluation_id: str,
    channel_id: str,
    channel_name: str,
    channel_type: str,
    channel_data: Dict,
    all_channels: List[Dict],
    incentives_paid: Dict,
    performance_change: Dict,
    evaluation_period: str,
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate channel performance.

    Business Rules:
    1. Profitability analysis
    2. Performance metric scoring
    3. Conflict detection
    4. Optimization recommendations

    Args:
        evaluation_id: Evaluation identifier
        channel_id: Channel identifier
        channel_name: Channel name
        channel_type: Type of channel
        channel_data: Channel financial and operational data
        all_channels: All channels for conflict analysis
        incentives_paid: Incentives paid to channel
        performance_change: Performance changes for incentive analysis
        evaluation_period: Period evaluated
        evaluation_date: Evaluation date

    Returns:
        Channel performance evaluation results
    """
    config = load_channel_metrics()
    channel_types = config.get("channel_types", {})
    performance_metrics = config.get("performance_metrics", {})
    performance_ratings = config.get("performance_ratings", {})
    conflict_indicators = config.get("conflict_indicators", {})
    incentive_structures = config.get("incentive_structures", {})
    optimization_levers = config.get("optimization_levers", {})

    # Get channel type config
    channel_config = channel_types.get(channel_type, {})

    # Calculate profitability
    profitability = calculate_channel_profitability(channel_data, channel_config)

    # Calculate performance metrics
    performance = calculate_performance_metrics(channel_data, performance_metrics)

    # Rate performance
    rating = rate_channel_performance(performance["overall_score"], performance_ratings)

    # Detect conflicts
    conflicts = detect_channel_conflicts(channel_data, all_channels, conflict_indicators)

    # Analyze incentive effectiveness
    incentive_analysis = calculate_incentive_effectiveness(
        incentives_paid,
        performance_change,
        incentive_structures
    )

    # Identify optimization opportunities
    opportunities = identify_optimization_opportunities(
        profitability,
        performance,
        channel_type,
        optimization_levers
    )

    # Calculate channel share metrics
    total_revenue = sum(c.get("revenue", 0) for c in all_channels)
    channel_revenue = channel_data.get("revenue", 0)
    revenue_share = channel_revenue / total_revenue if total_revenue > 0 else 0

    return {
        "evaluation_id": evaluation_id,
        "channel_id": channel_id,
        "channel_name": channel_name,
        "channel_type": channel_type,
        "evaluation_date": evaluation_date,
        "evaluation_period": evaluation_period,
        "profitability_analysis": profitability,
        "performance_analysis": {
            "metrics": performance["metrics"],
            "overall_score": performance["overall_score"],
            "rating": rating
        },
        "channel_share": {
            "revenue": channel_revenue,
            "total_market_revenue": total_revenue,
            "share_pct": round(revenue_share * 100, 1)
        },
        "conflict_analysis": {
            "conflict_count": len(conflicts),
            "conflicts": conflicts
        },
        "incentive_analysis": incentive_analysis,
        "optimization_opportunities": opportunities,
        "evaluation_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = evaluate_channel_performance(
        evaluation_id="CHAN-2026-001",
        channel_id="DIST-001",
        channel_name="Northeast Distributor Network",
        channel_type="distributor",
        channel_data={
            "revenue": 5000000,
            "cost_of_goods": 3000000,
            "variable_costs": 500000,
            "allocated_fixed_costs": 300000,
            "average_selling_price": 150,
            "territories": ["NY", "NJ", "CT", "MA"],
            "conversion_rate": 0.025,
            "customer_satisfaction": 42,
            "inventory_turnover": 6
        },
        all_channels=[
            {"channel_id": "DIST-001", "revenue": 5000000, "average_selling_price": 150, "territories": ["NY", "NJ", "CT", "MA"]},
            {"channel_id": "DIST-002", "revenue": 3500000, "average_selling_price": 142, "territories": ["PA", "NJ", "DE"]},
            {"channel_id": "ECOM-001", "revenue": 2500000, "average_selling_price": 165, "territories": []}
        ],
        incentives_paid={
            "volume_rebate": 100000,
            "growth_bonus": 50000,
            "market_development_fund": 25000
        },
        performance_change={
            "volume_rebate_impact": 180000,
            "growth_bonus_impact": 85000,
            "market_development_fund_impact": 40000
        },
        evaluation_period="2025",
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
