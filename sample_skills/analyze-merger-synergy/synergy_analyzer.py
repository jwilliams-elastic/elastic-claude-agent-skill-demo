"""
Merger Synergy Analysis Module

Implements M&A synergy identification and quantification
including cost savings, revenue enhancement, and integration costs.
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


def load_synergy_benchmarks() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    industries_data = load_csv_as_dict("industries.csv")
    default_data = load_csv_as_dict("default.csv")
    integration_costs_data = load_csv_as_dict("integration_costs.csv")
    typical_synergy_ranges_data = load_csv_as_dict("typical_synergy_ranges.csv")
    params = load_parameters()
    return {
        "industries": industries_data,
        "default": default_data,
        "integration_costs": integration_costs_data,
        "typical_synergy_ranges": typical_synergy_ranges_data,
        **params
    }


def estimate_cost_synergies(
    acquirer_financials: Dict,
    target_financials: Dict,
    overlap_analysis: Dict,
    cost_benchmarks: Dict
) -> Dict[str, Any]:
    """Estimate cost synergies from merger."""
    synergies = {}

    combined_revenue = acquirer_financials.get("revenue", 0) + target_financials.get("revenue", 0)
    target_employees = target_financials.get("employees", 0)
    acquirer_employees = acquirer_financials.get("employees", 0)

    # SG&A synergies (headcount reduction in overlapping functions)
    geographic_overlap = overlap_analysis.get("geographic", 0)
    employee_reduction_pct = geographic_overlap * cost_benchmarks.get("employee_reduction_factor", 0.15)
    avg_cost_per_employee = cost_benchmarks.get("avg_cost_per_employee", 100000)

    sga_synergy = target_employees * employee_reduction_pct * avg_cost_per_employee

    synergies["sga"] = {
        "amount": round(sga_synergy, 0),
        "basis": "Headcount consolidation",
        "confidence": "high" if geographic_overlap > 0.3 else "medium"
    }

    # Procurement synergies
    vendor_overlap = overlap_analysis.get("vendor", 0)
    target_cogs = target_financials.get("cogs", target_financials.get("revenue", 0) * 0.6)
    procurement_synergy_pct = vendor_overlap * cost_benchmarks.get("procurement_leverage", 0.05)
    procurement_synergy = target_cogs * procurement_synergy_pct

    synergies["procurement"] = {
        "amount": round(procurement_synergy, 0),
        "basis": "Purchasing leverage",
        "confidence": "medium"
    }

    # Technology/IT synergies
    it_consolidation = cost_benchmarks.get("it_consolidation_pct", 0.20)
    target_it_spend = target_financials.get("revenue", 0) * 0.03  # Assume 3% IT spend
    it_synergy = target_it_spend * it_consolidation

    synergies["technology"] = {
        "amount": round(it_synergy, 0),
        "basis": "IT infrastructure consolidation",
        "confidence": "medium"
    }

    total_cost_synergies = sum(s["amount"] for s in synergies.values())

    return {
        "total": round(total_cost_synergies, 0),
        "breakdown": synergies,
        "as_pct_of_target_revenue": round(total_cost_synergies / target_financials.get("revenue", 1) * 100, 1)
    }


def estimate_revenue_synergies(
    acquirer_financials: Dict,
    target_financials: Dict,
    overlap_analysis: Dict,
    revenue_benchmarks: Dict
) -> Dict[str, Any]:
    """Estimate revenue synergies from merger."""
    synergies = {}

    target_revenue = target_financials.get("revenue", 0)
    acquirer_revenue = acquirer_financials.get("revenue", 0)

    # Cross-sell opportunities
    customer_overlap = overlap_analysis.get("customer", 0)
    non_overlap_customers = 1 - customer_overlap
    cross_sell_rate = revenue_benchmarks.get("cross_sell_conversion", 0.10)
    avg_deal_size_pct = revenue_benchmarks.get("avg_deal_size_pct", 0.01)

    cross_sell_synergy = (acquirer_revenue * non_overlap_customers *
                          cross_sell_rate * avg_deal_size_pct)

    synergies["cross_sell"] = {
        "amount": round(cross_sell_synergy, 0),
        "basis": "Cross-sell to acquirer customers",
        "confidence": "low"
    }

    # Market expansion
    geographic_complement = 1 - overlap_analysis.get("geographic", 0)
    market_expansion = target_revenue * geographic_complement * revenue_benchmarks.get("expansion_factor", 0.05)

    synergies["market_expansion"] = {
        "amount": round(market_expansion, 0),
        "basis": "Geographic market expansion",
        "confidence": "low"
    }

    total_revenue_synergies = sum(s["amount"] for s in synergies.values())

    return {
        "total": round(total_revenue_synergies, 0),
        "breakdown": synergies,
        "as_pct_of_combined_revenue": round(total_revenue_synergies / (acquirer_revenue + target_revenue) * 100, 2)
    }


def estimate_integration_costs(
    acquirer_financials: Dict,
    target_financials: Dict,
    integration_plan: Dict,
    cost_factors: Dict
) -> Dict[str, Any]:
    """Estimate one-time integration costs."""
    costs = {}

    target_employees = target_financials.get("employees", 0)
    target_revenue = target_financials.get("revenue", 0)
    approach = integration_plan.get("approach", "partial")

    # Severance costs
    severance_pct = cost_factors.get("severance_eligible_pct", {}).get(approach, 0.15)
    avg_severance = cost_factors.get("avg_severance_weeks", 26) * cost_factors.get("avg_weekly_wage", 1500)
    severance_cost = target_employees * severance_pct * avg_severance

    costs["severance"] = round(severance_cost, 0)

    # IT integration
    it_cost_per_employee = cost_factors.get("it_integration_per_employee", 5000)
    it_integration = target_employees * it_cost_per_employee

    costs["it_integration"] = round(it_integration, 0)

    # Facility consolidation
    facility_pct = cost_factors.get("facility_cost_pct", 0.005)
    facility_cost = target_revenue * facility_pct

    costs["facilities"] = round(facility_cost, 0)

    # Professional fees
    professional_fees = target_revenue * cost_factors.get("professional_fee_pct", 0.01)

    costs["professional_fees"] = round(professional_fees, 0)

    # Change management / retention
    retention_cost = target_employees * cost_factors.get("retention_per_employee", 2000)

    costs["retention_programs"] = round(retention_cost, 0)

    total_integration = sum(costs.values())

    return {
        "total": round(total_integration, 0),
        "breakdown": costs,
        "as_pct_of_target_revenue": round(total_integration / target_revenue * 100, 1)
    }


def calculate_synergy_timeline(
    cost_synergies: Dict,
    revenue_synergies: Dict,
    integration_plan: Dict,
    timeline_params: Dict
) -> List[Dict]:
    """Calculate phased synergy realization timeline."""
    timeline_months = integration_plan.get("timeline_months", 24)

    total_cost = cost_synergies.get("total", 0)
    total_revenue = revenue_synergies.get("total", 0)

    # Cost synergies realize faster than revenue
    cost_phases = timeline_params.get("cost_realization", [0.3, 0.6, 0.85, 1.0])
    revenue_phases = timeline_params.get("revenue_realization", [0.1, 0.3, 0.6, 0.85])

    timeline = []
    for i, (cost_pct, rev_pct) in enumerate(zip(cost_phases, revenue_phases)):
        year = i + 1
        timeline.append({
            "year": year,
            "cost_synergies_cumulative": round(total_cost * cost_pct, 0),
            "revenue_synergies_cumulative": round(total_revenue * rev_pct, 0),
            "total_cumulative": round(total_cost * cost_pct + total_revenue * rev_pct, 0),
            "cost_realization_pct": cost_pct,
            "revenue_realization_pct": rev_pct
        })

    return timeline


def analyze_synergies(
    deal_id: str,
    acquirer_financials: Dict,
    target_financials: Dict,
    overlap_analysis: Dict,
    integration_plan: Dict,
    market_data: Dict
) -> Dict[str, Any]:
    """
    Analyze merger synergies.

    Business Rules:
    1. Cost synergy categorization
    2. Revenue synergy estimation
    3. Integration cost modeling
    4. Synergy realization timeline

    Args:
        deal_id: Transaction identifier
        acquirer_financials: Acquirer financial data
        target_financials: Target financial data
        overlap_analysis: Business overlap assessment
        integration_plan: Integration approach
        market_data: Industry benchmarks

    Returns:
        Synergy analysis results
    """
    benchmarks = load_synergy_benchmarks()

    industry = market_data.get("industry", "general")
    industry_benchmarks = benchmarks.get("industries", {}).get(industry, benchmarks.get("default", {}))

    risk_factors = []

    # Cost synergies
    cost_synergies = estimate_cost_synergies(
        acquirer_financials,
        target_financials,
        overlap_analysis,
        industry_benchmarks.get("cost_benchmarks", {})
    )

    # Revenue synergies
    revenue_synergies = estimate_revenue_synergies(
        acquirer_financials,
        target_financials,
        overlap_analysis,
        industry_benchmarks.get("revenue_benchmarks", {})
    )

    # Integration costs
    integration_costs = estimate_integration_costs(
        acquirer_financials,
        target_financials,
        integration_plan,
        benchmarks.get("integration_costs", {})
    )

    # Net value creation
    net_value = cost_synergies["total"] + revenue_synergies["total"] - integration_costs["total"]

    # Synergy timeline
    realization_timeline = calculate_synergy_timeline(
        cost_synergies,
        revenue_synergies,
        integration_plan,
        benchmarks.get("timeline_params", {})
    )

    # Risk assessment
    if revenue_synergies["total"] > cost_synergies["total"]:
        risk_factors.append({
            "factor": "Revenue synergy heavy",
            "description": "Revenue synergies exceed cost synergies - higher execution risk",
            "mitigation": "Develop detailed cross-sell implementation plan"
        })

    avg_synergy_pct = market_data.get("avg_synergy_pct", 0.05)
    target_revenue = target_financials.get("revenue", 0)
    total_synergies_pct = (cost_synergies["total"] + revenue_synergies["total"]) / target_revenue if target_revenue > 0 else 0

    if total_synergies_pct > avg_synergy_pct * 1.5:
        risk_factors.append({
            "factor": "Aggressive synergy estimates",
            "description": f"Synergies at {total_synergies_pct:.1%} exceed industry average by >50%",
            "mitigation": "Validate assumptions with detailed bottom-up analysis"
        })

    return {
        "deal_id": deal_id,
        "total_synergies": {
            "cost": cost_synergies["total"],
            "revenue": revenue_synergies["total"],
            "total": cost_synergies["total"] + revenue_synergies["total"]
        },
        "cost_synergies": cost_synergies,
        "revenue_synergies": revenue_synergies,
        "integration_costs": integration_costs,
        "net_value_creation": round(net_value, 0),
        "realization_timeline": realization_timeline,
        "risk_factors": risk_factors
    }


if __name__ == "__main__":
    import json
    result = analyze_synergies(
        deal_id="DEAL-001",
        acquirer_financials={"revenue": 500000000, "ebitda": 75000000, "employees": 2000, "cogs": 300000000},
        target_financials={"revenue": 150000000, "ebitda": 20000000, "employees": 600, "cogs": 90000000},
        overlap_analysis={"geographic": 0.3, "customer": 0.15, "vendor": 0.4},
        integration_plan={"approach": "full", "timeline_months": 24},
        market_data={"industry": "manufacturing", "avg_synergy_pct": 0.05}
    )
    print(json.dumps(result, indent=2))
