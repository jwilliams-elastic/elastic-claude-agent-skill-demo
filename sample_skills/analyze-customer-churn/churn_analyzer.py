"""
Customer Churn Analysis Module

Implements churn risk scoring using behavioral signals,
usage patterns, and engagement metrics.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta



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


def load_churn_signals() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    usage_benchmarks_data = load_key_value_csv("usage_benchmarks.csv")
    engagement_windows_data = load_key_value_csv("engagement_windows.csv")
    sentiment_weights_data = load_key_value_csv("sentiment_weights.csv")
    billing_thresholds_data = load_key_value_csv("billing_thresholds.csv")
    savability_factors_data = load_key_value_csv("savability_factors.csv")
    risk_weights_data = load_key_value_csv("risk_weights.csv")
    signal_definitions_data = load_csv_as_dict("signal_definitions.csv")
    intervention_playbook_data = load_csv_as_dict("intervention_playbook.csv")
    cohort_benchmarks_data = load_csv_as_dict("cohort_benchmarks.csv")
    params = load_parameters()
    return {
        "usage_benchmarks": usage_benchmarks_data,
        "engagement_windows": engagement_windows_data,
        "sentiment_weights": sentiment_weights_data,
        "billing_thresholds": billing_thresholds_data,
        "savability_factors": savability_factors_data,
        "risk_weights": risk_weights_data,
        "signal_definitions": signal_definitions_data,
        "intervention_playbook": intervention_playbook_data,
        "cohort_benchmarks": cohort_benchmarks_data,
        **params
    }


def analyze_usage_decline(
    usage_metrics: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Analyze usage metrics for decline signals."""
    signals = []
    risk_contribution = 0

    logins_30d = usage_metrics.get("logins_30d", 0)
    features_used = usage_metrics.get("features_used", 0)
    api_calls = usage_metrics.get("api_calls", 0)

    login_benchmark = benchmarks.get("healthy_logins_30d", 20)
    feature_benchmark = benchmarks.get("healthy_features", 5)

    # Login frequency decline
    if logins_30d < login_benchmark * 0.25:
        signals.append({
            "signal": "critical_login_decline",
            "severity": "high",
            "detail": f"{logins_30d} logins vs {login_benchmark} healthy benchmark"
        })
        risk_contribution += 30
    elif logins_30d < login_benchmark * 0.5:
        signals.append({
            "signal": "moderate_login_decline",
            "severity": "medium",
            "detail": f"{logins_30d} logins showing reduced engagement"
        })
        risk_contribution += 15

    # Feature adoption
    if features_used < feature_benchmark * 0.3:
        signals.append({
            "signal": "low_feature_adoption",
            "severity": "medium",
            "detail": f"Only {features_used} features used"
        })
        risk_contribution += 10

    return {
        "signals": signals,
        "risk_contribution": risk_contribution,
        "metrics_analyzed": {
            "logins_30d": logins_30d,
            "features_used": features_used,
            "api_calls": api_calls
        }
    }


