#!/usr/bin/env python3
"""
Lab Sample Viability Validation

Implements proprietary business rules for biospecimen accessioning and quality control.
These rules are based on validated laboratory protocols specific to the institution.
"""

import csv
import ast
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any


def load_biomarker_constraints() -> Dict[str, Any]:
    """Load sample type constraints from configuration file."""
    constraints_file = Path(__file__).parent / "biomarker_constraints.json"
    with open(constraints_file, 'r') as f:
        return json.load(f)


def parse_iso_datetime(dt_string: str) -> datetime:
    """Parse ISO 8601 datetime string."""
    # Handle both with and without microseconds
    for fmt in ["%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S"]:
        try:
            return datetime.strptime(dt_string.replace('Z', ''), fmt)
        except ValueError:
            continue
    raise ValueError(f"Cannot parse datetime: {dt_string}")


def validate_sample_viability(
    sample_id: str,
    sample_type: str,
    collection_time: str,
    receipt_time: str,
    turbidity_index: float,
    storage_temp: float,
    volume_ml: float
) -> Dict[str, Any]:
    """
    Validate sample viability based on proprietary laboratory rules.

    Business Rules:
    1. Plasma-EDTA samples must be processed within 4 hours
    2. Turbidity > 0.8 requires ultracentrifugation
    3. Storage temp must be between -80°C and -70°C (strict)
    4. Minimum volume requirements per sample type

    Args:
        sample_id: Unique sample identifier
        sample_type: Type of biospecimen
        collection_time: ISO 8601 datetime of collection
        receipt_time: ISO 8601 datetime of receipt
        turbidity_index: Optical turbidity (0.0-1.0)
        storage_temp: Temperature in Celsius
        volume_ml: Sample volume in milliliters

    Returns:
        Dictionary with viability assessment and recommendations
    """
    constraints = load_biomarker_constraints()

    viable = True
    flags = []
    violations = []

    # Parse timestamps
    collection_dt = parse_iso_datetime(collection_time)
    receipt_dt = parse_iso_datetime(receipt_time)
    time_elapsed = receipt_dt - collection_dt

    # RULE 1: Time-Sensitive Processing for Plasma-EDTA
    if sample_type == "Plasma-EDTA":
        max_processing_time = timedelta(hours=4)
        if time_elapsed > max_processing_time:
            viable = False
            violations.append(
                f"Plasma-EDTA processing time exceeded: {time_elapsed.total_seconds()/3600:.1f}h "
                f"(maximum: 4h). EDTA anticoagulant stability compromised."
            )

    # RULE 2: Turbidity Quality Control
    if turbidity_index > 0.8:
        flags.append(
            f"HIGH_TURBIDITY: Index {turbidity_index:.2f} exceeds 0.8 threshold. "
            "Sample requires Ultracentrifugation pre-treatment before biomarker analysis."
        )

    # RULE 3: Ultra-Cold Storage Requirements (Strict Range)
    if not (-80.0 <= storage_temp <= -70.0):
        viable = False
        violations.append(
            f"Storage temperature {storage_temp}°C is outside the validated range "
            f"(-80°C to -70°C). Sample integrity compromised."
        )

    # RULE 4: Minimum Volume Requirements
    if sample_type in constraints["sample_types"]:
        min_volume = constraints["sample_types"][sample_type]["min_volume_ml"]
        required_assays = constraints["sample_types"][sample_type]["required_assays"]

        if volume_ml < min_volume:
            viable = False
            violations.append(
                f"Insufficient volume: {volume_ml}ml < {min_volume}ml required "
                f"for assay panel: {', '.join(required_assays)}"
            )
    else:
        flags.append(f"WARNING: Sample type '{sample_type}' not found in constraints database")

    # Determine recommended action
    if not viable:
        recommended_action = "REJECT_SAMPLE - Does not meet viability criteria"
    elif flags:
        if "HIGH_TURBIDITY" in str(flags):
            recommended_action = "PROCESS_WITH_ULTRACENTRIFUGATION"
        else:
            recommended_action = "PROCESS_WITH_CAUTION - Review flags"
    else:
        recommended_action = "ACCEPT_FOR_STANDARD_PROCESSING"

    return {
        "sample_id": sample_id,
        "sample_type": sample_type,
        "viable": viable,
        "time_elapsed_hours": round(time_elapsed.total_seconds() / 3600, 2),
        "flags": flags,
        "violations": violations,
        "recommended_action": recommended_action
    }


def main():
    """Command-line interface for sample validation."""
    if len(sys.argv) < 2:
        print("Usage: python viability_check.py <sample_data_json>")
        print("\nExample:")
        print('  python viability_check.py \'{"sample_id": "S12345", "sample_type": "Plasma-EDTA", '
              '"collection_time": "2026-01-14T08:00:00", "receipt_time": "2026-01-14T09:30:00", '
              '"turbidity_index": 0.3, "storage_temp": -75.0, "volume_ml": 5.0}\'')
        sys.exit(1)

    try:
        sample_data = json.loads(sys.argv[1])

        result = validate_sample_viability(
            sample_id=sample_data["sample_id"],
            sample_type=sample_data["sample_type"],
            collection_time=sample_data["collection_time"],
            receipt_time=sample_data["receipt_time"],
            turbidity_index=sample_data["turbidity_index"],
            storage_temp=sample_data["storage_temp"],
            volume_ml=sample_data["volume_ml"]
        )

        print(json.dumps(result, indent=2))

        # Exit with non-zero if sample is not viable
        sys.exit(0 if result["viable"] else 1)

    except json.JSONDecodeError as e:
        print(f"Error: Invalid JSON input - {e}", file=sys.stderr)
        sys.exit(2)
    except KeyError as e:
        print(f"Error: Missing required field - {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    import json
    main()
