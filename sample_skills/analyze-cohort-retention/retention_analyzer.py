"""
Cohort Retention Analysis Module

Implements customer cohort retention analysis including
retention curves, benchmarking, and LTV calculations.
"""

import csv
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from math import exp, log



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


def load_retention_models() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    retention_metrics_data = load_csv_as_dict("retention_metrics.csv")
    industry_benchmarks_data = load_csv_as_dict("industry_benchmarks.csv")
    retention_curve_types_data = load_csv_as_dict("retention_curve_types.csv")
    health_ratings_data = load_csv_as_dict("health_ratings.csv")
    ltv_calculation_data = load_key_value_csv("ltv_calculation.csv")
    alert_thresholds_data = load_csv_as_dict("alert_thresholds.csv")
    params = load_parameters()
    return {
        "retention_metrics": retention_metrics_data,
        "industry_benchmarks": industry_benchmarks_data,
        "retention_curve_types": retention_curve_types_data,
        "health_ratings": health_ratings_data,
        "ltv_calculation": ltv_calculation_data,
        "alert_thresholds": alert_thresholds_data,
        **params
    }


def calculate_retention_rates(
    cohort_data: Dict[str, List[int]]
) -> Dict[str, Any]:
    """Calculate retention rates from cohort data."""
    retention_rates = {}
    periods = sorted(cohort_data.keys())

    for period in periods:
        users = cohort_data[period]
        if len(users) < 2:
            continue

        initial_users = users[0]
        period_rates = []

        for i, active_users in enumerate(users):
            if i == 0:
                continue
            rate = active_users / initial_users if initial_users > 0 else 0
            period_rates.append({
                "period": i,
                "active_users": active_users,
                "retention_rate": round(rate, 4)
            })

        retention_rates[period] = {
            "initial_users": initial_users,
            "retention_curve": period_rates
        }

    return retention_rates


def calculate_period_retention(
    retention_curve: List[Dict],
    period_days: int
) -> Optional[float]:
    """Get retention rate for specific period."""
    # Map period days to curve index
    period_map = {1: 1, 7: 2, 14: 3, 30: 4, 60: 5, 90: 6}
    index = period_map.get(period_days)

    if index is None or index > len(retention_curve):
        return None

    return retention_curve[index - 1]["retention_rate"]


