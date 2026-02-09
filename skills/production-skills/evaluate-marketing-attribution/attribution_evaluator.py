"""
Marketing Attribution Evaluation Module

Implements multi-touch attribution analysis including
channel performance, ROI calculation, and model comparison.
"""

import csv
import ast
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import math



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


def load_attribution_models() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    attribution_models_data = load_csv_as_dict("attribution_models.csv")
    channel_categories_data = load_csv_as_dict("channel_categories.csv")
    conversion_windows_data = load_csv_as_dict("conversion_windows.csv")
    roi_benchmarks_data = load_csv_as_dict("roi_benchmarks.csv")
    incrementality_factors_data = load_key_value_csv("incrementality_factors.csv")
    funnel_stages_data = load_csv_as_dict("funnel_stages.csv")
    params = load_parameters()
    return {
        "attribution_models": attribution_models_data,
        "channel_categories": channel_categories_data,
        "conversion_windows": conversion_windows_data,
        "roi_benchmarks": roi_benchmarks_data,
        "incrementality_factors": incrementality_factors_data,
        "funnel_stages": funnel_stages_data,
        **params
    }


def apply_last_touch(
    touchpoints: List[Dict],
    conversion_value: float
) -> Dict[str, float]:
    """Apply last-touch attribution."""
    if not touchpoints:
        return {}

    last_touch = touchpoints[-1]
    return {last_touch.get("channel", "unknown"): conversion_value}


def apply_first_touch(
    touchpoints: List[Dict],
    conversion_value: float
) -> Dict[str, float]:
    """Apply first-touch attribution."""
    if not touchpoints:
        return {}

    first_touch = touchpoints[0]
    return {first_touch.get("channel", "unknown"): conversion_value}


def apply_linear(
    touchpoints: List[Dict],
    conversion_value: float
) -> Dict[str, float]:
    """Apply linear attribution."""
    if not touchpoints:
        return {}

    credit_per_touch = conversion_value / len(touchpoints)
    attribution = {}

    for touch in touchpoints:
        channel = touch.get("channel", "unknown")
        attribution[channel] = attribution.get(channel, 0) + credit_per_touch

    return attribution


def apply_time_decay(
    touchpoints: List[Dict],
    conversion_value: float,
    half_life_days: int = 7
) -> Dict[str, float]:
    """Apply time-decay attribution."""
    if not touchpoints:
        return {}

    # Calculate days from conversion for each touchpoint
    conversion_time = datetime.now()
    weights = []

    for touch in touchpoints:
        touch_time = datetime.strptime(touch.get("timestamp", ""), "%Y-%m-%d %H:%M:%S")
        days_before = (conversion_time - touch_time).days
        weight = math.pow(0.5, days_before / half_life_days)
        weights.append(weight)

    total_weight = sum(weights)
    attribution = {}

    for i, touch in enumerate(touchpoints):
        channel = touch.get("channel", "unknown")
        credit = (weights[i] / total_weight) * conversion_value if total_weight > 0 else 0
        attribution[channel] = attribution.get(channel, 0) + credit

    return attribution


def apply_position_based(
    touchpoints: List[Dict],
    conversion_value: float,
    weights: Dict
) -> Dict[str, float]:
    """Apply position-based attribution."""
    if not touchpoints:
        return {}

    first_weight = weights.get("first", 0.40)
    last_weight = weights.get("last", 0.40)
    middle_weight = weights.get("middle", 0.20)

    attribution = {}
    n = len(touchpoints)

    if n == 1:
        channel = touchpoints[0].get("channel", "unknown")
        attribution[channel] = conversion_value
    elif n == 2:
        attribution[touchpoints[0].get("channel", "unknown")] = conversion_value * 0.5
        attribution[touchpoints[1].get("channel", "unknown")] = attribution.get(
            touchpoints[1].get("channel", "unknown"), 0) + conversion_value * 0.5
    else:
        # First touch
        channel = touchpoints[0].get("channel", "unknown")
        attribution[channel] = conversion_value * first_weight

        # Last touch
        channel = touchpoints[-1].get("channel", "unknown")
        attribution[channel] = attribution.get(channel, 0) + conversion_value * last_weight

        # Middle touches
        middle_credit = (conversion_value * middle_weight) / (n - 2)
        for touch in touchpoints[1:-1]:
            channel = touch.get("channel", "unknown")
            attribution[channel] = attribution.get(channel, 0) + middle_credit

    return attribution


