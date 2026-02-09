"""
Product Profitability Analysis Module

Implements product-level profitability analysis including
margin calculation, cost allocation, and portfolio analysis.
"""

import csv
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


def load_profitability_metrics() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    cost_allocation_methods_data = load_csv_as_dict("cost_allocation_methods.csv")
    margin_thresholds_data = load_csv_as_dict("margin_thresholds.csv")
    profitability_segments_data = load_csv_as_dict("profitability_segments.csv")
    overhead_categories_data = load_csv_as_dict("overhead_categories.csv")
    analysis_dimensions_data = load_csv_as_dict("analysis_dimensions.csv")
    break_even_factors_data = load_key_value_csv("break_even_factors.csv")
    pricing_analysis_data = load_key_value_csv("pricing_analysis.csv")
    params = load_parameters()
    return {
        "cost_allocation_methods": cost_allocation_methods_data,
        "margin_thresholds": margin_thresholds_data,
        "profitability_segments": profitability_segments_data,
        "overhead_categories": overhead_categories_data,
        "analysis_dimensions": analysis_dimensions_data,
        "break_even_factors": break_even_factors_data,
        "pricing_analysis": pricing_analysis_data,
        **params
    }


def calculate_gross_margin(
    revenue: float,
    cost_of_goods: float
) -> Dict[str, Any]:
    """Calculate gross margin."""
    gross_profit = revenue - cost_of_goods
    gross_margin_pct = gross_profit / revenue if revenue > 0 else 0

    return {
        "revenue": revenue,
        "cost_of_goods": cost_of_goods,
        "gross_profit": round(gross_profit, 2),
        "gross_margin_pct": round(gross_margin_pct * 100, 1)
    }


def calculate_contribution_margin(
    revenue: float,
    variable_costs: float
) -> Dict[str, Any]:
    """Calculate contribution margin."""
    contribution = revenue - variable_costs
    contribution_margin_pct = contribution / revenue if revenue > 0 else 0

    return {
        "revenue": revenue,
        "variable_costs": variable_costs,
        "contribution": round(contribution, 2),
        "contribution_margin_pct": round(contribution_margin_pct * 100, 1)
    }


def allocate_overhead(
    products: List[Dict],
    overhead_pool: float,
    allocation_base: str
) -> List[Dict]:
    """Allocate overhead costs to products."""
    # Calculate total allocation base
    total_base = sum(p.get(allocation_base, 0) for p in products)

    allocated_products = []
    for product in products:
        base_value = product.get(allocation_base, 0)
        allocation_pct = base_value / total_base if total_base > 0 else 0
        allocated_overhead = overhead_pool * allocation_pct

        product_copy = product.copy()
        product_copy["allocated_overhead"] = round(allocated_overhead, 2)
        product_copy["allocation_pct"] = round(allocation_pct * 100, 1)
        allocated_products.append(product_copy)

    return allocated_products


def calculate_fully_loaded_margin(
    revenue: float,
    direct_costs: float,
    allocated_overhead: float
) -> Dict[str, Any]:
    """Calculate fully loaded product margin."""
    total_cost = direct_costs + allocated_overhead
    net_profit = revenue - total_cost
    net_margin_pct = net_profit / revenue if revenue > 0 else 0

    return {
        "revenue": revenue,
        "direct_costs": direct_costs,
        "allocated_overhead": allocated_overhead,
        "total_cost": round(total_cost, 2),
        "net_profit": round(net_profit, 2),
        "net_margin_pct": round(net_margin_pct * 100, 1)
    }


def rate_margin_performance(
    margin_pct: float,
    thresholds: Dict,
    margin_type: str = "gross_margin"
) -> Dict[str, Any]:
    """Rate margin performance against thresholds."""
    type_thresholds = thresholds.get(margin_type, {})

    if margin_pct >= type_thresholds.get("excellent", 0.50) * 100:
        rating = "EXCELLENT"
    elif margin_pct >= type_thresholds.get("good", 0.35) * 100:
        rating = "GOOD"
    elif margin_pct >= type_thresholds.get("acceptable", 0.20) * 100:
        rating = "ACCEPTABLE"
    elif margin_pct >= type_thresholds.get("poor", 0.10) * 100:
        rating = "POOR"
    else:
        rating = "CRITICAL"

    return {
        "margin_type": margin_type,
        "margin_pct": margin_pct,
        "rating": rating
    }


def segment_products(
    products: List[Dict],
    segments: Dict
) -> Dict[str, List]:
    """Segment products by profitability matrix."""
    total_revenue = sum(p.get("revenue", 0) for p in products)

    segmented = {"star": [], "cash_cow": [], "question_mark": [], "dog": []}

    for product in products:
        revenue = product.get("revenue", 0)
        margin = product.get("net_margin_pct", 0) / 100
        revenue_share = revenue / total_revenue if total_revenue > 0 else 0

        # Classify based on margin and revenue share
        if margin >= segments["star"]["margin"] and revenue_share >= segments["star"]["revenue_share"]:
            segment = "star"
        elif margin >= segments["cash_cow"]["margin"]:
            segment = "cash_cow"
        elif revenue_share >= segments["question_mark"]["revenue_share"]:
            segment = "question_mark"
        else:
            segment = "dog"

        product_with_segment = product.copy()
        product_with_segment["segment"] = segment
        product_with_segment["revenue_share_pct"] = round(revenue_share * 100, 1)
        segmented[segment].append(product_with_segment)

    return segmented


