"""
ESG Score Analysis Module

Implements ESG factor analysis and scoring using
environmental, social, and governance metrics.
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


def load_esg_frameworks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    pillar_weights_data = load_csv_as_dict("pillar_weights.csv")
    environmental_benchmarks_data = load_csv_as_dict("environmental_benchmarks.csv")
    social_benchmarks_data = load_key_value_csv("social_benchmarks.csv")
    governance_requirements_data = load_key_value_csv("governance_requirements.csv")
    scoring_thresholds_data = load_key_value_csv("scoring_thresholds.csv")
    params = load_parameters()
    return {
        "pillar_weights": pillar_weights_data,
        "environmental_benchmarks": environmental_benchmarks_data,
        "social_benchmarks": social_benchmarks_data,
        "governance_requirements": governance_requirements_data,
        "scoring_thresholds": scoring_thresholds_data,
        **params
    }


def score_environmental(
    environmental_data: Dict,
    industry: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Score environmental factors."""
    scores = {}
    issues = []

    industry_benchmarks = benchmarks.get(industry, benchmarks.get("default", {}))

    # Carbon intensity
    carbon_intensity = environmental_data.get("carbon_intensity", 0)
    benchmark_carbon = industry_benchmarks.get("carbon_intensity", 200)

    if carbon_intensity <= benchmark_carbon * 0.5:
        scores["carbon"] = 100
    elif carbon_intensity <= benchmark_carbon:
        scores["carbon"] = 75
    elif carbon_intensity <= benchmark_carbon * 1.5:
        scores["carbon"] = 50
    else:
        scores["carbon"] = 25
        issues.append("Carbon intensity significantly above benchmark")

    # Renewable energy
    renewable_pct = environmental_data.get("renewable_pct", 0)
    if renewable_pct >= 0.75:
        scores["energy"] = 100
    elif renewable_pct >= 0.50:
        scores["energy"] = 75
    elif renewable_pct >= 0.25:
        scores["energy"] = 50
    else:
        scores["energy"] = 25

    # Waste recycled
    waste_recycled = environmental_data.get("waste_recycled", 0)
    if waste_recycled >= 0.80:
        scores["waste"] = 100
    elif waste_recycled >= 0.60:
        scores["waste"] = 75
    elif waste_recycled >= 0.40:
        scores["waste"] = 50
    else:
        scores["waste"] = 25

    weights = {"carbon": 0.5, "energy": 0.3, "waste": 0.2}
    total_score = sum(scores[k] * weights[k] for k in scores)

    return {
        "score": round(total_score, 1),
        "component_scores": scores,
        "issues": issues
    }


