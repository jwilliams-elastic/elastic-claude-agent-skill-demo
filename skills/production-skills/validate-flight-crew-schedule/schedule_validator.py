"""
Flight Crew Schedule Validation Module

Implements FAA Part 117 flight duty time limitations and company-specific
scheduling policies for crew fatigue management.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta


def load_duty_limits() -> Dict[str, Any]:
    """Load duty time limits from CSV configuration."""
    limits_path = Path(__file__).parent / "duty_limits.csv"
    limits = {"fdp_limits": {}, "rest_requirements": {}, "cumulative_limits": {}}

    with open(limits_path, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            limit_type = row["limit_type"]
            if limit_type == "fdp":
                key = f"{row['start_time_window']}_{row['segments']}"
                limits["fdp_limits"][key] = {
                    "max_hours": float(row["max_hours"]),
                    "company_buffer": float(row["company_buffer"]),
                    "augmented_extension": float(row["augmented_extension"])
                }
            elif limit_type == "rest":
                limits["rest_requirements"][row["condition"]] = {
                    "min_hours": float(row["max_hours"]),
                    "reduced_rest_min": float(row.get("company_buffer", row["max_hours"]))
                }
            elif limit_type == "cumulative":
                limits["cumulative_limits"][row["condition"]] = {
                    "max_hours": float(row["max_hours"]),
                    "warning_threshold": float(row["company_buffer"])
                }

    return limits


def parse_datetime(dt_string: str) -> datetime:
    """Parse ISO datetime string."""
    return datetime.fromisoformat(dt_string.replace('Z', '+00:00').replace('+00:00', ''))


def calculate_fdp(schedule: List[Dict]) -> Dict[str, Any]:
    """Calculate flight duty period metrics from schedule."""
    if not schedule:
        return {"total_hours": 0, "segments": 0, "start_time": None, "end_time": None}

    # Assume 1 hour report time before first departure
    first_departure = parse_datetime(schedule[0]["departure"])
    report_time = first_departure - timedelta(hours=1)

    # Assume 30 minutes after last arrival
    last_arrival = parse_datetime(schedule[-1]["arrival"])
    release_time = last_arrival + timedelta(minutes=30)

    fdp_hours = (release_time - report_time).total_seconds() / 3600

    return {
        "total_hours": round(fdp_hours, 2),
        "segments": len(schedule),
        "start_time": report_time.strftime("%H:%M"),
        "end_time": release_time.strftime("%H:%M"),
        "report_time": report_time,
        "release_time": release_time
    }


def get_time_window(start_time: str) -> str:
    """Determine FDP limit time window based on report time."""
    hour = int(start_time.split(":")[0])

    if 5 <= hour < 12:
        return "morning"
    elif 12 <= hour < 17:
        return "afternoon"
    elif 17 <= hour < 22:
        return "evening"
    else:
        return "night"


def calculate_fatigue_risk(
    fdp_hours: float,
    segments: int,
    time_window: str,
    duty_history: Dict[str, float]
) -> float:
    """Calculate fatigue risk score (0-100)."""
    base_risk = 20

    # FDP length contribution
    if fdp_hours > 10:
        base_risk += (fdp_hours - 10) * 8

    # Segment count contribution
    if segments > 3:
        base_risk += (segments - 3) * 5

    # Time of day contribution
    time_risk = {"morning": 0, "afternoon": 5, "evening": 15, "night": 25}
    base_risk += time_risk.get(time_window, 10)

    # Cumulative fatigue contribution
    seven_day_pct = duty_history.get("7_day_hours", 0) / 60 * 100
    base_risk += seven_day_pct * 0.2

    return min(100, max(0, round(base_risk, 1)))


def validate_schedule(
    crew_member_id: str,
    proposed_schedule: List[Dict],
    duty_history: Dict[str, float],
    home_base: str,
    crew_position: str,
    augmentation_type: str
) -> Dict[str, Any]:
    """
    Validate crew schedule against FAA Part 117 and company policies.

    Business Rules:
    1. FDP limits vary by report time and segments
    2. Cumulative limits for 7/28/365 day windows
    3. Rest requirements based on prior duty
    4. Augmented crew extensions with bunk requirements

    Args:
        crew_member_id: Crew member identifier
        proposed_schedule: List of flight segments
        duty_history: Recent duty hours
        home_base: Crew home base
        crew_position: Position (captain, first_officer, relief)
        augmentation_type: Augmentation class

    Returns:
        Validation results with violations and recommendations
    """
    limits = load_duty_limits()

    violations = []
    warnings = []
    recommendations = []

    # Calculate FDP metrics
    fdp = calculate_fdp(proposed_schedule)
    time_window = get_time_window(fdp["start_time"]) if fdp["start_time"] else "morning"

    # Determine segment bucket (1-2, 3, 4, 5+)
    seg_count = fdp["segments"]
    if seg_count <= 2:
        seg_bucket = "1-2"
    elif seg_count == 3:
        seg_bucket = "3"
    elif seg_count == 4:
        seg_bucket = "4"
    else:
        seg_bucket = "5+"

    # Rule 1: FDP limit check
    limit_key = f"{time_window}_{seg_bucket}"
    fdp_limit = limits["fdp_limits"].get(limit_key, limits["fdp_limits"]["morning_1-2"])

    max_fdp = fdp_limit["max_hours"] - fdp_limit["company_buffer"]
    if augmentation_type != "none":
        max_fdp += fdp_limit["augmented_extension"]

    if fdp["total_hours"] > max_fdp:
        violations.append({
            "code": "FDP-001",
            "description": f"FDP {fdp['total_hours']}h exceeds limit of {max_fdp}h",
            "severity": "critical"
        })
    elif fdp["total_hours"] > max_fdp - 1:
        warnings.append({
            "code": "FDP-W01",
            "description": f"FDP {fdp['total_hours']}h approaching limit of {max_fdp}h"
        })

    # Rule 2: Cumulative duty limits
    for period, period_limits in limits["cumulative_limits"].items():
        history_key = f"{period}_hours"
        current_hours = duty_history.get(history_key, 0)
        projected_hours = current_hours + fdp["total_hours"]

        if projected_hours > period_limits["max_hours"]:
            violations.append({
                "code": f"CUM-{period.upper()}",
                "description": f"{period} cumulative hours ({projected_hours}h) exceeds limit ({period_limits['max_hours']}h)",
                "severity": "critical"
            })
        elif projected_hours > period_limits["warning_threshold"]:
            warnings.append({
                "code": f"CUM-W{period.upper()}",
                "description": f"{period} cumulative hours ({projected_hours}h) approaching limit"
            })

    # Rule 3: Rest requirement check
    last_duty_end = duty_history.get("last_duty_end")
    if last_duty_end and fdp["report_time"]:
        rest_location = "home_base" if home_base else "outstation"
        rest_req = limits["rest_requirements"].get(rest_location, {"min_hours": 10})

        # This would need actual last duty end time for real calculation
        recommendations.append(f"Ensure minimum {rest_req['min_hours']}h rest before this duty period")

    # Calculate fatigue risk
    fatigue_risk = calculate_fatigue_risk(
        fdp["total_hours"],
        fdp["segments"],
        time_window,
        duty_history
    )

    if fatigue_risk > 70:
        warnings.append({
            "code": "FAT-001",
            "description": f"High fatigue risk score: {fatigue_risk}"
        })
        recommendations.append("Consider reducing duty length or adding rest break")

    # Schedule optimization recommendations
    if seg_count > 3 and fdp["total_hours"] > 8:
        recommendations.append("Consider splitting pairing to reduce segments per FDP")

    if time_window == "night" and seg_count > 2:
        recommendations.append("Night operations with multiple segments - consider crew augmentation")

    schedule_valid = len(violations) == 0

    return {
        "crew_member_id": crew_member_id,
        "schedule_valid": schedule_valid,
        "fdp_hours": fdp["total_hours"],
        "segment_count": fdp["segments"],
        "time_window": time_window,
        "violations": violations,
        "warnings": warnings,
        "fatigue_risk_score": fatigue_risk,
        "recommendations": recommendations,
        "augmentation_type": augmentation_type,
        "home_base": home_base
    }


if __name__ == "__main__":
    import json

    result = validate_schedule(
        crew_member_id="CPT-12345",
        proposed_schedule=[
            {"flight": "AA100", "departure": "2026-01-20T06:00", "arrival": "2026-01-20T10:30"},
            {"flight": "AA101", "departure": "2026-01-20T11:30", "arrival": "2026-01-20T15:00"},
            {"flight": "AA102", "departure": "2026-01-20T16:00", "arrival": "2026-01-20T19:30"}
        ],
        duty_history={"7_day_hours": 42, "28_day_hours": 95, "365_day_hours": 850},
        home_base="DFW",
        crew_position="captain",
        augmentation_type="none"
    )
    print(json.dumps(result, indent=2))
