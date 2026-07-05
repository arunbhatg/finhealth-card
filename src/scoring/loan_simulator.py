"""Loan simulation based on financial health score."""

from __future__ import annotations

from src.utils.helpers import score_to_grade


def simulate_loan(score: float, requested_lakhs: float, avg_turnover_lakhs: float) -> dict:
    grade = score_to_grade(score)

    if score < 500:
        return {
            "eligible": False,
            "grade": grade,
            "requested_lakhs": requested_lakhs,
            "approved_lakhs": 0,
            "interest_rate_pct": None,
            "tenure_months": None,
            "reason": "Score below minimum threshold (500). Recommend secured product or 6-month data rebuild.",
        }

    multiplier = {750: 0.5, 650: 0.35, 550: 0.2, 0: 0.1}
    for threshold, mult in sorted(multiplier.items(), reverse=True):
        if score >= threshold:
            max_limit = avg_turnover_lakhs * mult * 12
            break

    approved = min(requested_lakhs, max_limit)
    rate_map = {750: 11.5, 650: 13.5, 550: 16.0, 0: 18.5}
    for threshold, rate in sorted(rate_map.items(), reverse=True):
        if score >= threshold:
            interest = rate
            break

    tenure = 36 if score >= 650 else 24

    return {
        "eligible": approved >= requested_lakhs * 0.5,
        "grade": grade,
        "requested_lakhs": requested_lakhs,
        "approved_lakhs": round(approved, 2),
        "max_eligible_lakhs": round(max_limit, 2),
        "interest_rate_pct": interest,
        "tenure_months": tenure,
        "reason": f"Approved based on {grade} rating and turnover-backed limit.",
    }