def compare_to_benchmarks(
    retention_rates: Dict,
    industry: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Compare retention to industry benchmarks."""
    industry_bench = benchmarks.get(industry, {})

    comparisons = []
    periods = ["day_1", "day_7", "day_30", "day_90"]

    for period in periods:
        benchmark = industry_bench.get(period, 0)
        period_days = int(period.split("_")[1])

        # Calculate average actual retention across cohorts
        actual_rates = []
        for cohort_data in retention_rates.values():
            curve = cohort_data.get("retention_curve", [])
            rate = calculate_period_retention(curve, period_days)
            if rate is not None:
                actual_rates.append(rate)

        if actual_rates:
            avg_actual = sum(actual_rates) / len(actual_rates)
            vs_benchmark = avg_actual - benchmark

            comparisons.append({
                "period": period,
                "period_days": period_days,
                "benchmark": benchmark,
                "actual": round(avg_actual, 4),
                "vs_benchmark": round(vs_benchmark, 4),
                "vs_benchmark_pct": round((vs_benchmark / benchmark) * 100, 1) if benchmark > 0 else 0
            })

    return {
        "industry": industry,
        "comparisons": comparisons
    }


def rate_retention_health(
    vs_benchmark_ratio: float,
    health_ratings: Dict
) -> Dict[str, Any]:
    """Rate retention health based on benchmark comparison."""
    for rating, config in sorted(
        health_ratings.items(),
        key=lambda x: x[1].get("min_vs_benchmark", 0),
        reverse=True
    ):
        if vs_benchmark_ratio >= config.get("min_vs_benchmark", 0):
            return {
                "rating": rating.upper().replace("_", " "),
                "color": config.get("color", "gray"),
                "action": config.get("action", "monitor")
            }

    return {
        "rating": "CRITICAL",
        "color": "red",
        "action": "urgent_intervention"
    }


def calculate_churn_rate(
    retention_rate: float,
    period_type: str = "monthly"
) -> Dict[str, Any]:
    """Calculate churn rate from retention rate."""
    churn = 1 - retention_rate

    # Annualize if needed
    if period_type == "monthly":
        annual_churn = 1 - (retention_rate ** 12)
    elif period_type == "weekly":
        annual_churn = 1 - (retention_rate ** 52)
    else:
        annual_churn = churn

    return {
        "period_churn_rate": round(churn, 4),
        "annual_churn_rate": round(annual_churn, 4),
        "annual_retention_rate": round(1 - annual_churn, 4)
    }


def calculate_ltv(
    arpu: float,
    gross_margin: float,
    churn_rate: float,
    discount_rate: float
) -> Dict[str, Any]:
    """Calculate customer lifetime value."""
    if churn_rate <= 0:
        return {"error": "Invalid churn rate"}

    # Simple LTV = Margin per customer / Churn rate
    margin_per_customer = arpu * gross_margin
    simple_ltv = margin_per_customer / churn_rate

    # Discounted LTV
    if discount_rate + churn_rate > 0:
        discounted_ltv = margin_per_customer / (discount_rate + churn_rate)
    else:
        discounted_ltv = simple_ltv

    # Expected lifetime in months
    expected_lifetime = 1 / churn_rate if churn_rate > 0 else float('inf')

    return {
        "arpu": arpu,
        "gross_margin": gross_margin,
        "margin_per_customer": round(margin_per_customer, 2),
        "churn_rate": churn_rate,
        "simple_ltv": round(simple_ltv, 2),
        "discounted_ltv": round(discounted_ltv, 2),
        "expected_lifetime_months": round(expected_lifetime, 1)
    }


def segment_cohorts(
    retention_rates: Dict,
    segmentation_dimension: str,
    segment_values: List[str]
) -> Dict[str, Any]:
    """Segment retention analysis by dimension."""
    segmented_results = {}

    for segment in segment_values:
        segment_cohorts = {
            k: v for k, v in retention_rates.items()
            if segment.lower() in k.lower()
        }

        if segment_cohorts:
            # Calculate average retention for segment
            all_rates = []
            for cohort in segment_cohorts.values():
                curve = cohort.get("retention_curve", [])
                if len(curve) >= 4:  # At least day 30
                    all_rates.append(curve[3]["retention_rate"])

            avg_retention = sum(all_rates) / len(all_rates) if all_rates else 0

            segmented_results[segment] = {
                "cohort_count": len(segment_cohorts),
                "avg_day30_retention": round(avg_retention, 4),
                "total_users": sum(c.get("initial_users", 0) for c in segment_cohorts.values())
            }

    return {
        "dimension": segmentation_dimension,
        "segments": segmented_results
    }


def detect_retention_alerts(
    retention_rates: Dict,
    alert_thresholds: Dict
) -> List[Dict]:
    """Detect retention anomalies and alerts."""
    alerts = []

    # Get recent cohorts for comparison
    sorted_periods = sorted(retention_rates.keys(), reverse=True)

    if len(sorted_periods) < 2:
        return alerts

    recent_cohort = retention_rates[sorted_periods[0]]
    prior_cohort = retention_rates[sorted_periods[1]]

    recent_curve = recent_cohort.get("retention_curve", [])
    prior_curve = prior_cohort.get("retention_curve", [])

    if len(recent_curve) >= 4 and len(prior_curve) >= 4:
        # Check day 30 retention change
        recent_d30 = recent_curve[3]["retention_rate"]
        prior_d30 = prior_curve[3]["retention_rate"]

        pct_change = (recent_d30 - prior_d30) / prior_d30 if prior_d30 > 0 else 0

        # Check against thresholds
        sudden_drop = alert_thresholds.get("sudden_drop", {})
        if pct_change <= sudden_drop.get("pct_change", -0.20):
            alerts.append({
                "type": "SUDDEN_DROP",
                "severity": sudden_drop.get("severity", "critical"),
                "metric": "day_30_retention",
                "change_pct": round(pct_change * 100, 1),
                "threshold": sudden_drop.get("pct_change", -0.20) * 100,
                "message": f"Day 30 retention dropped {abs(pct_change * 100):.1f}% vs prior cohort"
            })

        gradual_decline = alert_thresholds.get("gradual_decline", {})
        if gradual_decline.get("pct_change", -0.10) < pct_change <= sudden_drop.get("pct_change", -0.20):
            alerts.append({
                "type": "GRADUAL_DECLINE",
                "severity": gradual_decline.get("severity", "warning"),
                "metric": "day_30_retention",
                "change_pct": round(pct_change * 100, 1),
                "message": f"Day 30 retention declined {abs(pct_change * 100):.1f}% vs prior cohort"
            })

        improvement = alert_thresholds.get("improvement", {})
        if pct_change >= improvement.get("pct_change", 0.10):
            alerts.append({
                "type": "IMPROVEMENT",
                "severity": improvement.get("severity", "positive"),
                "metric": "day_30_retention",
                "change_pct": round(pct_change * 100, 1),
                "message": f"Day 30 retention improved {pct_change * 100:.1f}% vs prior cohort"
            })

    return alerts


def analyze_cohort_retention(
    analysis_id: str,
    product_name: str,
    industry: str,
    cohort_data: Dict[str, List[int]],
    arpu: float,
    gross_margin: float,
    segmentation_dimension: Optional[str],
    segment_values: Optional[List[str]],
    analysis_date: str
) -> Dict[str, Any]:
    """
    Analyze cohort retention.

    Business Rules:
    1. Retention curve calculation
    2. Industry benchmarking
    3. LTV estimation
    4. Alert detection

    Args:
        analysis_id: Analysis identifier
        product_name: Product name
        industry: Industry for benchmarking
        cohort_data: Cohort user counts by period
        arpu: Average revenue per user (monthly)
        gross_margin: Gross margin percentage
        segmentation_dimension: Optional segmentation dimension
        segment_values: Optional segment values to analyze
        analysis_date: Analysis date

    Returns:
        Cohort retention analysis results
    """
    config = load_retention_models()
    industry_benchmarks = config.get("industry_benchmarks", {})
    health_ratings = config.get("health_ratings", {})
    ltv_config = config.get("ltv_calculation", {})
    alert_thresholds = config.get("alert_thresholds", {})

    # Calculate retention rates
    retention_rates = calculate_retention_rates(cohort_data)

    # Compare to benchmarks
    benchmark_comparison = compare_to_benchmarks(
        retention_rates,
        industry,
        industry_benchmarks
    )

    # Calculate overall vs benchmark ratio
    if benchmark_comparison["comparisons"]:
        avg_vs_benchmark = sum(
            1 + c["vs_benchmark_pct"] / 100
            for c in benchmark_comparison["comparisons"]
        ) / len(benchmark_comparison["comparisons"])
    else:
        avg_vs_benchmark = 1.0

    # Rate retention health
    health_rating = rate_retention_health(avg_vs_benchmark, health_ratings)

    # Calculate churn and LTV
    # Use average day 30 retention as base
    d30_rates = []
    for cohort in retention_rates.values():
        curve = cohort.get("retention_curve", [])
        if len(curve) >= 4:
            d30_rates.append(curve[3]["retention_rate"])

    avg_d30_retention = sum(d30_rates) / len(d30_rates) if d30_rates else 0.5

    churn_analysis = calculate_churn_rate(avg_d30_retention, "monthly")

    ltv_analysis = calculate_ltv(
        arpu,
        gross_margin,
        churn_analysis["period_churn_rate"],
        ltv_config.get("discount_rate", 0.10)
    )

    # Segmentation analysis
    segmentation = None
    if segmentation_dimension and segment_values:
        segmentation = segment_cohorts(
            retention_rates,
            segmentation_dimension,
            segment_values
        )

    # Detect alerts
    alerts = detect_retention_alerts(retention_rates, alert_thresholds)

    # Summary statistics
    total_users = sum(c.get("initial_users", 0) for c in retention_rates.values())

    return {
        "analysis_id": analysis_id,
        "product_name": product_name,
        "industry": industry,
        "analysis_date": analysis_date,
        "summary": {
            "total_cohorts": len(retention_rates),
            "total_users_analyzed": total_users,
            "avg_day30_retention": round(avg_d30_retention, 4),
            "health_rating": health_rating
        },
        "retention_by_cohort": retention_rates,
        "benchmark_comparison": benchmark_comparison,
        "churn_analysis": churn_analysis,
        "ltv_analysis": ltv_analysis,
        "segmentation": segmentation,
        "alerts": alerts,
        "analysis_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = analyze_cohort_retention(
        analysis_id="RET-001",
        product_name="SaaS Platform Pro",
        industry="saas_b2b",
        cohort_data={
            "2025-10": [1000, 850, 750, 700, 650, 620, 600],
            "2025-11": [1200, 1020, 900, 840, 780, 750, 720],
            "2025-12": [1100, 935, 825, 770, 715, 682, 660]
        },
        arpu=99,
        gross_margin=0.75,
        segmentation_dimension="acquisition_channel",
        segment_values=["organic", "paid"],
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
