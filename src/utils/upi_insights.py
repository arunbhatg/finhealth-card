"""UPI merchant insights for underwriter UI."""

from __future__ import annotations

from src.utils.helpers import avg_recent


def _avg_ticket(upi: dict) -> float:
    ticket = upi.get("avg_ticket_size", 0)
    if isinstance(ticket, list):
        return avg_recent(ticket, min(3, len(ticket)))
    return float(ticket)


def upi_insight_metrics(profile: dict, features: dict) -> list[dict]:
    upi = profile["upi"]
    return [
        {"label": "P2M share", "value": f"{upi['p2m_ratio'] * 100:.0f}%"},
        {"label": "6M avg volume", "value": f"₹{features['upi_avg_monthly_volume']:.1f}L"},
        {"label": "Volume YoY", "value": f"{features['upi_volume_yoy_growth']:+.1f}%"},
        {"label": "Failed txn rate", "value": f"{upi['failed_txn_rate'] * 100:.2f}%"},
        {"label": "Avg ticket", "value": f"₹{_avg_ticket(upi):,.0f}"},
    ]


def upi_momentum(volume: list[float]) -> str:
    if len(volume) < 3:
        return "Stable"
    recent = sum(volume[-3:]) / 3
    prior = sum(volume[-6:-3]) / 3 if len(volume) >= 6 else volume[0]
    if prior <= 0:
        return "Stable"
    change = (recent - prior) / prior * 100
    if change > 5:
        return f"Accelerating (+{change:.0f}% vs prior quarter)"
    if change < -5:
        return f"Slowing ({change:.0f}% vs prior quarter)"
    return "Stable"
