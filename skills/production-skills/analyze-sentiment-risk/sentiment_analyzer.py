"""
Sentiment Risk Analysis Module

Implements sentiment-based risk analysis including
source aggregation, trend detection, and alert generation.
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


def load_sentiment_config() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    sentiment_categories_data = load_csv_as_dict("sentiment_categories.csv")
    source_weights_data = load_csv_as_dict("source_weights.csv")
    risk_thresholds_data = load_csv_as_dict("risk_thresholds.csv")
    velocity_alerts_data = load_csv_as_dict("velocity_alerts.csv")
    topic_categories_data = load_csv_as_dict("topic_categories.csv")
    industry_adjustments_data = load_csv_as_dict("industry_adjustments.csv")
    params = load_parameters()
    return {
        "sentiment_categories": sentiment_categories_data,
        "source_weights": source_weights_data,
        "risk_thresholds": risk_thresholds_data,
        "velocity_alerts": velocity_alerts_data,
        "topic_categories": topic_categories_data,
        "industry_adjustments": industry_adjustments_data,
        **params
    }


def classify_sentiment(
    score: float,
    categories: Dict
) -> str:
    """Classify sentiment score into category."""
    for category, config in categories.items():
        score_range = config.get("score_range", {})
        if score_range.get("min", 0) <= score <= score_range.get("max", 1):
            return category
    return "neutral"


def calculate_source_sentiment(
    text_items: List[Dict],
    source_type: str,
    source_config: Dict
) -> Dict[str, Any]:
    """Calculate aggregated sentiment for a source."""
    if not text_items:
        return {"source": source_type, "count": 0, "avg_sentiment": 0.5}

    total_sentiment = sum(item.get("sentiment_score", 0.5) for item in text_items)
    avg_sentiment = total_sentiment / len(text_items)

    weight = source_config.get("weight", 0.10)
    weighted_sentiment = avg_sentiment * weight

    return {
        "source": source_type,
        "count": len(text_items),
        "avg_sentiment": round(avg_sentiment, 3),
        "weight": weight,
        "weighted_sentiment": round(weighted_sentiment, 4)
    }


def aggregate_sentiments(
    source_sentiments: List[Dict],
    source_weights: Dict
) -> Dict[str, Any]:
    """Aggregate sentiments across all sources."""
    total_weighted = sum(s.get("weighted_sentiment", 0) for s in source_sentiments)
    total_weight = sum(s.get("weight", 0) for s in source_sentiments)

    if total_weight > 0:
        normalized_sentiment = total_weighted / total_weight
    else:
        normalized_sentiment = 0.5

    total_volume = sum(s.get("count", 0) for s in source_sentiments)

    return {
        "aggregate_sentiment": round(normalized_sentiment, 3),
        "total_volume": total_volume,
        "source_count": len(source_sentiments),
        "total_weight_applied": round(total_weight, 3)
    }


def determine_risk_level(
    sentiment_score: float,
    risk_thresholds: Dict
) -> Dict[str, Any]:
    """Determine risk level based on sentiment score."""
    for level, config in sorted(
        risk_thresholds.items(),
        key=lambda x: x[1].get("sentiment_score_max", 1)
    ):
        if sentiment_score <= config.get("sentiment_score_max", 1):
            return {
                "risk_level": level.upper(),
                "risk_score": config.get("risk_level", 1),
                "sentiment_score": sentiment_score
            }

    return {
        "risk_level": "LOW",
        "risk_score": 1,
        "sentiment_score": sentiment_score
    }


def detect_velocity_alerts(
    current_volume: int,
    baseline_volume: int,
    current_sentiment: float,
    baseline_sentiment: float,
    velocity_config: Dict
) -> List[Dict]:
    """Detect sentiment velocity alerts."""
    alerts = []

    # Volume change
    if baseline_volume > 0:
        volume_change = (current_volume - baseline_volume) / baseline_volume
    else:
        volume_change = 0

    # Sentiment change
    sentiment_change = current_sentiment - baseline_sentiment

    for alert_type, config in velocity_config.items():
        threshold = config.get("threshold_pct", 0.25)

        # Check for negative sentiment surge with volume increase
        if sentiment_change < -threshold and volume_change > threshold:
            alerts.append({
                "alert_type": alert_type.upper(),
                "severity": config.get("severity", "medium"),
                "description": f"Negative sentiment {alert_type} detected",
                "sentiment_change": round(sentiment_change, 3),
                "volume_change_pct": round(volume_change * 100, 1),
                "window_hours": config.get("window_hours", 24)
            })
            break

    return alerts


def analyze_topics(
    text_items: List[Dict],
    topic_categories: Dict
) -> Dict[str, Any]:
    """Analyze sentiment by topic."""
    topic_results = []

    for topic, config in topic_categories.items():
        keywords = config.get("keywords", [])
        risk_weight = config.get("risk_weight", 1.0)

        # Find items mentioning this topic
        topic_items = [
            item for item in text_items
            if any(kw.lower() in item.get("text", "").lower() for kw in keywords)
        ]

        if topic_items:
            avg_sentiment = sum(item.get("sentiment_score", 0.5) for item in topic_items) / len(topic_items)
            weighted_risk = (1 - avg_sentiment) * risk_weight

            topic_results.append({
                "topic": topic,
                "mention_count": len(topic_items),
                "avg_sentiment": round(avg_sentiment, 3),
                "risk_weight": risk_weight,
                "weighted_risk": round(weighted_risk, 3)
            })

    # Sort by weighted risk
    topic_results.sort(key=lambda x: x["weighted_risk"], reverse=True)

    return {
        "topics_analyzed": len(topic_results),
        "high_risk_topics": [t for t in topic_results if t["weighted_risk"] > 0.5],
        "topic_breakdown": topic_results
    }


def apply_industry_adjustment(
    base_risk: float,
    industry: str,
    industry_adjustments: Dict
) -> Dict[str, Any]:
    """Apply industry-specific risk adjustments."""
    adjustment = industry_adjustments.get(industry, {
        "baseline_volatility": 1.0,
        "negative_sensitivity": 1.0
    })

    volatility = adjustment.get("baseline_volatility", 1.0)
    sensitivity = adjustment.get("negative_sensitivity", 1.0)

    adjusted_risk = base_risk * volatility * sensitivity

    return {
        "industry": industry,
        "base_risk": base_risk,
        "volatility_factor": volatility,
        "sensitivity_factor": sensitivity,
        "adjusted_risk": round(min(adjusted_risk, 5), 2)
    }


def generate_recommendations(
    risk_level: str,
    alerts: List[Dict],
    topic_analysis: Dict,
    alert_actions: Dict
) -> List[Dict]:
    """Generate recommended actions based on risk assessment."""
    recommendations = []

    # Get actions for current risk level
    level_actions = alert_actions.get(risk_level.lower(), ["standard_monitoring"])

    for action in level_actions:
        recommendations.append({
            "action": action.replace("_", " ").title(),
            "priority": "HIGH" if risk_level in ["CRITICAL", "HIGH"] else "MEDIUM",
            "trigger": f"Risk level: {risk_level}"
        })

    # Add topic-specific recommendations
    high_risk_topics = topic_analysis.get("high_risk_topics", [])
    for topic in high_risk_topics[:2]:  # Top 2 risky topics
        recommendations.append({
            "action": f"Monitor {topic['topic'].replace('_', ' ')} mentions",
            "priority": "MEDIUM",
            "trigger": f"High risk topic: {topic['topic']}"
        })

    return recommendations


def analyze_sentiment_risk(
    analysis_id: str,
    entity_name: str,
    text_sources: List[Dict],
    baseline_sentiment: float,
    baseline_volume: int,
    industry: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Analyze sentiment risk.

    Business Rules:
    1. Multi-source sentiment aggregation
    2. Risk level determination
    3. Velocity alert detection
    4. Topic-based risk analysis

    Args:
        analysis_id: Analysis identifier
        entity_name: Entity being analyzed
        text_sources: Text items with sentiment scores
        baseline_sentiment: Historical baseline sentiment
        baseline_volume: Historical baseline volume
        industry: Industry for adjustment
        analysis_date: Analysis date

    Returns:
        Sentiment risk analysis results
    """
    config = load_sentiment_config()
    sentiment_categories = config.get("sentiment_categories", {})
    source_weights = config.get("source_weights", {})
    risk_thresholds = config.get("risk_thresholds", {})
    velocity_config = config.get("velocity_alerts", {})
    topic_categories = config.get("topic_categories", {})
    industry_adjustments = config.get("industry_adjustments", {})
    alert_actions = config.get("alert_actions", {})

    # Group items by source
    source_sentiments = []
    all_items = []

    for source_category, sources in source_weights.items():
        for source_type, source_config in sources.items():
            # Skip empty or non-dict source configs
            if not source_config or not isinstance(source_config, dict):
                continue
            source_items = [
                item for item in text_sources
                if item.get("source_type", "").lower() == source_type.lower()
            ]
            if source_items:
                sentiment = calculate_source_sentiment(source_items, source_type, source_config)
                source_sentiments.append(sentiment)
                all_items.extend(source_items)

    # Aggregate sentiments
    aggregated = aggregate_sentiments(source_sentiments, source_weights)

    # Classify sentiment
    sentiment_class = classify_sentiment(
        aggregated["aggregate_sentiment"],
        sentiment_categories
    )

    # Determine risk level
    risk = determine_risk_level(aggregated["aggregate_sentiment"], risk_thresholds)

    # Detect velocity alerts
    alerts = detect_velocity_alerts(
        aggregated["total_volume"],
        baseline_volume,
        aggregated["aggregate_sentiment"],
        baseline_sentiment,
        velocity_config
    )

    # Topic analysis
    topics = analyze_topics(all_items, topic_categories)

    # Industry adjustment
    industry_risk = apply_industry_adjustment(
        risk["risk_score"],
        industry,
        industry_adjustments
    )

    # Generate recommendations
    recommendations = generate_recommendations(
        risk["risk_level"],
        alerts,
        topics,
        alert_actions
    )

    # Trend vs baseline
    sentiment_trend = aggregated["aggregate_sentiment"] - baseline_sentiment
    trend_direction = "IMPROVING" if sentiment_trend > 0.05 else "DECLINING" if sentiment_trend < -0.05 else "STABLE"

    return {
        "analysis_id": analysis_id,
        "entity_name": entity_name,
        "analysis_date": analysis_date,
        "industry": industry,
        "sentiment_summary": {
            "aggregate_score": aggregated["aggregate_sentiment"],
            "classification": sentiment_class.upper(),
            "total_volume": aggregated["total_volume"],
            "vs_baseline": round(sentiment_trend, 3),
            "trend_direction": trend_direction
        },
        "risk_assessment": {
            "risk_level": risk["risk_level"],
            "base_risk_score": risk["risk_score"],
            "industry_adjusted": industry_risk
        },
        "source_breakdown": source_sentiments,
        "velocity_alerts": {
            "alert_count": len(alerts),
            "alerts": alerts
        },
        "topic_analysis": topics,
        "recommendations": recommendations,
        "analysis_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = analyze_sentiment_risk(
        analysis_id="SENT-2026-001",
        entity_name="TechCorp Inc",
        text_sources=[
            {"source_type": "twitter", "text": "TechCorp product quality is declining", "sentiment_score": 0.25},
            {"source_type": "twitter", "text": "Love the new TechCorp features!", "sentiment_score": 0.85},
            {"source_type": "twitter", "text": "TechCorp support was helpful", "sentiment_score": 0.72},
            {"source_type": "major_outlets", "text": "TechCorp earnings beat expectations", "sentiment_score": 0.78},
            {"source_type": "major_outlets", "text": "TechCorp faces supply chain issues", "sentiment_score": 0.35},
            {"source_type": "reviews", "text": "Product broke after 2 weeks, defect issue", "sentiment_score": 0.15},
            {"source_type": "reviews", "text": "Best purchase I made this year", "sentiment_score": 0.92}
        ],
        baseline_sentiment=0.62,
        baseline_volume=50,
        industry="technology",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
