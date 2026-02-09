"""
Data Quality Validation Module

Implements data quality assessment including
completeness, accuracy, consistency, and anomaly detection.
"""

import csv
import re
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


def load_quality_rules() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    quality_dimensions_data = load_csv_as_dict("quality_dimensions.csv")
    validation_rules_data = load_csv_as_dict("validation_rules.csv")
    field_type_rules_data = load_csv_as_dict("field_type_rules.csv")
    scoring_thresholds_data = load_key_value_csv("scoring_thresholds.csv")
    severity_weights_data = load_key_value_csv("severity_weights.csv")
    remediation_priorities_data = load_csv_as_dict("remediation_priorities.csv")
    data_profiling_data = load_key_value_csv("data_profiling.csv")
    anomaly_detection_data = load_key_value_csv("anomaly_detection.csv")
    params = load_parameters()
    return {
        "quality_dimensions": quality_dimensions_data,
        "validation_rules": validation_rules_data,
        "field_type_rules": field_type_rules_data,
        "scoring_thresholds": scoring_thresholds_data,
        "severity_weights": severity_weights_data,
        "remediation_priorities": remediation_priorities_data,
        "data_profiling": data_profiling_data,
        "anomaly_detection": anomaly_detection_data,
        **params
    }


def check_completeness(
    records: List[Dict],
    required_fields: List[str]
) -> Dict[str, Any]:
    """Check data completeness."""
    total_records = len(records)
    field_completeness = {}
    missing_counts = {}

    for field in required_fields:
        missing = sum(1 for r in records if r.get(field) is None or r.get(field) == "")
        completeness = ((total_records - missing) / total_records * 100) if total_records > 0 else 0
        field_completeness[field] = round(completeness, 2)
        missing_counts[field] = missing

    overall_completeness = sum(field_completeness.values()) / len(field_completeness) if field_completeness else 0

    return {
        "dimension": "completeness",
        "overall_score": round(overall_completeness, 2),
        "field_completeness": field_completeness,
        "missing_counts": missing_counts,
        "total_records": total_records,
        "required_fields": required_fields
    }


def check_accuracy(
    records: List[Dict],
    field_rules: Dict
) -> Dict[str, Any]:
    """Check data accuracy against rules."""
    total_records = len(records)
    field_accuracy = {}
    invalid_samples = {}

    for field, rules in field_rules.items():
        valid_count = 0
        invalid_examples = []

        for record in records:
            value = record.get(field)
            if value is None:
                continue

            is_valid = True

            # Pattern check
            if "pattern" in rules:
                if not re.match(rules["pattern"], str(value)):
                    is_valid = False

            # Range check
            if "min" in rules:
                try:
                    if float(value) < rules["min"]:
                        is_valid = False
                except (ValueError, TypeError):
                    is_valid = False

            if "max" in rules:
                try:
                    if float(value) > rules["max"]:
                        is_valid = False
                except (ValueError, TypeError):
                    is_valid = False

            if is_valid:
                valid_count += 1
            elif len(invalid_examples) < 5:
                invalid_examples.append(str(value)[:50])

        non_null_count = sum(1 for r in records if r.get(field) is not None)
        accuracy = (valid_count / non_null_count * 100) if non_null_count > 0 else 100
        field_accuracy[field] = round(accuracy, 2)

        if invalid_examples:
            invalid_samples[field] = invalid_examples

    overall_accuracy = sum(field_accuracy.values()) / len(field_accuracy) if field_accuracy else 100

    return {
        "dimension": "accuracy",
        "overall_score": round(overall_accuracy, 2),
        "field_accuracy": field_accuracy,
        "invalid_samples": invalid_samples
    }


def check_consistency(
    records: List[Dict],
    consistency_rules: List[Dict]
) -> Dict[str, Any]:
    """Check cross-field consistency."""
    total_records = len(records)
    rule_results = []

    for rule in consistency_rules:
        rule_name = rule.get("name", "unnamed")
        field1 = rule.get("field1", "")
        field2 = rule.get("field2", "")
        condition = rule.get("condition", "")

        violations = 0

        for record in records:
            val1 = record.get(field1)
            val2 = record.get(field2)

            if val1 is None or val2 is None:
                continue

            if condition == "less_than":
                if val1 >= val2:
                    violations += 1
            elif condition == "equal":
                if val1 != val2:
                    violations += 1
            elif condition == "not_equal":
                if val1 == val2:
                    violations += 1

        consistency_pct = ((total_records - violations) / total_records * 100) if total_records > 0 else 100
        rule_results.append({
            "rule": rule_name,
            "violations": violations,
            "consistency_pct": round(consistency_pct, 2)
        })

    overall_consistency = sum(r["consistency_pct"] for r in rule_results) / len(rule_results) if rule_results else 100

    return {
        "dimension": "consistency",
        "overall_score": round(overall_consistency, 2),
        "rule_results": rule_results
    }


