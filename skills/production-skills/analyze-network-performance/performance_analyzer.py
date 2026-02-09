"""
Network Performance Analysis Module

Implements network performance assessment including
latency analysis, capacity planning, and SLA compliance.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
import math



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


def load_network_thresholds() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    performance_metrics_data = load_csv_as_dict("performance_metrics.csv")
    application_requirements_data = load_csv_as_dict("application_requirements.csv")
    capacity_planning_data = load_key_value_csv("capacity_planning.csv")
    sla_definitions_data = load_csv_as_dict("sla_definitions.csv")
    alert_thresholds_data = load_key_value_csv("alert_thresholds.csv")
    baseline_deviation_data = load_key_value_csv("baseline_deviation.csv")
    params = load_parameters()
    return {
        "performance_metrics": performance_metrics_data,
        "application_requirements": application_requirements_data,
        "capacity_planning": capacity_planning_data,
        "sla_definitions": sla_definitions_data,
        "alert_thresholds": alert_thresholds_data,
        "baseline_deviation": baseline_deviation_data,
        **params
    }


def calculate_statistics(
    values: List[float]
) -> Dict[str, float]:
    """Calculate statistical measures."""
    if not values:
        return {"mean": 0, "std_dev": 0, "min": 0, "max": 0, "p95": 0}

    n = len(values)
    mean = sum(values) / n
    variance = sum((x - mean) ** 2 for x in values) / n if n > 1 else 0
    std_dev = math.sqrt(variance)

    sorted_values = sorted(values)
    p95_idx = int(n * 0.95)
    p95 = sorted_values[min(p95_idx, n - 1)]

    return {
        "mean": round(mean, 2),
        "std_dev": round(std_dev, 2),
        "min": round(min(values), 2),
        "max": round(max(values), 2),
        "p95": round(p95, 2)
    }


def score_metric(
    value: float,
    thresholds: Dict,
    lower_is_better: bool = True
) -> Dict[str, Any]:
    """Score a metric against thresholds."""
    if lower_is_better:
        if value <= thresholds.get("excellent", 0):
            rating = "EXCELLENT"
            score = 100
        elif value <= thresholds.get("good", 0):
            rating = "GOOD"
            score = 80
        elif value <= thresholds.get("acceptable", 0):
            rating = "ACCEPTABLE"
            score = 60
        else:
            rating = "POOR"
            score = 30
    else:
        if value >= thresholds.get("excellent", 100):
            rating = "EXCELLENT"
            score = 100
        elif value >= thresholds.get("good", 99):
            rating = "GOOD"
            score = 80
        elif value >= thresholds.get("acceptable", 95):
            rating = "ACCEPTABLE"
            score = 60
        else:
            rating = "POOR"
            score = 30

    return {"value": value, "rating": rating, "score": score}


def analyze_latency(
    latency_samples: List[float],
    thresholds: Dict
) -> Dict[str, Any]:
    """Analyze latency metrics."""
    stats = calculate_statistics(latency_samples)
    score_result = score_metric(stats["mean"], thresholds)

    return {
        "statistics": stats,
        "rating": score_result["rating"],
        "score": score_result["score"],
        "high_latency_samples": sum(1 for l in latency_samples if l > thresholds.get("acceptable", 100)),
        "high_latency_pct": round(sum(1 for l in latency_samples if l > thresholds.get("acceptable", 100)) / len(latency_samples) * 100, 1) if latency_samples else 0
    }


def analyze_packet_loss(
    packet_loss_samples: List[float],
    thresholds: Dict
) -> Dict[str, Any]:
    """Analyze packet loss metrics."""
    stats = calculate_statistics(packet_loss_samples)
    score_result = score_metric(stats["mean"], thresholds)

    return {
        "statistics": stats,
        "rating": score_result["rating"],
        "score": score_result["score"],
        "loss_events": sum(1 for p in packet_loss_samples if p > thresholds.get("good", 0.1))
    }


def analyze_bandwidth_utilization(
    utilization_samples: List[float],
    thresholds: Dict
) -> Dict[str, Any]:
    """Analyze bandwidth utilization."""
    stats = calculate_statistics(utilization_samples)

    optimal_max = thresholds.get("optimal_max", 70)
    warning = thresholds.get("warning", 80)
    critical = thresholds.get("critical", 90)

    if stats["mean"] <= optimal_max:
        rating = "OPTIMAL"
        score = 100
    elif stats["mean"] <= warning:
        rating = "WARNING"
        score = 70
    elif stats["mean"] <= critical:
        rating = "HIGH"
        score = 40
    else:
        rating = "CRITICAL"
        score = 20

    peak_count = sum(1 for u in utilization_samples if u > critical)

    return {
        "statistics": stats,
        "rating": rating,
        "score": score,
        "peak_events": peak_count,
        "headroom_pct": round(100 - stats["mean"], 1)
    }


def check_application_requirements(
    metrics: Dict,
    application: str,
    app_requirements: Dict
) -> Dict[str, Any]:
    """Check if metrics meet application requirements."""
    requirements = app_requirements.get(application, app_requirements.get("web_application", {}))

    compliance = {}
    all_compliant = True

    # Latency check
    latency = metrics.get("latency_mean", 0)
    max_latency = requirements.get("max_latency", 200)
    compliance["latency"] = {
        "actual": latency,
        "requirement": max_latency,
        "compliant": latency <= max_latency
    }
    if latency > max_latency:
        all_compliant = False

    # Jitter check
    jitter = metrics.get("jitter_mean", 0)
    max_jitter = requirements.get("max_jitter", 50)
    compliance["jitter"] = {
        "actual": jitter,
        "requirement": max_jitter,
        "compliant": jitter <= max_jitter
    }
    if jitter > max_jitter:
        all_compliant = False

    # Packet loss check
    packet_loss = metrics.get("packet_loss_mean", 0)
    max_packet_loss = requirements.get("max_packet_loss", 1.0)
    compliance["packet_loss"] = {
        "actual": packet_loss,
        "requirement": max_packet_loss,
        "compliant": packet_loss <= max_packet_loss
    }
    if packet_loss > max_packet_loss:
        all_compliant = False

    return {
        "application": application,
        "overall_compliant": all_compliant,
        "compliance_details": compliance
    }


def check_sla_compliance(
    metrics: Dict,
    sla_tier: str,
    sla_definitions: Dict
) -> Dict[str, Any]:
    """Check SLA compliance."""
    sla = sla_definitions.get(sla_tier, sla_definitions.get("standard", {}))

    violations = []

    # Availability
    availability = metrics.get("availability", 100)
    if availability < sla.get("availability", 99.9):
        violations.append({
            "metric": "availability",
            "actual": availability,
            "sla_requirement": sla.get("availability", 99.9),
            "severity": "critical"
        })

    # Latency
    latency = metrics.get("latency_mean", 0)
    if latency > sla.get("max_latency", 100):
        violations.append({
            "metric": "latency",
            "actual": latency,
            "sla_requirement": sla.get("max_latency", 100),
            "severity": "major"
        })

    # Packet loss
    packet_loss = metrics.get("packet_loss_mean", 0)
    if packet_loss > sla.get("max_packet_loss", 0.1):
        violations.append({
            "metric": "packet_loss",
            "actual": packet_loss,
            "sla_requirement": sla.get("max_packet_loss", 0.1),
            "severity": "major"
        })

    return {
        "sla_tier": sla_tier,
        "compliant": len(violations) == 0,
        "violations": violations,
        "violation_count": len(violations)
    }


def detect_anomalies(
    current_values: List[float],
    baseline_mean: float,
    baseline_std: float,
    deviation_threshold: float
) -> Dict[str, Any]:
    """Detect anomalies based on baseline deviation."""
    anomalies = []
    current_mean = sum(current_values) / len(current_values) if current_values else 0

    for i, value in enumerate(current_values):
        if baseline_std > 0:
            z_score = (value - baseline_mean) / baseline_std
            if abs(z_score) > deviation_threshold:
                anomalies.append({
                    "index": i,
                    "value": value,
                    "z_score": round(z_score, 2),
                    "deviation_type": "high" if z_score > 0 else "low"
                })

    # Check trend deviation
    trend_change_pct = ((current_mean - baseline_mean) / baseline_mean * 100) if baseline_mean > 0 else 0

    return {
        "anomaly_count": len(anomalies),
        "anomalies": anomalies[:10],  # First 10
        "baseline_mean": baseline_mean,
        "current_mean": round(current_mean, 2),
        "trend_change_pct": round(trend_change_pct, 1)
    }


def forecast_capacity(
    current_utilization: float,
    growth_rate_monthly: float,
    capacity_config: Dict,
    months: int = 12
) -> Dict[str, Any]:
    """Forecast capacity requirements."""
    forecasts = []
    utilization = current_utilization
    warning_threshold = 80
    critical_threshold = 90

    warning_month = None
    critical_month = None

    for month in range(1, months + 1):
        utilization = utilization * (1 + growth_rate_monthly)
        forecasts.append({
            "month": month,
            "projected_utilization": round(utilization, 1)
        })

        if warning_month is None and utilization >= warning_threshold:
            warning_month = month
        if critical_month is None and utilization >= critical_threshold:
            critical_month = month

    return {
        "current_utilization": current_utilization,
        "growth_rate_monthly": growth_rate_monthly,
        "forecast_months": months,
        "projected_utilization_eoy": forecasts[-1]["projected_utilization"] if forecasts else current_utilization,
        "warning_threshold_month": warning_month,
        "critical_threshold_month": critical_month,
        "upgrade_recommended": warning_month is not None and warning_month <= 6
    }


def analyze_network_performance(
    network_id: str,
    latency_samples: List[float],
    packet_loss_samples: List[float],
    jitter_samples: List[float],
    utilization_samples: List[float],
    availability_pct: float,
    application_type: str,
    sla_tier: str,
    baseline_latency: Dict,
    growth_rate_monthly: float,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Analyze network performance.

    Business Rules:
    1. Multi-metric performance scoring
    2. Application requirement validation
    3. SLA compliance checking
    4. Capacity forecasting

    Args:
        network_id: Network identifier
        latency_samples: Latency measurements (ms)
        packet_loss_samples: Packet loss measurements (%)
        jitter_samples: Jitter measurements (ms)
        utilization_samples: Bandwidth utilization (%)
        availability_pct: Network availability
        application_type: Primary application type
        sla_tier: SLA tier
        baseline_latency: Baseline latency statistics
        growth_rate_monthly: Monthly traffic growth rate
        analysis_date: Analysis date

    Returns:
        Network performance analysis results
    """
    thresholds = load_network_thresholds()
    metrics = thresholds.get("performance_metrics", {})

    # Analyze individual metrics
    latency_analysis = analyze_latency(latency_samples, metrics.get("latency_ms", {}))
    packet_loss_analysis = analyze_packet_loss(packet_loss_samples, metrics.get("packet_loss_pct", {}))
    jitter_stats = calculate_statistics(jitter_samples)
    utilization_analysis = analyze_bandwidth_utilization(utilization_samples, metrics.get("bandwidth_utilization_pct", {}))

    # Calculate overall metrics for compliance checks
    overall_metrics = {
        "latency_mean": latency_analysis["statistics"]["mean"],
        "packet_loss_mean": packet_loss_analysis["statistics"]["mean"],
        "jitter_mean": jitter_stats["mean"],
        "utilization_mean": utilization_analysis["statistics"]["mean"],
        "availability": availability_pct
    }

    # Check application requirements
    app_compliance = check_application_requirements(
        overall_metrics,
        application_type,
        thresholds.get("application_requirements", {})
    )

    # Check SLA compliance
    sla_compliance = check_sla_compliance(
        overall_metrics,
        sla_tier,
        thresholds.get("sla_definitions", {})
    )

    # Detect anomalies
    anomaly_analysis = detect_anomalies(
        latency_samples,
        baseline_latency.get("mean", 50),
        baseline_latency.get("std_dev", 10),
        thresholds.get("baseline_deviation", {}).get("anomaly_std_dev", 2.5)
    )

    # Capacity forecast
    capacity_forecast = forecast_capacity(
        utilization_analysis["statistics"]["mean"],
        growth_rate_monthly,
        thresholds.get("capacity_planning", {}),
        thresholds.get("capacity_planning", {}).get("forecast_months", 12)
    )

    # Calculate overall health score
    health_score = (
        latency_analysis["score"] * 0.30 +
        packet_loss_analysis["score"] * 0.25 +
        utilization_analysis["score"] * 0.25 +
        (100 if sla_compliance["compliant"] else 50) * 0.20
    )

    # Determine overall status
    if health_score >= 85:
        status = "HEALTHY"
    elif health_score >= 70:
        status = "GOOD"
    elif health_score >= 50:
        status = "DEGRADED"
    else:
        status = "CRITICAL"

    return {
        "network_id": network_id,
        "analysis_date": analysis_date,
        "performance_analysis": {
            "latency": latency_analysis,
            "packet_loss": packet_loss_analysis,
            "jitter": jitter_stats,
            "bandwidth_utilization": utilization_analysis,
            "availability": availability_pct
        },
        "application_compliance": app_compliance,
        "sla_compliance": sla_compliance,
        "anomaly_detection": anomaly_analysis,
        "capacity_forecast": capacity_forecast,
        "health_score": round(health_score, 1),
        "overall_status": status,
        "recommendations": generate_recommendations(
            latency_analysis,
            utilization_analysis,
            sla_compliance,
            capacity_forecast
        )
    }


