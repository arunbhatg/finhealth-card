"""Create minimal demo profiles without full dataset generation."""

from pathlib import Path

from src.utils.constants import PROFILES_DIR, SYNTHETIC_DIR


def _series(base: float, months: int, drift: float = 1.02) -> list[float]:
    vals = []
    v = base
    for _ in range(months):
        v *= drift
        vals.append(round(v, 2))
    return vals


def _demo_profile(
    msme_id: str,
    name: str,
    sector: str,
    city: str,
    state: str,
    persona: str,
    turnover_base: float,
    turnover_drift: float,
    compliance: float,
    bureau: int,
    court_cases: int,
    sentiment: str,
    rating: float,
    elec_drift: float,
    monsoon: float,
) -> dict:
    turnover = _series(turnover_base, 24, turnover_drift)
    upi_vol = _series(turnover_base * 0.6, 12, turnover_drift)
    balance = _series(turnover_base * 0.3, 12, 1.01)
    credits = _series(turnover_base * 0.9, 12, turnover_drift)
    debits = [round(c * 0.85, 2) for c in credits]
    employees = [max(5, int(x)) for x in _series(18, 12, 1.005)]
    wages = [round(e * 22000 / 100000, 2) for e in employees]
    kwh = _series(2000, 12, elec_drift)

    filing = ["filed" if compliance > 0.9 else "delayed" for _ in range(24)]
    epfo = ["paid" if compliance > 0.85 else "delayed" for _ in range(12)]

    reviews = {
        "positive": [
            {"rating": 5, "text": "Excellent quality and timely delivery.", "sentiment": "positive", "days_ago": 30},
            {"rating": 4, "text": "Reliable partner for our business.", "sentiment": "positive", "days_ago": 90},
        ],
        "negative": [
            {"rating": 2, "text": "Delayed delivery and poor communication.", "sentiment": "negative", "days_ago": 45},
            {"rating": 1, "text": "Quality has declined recently.", "sentiment": "negative", "days_ago": 120},
        ],
    }

    return {
        "msme_id": msme_id,
        "business_name": name,
        "pan": f"AAAC{msme_id[-3:]}1D",
        "gstin": f"27AAAC{msme_id[-3:]}1Z1",
        "sector": sector,
        "city": city,
        "state": state,
        "years_in_business": 8,
        "udyam_number": f"UDYAM-MH-{msme_id[-3:]}0001",
        "persona": persona,
        "gst": {
            "registration_date": "2018-04-12",
            "business_type": sector,
            "monthly_turnover_lakhs": turnover,
            "filing_status": filing,
            "b2b_sales_ratio": 0.72,
            "payment_delays_count": 0 if compliance > 0.9 else 5,
            "primary_customer_sectors": {"Manufacturing": 0.4, "Retail": 0.35, "Services": 0.25},
        },
        "upi": {
            "vpa": f"{name.split()[0].lower()}@okaxis",
            "monthly_txn_count": [int(v * 10) for v in upi_vol],
            "monthly_volume_lakhs": upi_vol,
            "avg_ticket_size": [450.0] * 12,
            "p2m_ratio": 0.82,
            "failed_txn_rate": 0.01 if compliance > 0.9 else 0.04,
        },
        "aa": {
            "consent_id": f"AA-CONSENT-{msme_id}",
            "accounts": [{"bank": "HDFC", "type": "current"}],
            "monthly_closing_balance_lakhs": balance,
            "monthly_credits_lakhs": credits,
            "monthly_debits_lakhs": debits,
            "abb_lakhs": round(sum(balance[-3:]) / 3, 2),
            "emi_on_time_rate": 0.98 if bureau > 700 else 0.78,
            "bounce_count_12m": 0 if bureau > 700 else 3,
            "od_utilization": 0.25 if bureau > 700 else 0.68,
        },
        "epfo": {
            "establishment_id": f"MH/{city[:3].upper()}/123456",
            "employee_count": employees,
            "monthly_wage_bill_lakhs": wages,
            "contribution_status": epfo,
            "new_joiners_12m": 3,
            "attrition_rate": 0.08 if compliance > 0.9 else 0.22,
        },
        "google": {
            "place_id": f"ChIJ{msme_id}",
            "rating": rating,
            "review_count": 28,
            "reviews": reviews[sentiment] * 5,
            "response_rate": 0.88 if sentiment == "positive" else 0.35,
            "review_velocity_6m": 12 if sentiment == "positive" else 3,
        },
        "bureau": {
            "promoter_name": "Rajesh Sharma",
            "cibil_score": bureau,
            "active_loans": 1,
            "dpd_12m": 0 if bureau > 700 else 2,
            "write_offs_36m": 0 if bureau > 650 else 1,
            "credit_utilization": 0.35 if bureau > 700 else 0.78,
        },
        "courts": {
            "civil_cases": court_cases,
            "criminal_cases": 1 if court_cases >= 2 else 0,
            "insolvency_petitions": 1 if court_cases >= 2 else 0,
            "total_outstanding_litigation_lakhs": court_cases * 8.5,
        },
        "electricity": {
            "consumer_number": f"ELC{msme_id[-3:]}",
            "monthly_kwh": kwh,
            "tariff_category": "Industrial" if sector == "Manufacturing" else "Commercial",
            "payment_regularity": compliance,
        },
        "macro": {"sector_growth_pct": None, "monsoon_index_pct": monsoon, "region_tier": "Tier-1"},
        "investment": {
            "rnd_spend_lakhs_annual": 3.5 if persona == "healthy_manufacturer" else 0.5,
            "capex_lakhs_12m": 12.0 if persona == "healthy_manufacturer" else 1.0,
            "patents_count": 2 if persona == "healthy_manufacturer" else 0,
            "govt_scheme_beneficiary": persona != "distressed",
        },
    }


def seed_demo_profiles() -> None:
    import json

    import pandas as pd

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

    demos = [
        ("MSME001", "Sharma Precision Works", "Manufacturing", "Pune", "Maharashtra", "healthy_manufacturer", 25, 1.012, 0.98, 785, 0, "positive", 4.6, 1.01, 108),
        ("MSME002", "Patel Kirana & General Store", "Retail", "Ahmedabad", "Gujarat", "healthy_retail", 12, 1.015, 0.96, 760, 0, "positive", 4.4, 1.005, 102),
        ("MSME003", "Gupta Trading Company", "Retail", "Delhi", "Delhi", "distressed", 18, 0.995, 0.58, 620, 3, "negative", 3.2, 0.985, 88),
        ("MSME004", "Krishi Mitra Agro Supplies", "Agri-Input", "Nagpur", "Maharashtra", "agri_favorable", 15, 1.008, 0.94, 745, 0, "positive", 4.3, 1.006, 115),
    ]

    rows = []
    for args in demos:
        profile = _demo_profile(*args)
        path = PROFILES_DIR / f"{args[0]}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)
        rows.append(
            {
                "msme_id": args[0],
                "business_name": args[1],
                "pan": profile["pan"],
                "gstin": profile["gstin"],
                "sector": args[2],
                "city": args[3],
                "state": args[4],
                "years_in_business": 8,
                "persona": args[5],
            }
        )

    pd.DataFrame(rows).to_csv(SYNTHETIC_DIR / "msme_master.csv", index=False)
