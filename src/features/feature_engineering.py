"""Unified feature engineering from all alternative data sources."""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

from src.connectors.base import load_profile
from src.utils.constants import PROFILES_DIR, SECTOR_GROWTH
from src.utils.helpers import avg_recent, compliance_rate, yoy_growth


def _google_sentiment(reviews: list[dict]) -> float:
    if not reviews:
        return 0.5
    weights = {"positive": 1.0, "neutral": 0.5, "negative": 0.0}
    return sum(weights.get(r.get("sentiment", "neutral"), 0.5) for r in reviews) / len(reviews)


def extract_features(profile: dict) -> dict:
    gst = profile["gst"]
    upi = profile["upi"]
    aa = profile["aa"]
    epfo = profile["epfo"]
    google = profile["google"]
    bureau = profile["bureau"]
    courts = profile["courts"]
    electricity = profile["electricity"]
    macro = profile["macro"]
    investment = profile["investment"]

    turnover = gst["monthly_turnover_lakhs"]
    credits = aa["monthly_credits_lakhs"]
    debits = aa["monthly_debits_lakhs"]
    cashflow_surplus = [
        round(c - d, 2) for c, d in zip(credits, debits)
    ]

    features = {
        "msme_id": profile["msme_id"],
        "sector": profile["sector"],
        "years_in_business": profile["years_in_business"],
        # GST
        "gst_filing_compliance": compliance_rate(gst["filing_status"], {"filed"}),
        "gst_turnover_yoy_growth": yoy_growth(turnover),
        "gst_avg_monthly_turnover": avg_recent(turnover, 6),
        "gst_payment_delays": gst["payment_delays_count"],
        "gst_b2b_ratio": gst["b2b_sales_ratio"],
        # UPI
        "upi_volume_yoy_growth": yoy_growth(upi["monthly_volume_lakhs"]),
        "upi_avg_monthly_volume": avg_recent(upi["monthly_volume_lakhs"], 6),
        "upi_p2m_ratio": upi["p2m_ratio"],
        "upi_failed_txn_rate": upi["failed_txn_rate"],
        # AA
        "aa_abb_lakhs": aa["abb_lakhs"],
        "aa_emi_on_time_rate": aa["emi_on_time_rate"],
        "aa_bounce_count": aa["bounce_count_12m"],
        "aa_od_utilization": aa["od_utilization"],
        "aa_cashflow_surplus_ratio": (
            sum(cashflow_surplus[-6:]) / max(1, sum(credits[-6:]))
        ),
        "aa_balance_trend": yoy_growth(aa["monthly_closing_balance_lakhs"]),
        # EPFO
        "epfo_headcount": epfo["employee_count"][-1],
        "epfo_headcount_growth": yoy_growth([float(x) for x in epfo["employee_count"]]),
        "epfo_contribution_compliance": compliance_rate(epfo["contribution_status"], {"paid"}),
        "epfo_wage_bill_trend": yoy_growth(epfo["monthly_wage_bill_lakhs"]),
        "epfo_attrition_rate": epfo["attrition_rate"],
        # Google
        "google_rating": google["rating"],
        "google_sentiment_score": _google_sentiment(google["reviews"]),
        "google_review_velocity_6m": google["review_velocity_6m"],
        "google_response_rate": google["response_rate"],
        # Bureau
        "promoter_cibil": bureau["cibil_score"],
        "promoter_dpd_12m": bureau["dpd_12m"],
        "promoter_write_offs": bureau["write_offs_36m"],
        "promoter_credit_utilization": bureau["credit_utilization"],
        # Courts
        "court_civil_cases": courts["civil_cases"],
        "court_criminal_cases": courts["criminal_cases"],
        "court_insolvency": courts["insolvency_petitions"],
        "court_litigation_amount": courts["total_outstanding_litigation_lakhs"],
        # Electricity
        "electricity_kwh_yoy": yoy_growth(electricity["monthly_kwh"]),
        "electricity_avg_kwh": avg_recent(electricity["monthly_kwh"], 6),
        "electricity_payment_regularity": electricity["payment_regularity"],
        # Macro / context
        "sector_growth_pct": SECTOR_GROWTH.get(profile["sector"], 5.0),
        "monsoon_index_pct": macro.get("monsoon_index_pct", 100.0),
        # Investment
        "rnd_spend": investment["rnd_spend_lakhs_annual"],
        "capex_12m": investment["capex_lakhs_12m"],
        "patents_count": investment["patents_count"],
        "govt_scheme": int(investment["govt_scheme_beneficiary"]),
    }
    return features


def features_to_vector(features: dict, feature_cols: list[str]) -> np.ndarray:
    row = []
    for col in feature_cols:
        val = features.get(col, 0)
        if isinstance(val, str):
            val = hash(val) % 1000
        row.append(float(val))
    return np.array(row, dtype=float)


FEATURE_COLUMNS = [
    "years_in_business",
    "gst_filing_compliance",
    "gst_turnover_yoy_growth",
    "gst_avg_monthly_turnover",
    "gst_payment_delays",
    "gst_b2b_ratio",
    "upi_volume_yoy_growth",
    "upi_avg_monthly_volume",
    "upi_p2m_ratio",
    "upi_failed_txn_rate",
    "aa_abb_lakhs",
    "aa_emi_on_time_rate",
    "aa_bounce_count",
    "aa_od_utilization",
    "aa_cashflow_surplus_ratio",
    "aa_balance_trend",
    "epfo_headcount",
    "epfo_headcount_growth",
    "epfo_contribution_compliance",
    "epfo_wage_bill_trend",
    "epfo_attrition_rate",
    "google_rating",
    "google_sentiment_score",
    "google_review_velocity_6m",
    "google_response_rate",
    "promoter_cibil",
    "promoter_dpd_12m",
    "promoter_write_offs",
    "promoter_credit_utilization",
    "court_civil_cases",
    "court_criminal_cases",
    "court_insolvency",
    "court_litigation_amount",
    "electricity_kwh_yoy",
    "electricity_avg_kwh",
    "electricity_payment_regularity",
    "sector_growth_pct",
    "monsoon_index_pct",
    "rnd_spend",
    "capex_12m",
    "patents_count",
    "govt_scheme",
]


def build_feature_matrix(profile_dir: Path | None = None) -> pd.DataFrame:
    profile_dir = profile_dir or PROFILES_DIR
    rows = []
    for path in sorted(profile_dir.glob("*.json")):
        with open(path, encoding="utf-8") as f:
            profile = json.load(f)
        rows.append(extract_features(profile))
    return pd.DataFrame(rows)