def generate_recommendations(
    latency: Dict,
    utilization: Dict,
    sla: Dict,
    capacity: Dict
) -> List[str]:
    """Generate performance recommendations."""
    recommendations = []

    if latency["rating"] in ["ACCEPTABLE", "POOR"]:
        recommendations.append("Investigate latency sources and consider WAN optimization")

    if utilization["rating"] in ["HIGH", "CRITICAL"]:
        recommendations.append("Consider bandwidth upgrade or traffic shaping")

    if not sla["compliant"]:
        recommendations.append(f"Address {sla['violation_count']} SLA violations immediately")

    if capacity.get("upgrade_recommended"):
        recommendations.append(f"Plan capacity upgrade - warning threshold projected in {capacity['warning_threshold_month']} months")

    return recommendations


if __name__ == "__main__":
    import json
    result = analyze_network_performance(
        network_id="NET-001",
        latency_samples=[45, 52, 48, 55, 42, 60, 47, 51, 49, 53, 150, 48, 52, 46, 55],
        packet_loss_samples=[0.05, 0.02, 0.08, 0.03, 0.01, 0.5, 0.02, 0.04, 0.03, 0.02],
        jitter_samples=[8, 12, 10, 15, 9, 11, 13, 10, 12, 14],
        utilization_samples=[65, 70, 68, 72, 75, 78, 73, 71, 69, 74],
        availability_pct=99.95,
        application_type="voip",
        sla_tier="premium",
        baseline_latency={"mean": 50, "std_dev": 8},
        growth_rate_monthly=0.03,
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
