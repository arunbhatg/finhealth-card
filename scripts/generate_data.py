"""Generate synthetic MSME profiles for all alternative data sources."""

from __future__ import annotations

import json
import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

import numpy as np
import pandas as pd
from faker import Faker

from src.utils.constants import DEMO_PERSONAS, PROFILES_DIR, SYNTHETIC_DIR
from src.utils.helpers import generate_gstin, generate_pan

fake = Faker("en_IN")
SECTORS = list(
    {
        "Manufacturing",
        "Retail",
        "Services",
        "Agri-Input",
        "Textiles",
        "Pharma",
        "Food Processing",
        "Logistics",
    }
)
STATES = {
    "Maharashtra": "27",
    "Gujarat": "24",
    "Karnataka": "29",
    "Delhi": "07",
    "Tamil Nadu": "33",
    "Rajasthan": "08",
}


def _trend(base: float, months: int, growth: float, noise: float, rng: random.Random) -> list[float]:
    values = []
    current = base
    for i in range(months):
        drift = 1 + (growth / 100 / 12)
        current = max(0, current * drift + rng.uniform(-noise, noise))
        values.append(round(current, 2))
    return values


def _status_series(
    months: int,
    compliance: float,
    rng: random.Random,
    good: str = "filed",
    bad: tuple[str, ...] = ("delayed", "missed"),
) -> list[str]:
    statuses = []
    for _ in range(months):
        statuses.append(good if rng.random() < compliance else rng.choice(bad))
    return statuses


def _review_text(sentiment: str, rng: random.Random) -> str:
    positive = [
        "Excellent quality products and timely delivery.",
        "Very professional team, highly recommended.",
        "Great service, fair pricing.",
        "Reliable supplier for our business needs.",
        "Consistently good experience over the years.",
    ]
    negative = [
        "Delayed delivery and poor communication.",
        "Payment issues and unresponsive staff.",
        "Quality has declined recently.",
        "Refund process was very slow.",
        "Would not recommend due to service gaps.",
    ]
    neutral = [
        "Average experience, nothing exceptional.",
        "Decent products at market rates.",
        "Standard service for the sector.",
    ]
    pool = {"positive": positive, "negative": negative, "neutral": neutral}[sentiment]
    return rng.choice(pool)