def calculate_channel_metrics(
    conversions: List[Dict],
    channel_spend: Dict[str, float],
    attribution_results: Dict[str, float]
) -> Dict[str, Any]:
    """Calculate channel performance metrics."""
    metrics = {}

    for channel, attributed_value in attribution_results.items():
        spend = channel_spend.get(channel, 0)

        roas = attributed_value / spend if spend > 0 else 0
        conversion_count = sum(1 for c in conversions if channel in [t.get("channel") for t in c.get("touchpoints", [])])
        cpa = spend / conversion_count if conversion_count > 0 else 0

        metrics[channel] = {
            "attributed_revenue": round(attributed_value, 2),
            "spend": spend,
            "roas": round(roas, 2),
            "conversion_count": conversion_count,
            "cpa": round(cpa, 2)
        }

    return metrics


def compare_models(
    touchpoints: List[Dict],
    conversion_value: float,
    models_config: Dict
) -> Dict[str, Dict]:
    """Compare attribution across different models."""
    comparisons = {}

    # Last touch
    comparisons["last_touch"] = apply_last_touch(touchpoints, conversion_value)

    # First touch
    comparisons["first_touch"] = apply_first_touch(touchpoints, conversion_value)

    # Linear
    comparisons["linear"] = apply_linear(touchpoints, conversion_value)

    # Time decay
    time_decay_config = models_config.get("time_decay", {})
    comparisons["time_decay"] = apply_time_decay(
        touchpoints,
        conversion_value,
        time_decay_config.get("half_life_days", 7)
    )

    # Position based
    position_config = models_config.get("position_based", {}).get("weights", {})
    comparisons["position_based"] = apply_position_based(
        touchpoints,
        conversion_value,
        position_config
    )

    return comparisons


def analyze_funnel_contribution(
    touchpoints: List[Dict],
    funnel_stages: Dict,
    channel_categories: Dict
) -> Dict[str, Any]:
    """Analyze channel contribution by funnel stage."""
    stage_analysis = {}

    for stage, config in funnel_stages.items():
        stage_channels = config.get("channels", [])
        stage_touches = [t for t in touchpoints if t.get("channel") in stage_channels]

        stage_analysis[stage] = {
            "touch_count": len(stage_touches),
            "channels_present": list(set(t.get("channel") for t in stage_touches)),
            "pct_of_journey": round(len(stage_touches) / len(touchpoints) * 100, 1) if touchpoints else 0
        }

    return stage_analysis


def calculate_incrementality_adjusted_value(
    attributed_value: float,
    channel: str,
    channel_type: str,
    incrementality_factors: Dict
) -> Dict[str, Any]:
    """Adjust attribution for incrementality."""
    factor_key = f"{channel}_{channel_type}"
    factor = incrementality_factors.get(factor_key, 0.50)

    incremental_value = attributed_value * factor

    return {
        "attributed_value": attributed_value,
        "incrementality_factor": factor,
        "incremental_value": round(incremental_value, 2)
    }