def calculate_product_mix_impact(
    products: List[Dict]
) -> Dict[str, Any]:
    """Analyze product mix and profitability impact."""
    total_revenue = sum(p.get("revenue", 0) for p in products)
    total_profit = sum(p.get("net_profit", 0) for p in products)

    weighted_margin = 0
    mix_analysis = []

    for product in products:
        revenue = product.get("revenue", 0)
        margin = product.get("net_margin_pct", 0)
        revenue_share = revenue / total_revenue if total_revenue > 0 else 0

        weighted_contribution = revenue_share * margin
        weighted_margin += weighted_contribution

        mix_analysis.append({
            "product_id": product.get("product_id", ""),
            "revenue_share_pct": round(revenue_share * 100, 1),
            "margin_pct": margin,
            "weighted_contribution": round(weighted_contribution, 2)
        })

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "weighted_average_margin": round(weighted_margin, 1),
        "mix_analysis": sorted(mix_analysis, key=lambda x: x["weighted_contribution"], reverse=True)
    }


def analyze_cost_structure(
    product: Dict
) -> Dict[str, Any]:
    """Analyze product cost structure."""
    revenue = product.get("revenue", 0)
    direct_materials = product.get("direct_materials", 0)
    direct_labor = product.get("direct_labor", 0)
    variable_overhead = product.get("variable_overhead", 0)
    fixed_overhead = product.get("allocated_overhead", 0)

    total_cost = direct_materials + direct_labor + variable_overhead + fixed_overhead

    cost_breakdown = {
        "direct_materials": {
            "amount": direct_materials,
            "pct_of_cost": round(direct_materials / total_cost * 100, 1) if total_cost > 0 else 0,
            "pct_of_revenue": round(direct_materials / revenue * 100, 1) if revenue > 0 else 0
        },
        "direct_labor": {
            "amount": direct_labor,
            "pct_of_cost": round(direct_labor / total_cost * 100, 1) if total_cost > 0 else 0,
            "pct_of_revenue": round(direct_labor / revenue * 100, 1) if revenue > 0 else 0
        },
        "variable_overhead": {
            "amount": variable_overhead,
            "pct_of_cost": round(variable_overhead / total_cost * 100, 1) if total_cost > 0 else 0,
            "pct_of_revenue": round(variable_overhead / revenue * 100, 1) if revenue > 0 else 0
        },
        "fixed_overhead": {
            "amount": fixed_overhead,
            "pct_of_cost": round(fixed_overhead / total_cost * 100, 1) if total_cost > 0 else 0,
            "pct_of_revenue": round(fixed_overhead / revenue * 100, 1) if revenue > 0 else 0
        }
    }

    return {
        "total_cost": round(total_cost, 2),
        "cost_breakdown": cost_breakdown,
        "cost_to_revenue_ratio": round(total_cost / revenue, 2) if revenue > 0 else 0
    }


def calculate_break_even_volume(
    fixed_costs: float,
    contribution_per_unit: float
) -> Dict[str, Any]:
    """Calculate break-even volume."""
    if contribution_per_unit <= 0:
        return {"error": "Contribution per unit must be positive"}

    break_even_units = fixed_costs / contribution_per_unit

    return {
        "fixed_costs": fixed_costs,
        "contribution_per_unit": contribution_per_unit,
        "break_even_units": round(break_even_units, 0)
    }


def generate_recommendations(
    products: List[Dict],
    segments: Dict
) -> List[Dict]:
    """Generate profitability improvement recommendations."""
    recommendations = []

    for product in products:
        product_id = product.get("product_id", "")
        segment = product.get("segment", "")
        margin = product.get("net_margin_pct", 0)

        action = segments.get(segment, {}).get("action", "evaluate")

        if segment == "dog" and margin < 5:
            recommendations.append({
                "product_id": product_id,
                "segment": segment,
                "priority": "high",
                "recommendation": "Consider discontinuation or major repositioning",
                "action": action
            })
        elif segment == "question_mark":
            recommendations.append({
                "product_id": product_id,
                "segment": segment,
                "priority": "medium",
                "recommendation": "Evaluate investment vs. phase-out decision",
                "action": action
            })
        elif segment == "star":
            recommendations.append({
                "product_id": product_id,
                "segment": segment,
                "priority": "low",
                "recommendation": "Continue investment to maintain leadership",
                "action": action
            })

    return sorted(recommendations, key=lambda x: {"high": 0, "medium": 1, "low": 2}.get(x["priority"], 3))


