"""Score explainability — top boosters and draggers with point contributions."""

from __future__ import annotations

from src.utils.constants import PILLAR_WEIGHTS, SCORE_MAX, SCORE_MIN

# Map driver factor labels to data source for UI grouping
FACTOR_SOURCE = {
    "GST": "gst",
    "UPI": "upi",
    "Average bank balance": "aa",
    "EMI": "aa",
    "Cashflow": "aa",
    "EPFO": "epfo",
    "Payment bounce": "aa",
    "Promoter CIBIL": "bureau",
    "Credit utilization": "bureau",
    "DPD": "bureau",
    "Litigation": "courts",
    "Sector growth": "macro",
    "Monsoon": "macro",
    "Govt scheme": "investment",
    "Google": "google",
    "Review": "google",
    "Owner response": "google",
    "Electricity": "electricity",
}


def _source_for_factor(factor: str) -> str:
    for prefix, source in FACTOR_SOURCE.items():
        if prefix.lower() in factor.lower():
            return source
    return "other"


def _impact_to_score_points(impact: float, pillar: str, n_drivers: int) -> float:
    """Convert a 0–100 driver impact to approximate score-point contribution."""
    scale = (SCORE_MAX - SCORE_MIN) / 100
    weight = PILLAR_WEIGHTS.get(pillar, 0.1)
    if impact < 0:
        return impact * weight * scale / max(n_drivers, 1)
    return (impact - 50) * weight * scale / max(n_drivers, 1)


def _skip_driver(d: dict) -> bool:
    """Skip non-informative drivers (e.g. zero DPD is expected, not a differentiator)."""
    if "DPD" in d["factor"] and str(d["value"]).strip() in {"0", "0.0"}:
        return True
    return False


def extract_score_drivers(pillars: dict) -> dict:
    """Flatten pillar drivers into ranked boosters and draggers."""
    all_drivers = []

    for pillar, data in pillars.items():
        drivers = data.get("drivers", [])
        n = len(drivers) or 1
        for d in drivers:
            impact = d["impact"]
            pts = _impact_to_score_points(impact, pillar, n)
            all_drivers.append(
                {
                    "factor": d["factor"],
                    "value": d["value"],
                    "pillar": pillar,
                    "source": _source_for_factor(d["factor"]),
                    "impact": impact,
                    "score_points": round(pts, 1),
                    "direction": "boost" if pts > 0 else "drag",
                }
            )

    boosters = sorted(
        [d for d in all_drivers if d["score_points"] > 5 and d["impact"] >= 58 and not _skip_driver(d)],
        key=lambda x: -x["score_points"],
    )
    draggers = sorted(
        [d for d in all_drivers if (d["score_points"] < -5 or d["impact"] < 42) and not _skip_driver(d)],
        key=lambda x: x["score_points"],
    )

    return {
        "boosters": boosters[:5],
        "draggers": draggers[:5],
        "all_drivers": all_drivers,
    }


def build_score_narrative(final_score: float, boosters: list[dict], draggers: list[dict]) -> str:
    if final_score >= 700:
        tone = "strong"
    elif final_score >= 550:
        tone = "moderate"
    else:
        tone = "weak"

    top_up = boosters[0]["factor"] if boosters else "consistent compliance"
    top_down = draggers[0]["factor"] if draggers else "no major negatives"

    if tone == "strong":
        return (
            f"Score is **{tone}** primarily driven by {top_up}. "
            f"Key watch item: {top_down}."
        )
    if tone == "weak":
        return (
            f"Score is **{tone}** — dragged down by {top_down}. "
            f"Partially offset by {top_up}."
        )
    return (
        f"Score is **{tone}** — uplift from {top_up}, "
        f"partially offset by {top_down}."
    )