def check_uniqueness(
    records: List[Dict],
    unique_fields: List[str]
) -> Dict[str, Any]:
    """Check for duplicate records."""
    total_records = len(records)
    duplicate_info = {}

    for field in unique_fields:
        values = [r.get(field) for r in records if r.get(field) is not None]
        unique_values = len(set(values))
        duplicates = len(values) - unique_values

        uniqueness = (unique_values / len(values) * 100) if values else 100
        duplicate_info[field] = {
            "total_values": len(values),
            "unique_values": unique_values,
            "duplicate_count": duplicates,
            "uniqueness_pct": round(uniqueness, 2)
        }

    overall_uniqueness = sum(d["uniqueness_pct"] for d in duplicate_info.values()) / len(duplicate_info) if duplicate_info else 100

    return {
        "dimension": "uniqueness",
        "overall_score": round(overall_uniqueness, 2),
        "field_analysis": duplicate_info,
        "total_records": total_records
    }


def check_timeliness(
    records: List[Dict],
    timestamp_field: str,
    freshness_threshold_hours: int
) -> Dict[str, Any]:
    """Check data timeliness."""
    from datetime import datetime, timedelta

    total_records = len(records)
    stale_count = 0
    current_time = datetime.now()
    threshold = current_time - timedelta(hours=freshness_threshold_hours)

    age_distribution = {"fresh": 0, "recent": 0, "stale": 0, "very_stale": 0}

    for record in records:
        timestamp = record.get(timestamp_field)
        if timestamp:
            try:
                if isinstance(timestamp, str):
                    record_time = datetime.fromisoformat(timestamp.replace("Z", "+00:00").replace("+00:00", ""))
                else:
                    record_time = timestamp

                age_hours = (current_time - record_time).total_seconds() / 3600

                if age_hours <= freshness_threshold_hours:
                    age_distribution["fresh"] += 1
                elif age_hours <= freshness_threshold_hours * 2:
                    age_distribution["recent"] += 1
                elif age_hours <= freshness_threshold_hours * 7:
                    age_distribution["stale"] += 1
                    stale_count += 1
                else:
                    age_distribution["very_stale"] += 1
                    stale_count += 1
            except (ValueError, TypeError):
                stale_count += 1
                age_distribution["very_stale"] += 1

    timeliness_score = ((total_records - stale_count) / total_records * 100) if total_records > 0 else 100

    return {
        "dimension": "timeliness",
        "overall_score": round(timeliness_score, 2),
        "freshness_threshold_hours": freshness_threshold_hours,
        "stale_records": stale_count,
        "age_distribution": age_distribution
    }


def detect_anomalies(
    records: List[Dict],
    numeric_fields: List[str],
    std_dev_threshold: float
) -> Dict[str, Any]:
    """Detect statistical anomalies."""
    anomalies = {}

    for field in numeric_fields:
        values = []
        for r in records:
            val = r.get(field)
            if val is not None:
                try:
                    values.append(float(val))
                except (ValueError, TypeError):
                    pass

        if len(values) < 10:
            continue

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std_dev = math.sqrt(variance) if variance > 0 else 0

        outliers = []
        for i, v in enumerate(values):
            if std_dev > 0:
                z_score = abs((v - mean) / std_dev)
                if z_score > std_dev_threshold:
                    outliers.append({"index": i, "value": v, "z_score": round(z_score, 2)})

        anomalies[field] = {
            "mean": round(mean, 2),
            "std_dev": round(std_dev, 2),
            "outlier_count": len(outliers),
            "outliers_sample": outliers[:5]
        }

    return {
        "anomaly_detection": anomalies,
        "fields_analyzed": numeric_fields
    }


def calculate_overall_score(
    dimension_scores: Dict,
    weights: Dict
) -> Dict[str, Any]:
    """Calculate overall data quality score."""
    weighted_score = 0
    score_breakdown = []

    for dimension, config in weights.items():
        weight = config.get("weight", 0)
        score = dimension_scores.get(dimension, 100)
        weighted_contribution = score * weight
        weighted_score += weighted_contribution

        score_breakdown.append({
            "dimension": dimension,
            "score": score,
            "weight": weight,
            "contribution": round(weighted_contribution, 2)
        })

    return {
        "overall_score": round(weighted_score, 2),
        "score_breakdown": score_breakdown
    }


def determine_quality_grade(
    score: float,
    thresholds: Dict
) -> Dict[str, Any]:
    """Determine quality grade from score."""
    if score >= thresholds.get("excellent", 95):
        grade = "EXCELLENT"
    elif score >= thresholds.get("good", 85):
        grade = "GOOD"
    elif score >= thresholds.get("acceptable", 70):
        grade = "ACCEPTABLE"
    elif score >= thresholds.get("poor", 50):
        grade = "POOR"
    else:
        grade = "CRITICAL"

    return {"grade": grade, "score": score}