def analyze_engagement_trend(
    engagement_history: List[Dict],
    windows: Dict
) -> Dict[str, Any]:
    """Analyze engagement trend over time."""
    if not engagement_history:
        return {
            "trend": "unknown",
            "risk_contribution": 20,
            "signals": [{"signal": "no_engagement_data", "severity": "medium"}]
        }

    # Sort by date
    sorted_history = sorted(engagement_history, key=lambda x: x.get("date", ""))

    # Calculate recent vs historical engagement
    recent_count = len([e for e in sorted_history[-10:] if e.get("type") == "login"])
    historical_avg = len(sorted_history) / max(1, len(sorted_history) // 10)

    if recent_count < historical_avg * 0.5:
        trend = "declining"
        risk_contribution = 25
    elif recent_count > historical_avg * 1.2:
        trend = "improving"
        risk_contribution = -10
    else:
        trend = "stable"
        risk_contribution = 0

    return {
        "trend": trend,
        "risk_contribution": max(0, risk_contribution),
        "recent_engagement": recent_count,
        "historical_average": round(historical_avg, 1)
    }


def analyze_support_sentiment(
    support_tickets: List[Dict],
    sentiment_weights: Dict
) -> Dict[str, Any]:
    """Analyze support ticket patterns and sentiment."""
    signals = []
    risk_contribution = 0

    if not support_tickets:
        return {
            "signals": [],
            "risk_contribution": 0,
            "ticket_count": 0
        }

    negative_count = sum(1 for t in support_tickets if t.get("sentiment") == "negative")
    bug_count = sum(1 for t in support_tickets if t.get("category") == "bug")
    total_tickets = len(support_tickets)

    # High negative sentiment
    negative_ratio = negative_count / total_tickets if total_tickets > 0 else 0
    if negative_ratio > 0.5:
        signals.append({
            "signal": "high_negative_sentiment",
            "severity": "high",
            "detail": f"{negative_ratio:.0%} of tickets have negative sentiment"
        })
        risk_contribution += 20

    # Many bug reports
    if bug_count >= 3:
        signals.append({
            "signal": "multiple_bug_reports",
            "severity": "medium",
            "detail": f"{bug_count} bug reports filed"
        })
        risk_contribution += 15

    # Recent escalation
    escalated = any(t.get("escalated") for t in support_tickets[-5:])
    if escalated:
        signals.append({
            "signal": "recent_escalation",
            "severity": "high",
            "detail": "Recent ticket escalation"
        })
        risk_contribution += 25

    return {
        "signals": signals,
        "risk_contribution": risk_contribution,
        "ticket_count": total_tickets,
        "negative_count": negative_count
    }


def analyze_billing_patterns(
    billing_history: List[Dict],
    thresholds: Dict
) -> Dict[str, Any]:
    """Analyze billing and payment patterns."""
    signals = []
    risk_contribution = 0

    if not billing_history:
        return {"signals": [], "risk_contribution": 0}

    late_payments = sum(1 for b in billing_history if b.get("days_late", 0) > 0)
    failed_payments = sum(1 for b in billing_history if b.get("status") == "failed")

    if failed_payments >= 2:
        signals.append({
            "signal": "payment_failures",
            "severity": "high",
            "detail": f"{failed_payments} failed payment attempts"
        })
        risk_contribution += 20

    if late_payments >= 3:
        signals.append({
            "signal": "chronic_late_payments",
            "severity": "medium",
            "detail": f"{late_payments} late payments"
        })
        risk_contribution += 10

    return {
        "signals": signals,
        "risk_contribution": risk_contribution,
        "late_payments": late_payments,
        "failed_payments": failed_payments
    }


def calculate_savability(
    account_info: Dict,
    risk_score: float,
    factors: Dict
) -> Dict[str, Any]:
    """Calculate customer savability score."""
    mrr = account_info.get("mrr", 0)
    tenure_months = account_info.get("tenure_months", 0)

    # Higher value customers are worth more effort
    value_factor = min(1.0, mrr / factors.get("high_value_threshold", 5000))

    # Longer tenure suggests stronger relationship
    tenure_factor = min(1.0, tenure_months / factors.get("mature_tenure_months", 24))

    # Lower risk scores are more savable
    risk_factor = 1 - (risk_score / 100)

    savability = (value_factor * 0.4 + tenure_factor * 0.3 + risk_factor * 0.3) * 100

    return {
        "savability_score": round(savability, 1),
        "value_factor": round(value_factor, 2),
        "tenure_factor": round(tenure_factor, 2),
        "intervention_priority": "high" if savability > 60 and mrr > 1000 else "medium" if savability > 40 else "low"
    }


def generate_recommendations(
    risk_factors: List[Dict],
    account_info: Dict,
    intervention_playbook: Dict
) -> List[Dict]:
    """Generate retention recommendations."""
    recommendations = []

    factor_types = [f.get("signal", "") for f in risk_factors]

    if any("login" in f for f in factor_types):
        recommendations.append({
            "action": "Schedule customer success call",
            "priority": "high",
            "rationale": "Low engagement detected"
        })

    if any("negative" in f or "escalation" in f for f in factor_types):
        recommendations.append({
            "action": "Executive sponsor outreach",
            "priority": "high",
            "rationale": "Negative sentiment or escalation"
        })

    if any("payment" in f for f in factor_types):
        recommendations.append({
            "action": "Review billing and offer payment plan",
            "priority": "medium",
            "rationale": "Payment issues detected"
        })

    # Default recommendation if none triggered
    if not recommendations:
        recommendations.append({
            "action": "Proactive check-in",
            "priority": "low",
            "rationale": "Regular engagement maintenance"
        })

    return recommendations


def analyze_churn(
    customer_id: str,
    usage_metrics: Dict,
    engagement_history: List[Dict],
    account_info: Dict,
    support_tickets: List[Dict],
    billing_history: List[Dict]
) -> Dict[str, Any]:
    """
    Analyze customer churn risk.

    Business Rules:
    1. Engagement decay detection
    2. Risk signal weighting
    3. Cohort comparison
    4. Intervention prioritization

    Args:
        customer_id: Customer identifier
        usage_metrics: Product usage data
        engagement_history: Interaction timeline
        account_info: Customer profile
        support_tickets: Support history
        billing_history: Payment patterns

    Returns:
        Churn risk analysis results
    """
    signals = load_churn_signals()

    all_risk_factors = []
    total_risk = 0

    # Usage analysis
    usage_result = analyze_usage_decline(usage_metrics, signals.get("usage_benchmarks", {}))
    total_risk += usage_result["risk_contribution"]
    all_risk_factors.extend(usage_result["signals"])

    # Engagement trend
    engagement_result = analyze_engagement_trend(
        engagement_history,
        signals.get("engagement_windows", {})
    )
    total_risk += engagement_result["risk_contribution"]

    # Support sentiment
    support_result = analyze_support_sentiment(
        support_tickets,
        signals.get("sentiment_weights", {})
    )
    total_risk += support_result["risk_contribution"]
    all_risk_factors.extend(support_result["signals"])

    # Billing patterns
    billing_result = analyze_billing_patterns(
        billing_history,
        signals.get("billing_thresholds", {})
    )
    total_risk += billing_result["risk_contribution"]
    all_risk_factors.extend(billing_result["signals"])

    # Cap risk score at 100
    churn_risk_score = min(100, total_risk)

    # Calculate savability
    savability = calculate_savability(
        account_info,
        churn_risk_score,
        signals.get("savability_factors", {})
    )

    # Generate recommendations
    recommendations = generate_recommendations(
        all_risk_factors,
        account_info,
        signals.get("intervention_playbook", {})
    )

    # Determine trend
    risk_trend = engagement_result.get("trend", "stable")

    # Estimate churn timing
    if churn_risk_score > 80:
        predicted_churn = "Within 30 days"
    elif churn_risk_score > 60:
        predicted_churn = "Within 60 days"
    elif churn_risk_score > 40:
        predicted_churn = "Within 90 days"
    else:
        predicted_churn = "Low risk - no imminent churn expected"

    return {
        "customer_id": customer_id,
        "churn_risk_score": churn_risk_score,
        "risk_factors": all_risk_factors,
        "risk_trend": risk_trend,
        "recommended_actions": recommendations,
        "predicted_churn_date": predicted_churn,
        "savability": savability,
        "analysis_details": {
            "usage": usage_result,
            "engagement": engagement_result,
            "support": support_result,
            "billing": billing_result
        }
    }


if __name__ == "__main__":
    import json
    result = analyze_churn(
        customer_id="CUST-001",
        usage_metrics={"logins_30d": 5, "features_used": 3, "api_calls": 100},
        engagement_history=[
            {"date": "2025-12-01", "type": "login"},
            {"date": "2025-12-15", "type": "login"}
        ],
        account_info={"mrr": 5000, "tenure_months": 18, "plan": "enterprise"},
        support_tickets=[
            {"date": "2025-12-15", "category": "bug", "sentiment": "negative", "escalated": False}
        ],
        billing_history=[
            {"date": "2025-12-01", "status": "paid", "days_late": 0}
        ]
    )
    print(json.dumps(result, indent=2))
