"""
Brand Equity Evaluation Module

Implements brand equity assessment including
valuation, strength scoring, and market positioning analysis.
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


def load_brand_metrics() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    equity_dimensions_data = load_csv_as_dict("equity_dimensions.csv")
    valuation_methods_data = load_csv_as_dict("valuation_methods.csv")
    performance_ratings_data = load_csv_as_dict("performance_ratings.csv")
    industry_benchmarks_data = load_csv_as_dict("industry_benchmarks.csv")
    nps_interpretation_data = load_csv_as_dict("nps_interpretation.csv")
    nps_benchmarks_data = load_csv_as_dict("nps_benchmarks.csv")
    price_premium_factors_data = load_csv_as_dict("price_premium_factors.csv")
    params = load_parameters()
    return {
        "equity_dimensions": equity_dimensions_data,
        "valuation_methods": valuation_methods_data,
        "performance_ratings": performance_ratings_data,
        "industry_benchmarks": industry_benchmarks_data,
        "nps_interpretation": nps_interpretation_data,
        "nps_benchmarks": nps_benchmarks_data,
        "price_premium_factors": price_premium_factors_data,
        **params
    }


def calculate_dimension_score(
    dimension_name: str,
    dimension_config: Dict,
    dimension_data: Dict
) -> Dict[str, Any]:
    """Calculate score for a brand equity dimension."""
    metrics = dimension_config.get("metrics", [])
    weight = dimension_config.get("weight", 0)
    benchmark = dimension_config.get("benchmark_threshold", 0.5)

    metric_scores = []
    total_score = 0

    for metric in metrics:
        if metric in dimension_data:
            score = dimension_data[metric]
            total_score += score
            metric_scores.append({
                "metric": metric,
                "score": score
            })

    avg_score = total_score / len(metric_scores) if metric_scores else 0
    vs_benchmark = avg_score - benchmark

    return {
        "dimension": dimension_name,
        "weight": weight,
        "score": round(avg_score, 3),
        "weighted_score": round(avg_score * weight, 4),
        "benchmark": benchmark,
        "vs_benchmark": round(vs_benchmark, 3),
        "metrics": metric_scores
    }


def calculate_overall_equity(
    dimension_scores: List[Dict]
) -> Dict[str, Any]:
    """Calculate overall brand equity score."""
    total_weighted = sum(d["weighted_score"] for d in dimension_scores)
    total_weight = sum(d["weight"] for d in dimension_scores)

    overall_score = total_weighted / total_weight if total_weight > 0 else 0

    return {
        "overall_score": round(overall_score, 3),
        "score_pct": round(overall_score * 100, 1),
        "dimensions_evaluated": len(dimension_scores)
    }


def rate_brand_performance(
    equity_score: float,
    ratings: Dict
) -> Dict[str, Any]:
    """Rate brand based on equity score."""
    score_pct = equity_score * 100

    for rating_name, config in sorted(
        ratings.items(),
        key=lambda x: x[1].get("min_score", 0),
        reverse=True
    ):
        if score_pct >= config.get("min_score", 0):
            return {
                "rating": rating_name.upper(),
                "score_pct": round(score_pct, 1),
                "multiplier": config.get("multiplier", 1.0),
                "threshold_met": config.get("min_score", 0)
            }

    return {
        "rating": "DISTRESSED",
        "score_pct": round(score_pct, 1),
        "multiplier": 0.50,
        "threshold_met": 0
    }


def calculate_brand_value_income(
    annual_revenue: float,
    valuation_config: Dict
) -> Dict[str, Any]:
    """Calculate brand value using income approach."""
    brand_contribution = valuation_config.get("brand_contribution_factor", 0.25)
    discount_rate = valuation_config.get("discount_rate", 0.10)
    growth_rate = valuation_config.get("growth_rate", 0.03)

    brand_earnings = annual_revenue * brand_contribution

    # Gordon Growth Model for perpetuity value
    if discount_rate > growth_rate:
        brand_value = brand_earnings / (discount_rate - growth_rate)
    else:
        brand_value = brand_earnings * 10  # Fallback multiplier

    return {
        "method": "income_approach",
        "annual_revenue": annual_revenue,
        "brand_contribution_factor": brand_contribution,
        "brand_earnings": round(brand_earnings, 2),
        "discount_rate": discount_rate,
        "growth_rate": growth_rate,
        "estimated_brand_value": round(brand_value, 2)
    }


def calculate_brand_value_market(
    annual_revenue: float,
    profit: float,
    valuation_config: Dict
) -> Dict[str, Any]:
    """Calculate brand value using market approach."""
    revenue_mult_range = valuation_config.get("revenue_multiple_range", {})
    profit_mult_range = valuation_config.get("profit_multiple_range", {})

    revenue_low = annual_revenue * revenue_mult_range.get("min", 0.5)
    revenue_high = annual_revenue * revenue_mult_range.get("max", 3.0)

    profit_low = profit * profit_mult_range.get("min", 5)
    profit_high = profit * profit_mult_range.get("max", 20)

    avg_value = (revenue_low + revenue_high + profit_low + profit_high) / 4

    return {
        "method": "market_approach",
        "revenue_based_range": {
            "low": round(revenue_low, 2),
            "high": round(revenue_high, 2)
        },
        "profit_based_range": {
            "low": round(profit_low, 2),
            "high": round(profit_high, 2)
        },
        "average_estimate": round(avg_value, 2)
    }


def calculate_nps(
    promoters: int,
    passives: int,
    detractors: int,
    nps_benchmarks: Dict
) -> Dict[str, Any]:
    """Calculate Net Promoter Score."""
    total = promoters + passives + detractors
    if total == 0:
        return {"error": "No respondents"}

    promoter_pct = promoters / total
    detractor_pct = detractors / total
    nps = (promoter_pct - detractor_pct) * 100

    # Determine NPS rating
    for rating, config in sorted(
        nps_benchmarks.items(),
        key=lambda x: x[1].get("min", -100),
        reverse=True
    ):
        if nps >= config.get("min", -100):
            nps_rating = rating.upper()
            description = config.get("description", "")
            break
    else:
        nps_rating = "CRITICAL"
        description = "Brand crisis"

    return {
        "promoters": promoters,
        "passives": passives,
        "detractors": detractors,
        "total_respondents": total,
        "promoter_pct": round(promoter_pct * 100, 1),
        "detractor_pct": round(detractor_pct * 100, 1),
        "nps": round(nps, 0),
        "nps_rating": nps_rating,
        "description": description
    }


def compare_to_industry(
    equity_metrics: Dict,
    industry: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Compare brand metrics to industry benchmarks."""
    industry_bench = benchmarks.get(industry, {})

    comparisons = []

    # Awareness comparison
    if "awareness" in equity_metrics:
        benchmark = industry_bench.get("avg_awareness", 0.60)
        actual = equity_metrics["awareness"]
        variance = actual - benchmark
        comparisons.append({
            "metric": "awareness",
            "actual": round(actual, 2),
            "benchmark": benchmark,
            "variance": round(variance, 2),
            "status": "ABOVE" if variance > 0 else "BELOW"
        })

    # Loyalty comparison
    if "loyalty" in equity_metrics:
        benchmark = industry_bench.get("avg_loyalty", 0.50)
        actual = equity_metrics["loyalty"]
        variance = actual - benchmark
        comparisons.append({
            "metric": "loyalty",
            "actual": round(actual, 2),
            "benchmark": benchmark,
            "variance": round(variance, 2),
            "status": "ABOVE" if variance > 0 else "BELOW"
        })

    premium_factor = industry_bench.get("premium_factor", 1.0)

    return {
        "industry": industry,
        "comparisons": comparisons,
        "industry_premium_factor": premium_factor
    }