def analyze_product_profitability(
    analysis_id: str,
    products: List[Dict],
    overhead_pool: float,
    allocation_base: str,
    analysis_period: str,
    analysis_date: str
) -> Dict[str, Any]:
    """
    Analyze product profitability.

    Business Rules:
    1. Multi-level margin calculation
    2. Overhead allocation
    3. Portfolio segmentation
    4. Profitability recommendations

    Args:
        analysis_id: Analysis identifier
        products: Product financial data
        overhead_pool: Total overhead to allocate
        allocation_base: Basis for overhead allocation
        analysis_period: Period analyzed
        analysis_date: Analysis date

    Returns:
        Product profitability analysis results
    """
    config = load_profitability_metrics()
    margin_thresholds = config.get("margin_thresholds", {})
    segments = config.get("profitability_segments", {})

    # Allocate overhead
    products_with_overhead = allocate_overhead(products, overhead_pool, allocation_base)

    # Calculate margins for each product
    product_analysis = []

    for product in products_with_overhead:
        revenue = product.get("revenue", 0)
        cogs = product.get("cost_of_goods", 0)
        variable_costs = product.get("variable_costs", cogs)
        direct_costs = cogs
        allocated_overhead = product.get("allocated_overhead", 0)

        # Gross margin
        gross = calculate_gross_margin(revenue, cogs)

        # Contribution margin
        contribution = calculate_contribution_margin(revenue, variable_costs)

        # Fully loaded margin
        fully_loaded = calculate_fully_loaded_margin(revenue, direct_costs, allocated_overhead)

        # Rate performance
        gross_rating = rate_margin_performance(gross["gross_margin_pct"], margin_thresholds, "gross_margin")
        net_rating = rate_margin_performance(fully_loaded["net_margin_pct"], margin_thresholds, "net_margin")

        # Cost structure
        cost_structure = analyze_cost_structure({
            **product,
            "revenue": revenue,
            "direct_materials": product.get("direct_materials", cogs * 0.5),
            "direct_labor": product.get("direct_labor", cogs * 0.3),
            "variable_overhead": product.get("variable_overhead", cogs * 0.2)
        })

        product_analysis.append({
            "product_id": product.get("product_id", ""),
            "product_name": product.get("product_name", ""),
            "revenue": revenue,
            "gross_margin": gross,
            "contribution_margin": contribution,
            "fully_loaded_margin": fully_loaded,
            "gross_margin_rating": gross_rating,
            "net_margin_rating": net_rating,
            "net_margin_pct": fully_loaded["net_margin_pct"],
            "net_profit": fully_loaded["net_profit"],
            "cost_structure": cost_structure
        })

    # Segment products
    segmented = segment_products(product_analysis, segments)

    # Product mix analysis
    mix_impact = calculate_product_mix_impact(product_analysis)

    # Generate recommendations
    # Add segment to product analysis for recommendations
    for product in product_analysis:
        for segment_name, segment_product_list in segmented.items():
            if any(p["product_id"] == product["product_id"] for p in segment_product_list):
                product["segment"] = segment_name
                break

    recommendations = generate_recommendations(product_analysis, segments)

    # Summary statistics
    total_revenue = sum(p["revenue"] for p in product_analysis)
    total_profit = sum(p["net_profit"] for p in product_analysis)
    profitable_products = sum(1 for p in product_analysis if p["net_profit"] > 0)

    return {
        "analysis_id": analysis_id,
        "analysis_date": analysis_date,
        "analysis_period": analysis_period,
        "summary": {
            "total_products": len(products),
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "overall_margin_pct": round(total_profit / total_revenue * 100, 1) if total_revenue > 0 else 0,
            "profitable_products": profitable_products,
            "unprofitable_products": len(products) - profitable_products
        },
        "product_analysis": product_analysis,
        "portfolio_segmentation": {
            "stars": len(segmented["star"]),
            "cash_cows": len(segmented["cash_cow"]),
            "question_marks": len(segmented["question_mark"]),
            "dogs": len(segmented["dog"])
        },
        "mix_analysis": mix_impact,
        "recommendations": recommendations
    }


if __name__ == "__main__":
    import json
    result = analyze_product_profitability(
        analysis_id="PROF-001",
        products=[
            {"product_id": "P001", "product_name": "Widget A", "revenue": 500000, "cost_of_goods": 275000, "machine_hours": 1000},
            {"product_id": "P002", "product_name": "Widget B", "revenue": 300000, "cost_of_goods": 180000, "machine_hours": 800},
            {"product_id": "P003", "product_name": "Widget C", "revenue": 150000, "cost_of_goods": 120000, "machine_hours": 500},
            {"product_id": "P004", "product_name": "Widget D", "revenue": 50000, "cost_of_goods": 48000, "machine_hours": 200}
        ],
        overhead_pool=100000,
        allocation_base="machine_hours",
        analysis_period="2026-Q1",
        analysis_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
