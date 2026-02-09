"""
Spend Category Analysis Module

Implements procurement spend analysis including
category breakdown, supplier concentration, and savings identification.
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


def load_spend_categories() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    category_taxonomy_data = load_csv_as_dict("category_taxonomy.csv")
    analysis_dimensions_data = load_csv_as_dict("analysis_dimensions.csv")
    opportunity_levers_data = load_csv_as_dict("opportunity_levers.csv")
    compliance_requirements_data = load_csv_as_dict("compliance_requirements.csv")
    risk_indicators_data = load_csv_as_dict("risk_indicators.csv")
    params = load_parameters()
    return {
        "category_taxonomy": category_taxonomy_data,
        "analysis_dimensions": analysis_dimensions_data,
        "opportunity_levers": opportunity_levers_data,
        "compliance_requirements": compliance_requirements_data,
        "risk_indicators": risk_indicators_data,
        **params
    }


def analyze_category_spend(
    category_name: str,
    category_config: Dict,
    spend_data: Dict
) -> Dict[str, Any]:
    """Analyze spend for a single category."""
    typical_share = category_config.get("typical_spend_share", 0)
    savings_potential = category_config.get("savings_potential", {})

    actual_spend = spend_data.get("total_spend", 0)
    total_org_spend = spend_data.get("total_org_spend", 1)
    actual_share = actual_spend / total_org_spend if total_org_spend > 0 else 0

    vs_typical = actual_share - typical_share

    # Calculate potential savings
    min_savings = actual_spend * savings_potential.get("min", 0)
    max_savings = actual_spend * savings_potential.get("max", 0)

    return {
        "category": category_name,
        "actual_spend": actual_spend,
        "actual_share_pct": round(actual_share * 100, 1),
        "typical_share_pct": round(typical_share * 100, 1),
        "vs_typical_pct": round(vs_typical * 100, 1),
        "savings_potential": {
            "min": round(min_savings, 2),
            "max": round(max_savings, 2),
            "midpoint": round((min_savings + max_savings) / 2, 2)
        },
        "subcategories": category_config.get("subcategories", [])
    }


def analyze_supplier_concentration(
    suppliers: List[Dict],
    thresholds: Dict
) -> Dict[str, Any]:
    """Analyze supplier concentration."""
    total_spend = sum(s.get("spend", 0) for s in suppliers)

    # Sort suppliers by spend
    sorted_suppliers = sorted(suppliers, key=lambda x: x.get("spend", 0), reverse=True)

    # Calculate top 20% supplier spend
    top_count = max(1, int(len(sorted_suppliers) * 0.2))
    top_suppliers = sorted_suppliers[:top_count]
    top_spend = sum(s.get("spend", 0) for s in top_suppliers)
    top_spend_pct = top_spend / total_spend if total_spend > 0 else 0

    # Determine concentration level
    if top_spend_pct >= thresholds.get("high", {}).get("threshold", 0.80):
        concentration = "HIGH"
        description = thresholds.get("high", {}).get("description", "")
    elif top_spend_pct >= thresholds.get("moderate", {}).get("threshold", 0.60):
        concentration = "MODERATE"
        description = thresholds.get("moderate", {}).get("description", "")
    else:
        concentration = "FRAGMENTED"
        description = thresholds.get("fragmented", {}).get("description", "")

    return {
        "total_suppliers": len(suppliers),
        "total_spend": total_spend,
        "top_20pct_supplier_count": top_count,
        "top_20pct_spend": round(top_spend, 2),
        "top_20pct_spend_pct": round(top_spend_pct * 100, 1),
        "concentration_level": concentration,
        "description": description,
        "top_suppliers": [
            {
                "supplier_id": s.get("supplier_id", ""),
                "supplier_name": s.get("supplier_name", ""),
                "spend": s.get("spend", 0),
                "spend_pct": round(s.get("spend", 0) / total_spend * 100, 1) if total_spend > 0 else 0
            }
            for s in top_suppliers[:5]
        ]
    }


def assess_supplier_diversity(
    supplier_count: int,
    diversity_thresholds: Dict
) -> Dict[str, Any]:
    """Assess supplier diversity risk."""
    if supplier_count == 1:
        diversity = "single_source"
    elif supplier_count == 2:
        diversity = "dual_source"
    else:
        diversity = "multi_source"

    config = diversity_thresholds.get(diversity, {})

    return {
        "supplier_count": supplier_count,
        "diversity_status": diversity.upper().replace("_", " "),
        "risk_level": config.get("risk", "unknown")
    }


def analyze_contract_coverage(
    contracted_spend: float,
    total_spend: float,
    coverage_thresholds: Dict
) -> Dict[str, Any]:
    """Analyze contract coverage."""
    coverage_pct = contracted_spend / total_spend if total_spend > 0 else 0

    # Filter out empty/non-dict values
    valid_thresholds = {k: v for k, v in coverage_thresholds.items() if v and isinstance(v, dict)}

    # Determine coverage rating
    coverage_rating = "critical"
    for rating, config in sorted(
        valid_thresholds.items(),
        key=lambda x: x[1].get("min_pct", 0),
        reverse=True
    ):
        if coverage_pct >= config.get("min_pct", 0):
            coverage_rating = config.get("rating", "unknown")
            break

    return {
        "contracted_spend": contracted_spend,
        "total_spend": total_spend,
        "maverick_spend": round(total_spend - contracted_spend, 2),
        "coverage_pct": round(coverage_pct * 100, 1),
        "coverage_rating": coverage_rating.upper()
    }


def identify_savings_opportunities(
    category_spend: float,
    current_practices: Dict,
    opportunity_levers: Dict
) -> List[Dict]:
    """Identify savings opportunities by lever."""
    opportunities = []

    for lever, config in opportunity_levers.items():
        potential_savings_pct = config.get("potential_savings", 0)
        implementation_effort = config.get("implementation_effort", "medium")
        time_to_value = config.get("time_to_value", "6_months")

        # Adjust potential based on current practices
        current_maturity = current_practices.get(lever, 0.5)
        adjusted_potential = potential_savings_pct * (1 - current_maturity)

        potential_savings = category_spend * adjusted_potential

        opportunities.append({
            "lever": lever.replace("_", " ").title(),
            "potential_savings": round(potential_savings, 2),
            "potential_savings_pct": round(adjusted_potential * 100, 1),
            "implementation_effort": implementation_effort,
            "time_to_value": time_to_value,
            "current_maturity": current_maturity,
            "priority_score": round(potential_savings / (1 if implementation_effort == "low" else 2 if implementation_effort == "medium" else 3), 2)
        })

    # Sort by priority score
    opportunities.sort(key=lambda x: x["priority_score"], reverse=True)

    return opportunities


def assess_compliance(
    actual_metrics: Dict,
    requirements: Dict
) -> Dict[str, Any]:
    """Assess compliance with procurement policies."""
    compliance_results = []
    total_score = 0
    total_weight = 0

    for metric, config in requirements.items():
        target = config.get("target", 0)
        weight = config.get("weight", 0)
        actual = actual_metrics.get(metric, 0)

        achievement = min(actual / target, 1.0) if target > 0 else 0
        weighted_score = achievement * weight

        compliance_results.append({
            "metric": metric.replace("_", " ").title(),
            "target": round(target * 100, 1),
            "actual": round(actual * 100, 1),
            "achievement_pct": round(achievement * 100, 1),
            "weight": weight,
            "weighted_score": round(weighted_score, 3),
            "status": "COMPLIANT" if actual >= target else "NON_COMPLIANT"
        })

        total_score += weighted_score
        total_weight += weight

    overall_compliance = total_score / total_weight if total_weight > 0 else 0

    return {
        "overall_compliance_score": round(overall_compliance * 100, 1),
        "metrics": compliance_results,
        "compliant_count": sum(1 for r in compliance_results if r["status"] == "COMPLIANT"),
        "non_compliant_count": sum(1 for r in compliance_results if r["status"] == "NON_COMPLIANT")
    }


def analyze_risks(
    category_data: Dict,
    risk_indicators: Dict
) -> List[Dict]:
    """Identify category risks."""
    risks = []

    for indicator, config in risk_indicators.items():
        threshold = config.get("threshold", 0)
        severity = config.get("severity", "medium")
        actual = category_data.get(indicator, 0)

        if actual >= threshold:
            risks.append({
                "risk": indicator.replace("_", " ").title(),
                "severity": severity.upper(),
                "threshold": threshold,
                "actual": actual,
                "exceeds_by": round(actual - threshold, 3)
            })

    # Sort by severity
    severity_order = {"CRITICAL": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3}
    risks.sort(key=lambda x: severity_order.get(x["severity"], 4))

    return risks


def analyze_spend_category(
    analysis_id: str,
    category_name: str,
    spend_data: Dict,
    suppliers: List[Dict],
    contracted_spend: float,
    current_practices: Dict,
    compliance_metrics: Dict,
    risk_data: Dict,
    analysis_period: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Analyze spend category.

    Business Rules:
    1. Category spend analysis
    2. Supplier concentration assessment
    3. Savings opportunity identification
    4. Compliance and risk assessment

    Args:
        analysis_id: Analysis identifier
        category_name: Spend category name
        spend_data: Category spend data
        suppliers: Supplier list with spend
        contracted_spend: Spend under contract
        current_practices: Current procurement practices maturity
        compliance_metrics: Actual compliance metrics
        risk_data: Risk indicator data
        analysis_period: Period analyzed
        analysis_date: Analysis date

    Returns:
        Spend category analysis results
    """
    config = load_spend_categories()
    category_taxonomy = config.get("category_taxonomy", {})
    analysis_dimensions = config.get("analysis_dimensions", {})
    opportunity_levers = config.get("opportunity_levers", {})
    compliance_requirements = config.get("compliance_requirements", {})
    risk_indicators = config.get("risk_indicators", {})

    # Get category config
    category_config = category_taxonomy.get(category_name, {})
    total_spend = spend_data.get("total_spend", 0)

    # Category spend analysis
    category_analysis = analyze_category_spend(
        category_name,
        category_config,
        spend_data
    )

    # Supplier concentration
    concentration = analyze_supplier_concentration(
        suppliers,
        analysis_dimensions.get("spend_concentration", {})
    )

    # Supplier diversity
    diversity = assess_supplier_diversity(
        len(suppliers),
        analysis_dimensions.get("supplier_diversity", {})
    )

    # Contract coverage
    coverage = analyze_contract_coverage(
        contracted_spend,
        total_spend,
        analysis_dimensions.get("contract_coverage", {})
    )

    # Savings opportunities
    opportunities = identify_savings_opportunities(
        total_spend,
        current_practices,
        opportunity_levers
    )

    total_potential_savings = sum(o["potential_savings"] for o in opportunities)

    # Compliance assessment
    compliance = assess_compliance(compliance_metrics, compliance_requirements)

    # Risk assessment
    risks = analyze_risks(risk_data, risk_indicators)

    return {
        "analysis_id": analysis_id,
        "category_name": category_name,
        "analysis_date": analysis_date,
        "analysis_period": analysis_period,
        "category_spend": category_analysis,
        "supplier_analysis": {
            "concentration": concentration,
            "diversity": diversity
        },
        "contract_coverage": coverage,
        "savings_opportunities": {
            "total_potential_savings": round(total_potential_savings, 2),
            "potential_savings_pct": round(total_potential_savings / total_spend * 100, 1) if total_spend > 0 else 0,
            "opportunities": opportunities
        },
        "compliance_assessment": compliance,
        "risk_assessment": {
            "risk_count": len(risks),
            "risks": risks
        },
        "analysis_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = analyze_spend_category(
        analysis_id="SPEND-001",
        category_name="technology",
        spend_data={
            "total_spend": 5000000,
            "total_org_spend": 50000000
        },
        suppliers=[
            {"supplier_id": "S001", "supplier_name": "Tech Provider A", "spend": 2000000},
            {"supplier_id": "S002", "supplier_name": "Tech Provider B", "spend": 1500000},
            {"supplier_id": "S003", "supplier_name": "Software Vendor C", "spend": 800000},
            {"supplier_id": "S004", "supplier_name": "Cloud Services D", "spend": 500000},
            {"supplier_id": "S005", "supplier_name": "Hardware Vendor E", "spend": 200000}
        ],
        contracted_spend=4000000,
        current_practices={
            "demand_management": 0.3,
            "specification_optimization": 0.4,
            "supplier_consolidation": 0.6,
            "competitive_bidding": 0.7,
            "contract_renegotiation": 0.5,
            "process_efficiency": 0.4
        },
        compliance_metrics={
            "preferred_supplier_usage": 0.75,
            "contract_compliance": 0.85,
            "po_compliance": 0.92,
            "invoice_accuracy": 0.96,
            "on_time_payment": 0.88
        },
        risk_data={
            "price_volatility": 0.12,
            "supply_disruption": 0.05,
            "quality_issues": 0.03,
            "delivery_delays": 0.08
        },
        analysis_period="2025",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
