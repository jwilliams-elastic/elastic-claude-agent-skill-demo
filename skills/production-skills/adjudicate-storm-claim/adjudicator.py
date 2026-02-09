"""
Storm Insurance Claim Adjudication Engine

Implements proprietary underwriting rules for storm damage claims.
These rules are based on internal risk assessment models and cannot be
inferred from public knowledge.
"""

import json
import csv
from pathlib import Path
from typing import Dict, List, Any


class ClaimAdjudicator:
    """
    Adjudicates storm insurance claims based on proprietary business rules.
    """

    def __init__(self, risk_matrix_path: str = None):
        """Initialize adjudicator with risk matrix data."""
        if risk_matrix_path is None:
            risk_matrix_path = Path(__file__).parent / "risk_matrix.csv"

        self.risk_matrix = self._load_risk_matrix(risk_matrix_path)

    def _load_risk_matrix(self, path: Path) -> Dict[str, Dict[str, Any]]:
        """Load risk assessment matrix from CSV."""
        matrix = {}
        with open(path, 'r') as f:
            reader = csv.DictReader(f)
            for row in reader:
                key = f"{row['roof_material']}_{row['region']}"
                matrix[key] = {
                    'base_risk_score': float(row['base_risk_score']),
                    'requires_retrofit': row['requires_retrofit'].lower() == 'true',
                    'min_retrofit_year': int(row['min_retrofit_year']) if row['min_retrofit_year'] else None,
                    'coverage_multiplier': float(row['coverage_multiplier'])
                }
        return matrix

    def adjudicate_claim(
        self,
        claim_id: str,
        storm_category: int,
        roof_material: str,
        region: str,
        retrofit_year: int = None,
        damage_amount: float = 0
    ) -> Dict[str, Any]:
        """
        Adjudicate a storm damage claim.

        Proprietary Business Rules:
        1. Storm category 3+ qualifies for deductible waiver
        2. Wood shake roofs in coastal regions denied unless retrofit_year > 2020
        3. Base coverage modified by material/region risk multiplier
        4. High-risk combinations require manual review

        Args:
            claim_id: Unique claim identifier
            storm_category: Storm severity (1-5)
            roof_material: Roofing material type
            region: Geographic region
            retrofit_year: Year of last structural retrofit (optional)
            damage_amount: Claimed damage amount in USD

        Returns:
            Dictionary containing adjudication decision and details
        """
        flags = []
        decision = "APPROVED"
        deductible_waived = False
        reason_parts = []

        # Rule 1: Deductible waiver for category 3+ storms
        if storm_category >= 3:
            deductible_waived = True
            reason_parts.append(f"Category {storm_category} storm qualifies for deductible waiver")

        # Look up risk factors from matrix
        matrix_key = f"{roof_material}_{region}"
        risk_factors = self.risk_matrix.get(matrix_key)

        if not risk_factors:
            # Unknown combination - flag for review
            decision = "REVIEW_REQUIRED"
            flags.append("UNKNOWN_MATERIAL_REGION_COMBINATION")
            reason_parts.append("Material/region combination requires manual review")
        else:
            # Rule 2: Wood shake coastal restriction
            if roof_material == "wood_shake" and region == "coastal":
                if retrofit_year is None or retrofit_year <= 2020:
                    decision = "DENIED"
                    flags.append("HIGH_RISK_MATERIAL_NO_RETROFIT")
                    reason_parts.append("Wood shake roof in coastal region requires retrofit after 2020")
                else:
                    flags.append("RETROFIT_APPROVED")
                    reason_parts.append(f"Retrofit completed in {retrofit_year} meets requirements")

            # Rule 3: Retrofit requirement check
            if risk_factors['requires_retrofit']:
                min_year = risk_factors['min_retrofit_year']
                if retrofit_year is None or (min_year and retrofit_year < min_year):
                    decision = "DENIED"
                    flags.append("RETROFIT_REQUIREMENT_NOT_MET")
                    reason_parts.append(f"Property requires retrofit after {min_year}")

            # Rule 4: High risk score triggers review
            if risk_factors['base_risk_score'] >= 8.0 and storm_category >= 4:
                if decision == "APPROVED":
                    decision = "REVIEW_REQUIRED"
                flags.append("HIGH_RISK_CATASTROPHIC_EVENT")
                reason_parts.append("High-risk property with catastrophic damage requires underwriter review")

        # Calculate coverage limit
        if decision == "APPROVED":
            if risk_factors:
                coverage_limit = damage_amount * risk_factors['coverage_multiplier']
                # Cap at damage amount (multiplier can reduce but not increase base coverage)
                coverage_limit = min(coverage_limit, damage_amount)
            else:
                coverage_limit = 0
        else:
            coverage_limit = 0

        # Build final reason string
        if not reason_parts:
            reason_parts.append("Standard claim processing applied")

        return {
            "claim_id": claim_id,
            "decision": decision,
            "deductible_waived": deductible_waived,
            "coverage_limit": round(coverage_limit, 2),
            "reason": "; ".join(reason_parts),
            "flags": flags
        }


def adjudicate_claim(
    claim_id: str,
    storm_category: int,
    roof_material: str,
    region: str,
    retrofit_year: int = None,
    damage_amount: float = 0
) -> Dict[str, Any]:
    """
    Convenience function to adjudicate a claim.

    See ClaimAdjudicator.adjudicate_claim for detailed documentation.
    """
    adjudicator = ClaimAdjudicator()
    return adjudicator.adjudicate_claim(
        claim_id=claim_id,
        storm_category=storm_category,
        roof_material=roof_material,
        region=region,
        retrofit_year=retrofit_year,
        damage_amount=damage_amount
    )


if __name__ == "__main__":
    # Test cases demonstrating proprietary rules
    test_cases = [
        {
            "name": "Category 4 storm - deductible waived",
            "params": {
                "claim_id": "CLM-001",
                "storm_category": 4,
                "roof_material": "asphalt_shingle",
                "region": "inland",
                "damage_amount": 50000
            }
        },
        {
            "name": "Wood shake coastal without retrofit - DENIED",
            "params": {
                "claim_id": "CLM-002",
                "storm_category": 3,
                "roof_material": "wood_shake",
                "region": "coastal",
                "retrofit_year": 2019,
                "damage_amount": 75000
            }
        },
        {
            "name": "Wood shake coastal with retrofit - APPROVED",
            "params": {
                "claim_id": "CLM-003",
                "storm_category": 3,
                "roof_material": "wood_shake",
                "region": "coastal",
                "retrofit_year": 2021,
                "damage_amount": 75000
            }
        },
        {
            "name": "High risk catastrophic - REVIEW_REQUIRED",
            "params": {
                "claim_id": "CLM-004",
                "storm_category": 5,
                "roof_material": "metal",
                "region": "coastal",
                "damage_amount": 200000
            }
        },
        {
            "name": "Category 2 standard claim",
            "params": {
                "claim_id": "CLM-005",
                "storm_category": 2,
                "roof_material": "tile",
                "region": "inland",
                "damage_amount": 25000
            }
        }
    ]

    print("Storm Insurance Claim Adjudication - Test Cases")
    print("=" * 80)

    for test in test_cases:
        print(f"\n{test['name']}")
        print("-" * 80)
        result = adjudicate_claim(**test['params'])
        print(json.dumps(result, indent=2))
