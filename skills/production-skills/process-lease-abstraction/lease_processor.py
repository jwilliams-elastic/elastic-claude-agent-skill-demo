"""
Lease Abstraction Processing Module

Implements commercial lease abstraction including
term extraction, obligation tracking, and compliance analysis.
"""

import csv
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta



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


def load_lease_terms() -> Dict[str, Any]:
    """Load configuration data from CSV files."""
    rent_escalation_types_data = load_csv_as_dict("rent_escalation_types.csv")
    lease_types_data = load_csv_as_dict("lease_types.csv")
    critical_dates_data = load_csv_as_dict("critical_dates.csv")
    compliance_requirements_data = load_csv_as_dict("compliance_requirements.csv")
    market_benchmarks_data = load_csv_as_dict("market_benchmarks.csv")
    risk_factors_data = load_csv_as_dict("risk_factors.csv")
    params = load_parameters()
    return {
        "rent_escalation_types": rent_escalation_types_data,
        "lease_types": lease_types_data,
        "critical_dates": critical_dates_data,
        "compliance_requirements": compliance_requirements_data,
        "market_benchmarks": market_benchmarks_data,
        "risk_factors": risk_factors_data,
        **params
    }


def extract_financial_terms(
    lease_data: Dict
) -> Dict[str, Any]:
    """Extract financial terms from lease."""
    financial = {}

    # Base rent
    base_rent = lease_data.get("base_rent_monthly", 0)
    sqft = lease_data.get("rentable_sqft", 1)
    rent_psf = (base_rent * 12) / sqft if sqft > 0 else 0

    financial["base_rent"] = {
        "monthly": base_rent,
        "annual": base_rent * 12,
        "per_sqft_annual": round(rent_psf, 2)
    }

    # Rent escalation
    escalation_type = lease_data.get("escalation_type", "fixed")
    escalation_rate = lease_data.get("escalation_rate", 0.03)
    financial["escalation"] = {
        "type": escalation_type,
        "rate": escalation_rate,
        "frequency": lease_data.get("escalation_frequency", "annual")
    }

    # Additional rent
    cam = lease_data.get("cam_monthly", 0)
    taxes = lease_data.get("taxes_monthly", 0)
    insurance = lease_data.get("insurance_monthly", 0)

    financial["additional_rent"] = {
        "cam": {"monthly": cam, "annual": cam * 12},
        "taxes": {"monthly": taxes, "annual": taxes * 12},
        "insurance": {"monthly": insurance, "annual": insurance * 12},
        "total_monthly": cam + taxes + insurance,
        "total_annual": (cam + taxes + insurance) * 12
    }

    # Total occupancy cost
    total_monthly = base_rent + cam + taxes + insurance
    financial["total_occupancy_cost"] = {
        "monthly": round(total_monthly, 2),
        "annual": round(total_monthly * 12, 2),
        "per_sqft_annual": round((total_monthly * 12) / sqft, 2) if sqft > 0 else 0
    }

    # Security deposit
    financial["security_deposit"] = lease_data.get("security_deposit", 0)

    return financial


def extract_term_dates(
    lease_data: Dict
) -> Dict[str, Any]:
    """Extract lease term and critical dates."""
    commencement = lease_data.get("commencement_date", "")
    expiration = lease_data.get("expiration_date", "")

    term_info = {
        "commencement_date": commencement,
        "expiration_date": expiration,
        "rent_commencement_date": lease_data.get("rent_commencement_date", commencement)
    }

    # Calculate term length
    if commencement and expiration:
        try:
            start = datetime.strptime(commencement, "%Y-%m-%d")
            end = datetime.strptime(expiration, "%Y-%m-%d")
            term_days = (end - start).days
            term_months = term_days / 30.44
            term_years = term_days / 365.25

            term_info["term_length"] = {
                "days": term_days,
                "months": round(term_months, 1),
                "years": round(term_years, 1)
            }
        except ValueError:
            term_info["term_length"] = {"error": "Invalid date format"}

    # Renewal options
    renewal_options = lease_data.get("renewal_options", [])
    term_info["renewal_options"] = renewal_options
    term_info["total_renewal_term_years"] = sum(r.get("term_years", 0) for r in renewal_options)

    # Early termination
    term_info["early_termination"] = {
        "allowed": lease_data.get("early_termination_allowed", False),
        "notice_days": lease_data.get("termination_notice_days", 0),
        "penalty": lease_data.get("termination_penalty", 0)
    }

    return term_info


