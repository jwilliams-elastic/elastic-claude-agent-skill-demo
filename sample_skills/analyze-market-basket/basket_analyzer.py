"""
Market Basket Analysis Module

Implements association rule mining and product affinity
analysis for retail merchandising optimization.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict



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


def load_basket_config() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    default_parameters_data = load_key_value_csv("default_parameters.csv")
    analysis_windows_data = load_key_value_csv("analysis_windows.csv")
    recommendation_thresholds_data = load_key_value_csv("recommendation_thresholds.csv")
    time_patterns_data = load_csv_as_dict("time_patterns.csv")
    segment_definitions_data = load_csv_as_dict("segment_definitions.csv")
    cross_sell_rules_data = load_key_value_csv("cross_sell_rules.csv")
    params = load_parameters()
    return {
        "default_parameters": default_parameters_data,
        "analysis_windows": analysis_windows_data,
        "recommendation_thresholds": recommendation_thresholds_data,
        "time_patterns": time_patterns_data,
        "segment_definitions": segment_definitions_data,
        "cross_sell_rules": cross_sell_rules_data,
        **params
    }


def calculate_support(
    transaction_data: List[Dict],
    itemset: frozenset
) -> float:
    """Calculate support for an itemset."""
    if not transaction_data:
        return 0.0

    count = 0
    for txn in transaction_data:
        items = set(txn.get("items", []))
        if itemset.issubset(items):
            count += 1

    return count / len(transaction_data)


def find_frequent_itemsets(
    transaction_data: List[Dict],
    min_support: float
) -> Dict[frozenset, float]:
    """Find frequent itemsets using Apriori-like approach."""
    # Get all unique items
    all_items = set()
    for txn in transaction_data:
        all_items.update(txn.get("items", []))

    frequent = {}

    # Find frequent 1-itemsets
    for item in all_items:
        itemset = frozenset([item])
        support = calculate_support(transaction_data, itemset)
        if support >= min_support:
            frequent[itemset] = support

    # Find frequent 2-itemsets
    items_list = list(all_items)
    for i in range(len(items_list)):
        for j in range(i + 1, len(items_list)):
            itemset = frozenset([items_list[i], items_list[j]])
            support = calculate_support(transaction_data, itemset)
            if support >= min_support:
                frequent[itemset] = support

    return frequent


def generate_association_rules(
    frequent_itemsets: Dict[frozenset, float],
    transaction_data: List[Dict],
    min_confidence: float
) -> List[Dict]:
    """Generate association rules from frequent itemsets."""
    rules = []

    for itemset, support in frequent_itemsets.items():
        if len(itemset) < 2:
            continue

        items = list(itemset)
        for i in range(len(items)):
            antecedent = frozenset([items[i]])
            consequent = frozenset(items[:i] + items[i+1:])

            antecedent_support = frequent_itemsets.get(antecedent, 0)
            if antecedent_support > 0:
                confidence = support / antecedent_support

                if confidence >= min_confidence:
                    # Calculate lift
                    consequent_support = calculate_support(
                        transaction_data,
                        consequent
                    )
                    lift = confidence / consequent_support if consequent_support > 0 else 0

                    rules.append({
                        "antecedent": list(antecedent),
                        "consequent": list(consequent),
                        "support": round(support, 4),
                        "confidence": round(confidence, 4),
                        "lift": round(lift, 2)
                    })

    # Sort by lift descending
    rules.sort(key=lambda x: x["lift"], reverse=True)
    return rules


def find_product_pairs(
    transaction_data: List[Dict],
    min_support: float
) -> List[Dict]:
    """Find frequently bought together product pairs."""
    pair_counts = defaultdict(int)
    total_txns = len(transaction_data)

    for txn in transaction_data:
        items = list(set(txn.get("items", [])))
        for i in range(len(items)):
            for j in range(i + 1, len(items)):
                pair = tuple(sorted([items[i], items[j]]))
                pair_counts[pair] += 1

    pairs = []
    for pair, count in pair_counts.items():
        support = count / total_txns if total_txns > 0 else 0
        if support >= min_support:
            pairs.append({
                "product_1": pair[0],
                "product_2": pair[1],
                "co_occurrence_count": count,
                "support": round(support, 4)
            })

    # Sort by support
    pairs.sort(key=lambda x: x["support"], reverse=True)
    return pairs[:20]  # Top 20 pairs


def generate_recommendations(
    association_rules: List[Dict],
    product_pairs: List[Dict],
    config: Dict
) -> List[Dict]:
    """Generate merchandising recommendations."""
    recommendations = []

    # High-lift rules for cross-sell
    high_lift_rules = [r for r in association_rules if r["lift"] > 2.0]
    for rule in high_lift_rules[:5]:
        recommendations.append({
            "type": "cross_sell",
            "recommendation": f"Promote {rule['consequent'][0]} to buyers of {rule['antecedent'][0]}",
            "lift": rule["lift"],
            "confidence": rule["confidence"]
        })

    # Co-location recommendations
    for pair in product_pairs[:3]:
        recommendations.append({
            "type": "product_placement",
            "recommendation": f"Place {pair['product_1']} near {pair['product_2']}",
            "support": pair["support"]
        })

    return recommendations


def calculate_summary_stats(
    transaction_data: List[Dict],
    association_rules: List[Dict],
    product_pairs: List[Dict]
) -> Dict[str, Any]:
    """Calculate analysis summary statistics."""
    total_transactions = len(transaction_data)
    total_items = set()
    basket_sizes = []

    for txn in transaction_data:
        items = txn.get("items", [])
        total_items.update(items)
        basket_sizes.append(len(items))

    avg_basket_size = sum(basket_sizes) / len(basket_sizes) if basket_sizes else 0

    return {
        "total_transactions": total_transactions,
        "unique_items": len(total_items),
        "avg_basket_size": round(avg_basket_size, 2),
        "rules_generated": len(association_rules),
        "pairs_identified": len(product_pairs)
    }


def analyze_basket(
    analysis_id: str,
    transaction_data: List[Dict],
    product_catalog: Dict,
    time_period: Dict,
    min_support: float,
    min_confidence: float
) -> Dict[str, Any]:
    """
    Analyze market basket data.

    Business Rules:
    1. Association rule mining
    2. Lift calculation
    3. Temporal patterns
    4. Customer segmentation

    Args:
        analysis_id: Analysis identifier
        transaction_data: Transaction records
        product_catalog: Product information
        time_period: Analysis time range
        min_support: Minimum support threshold
        min_confidence: Minimum confidence threshold

    Returns:
        Market basket analysis results
    """
    config = load_basket_config()

    # Find frequent itemsets
    frequent_itemsets = find_frequent_itemsets(
        transaction_data,
        min_support
    )

    # Generate association rules
    association_rules = generate_association_rules(
        frequent_itemsets,
        transaction_data,
        min_confidence
    )

    # Find product pairs
    product_pairs = find_product_pairs(
        transaction_data,
        min_support
    )

    # Generate recommendations
    recommendations = generate_recommendations(
        association_rules,
        product_pairs,
        config
    )

    # Calculate summary
    summary_stats = calculate_summary_stats(
        transaction_data,
        association_rules,
        product_pairs
    )

    return {
        "analysis_id": analysis_id,
        "time_period": time_period,
        "association_rules": association_rules[:20],
        "product_pairs": product_pairs,
        "recommendations": recommendations,
        "segment_insights": {},
        "summary_stats": summary_stats
    }


if __name__ == "__main__":
    import json
    result = analyze_basket(
        analysis_id="MBA-001",
        transaction_data=[
            {"txn_id": "T001", "items": ["bread", "milk", "eggs"]},
            {"txn_id": "T002", "items": ["bread", "butter"]},
            {"txn_id": "T003", "items": ["milk", "eggs", "cheese"]},
            {"txn_id": "T004", "items": ["bread", "milk", "butter"]},
            {"txn_id": "T005", "items": ["bread", "eggs"]}
        ],
        product_catalog={"bread": {"category": "bakery"}, "milk": {"category": "dairy"}},
        time_period={"start": "2025-01-01", "end": "2025-12-31"},
        min_support=0.2,
        min_confidence=0.3
    )
    print(json.dumps(result, indent=2))