def validate_data_quality(
    dataset_id: str,
    records: List[Dict],
    required_fields: List[str],
    field_rules: Dict,
    consistency_rules: List[Dict],
    unique_fields: List[str],
    timestamp_field: str,
    freshness_threshold_hours: int,
    numeric_fields: List[str],
    validation_date: str
) -> Dict[str, Any]:
    """
    Validate data quality.

    Business Rules:
    1. Multi-dimensional quality assessment
    2. Field-level validation rules
    3. Anomaly detection
    4. Quality scoring and grading

    Args:
        dataset_id: Dataset identifier
        records: Data records to validate
        required_fields: Fields that must be present
        field_rules: Validation rules by field
        consistency_rules: Cross-field consistency rules
        unique_fields: Fields that should be unique
        timestamp_field: Field for timeliness check
        freshness_threshold_hours: Freshness threshold
        numeric_fields: Fields for anomaly detection
        validation_date: Validation date

    Returns:
        Data quality validation results
    """
    rules = load_quality_rules()
    dimensions = rules.get("quality_dimensions", {})
    thresholds = rules.get("scoring_thresholds", {})
    anomaly_config = rules.get("anomaly_detection", {})

    # Check each dimension
    completeness = check_completeness(records, required_fields)
    accuracy = check_accuracy(records, field_rules)
    consistency = check_consistency(records, consistency_rules)
    uniqueness = check_uniqueness(records, unique_fields)
    timeliness = check_timeliness(records, timestamp_field, freshness_threshold_hours)

    # Detect anomalies
    anomalies = detect_anomalies(
        records,
        numeric_fields,
        anomaly_config.get("outlier_std_dev", 3.0)
    )

    # Aggregate dimension scores
    dimension_scores = {
        "completeness": completeness["overall_score"],
        "accuracy": accuracy["overall_score"],
        "consistency": consistency["overall_score"],
        "uniqueness": uniqueness["overall_score"],
        "timeliness": timeliness["overall_score"]
    }

    # Calculate overall score
    overall = calculate_overall_score(dimension_scores, dimensions)

    # Determine grade
    grade = determine_quality_grade(overall["overall_score"], thresholds)

    # Generate issues summary
    issues = []
    if completeness["overall_score"] < 90:
        issues.append({"dimension": "completeness", "severity": "high", "description": "Missing required data"})
    if accuracy["overall_score"] < 90:
        issues.append({"dimension": "accuracy", "severity": "high", "description": "Data format or range violations"})
    if consistency["overall_score"] < 90:
        issues.append({"dimension": "consistency", "severity": "medium", "description": "Cross-field consistency issues"})
    if uniqueness["overall_score"] < 95:
        issues.append({"dimension": "uniqueness", "severity": "medium", "description": "Duplicate records detected"})
    if timeliness["overall_score"] < 80:
        issues.append({"dimension": "timeliness", "severity": "low", "description": "Stale data detected"})

    return {
        "dataset_id": dataset_id,
        "validation_date": validation_date,
        "records_analyzed": len(records),
        "dimension_results": {
            "completeness": completeness,
            "accuracy": accuracy,
            "consistency": consistency,
            "uniqueness": uniqueness,
            "timeliness": timeliness
        },
        "anomaly_analysis": anomalies,
        "overall_assessment": overall,
        "quality_grade": grade,
        "issues": issues,
        "recommendations": generate_recommendations(issues, dimension_scores)
    }


def generate_recommendations(issues: List, scores: Dict) -> List[str]:
    """Generate improvement recommendations."""
    recommendations = []

    if scores.get("completeness", 100) < 90:
        recommendations.append("Implement data entry validation to enforce required fields")

    if scores.get("accuracy", 100) < 90:
        recommendations.append("Add format validation rules at data capture point")

    if scores.get("consistency", 100) < 90:
        recommendations.append("Review business rules for cross-field relationships")

    if scores.get("uniqueness", 100) < 95:
        recommendations.append("Implement deduplication process")

    if scores.get("timeliness", 100) < 80:
        recommendations.append("Review data refresh schedules")

    return recommendations


if __name__ == "__main__":
    import json
    result = validate_data_quality(
        dataset_id="DS-001",
        records=[
            {"id": "1", "email": "john@example.com", "amount": 100.50, "created_at": "2026-01-20T10:00:00", "status": "active"},
            {"id": "2", "email": "invalid-email", "amount": 200.00, "created_at": "2026-01-19T09:00:00", "status": "active"},
            {"id": "3", "email": "jane@test.com", "amount": -50, "created_at": "2026-01-15T08:00:00", "status": "pending"},
            {"id": "4", "email": None, "amount": 150.00, "created_at": "2026-01-10T07:00:00", "status": "active"},
            {"id": "5", "email": "bob@demo.org", "amount": 500.00, "created_at": "2025-12-01T06:00:00", "status": None}
        ],
        required_fields=["id", "email", "amount", "status"],
        field_rules={
            "email": {"pattern": "^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\\.[a-zA-Z0-9-.]+$"},
            "amount": {"min": 0}
        },
        consistency_rules=[
            {"name": "amount_positive", "field1": "amount", "field2": "amount", "condition": "not_equal"}
        ],
        unique_fields=["id", "email"],
        timestamp_field="created_at",
        freshness_threshold_hours=168,
        numeric_fields=["amount"],
        validation_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