def calculate_critical_dates(
    lease_dates: Dict,
    critical_date_config: Dict
) -> List[Dict]:
    """Calculate critical dates for lease management."""
    critical_dates = []
    current_date = datetime.now()

    expiration = lease_dates.get("expiration_date", "")
    if expiration:
        try:
            exp_date = datetime.strptime(expiration, "%Y-%m-%d")

            # Renewal notice deadline
            renewal_options = lease_dates.get("renewal_options", [])
            if renewal_options:
                notice_days = critical_date_config.get("renewal_option", {}).get("notice_days", 180)
                renewal_deadline = exp_date - timedelta(days=notice_days)
                critical_dates.append({
                    "date": renewal_deadline.strftime("%Y-%m-%d"),
                    "event": "Renewal Option Exercise Deadline",
                    "action": "Exercise or decline renewal option",
                    "days_from_today": (renewal_deadline - current_date).days
                })

            # Termination notice deadline
            if lease_dates.get("early_termination", {}).get("allowed"):
                term_notice = lease_dates.get("early_termination", {}).get("notice_days", 365)
                term_deadline = exp_date - timedelta(days=term_notice)
                critical_dates.append({
                    "date": term_deadline.strftime("%Y-%m-%d"),
                    "event": "Early Termination Notice Deadline",
                    "action": "Provide termination notice if applicable",
                    "days_from_today": (term_deadline - current_date).days
                })

            # Lease expiration
            critical_dates.append({
                "date": expiration,
                "event": "Lease Expiration",
                "action": "Vacate or commence renewal term",
                "days_from_today": (exp_date - current_date).days
            })

        except ValueError:
            pass

    # Sort by date
    critical_dates.sort(key=lambda x: x.get("days_from_today", 0))

    return critical_dates


def classify_lease_type(
    lease_data: Dict,
    lease_types: Dict
) -> Dict[str, Any]:
    """Classify lease type based on expense responsibilities."""
    tenant_pays = []
    landlord_pays = []

    if lease_data.get("tenant_pays_taxes"):
        tenant_pays.append("taxes")
    else:
        landlord_pays.append("taxes")

    if lease_data.get("tenant_pays_insurance"):
        tenant_pays.append("insurance")
    else:
        landlord_pays.append("insurance")

    if lease_data.get("tenant_pays_maintenance"):
        tenant_pays.append("maintenance")
    else:
        landlord_pays.append("maintenance")

    # Determine lease type
    if len(tenant_pays) == 0:
        lease_type = "gross"
    elif len(tenant_pays) == 1:
        lease_type = "modified_gross"
    elif len(tenant_pays) >= 3:
        if lease_data.get("tenant_pays_structural"):
            lease_type = "absolute_net"
        else:
            lease_type = "triple_net"
    else:
        lease_type = "modified_gross"

    return {
        "lease_type": lease_type,
        "tenant_responsibilities": tenant_pays,
        "landlord_responsibilities": landlord_pays,
        "type_description": lease_types.get(lease_type, {})
    }


def extract_operational_terms(
    lease_data: Dict
) -> Dict[str, Any]:
    """Extract operational provisions."""
    return {
        "permitted_use": lease_data.get("permitted_use", ""),
        "exclusive_use": lease_data.get("exclusive_use", None),
        "prohibited_uses": lease_data.get("prohibited_uses", []),
        "operating_hours": lease_data.get("operating_hours", ""),
        "signage": {
            "allowed": lease_data.get("signage_allowed", False),
            "specifications": lease_data.get("signage_specs", "")
        },
        "parking": {
            "spaces": lease_data.get("parking_spaces", 0),
            "ratio": lease_data.get("parking_ratio", ""),
            "reserved": lease_data.get("reserved_parking", 0)
        },
        "alterations": {
            "landlord_approval_required": lease_data.get("alterations_require_approval", True),
            "removal_required": lease_data.get("alterations_removal_required", False)
        }
    }


def compare_to_market(
    financial_terms: Dict,
    property_type: str,
    benchmarks: Dict
) -> Dict[str, Any]:
    """Compare lease terms to market benchmarks."""
    market = benchmarks.get(property_type, benchmarks.get("office", {}))

    rent_psf = financial_terms.get("base_rent", {}).get("per_sqft_annual", 0)
    market_rent = market.get("rent_psf", 0)
    rent_variance = (rent_psf / market_rent - 1) * 100 if market_rent > 0 else 0

    cam_psf = financial_terms.get("additional_rent", {}).get("cam", {}).get("annual", 0) / financial_terms.get("base_rent", {}).get("per_sqft_annual", 1) if financial_terms.get("base_rent", {}).get("per_sqft_annual", 0) > 0 else 0
    market_cam = market.get("cam_psf", 0)

    escalation = financial_terms.get("escalation", {}).get("rate", 0)
    market_escalation = market.get("escalation_pct", 0.03)

    return {
        "property_type": property_type,
        "rent_comparison": {
            "lease_rent_psf": rent_psf,
            "market_rent_psf": market_rent,
            "variance_pct": round(rent_variance, 1),
            "assessment": "above_market" if rent_variance > 10 else "at_market" if rent_variance > -10 else "below_market"
        },
        "escalation_comparison": {
            "lease_rate": escalation,
            "market_rate": market_escalation,
            "assessment": "favorable" if escalation <= market_escalation else "unfavorable"
        }
    }


