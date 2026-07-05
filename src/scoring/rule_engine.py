"""Rule-based pillar scoring for explainability."""

from __future__ import annotations

from src.utils.helpers import clamp


def _scale(value: float, lo: float, hi: float) -> float:
    if hi == lo:
        return 50.0
    return clamp((value - lo) / (hi - lo) * 100, 0, 100)


def score_revenue(f: dict) -> tuple[float, list[dict]]:
    signals = [
        ("GST turnover growth", _scale(f["gst_turnover_yoy_growth"], -10, 25), f"{f['gst_turnover_yoy_growth']:.1f}%"),
        ("GST filing compliance", f["gst_filing_compliance"] * 100, f"{f['gst_filing_compliance']*100:.0f}%"),
        ("UPI volume growth", _scale(f["upi_volume_yoy_growth"], -10, 30), f"{f['upi_volume_yoy_growth']:.1f}%"),
        ("Electricity consumption trend", _scale(f["electricity_kwh_yoy"], -15, 20), f"{f['electricity_kwh_yoy']:.1f}%"),
    ]
    score = sum(s[1] for s in signals) / len(signals)
    drivers = [{"factor": s[0], "impact": s[1], "value": s[2]} for s in signals]
    return score, drivers


def score_liquidity(f: dict) -> tuple[float, list[dict]]:
    signals = [
        ("Average bank balance (ABB)", _scale(f["aa_abb_lakhs"], 0, 20), f"₹{f['aa_abb_lakhs']:.1f}L"),
        ("EMI on-time rate", f["aa_emi_on_time_rate"] * 100, f"{f['aa_emi_on_time_rate']*100:.0f}%"),
        ("Cashflow surplus ratio", _scale(f["aa_cashflow_surplus_ratio"], -0.2, 0.3), f"{f['aa_cashflow_surplus_ratio']:.2f}"),
        ("EPFO contribution compliance", f["epfo_contribution_compliance"] * 100, f"{f['epfo_contribution_compliance']*100:.0f}%"),
    ]
    score = sum(s[1] for s in signals) / len(signals)
    penalties = f["aa_bounce_count"] * 8 + f["gst_payment_delays"] * 3
    score = clamp(score - penalties, 0, 100)
    drivers = [{"factor": s[0], "impact": s[1], "value": s[2]} for s in signals]
    if penalties:
        drivers.append({"factor": "Payment bounce / GST delay penalty", "impact": -penalties, "value": f"-{penalties:.0f} pts"})
    return score, drivers


def score_risk(f: dict) -> tuple[float, list[dict]]:
    bureau_pts = _scale(f["promoter_cibil"], 550, 850)
    court_penalty = (
        f["court_civil_cases"] * 12
        + f["court_criminal_cases"] * 20
        + f["court_insolvency"] * 30
    )
    signals = [
        ("Promoter CIBIL score", bureau_pts, str(int(f["promoter_cibil"]))),
        ("Credit utilization (inverse)", 100 - f["promoter_credit_utilization"] * 100, f"{f['promoter_credit_utilization']*100:.0f}%"),
        ("DPD last 12 months (inverse)", clamp(100 - f["promoter_dpd_12m"] * 25, 0, 100), str(f["promoter_dpd_12m"])),
    ]
    score = sum(s[1] for s in signals) / len(signals) - court_penalty
    score = clamp(score, 0, 100)
    drivers = [{"factor": s[0], "impact": s[1], "value": s[2]} for s in signals]
    if court_penalty:
        drivers.append({"factor": "Litigation penalty", "impact": -court_penalty, "value": f"{f['court_civil_cases']} civil cases"})
    return score, drivers


def score_context(f: dict) -> tuple[float, list[dict]]:
    sector_pts = _scale(f["sector_growth_pct"], -5, 12)
    monsoon_pts = _scale(f["monsoon_index_pct"], 80, 120)
    signals = [
        ("Sector growth outlook", sector_pts, f"{f['sector_growth_pct']:.1f}%"),
        ("Monsoon / regional index", monsoon_pts, f"{f['monsoon_index_pct']:.1f}%"),
        ("Govt scheme beneficiary", 80 if f["govt_scheme"] else 40, "Yes" if f["govt_scheme"] else "No"),
    ]
    score = sum(s[1] for s in signals) / len(signals)
    drivers = [{"factor": s[0], "impact": s[1], "value": s[2]} for s in signals]
    return score, drivers


def score_reputation(f: dict) -> tuple[float, list[dict]]:
    signals = [
        ("Google rating", _scale(f["google_rating"], 2.5, 5.0), f"{f['google_rating']:.1f} ★"),
        ("Review sentiment (NLP)", f["google_sentiment_score"] * 100, f"{f['google_sentiment_score']*100:.0f}%"),
        ("Review velocity (6m)", _scale(f["google_review_velocity_6m"], 0, 20), str(int(f["google_review_velocity_6m"]))),
        ("Owner response rate", f["google_response_rate"] * 100, f"{f['google_response_rate']*100:.0f}%"),
    ]
    score = sum(s[1] for s in signals) / len(signals)
    drivers = [{"factor": s[0], "impact": s[1], "value": s[2]} for s in signals]
    return score, drivers


def compute_rule_score(features: dict) -> dict:
    from src.utils.constants import PILLAR_WEIGHTS, SCORE_MAX, SCORE_MIN

    pillars = {
        "revenue": score_revenue(features),
        "liquidity": score_liquidity(features),
        "risk": score_risk(features),
        "context": score_context(features),
        "reputation": score_reputation(features),
    }

    weighted = sum(pillars[k][0] * PILLAR_WEIGHTS[k] for k in pillars)
    final = SCORE_MIN + (weighted / 100) * (SCORE_MAX - SCORE_MIN)

    return {
        "rule_score": round(final, 0),
        "pillars": {
            k: {"score": round(v[0], 1), "drivers": v[1]} for k, v in pillars.items()
        },
    }