def calculate_price_premium(
    brand_price: float,
    category_avg_price: float,
    price_premium_factors: Dict
) -> Dict[str, Any]:
    """Calculate brand price premium."""
    if category_avg_price <= 0:
        return {"error": "Invalid category price"}

    premium = (brand_price / category_avg_price) - 1

    # Determine premium tier
    for tier, config in price_premium_factors.items():
        range_config = config.get("premium_range", {})
        if range_config.get("min", -1) <= premium <= range_config.get("max", 5):
            premium_tier = tier.upper()
            break
    else:
        premium_tier = "UNKNOWN"

    return {
        "brand_price": brand_price,
        "category_avg_price": category_avg_price,
        "price_premium_pct": round(premium * 100, 1),
        "premium_tier": premium_tier
    }


def evaluate_brand_equity(
    brand_id: str,
    brand_name: str,
    industry: str,
    dimension_data: Dict[str, Dict],
    annual_revenue: float,
    annual_profit: float,
    nps_data: Dict,
    brand_price: float,
    category_avg_price: float,
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate brand equity.

    Business Rules:
    1. Multi-dimensional equity scoring
    2. Brand valuation (income and market approaches)
    3. NPS calculation
    4. Industry benchmarking

    Args:
        brand_id: Brand identifier
        brand_name: Brand name
        industry: Industry for benchmarking
        dimension_data: Scores for each equity dimension
        annual_revenue: Annual brand revenue
        annual_profit: Annual brand profit
        nps_data: NPS survey data
        brand_price: Average brand product price
        category_avg_price: Category average price
        evaluation_date: Evaluation date

    Returns:
        Brand equity evaluation results
    """
    config = load_brand_metrics()
    equity_dimensions = config.get("equity_dimensions", {})
    valuation_methods = config.get("valuation_methods", {})
    performance_ratings = config.get("performance_ratings", {})
    industry_benchmarks = config.get("industry_benchmarks", {})
    nps_benchmarks = config.get("nps_benchmarks", {})
    price_premium_factors = config.get("price_premium_factors", {})

    # Calculate dimension scores
    dimension_scores = []
    for dim_name, dim_config in equity_dimensions.items():
        dim_data = dimension_data.get(dim_name, {})
        score = calculate_dimension_score(dim_name, dim_config, dim_data)
        dimension_scores.append(score)

    # Calculate overall equity
    overall_equity = calculate_overall_equity(dimension_scores)

    # Rate brand performance
    performance_rating = rate_brand_performance(
        overall_equity["overall_score"],
        performance_ratings
    )

    # Brand valuation
    income_valuation = calculate_brand_value_income(
        annual_revenue,
        valuation_methods.get("income_approach", {})
    )

    market_valuation = calculate_brand_value_market(
        annual_revenue,
        annual_profit,
        valuation_methods.get("market_approach", {})
    )

    # Weighted average valuation
    income_weight = valuation_methods.get("income_approach", {}).get("weight", 0.5)
    market_weight = valuation_methods.get("market_approach", {}).get("weight", 0.3)
    total_weight = income_weight + market_weight

    blended_value = (
        income_valuation["estimated_brand_value"] * income_weight +
        market_valuation["average_estimate"] * market_weight
    ) / total_weight

    # NPS calculation
    nps_result = calculate_nps(
        nps_data.get("promoters", 0),
        nps_data.get("passives", 0),
        nps_data.get("detractors", 0),
        nps_benchmarks
    )

    # Industry comparison
    equity_metrics = {
        "awareness": dimension_data.get("brand_awareness", {}).get("unaided_recall", 0),
        "loyalty": dimension_data.get("brand_loyalty", {}).get("repeat_purchase", 0)
    }
    industry_comparison = compare_to_industry(equity_metrics, industry, industry_benchmarks)

    # Price premium
    price_premium = calculate_price_premium(
        brand_price,
        category_avg_price,
        price_premium_factors
    )

    return {
        "brand_id": brand_id,
        "brand_name": brand_name,
        "industry": industry,
        "evaluation_date": evaluation_date,
        "equity_score": {
            "overall": overall_equity,
            "rating": performance_rating
        },
        "dimension_scores": dimension_scores,
        "brand_valuation": {
            "income_approach": income_valuation,
            "market_approach": market_valuation,
            "blended_value": round(blended_value, 2)
        },
        "customer_advocacy": nps_result,
        "industry_comparison": industry_comparison,
        "price_premium_analysis": price_premium,
        "evaluation_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = evaluate_brand_equity(
        brand_id="BRD-001",
        brand_name="TechCorp Premium",
        industry="technology",
        dimension_data={
            "brand_awareness": {
                "unaided_recall": 0.72,
                "aided_recall": 0.88,
                "top_of_mind": 0.45
            },
            "brand_associations": {
                "attribute_strength": 0.78,
                "uniqueness": 0.70,
                "favorability": 0.82
            },
            "perceived_quality": {
                "quality_rating": 0.85,
                "reliability_score": 0.88,
                "value_perception": 0.75
            },
            "brand_loyalty": {
                "repeat_purchase": 0.65,
                "recommendation_rate": 0.72,
                "price_premium_acceptance": 0.58
            },
            "brand_assets": {
                "trademark_strength": 0.80,
                "visual_identity": 0.75,
                "brand_extensions": 0.60
            }
        },
        annual_revenue=50000000,
        annual_profit=8000000,
        nps_data={
            "promoters": 450,
            "passives": 280,
            "detractors": 120
        },
        brand_price=299,
        category_avg_price=249,
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