def build_profile(
    msme_id: str,
    persona: str,
    sector: str,
    state: str,
    city: str,
    business_name: str,
    rng: random.Random,
) -> dict:
    state_code = STATES.get(state, "27")
    gstin = generate_gstin(state_code, rng)
    pan = generate_pan(rng)

    if persona == "healthy_manufacturer":
        turnover_growth, compliance, emp_stability = 15, 0.98, 0.95
        bureau_score, court_cases = rng.randint(760, 820), 0
        review_sentiment, electricity_growth = "positive", 12
        monsoon_index = rng.uniform(98, 110)
    elif persona == "healthy_retail":
        turnover_growth, compliance, emp_stability = 18, 0.96, 0.92
        bureau_score, court_cases = rng.randint(740, 800), 0
        review_sentiment, electricity_growth = "positive", 5
        monsoon_index = rng.uniform(95, 105)
    elif persona == "distressed":
        turnover_growth, compliance, emp_stability = -8, 0.55, 0.6
        bureau_score, court_cases = rng.randint(580, 660), rng.randint(1, 3)
        review_sentiment, electricity_growth = "negative", -15
        monsoon_index = rng.uniform(85, 95)
    elif persona == "agri_favorable":
        turnover_growth, compliance, emp_stability = 10, 0.94, 0.9
        bureau_score, court_cases = rng.randint(720, 780), 0
        review_sentiment, electricity_growth = "positive", 6
        monsoon_index = rng.uniform(108, 118)
    else:
        turnover_growth = rng.uniform(-5, 20)
        compliance = rng.uniform(0.65, 0.99)
        emp_stability = rng.uniform(0.7, 0.98)
        bureau_score = int(rng.uniform(600, 820))
        court_cases = rng.choices([0, 0, 0, 1, 2], weights=[5, 5, 5, 3, 1])[0]
        review_sentiment = rng.choices(["positive", "neutral", "negative"], weights=[6, 3, 1])[0]
        electricity_growth = rng.uniform(-10, 15)
        monsoon_index = rng.uniform(85, 115)

    monthly_turnover = _trend(rng.uniform(8, 40), 24, turnover_growth, 1.5, rng)
    monthly_filings = _status_series(24, compliance, rng)
    monthly_upi_volume = _trend(rng.uniform(2, 25), 12, turnover_growth * 1.2, 0.8, rng)
    monthly_balance = _trend(rng.uniform(1, 15), 12, turnover_growth * 0.5, 0.5, rng)
    monthly_credits = _trend(rng.uniform(5, 30), 12, turnover_growth, 1.2, rng)
    monthly_debits = [round(c * rng.uniform(0.75, 0.95), 2) for c in monthly_credits]
    employee_count = _trend(rng.randint(5, 40), 12, turnover_growth * 0.3, 0.5, rng)
    employee_count = [max(1, int(x)) for x in employee_count]
    wage_bill = [round(c * rng.uniform(18000, 28000), 2) for c in employee_count]
    epfo_status = _status_series(12, emp_stability, rng, good="paid", bad=("delayed", "missed"))
    electricity_kwh = _trend(rng.uniform(500, 5000), 12, electricity_growth, 100, rng)

    num_reviews = rng.randint(12, 45)
    sentiment_weights = {
        "positive": [0.75, 0.2, 0.05],
        "neutral": [0.4, 0.45, 0.15],
        "negative": [0.15, 0.25, 0.6],
    }[review_sentiment]
    reviews = []
    for _ in range(num_reviews):
        s = rng.choices(["positive", "neutral", "negative"], weights=sentiment_weights)[0]
        reviews.append(
            {
                "rating": rng.choices([5, 4, 3, 2, 1], weights=[5, 3, 2, 1, 1] if s == "positive" else [1, 1, 2, 3, 5])[0],
                "text": _review_text(s, rng),
                "sentiment": s,
                "days_ago": rng.randint(1, 540),
            }
        )

    rnd_investment = round(rng.uniform(0, 5 if persona == "healthy_manufacturer" else 1.5), 2)
    customer_sectors = rng.sample(SECTORS, k=3)
    customer_mix = np.random.dirichlet(np.ones(3)).round(2).tolist()

    profile = {
        "msme_id": msme_id,
        "business_name": business_name,
        "pan": pan,
        "gstin": gstin,
        "sector": sector,
        "city": city,
        "state": state,
        "years_in_business": rng.randint(2, 18),
        "udyam_number": f"UDYAM-{state_code[:2]}-{rng.randint(1000000, 9999999)}",
        "persona": persona,
        "gst": {
            "registration_date": fake.date_between(start_date="-10y", end_date="-1y").isoformat(),
            "business_type": sector,
            "monthly_turnover_lakhs": monthly_turnover,
            "filing_status": monthly_filings,
            "b2b_sales_ratio": round(rng.uniform(0.3, 0.9), 2),
            "payment_delays_count": sum(1 for s in monthly_filings if s != "filed"),
            "primary_customer_sectors": dict(zip(customer_sectors, customer_mix)),
        },
        "upi": {
            "vpa": f"{business_name.split()[0].lower()}@{rng.choice(['okaxis', 'paytm', 'ybl'])}",
            "monthly_txn_count": [int(v / rng.uniform(200, 800)) for v in monthly_upi_volume],
            "monthly_volume_lakhs": monthly_upi_volume,
            "avg_ticket_size": [round(v / max(1, int(v / 500)), 2) for v in monthly_upi_volume],
            "p2m_ratio": round(rng.uniform(0.55, 0.95), 2),
            "failed_txn_rate": round(rng.uniform(0.005, 0.05 if persona == "distressed" else 0.02), 3),
        },
        "aa": {
            "consent_id": f"AA-CONSENT-{msme_id}",
            "accounts": [{"bank": rng.choice(["HDFC", "ICICI", "SBI", "Axis"]), "type": "current"}],
            "monthly_closing_balance_lakhs": monthly_balance,
            "monthly_credits_lakhs": monthly_credits,
            "monthly_debits_lakhs": monthly_debits,
            "abb_lakhs": round(sum(monthly_balance[-3:]) / 3, 2),
            "emi_on_time_rate": round(rng.uniform(0.7, 0.99 if persona != "distressed" else 0.75), 2),
            "bounce_count_12m": 0 if persona != "distressed" else rng.randint(1, 4),
            "od_utilization": round(rng.uniform(0.1, 0.75 if persona == "distressed" else 0.4), 2),
        },
        "epfo": {
            "establishment_id": f"{state[:2].upper()}/{city[:3].upper()}/{rng.randint(100000, 999999)}",
            "employee_count": employee_count,
            "monthly_wage_bill_lakhs": wage_bill,
            "contribution_status": epfo_status,
            "new_joiners_12m": rng.randint(0, 8),
            "attrition_rate": round(rng.uniform(0.05, 0.25 if persona == "distressed" else 0.12), 2),
        },
        "google": {
            "place_id": f"ChIJ{msme_id}",
            "rating": round(rng.uniform(3.2, 4.8 if review_sentiment == "positive" else 3.8), 1),
            "review_count": num_reviews,
            "reviews": reviews,
            "response_rate": round(rng.uniform(0.4, 0.95), 2),
            "review_velocity_6m": sum(1 for r in reviews if r["days_ago"] <= 180),
        },
        "bureau": {
            "promoter_name": fake.name(),
            "cibil_score": bureau_score,
            "active_loans": rng.randint(0, 3),
            "dpd_12m": 0 if bureau_score > 700 else rng.randint(1, 3),
            "write_offs_36m": 1 if bureau_score < 650 else 0,
            "credit_utilization": round(rng.uniform(0.2, 0.85 if persona == "distressed" else 0.45), 2),
        },
        "courts": {
            "civil_cases": court_cases if court_cases else 0,
            "criminal_cases": 1 if persona == "distressed" and rng.random() > 0.5 else 0,
            "insolvency_petitions": 1 if persona == "distressed" and court_cases >= 2 else 0,
            "total_outstanding_litigation_lakhs": round(court_cases * rng.uniform(2, 15), 2),
        },
        "electricity": {
            "consumer_number": f"ELC{rng.randint(100000, 999999)}",
            "monthly_kwh": electricity_kwh,
            "tariff_category": "Industrial" if sector == "Manufacturing" else "Commercial",
            "payment_regularity": round(compliance, 2),
        },
        "macro": {
            "sector_growth_pct": None,
            "monsoon_index_pct": round(monsoon_index, 1),
            "region_tier": rng.choice(["Metro", "Tier-1", "Tier-2"]),
        },
        "investment": {
            "rnd_spend_lakhs_annual": rnd_investment,
            "capex_lakhs_12m": round(rng.uniform(0, 20 if persona == "healthy_manufacturer" else 5), 2),
            "patents_count": rng.randint(0, 3 if persona == "healthy_manufacturer" else 1),
            "govt_scheme_beneficiary": persona in {"healthy_manufacturer", "agri_favorable"},
        },
    }
    return profile