def benchmark_performance(
    channel_metrics: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Compare channel performance against benchmarks."""
    benchmark_comparison = {}

    for channel, metrics in channel_metrics.items():
        channel_benchmark = benchmarks.get(channel, {})

        roas_benchmark = channel_benchmark.get("roas_benchmark", 0)
        cpa_benchmark = channel_benchmark.get("cpa_benchmark", 0)

        roas_performance = metrics.get("roas", 0) / roas_benchmark if roas_benchmark > 0 else 0
        cpa_performance = cpa_benchmark / metrics.get("cpa", 1) if metrics.get("cpa", 0) > 0 else 0

        benchmark_comparison[channel] = {
            "roas_vs_benchmark": round(roas_performance, 2),
            "cpa_vs_benchmark": round(cpa_performance, 2),
            "overall_performance": "above" if roas_performance > 1 and cpa_performance > 1 else "below"
        }

    return benchmark_comparison


def evaluate_marketing_attribution(
    campaign_id: str,
    conversions: List[Dict],
    channel_spend: Dict[str, float],
    attribution_model: str,
    conversion_window_days: int,
    evaluation_date: str
) -> Dict[str, Any]:
    """
    Evaluate marketing attribution.

    Business Rules:
    1. Multi-touch attribution modeling
    2. Channel performance analysis
    3. ROI and ROAS calculation
    4. Incrementality adjustment

    Args:
        campaign_id: Campaign identifier
        conversions: List of conversions with touchpoints
        channel_spend: Spend by channel
        attribution_model: Attribution model to use
        conversion_window_days: Conversion window
        evaluation_date: Evaluation date

    Returns:
        Marketing attribution evaluation results
    """
    config = load_attribution_models()
    models = config.get("attribution_models", {})

    # Aggregate touchpoints and conversion values
    all_touchpoints = []
    total_conversion_value = 0

    for conversion in conversions:
        touchpoints = conversion.get("touchpoints", [])
        all_touchpoints.extend(touchpoints)
        total_conversion_value += conversion.get("value", 0)

    # Apply selected attribution model
    model_config = models.get(attribution_model, models.get("linear", {}))

    if attribution_model == "last_touch":
        primary_attribution = {}
        for conversion in conversions:
            result = apply_last_touch(conversion.get("touchpoints", []), conversion.get("value", 0))
            for channel, value in result.items():
                primary_attribution[channel] = primary_attribution.get(channel, 0) + value
    elif attribution_model == "first_touch":
        primary_attribution = {}
        for conversion in conversions:
            result = apply_first_touch(conversion.get("touchpoints", []), conversion.get("value", 0))
            for channel, value in result.items():
                primary_attribution[channel] = primary_attribution.get(channel, 0) + value
    elif attribution_model == "time_decay":
        primary_attribution = {}
        for conversion in conversions:
            result = apply_time_decay(
                conversion.get("touchpoints", []),
                conversion.get("value", 0),
                model_config.get("half_life_days", 7)
            )
            for channel, value in result.items():
                primary_attribution[channel] = primary_attribution.get(channel, 0) + value
    elif attribution_model == "position_based":
        primary_attribution = {}
        for conversion in conversions:
            result = apply_position_based(
                conversion.get("touchpoints", []),
                conversion.get("value", 0),
                model_config.get("weights", {"first": 0.4, "last": 0.4, "middle": 0.2})
            )
            for channel, value in result.items():
                primary_attribution[channel] = primary_attribution.get(channel, 0) + value
    else:  # linear
        primary_attribution = {}
        for conversion in conversions:
            result = apply_linear(conversion.get("touchpoints", []), conversion.get("value", 0))
            for channel, value in result.items():
                primary_attribution[channel] = primary_attribution.get(channel, 0) + value

    # Round attribution values
    primary_attribution = {k: round(v, 2) for k, v in primary_attribution.items()}

    # Calculate channel metrics
    channel_metrics = calculate_channel_metrics(
        conversions,
        channel_spend,
        primary_attribution
    )

    # Model comparison (for first conversion as sample)
    model_comparison = {}
    if conversions:
        sample_conversion = conversions[0]
        model_comparison = compare_models(
            sample_conversion.get("touchpoints", []),
            sample_conversion.get("value", 0),
            models
        )

    # Funnel analysis
    funnel_analysis = analyze_funnel_contribution(
        all_touchpoints,
        config.get("funnel_stages", {}),
        config.get("channel_categories", {})
    )

    # Benchmark comparison
    benchmark_comparison = benchmark_performance(
        channel_metrics,
        config.get("roi_benchmarks", {})
    )

    # Calculate totals
    total_spend = sum(channel_spend.values())
    total_roas = total_conversion_value / total_spend if total_spend > 0 else 0

    return {
        "campaign_id": campaign_id,
        "evaluation_date": evaluation_date,
        "attribution_model": attribution_model,
        "conversion_window_days": conversion_window_days,
        "summary": {
            "total_conversions": len(conversions),
            "total_conversion_value": round(total_conversion_value, 2),
            "total_spend": round(total_spend, 2),
            "overall_roas": round(total_roas, 2)
        },
        "channel_attribution": primary_attribution,
        "channel_metrics": channel_metrics,
        "model_comparison_sample": model_comparison,
        "funnel_analysis": funnel_analysis,
        "benchmark_comparison": benchmark_comparison
    }


if __name__ == "__main__":
    import json
    result = evaluate_marketing_attribution(
        campaign_id="CAMP-001",
        conversions=[
            {
                "conversion_id": "CONV-001",
                "value": 150,
                "touchpoints": [
                    {"channel": "paid_social", "timestamp": "2026-01-10 10:00:00"},
                    {"channel": "organic_search", "timestamp": "2026-01-15 14:00:00"},
                    {"channel": "email", "timestamp": "2026-01-18 09:00:00"},
                    {"channel": "paid_search", "timestamp": "2026-01-20 11:00:00"}
                ]
            },
            {
                "conversion_id": "CONV-002",
                "value": 200,
                "touchpoints": [
                    {"channel": "display", "timestamp": "2026-01-12 08:00:00"},
                    {"channel": "paid_search", "timestamp": "2026-01-19 16:00:00"}
                ]
            }
        ],
        channel_spend={
            "paid_search": 5000,
            "paid_social": 3000,
            "display": 2000,
            "email": 500,
            "organic_search": 0
        },
        attribution_model="position_based",
        conversion_window_days=30,
        evaluation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