def assess_risks(
    lease_data: Dict,
    financial_terms: Dict,
    term_dates: Dict,
    risk_factors: Dict
) -> List[Dict]:
    """Assess lease risks."""
    risks = []

    # Above market rent
    # Would need market comparison data

    # Short termination notice
    term_notice = term_dates.get("early_termination", {}).get("notice_days", 0)
    if term_notice > 0 and term_notice < risk_factors.get("short_notice_termination", {}).get("threshold", 90):
        risks.append({
            "risk": "Short termination notice period",
            "severity": risk_factors.get("short_notice_termination", {}).get("severity", "high"),
            "details": f"{term_notice} days notice required",
            "mitigation": "Negotiate longer notice period"
        })

    # No renewal option
    if not term_dates.get("renewal_options"):
        risks.append({
            "risk": "No renewal option",
            "severity": risk_factors.get("no_renewal_option", {}).get("severity", "low"),
            "details": "Lease has no renewal provisions",
            "mitigation": "Negotiate renewal option before expiration"
        })

    # Percentage rent exposure
    if lease_data.get("percentage_rent_rate", 0) > risk_factors.get("percentage_rent_exposure", {}).get("threshold", 0.05):
        risks.append({
            "risk": "High percentage rent exposure",
            "severity": risk_factors.get("percentage_rent_exposure", {}).get("severity", "medium"),
            "details": f"{lease_data.get('percentage_rent_rate', 0) * 100}% of sales above breakpoint",
            "mitigation": "Monitor sales performance relative to breakpoint"
        })

    return risks


def process_lease_abstraction(
    lease_id: str,
    property_name: str,
    property_type: str,
    lease_data: Dict,
    processing_date: str
) -> Dict[str, Any]:
    """
    Process lease abstraction.

    Business Rules:
    1. Extract key financial terms
    2. Calculate critical dates
    3. Classify lease type
    4. Assess risks and market comparison

    Args:
        lease_id: Lease identifier
        property_name: Property name
        property_type: Type of property
        lease_data: Raw lease data
        processing_date: Processing date

    Returns:
        Lease abstraction results
    """
    config = load_lease_terms()

    # Extract financial terms
    financial = extract_financial_terms(lease_data)

    # Extract term dates
    term_dates = extract_term_dates(lease_data)

    # Calculate critical dates
    critical_dates = calculate_critical_dates(
        term_dates,
        config.get("critical_dates", {})
    )

    # Classify lease type
    lease_classification = classify_lease_type(
        lease_data,
        config.get("lease_types", {})
    )

    # Extract operational terms
    operational = extract_operational_terms(lease_data)

    # Market comparison
    market_comparison = compare_to_market(
        financial,
        property_type,
        config.get("market_benchmarks", {})
    )

    # Risk assessment
    risks = assess_risks(
        lease_data,
        financial,
        term_dates,
        config.get("risk_factors", {})
    )

    return {
        "lease_id": lease_id,
        "property_name": property_name,
        "property_type": property_type,
        "processing_date": processing_date,
        "financial_terms": financial,
        "term_summary": term_dates,
        "critical_dates": critical_dates,
        "lease_classification": lease_classification,
        "operational_terms": operational,
        "market_comparison": market_comparison,
        "risk_assessment": {
            "risk_count": len(risks),
            "risks": risks
        },
        "abstract_status": "COMPLETE"
    }


if __name__ == "__main__":
    import json
    result = process_lease_abstraction(
        lease_id="LEASE-001",
        property_name="Corporate HQ - Building A",
        property_type="office",
        lease_data={
            "base_rent_monthly": 45000,
            "rentable_sqft": 12000,
            "cam_monthly": 8000,
            "taxes_monthly": 3500,
            "insurance_monthly": 1500,
            "commencement_date": "2024-01-01",
            "expiration_date": "2029-12-31",
            "rent_commencement_date": "2024-03-01",
            "escalation_type": "fixed",
            "escalation_rate": 0.03,
            "escalation_frequency": "annual",
            "security_deposit": 90000,
            "renewal_options": [
                {"term_years": 5, "notice_days": 180, "rent_adjustment": "market"}
            ],
            "early_termination_allowed": True,
            "termination_notice_days": 365,
            "termination_penalty": 270000,
            "tenant_pays_taxes": True,
            "tenant_pays_insurance": True,
            "tenant_pays_maintenance": True,
            "permitted_use": "General office use",
            "signage_allowed": True,
            "parking_spaces": 48,
            "parking_ratio": "4:1000"
        },
        processing_date="2026-01-20"
    )
    print(json.dumps(result, indent=2))