def generate_all(seed: int = 42, count: int = 75) -> None:
    rng = random.Random(seed)
    np.random.seed(seed)

    PROFILES_DIR.mkdir(parents=True, exist_ok=True)
    SYNTHETIC_DIR.mkdir(parents=True, exist_ok=True)

    master_rows = []
    persona_map = {
        "MSME001": ("healthy_manufacturer", "Manufacturing", "Maharashtra", "Pune"),
        "MSME002": ("healthy_retail", "Retail", "Gujarat", "Ahmedabad"),
        "MSME003": ("distressed", "Retail", "Delhi", "Delhi"),
        "MSME004": ("agri_favorable", "Agri-Input", "Maharashtra", "Nagpur"),
    }

    for i in range(count):
        msme_id = f"MSME{i+1:03d}"
        if msme_id in persona_map:
            persona, sector, state, city = persona_map[msme_id]
            business_name = DEMO_PERSONAS[msme_id]["name"]
        else:
            persona = "random"
            sector = rng.choice(list(SECTORS))
            state = rng.choice(list(STATES.keys()))
            city = fake.city()
            business_name = fake.company()

        profile = build_profile(msme_id, persona, sector, state, city, business_name, rng)
        path = PROFILES_DIR / f"{msme_id}.json"
        with open(path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)

        master_rows.append(
            {
                "msme_id": msme_id,
                "business_name": business_name,
                "pan": profile["pan"],
                "gstin": profile["gstin"],
                "sector": sector,
                "city": city,
                "state": state,
                "years_in_business": profile["years_in_business"],
                "persona": persona,
            }
        )

    pd.DataFrame(master_rows).to_csv(SYNTHETIC_DIR / "msme_master.csv", index=False)
    print(f"Generated {count} profiles in {PROFILES_DIR}")


if __name__ == "__main__":
    generate_all()