def score_social(
    social_data: Dict,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Score social factors."""
    scores = {}
    issues = []

    # Workforce diversity
    diversity_pct = social_data.get("diversity_pct", 0)
    if diversity_pct >= 0.45:
        scores["diversity"] = 100
    elif diversity_pct >= 0.35:
        scores["diversity"] = 75
    elif diversity_pct >= 0.25:
        scores["diversity"] = 50
    else:
        scores["diversity"] = 25
        issues.append("Workforce diversity below benchmark")

    # Safety incidents
    safety_incidents = social_data.get("safety_incidents", 0)
    if safety_incidents == 0:
        scores["safety"] = 100
    elif safety_incidents <= 2:
        scores["safety"] = 75
    elif safety_incidents <= 5:
        scores["safety"] = 50
    else:
        scores["safety"] = 25
        issues.append("Safety incident rate above acceptable threshold")

    # Employee turnover
    turnover_rate = social_data.get("turnover_rate", 0)
    if turnover_rate <= 0.10:
        scores["retention"] = 100
    elif turnover_rate <= 0.15:
        scores["retention"] = 75
    elif turnover_rate <= 0.25:
        scores["retention"] = 50
    else:
        scores["retention"] = 25

    weights = {"diversity": 0.35, "safety": 0.40, "retention": 0.25}
    total_score = sum(scores[k] * weights[k] for k in scores)

    return {
        "score": round(total_score, 1),
        "component_scores": scores,
        "issues": issues
    }


def score_governance(
    governance_data: Dict,
    requirements: Dict
) -> Dict[str, Any]:
    """Score governance factors."""
    scores = {}
    issues = []

    # Board independence
    board_independence = governance_data.get("board_independence", 0)
    if board_independence >= 0.75:
        scores["board"] = 100
    elif board_independence >= 0.60:
        scores["board"] = 75
    elif board_independence >= 0.50:
        scores["board"] = 50
    else:
        scores["board"] = 25
        issues.append("Board independence below best practice")

    # Ethics policy
    has_ethics = governance_data.get("ethics_policy", False)
    scores["ethics"] = 100 if has_ethics else 0
    if not has_ethics:
        issues.append("No formal ethics policy documented")

    # Audit committee
    has_audit = governance_data.get("audit_committee", False)
    scores["audit"] = 100 if has_audit else 0

    # Executive compensation transparency
    exec_transparency = governance_data.get("exec_compensation_disclosure", False)
    scores["transparency"] = 100 if exec_transparency else 50

    weights = {"board": 0.35, "ethics": 0.25, "audit": 0.25, "transparency": 0.15}
    total_score = sum(scores[k] * weights[k] for k in scores)

    return {
        "score": round(total_score, 1),
        "component_scores": scores,
        "issues": issues
    }


def compare_to_peers(
    esg_score: float,
    peer_data: List[Dict]
) -> Dict[str, Any]:
    """Compare ESG score to peer group."""
    if not peer_data:
        return {"percentile": None, "peer_count": 0}

    peer_scores = [p.get("esg_score", 0) for p in peer_data]
    peer_scores.append(esg_score)
    peer_scores.sort()

    rank = peer_scores.index(esg_score) + 1
    percentile = (rank / len(peer_scores)) * 100

    return {
        "percentile": round(percentile, 0),
        "rank": rank,
        "peer_count": len(peer_data),
        "peer_avg": round(sum(peer_scores) / len(peer_scores), 1)
    }


def identify_improvement_areas(
    environmental: Dict,
    social: Dict,
    governance: Dict
) -> List[Dict]:
    """Identify areas for ESG improvement."""
    improvements = []

    all_issues = (
        environmental.get("issues", []) +
        social.get("issues", []) +
        governance.get("issues", [])
    )

    for issue in all_issues:
        improvements.append({
            "area": issue,
            "priority": "high",
            "type": "gap"
        })

    # Score-based improvements
    if environmental.get("score", 100) < 50:
        improvements.append({
            "area": "Environmental performance",
            "priority": "high",
            "type": "score_improvement"
        })

    if social.get("score", 100) < 50:
        improvements.append({
            "area": "Social responsibility",
            "priority": "high",
            "type": "score_improvement"
        })

    if governance.get("score", 100) < 50:
        improvements.append({
            "area": "Governance practices",
            "priority": "high",
            "type": "score_improvement"
        })

    return improvements


def analyze_esg(
    entity_id: str,
    environmental_data: Dict,
    social_data: Dict,
    governance_data: Dict,
    industry: str,
    peer_data: List[Dict]
) -> Dict[str, Any]:
    """
    Analyze ESG factors and calculate score.

    Business Rules:
    1. Environmental metrics scoring
    2. Social assessment
    3. Governance evaluation
    4. Industry-specific weighting

    Args:
        entity_id: Entity identifier
        environmental_data: Environmental metrics
        social_data: Social metrics
        governance_data: Governance metrics
        industry: Industry classification
        peer_data: Peer comparison data

    Returns:
        ESG analysis results
    """
    frameworks = load_esg_frameworks()

    # Score each pillar
    e_score = score_environmental(
        environmental_data,
        industry,
        frameworks.get("environmental_benchmarks", {})
    )

    s_score = score_social(
        social_data,
        frameworks.get("social_benchmarks", {})
    )

    g_score = score_governance(
        governance_data,
        frameworks.get("governance_requirements", {})
    )

    # Calculate composite score
    weights = frameworks.get("pillar_weights", {})
    industry_weights = weights.get(industry, weights.get("default", {"E": 0.33, "S": 0.33, "G": 0.34}))

    esg_score = (
        e_score["score"] * industry_weights.get("E", 0.33) +
        s_score["score"] * industry_weights.get("S", 0.33) +
        g_score["score"] * industry_weights.get("G", 0.34)
    )

    # Peer comparison
    peer_comparison = compare_to_peers(esg_score, peer_data)

    # Improvement areas
    improvement_areas = identify_improvement_areas(e_score, s_score, g_score)

    return {
        "entity_id": entity_id,
        "esg_score": round(esg_score, 1),
        "pillar_scores": {
            "environmental": e_score,
            "social": s_score,
            "governance": g_score
        },
        "materiality_assessment": {
            "industry": industry,
            "weights_applied": industry_weights
        },
        "peer_comparison": peer_comparison,
        "improvement_areas": improvement_areas
    }


if __name__ == "__main__":
    import json
    result = analyze_esg(
        entity_id="COMP-001",
        environmental_data={"carbon_intensity": 150, "renewable_pct": 0.35, "waste_recycled": 0.6},
        social_data={"diversity_pct": 0.40, "safety_incidents": 2, "turnover_rate": 0.12},
        governance_data={"board_independence": 0.7, "ethics_policy": True, "audit_committee": True},
        industry="manufacturing",
        peer_data=[{"id": "PEER-001", "esg_score": 65}]
    )
    print(json.dumps(result, indent=2))
