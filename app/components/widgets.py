"""Reusable Streamlit UI components."""

import plotly.graph_objects as go
import streamlit as st

__all__ = [
    "render_score_gauge",
    "pillar_bar_chart",
    "source_fetch_progress",
    "render_data_pull_summary",
    "render_score_drivers",
    "driver_impact_chart",
]


def render_score_gauge(score: float, grade: str) -> None:
    color = "#22C55E" if score >= 650 else "#EAB308" if score >= 550 else "#EF4444"
    fig = go.Figure(
        go.Indicator(
            mode="gauge+number",
            value=score,
            number={"suffix": " / 900", "font": {"size": 42}},
            title={"text": f"Grade: {grade}", "font": {"size": 20}},
            gauge={
                "axis": {"range": [300, 900], "tickwidth": 1},
                "bar": {"color": color},
                "steps": [
                    {"range": [300, 550], "color": "#FEE2E2"},
                    {"range": [550, 650], "color": "#FEF9C3"},
                    {"range": [650, 750], "color": "#DCFCE7"},
                    {"range": [750, 900], "color": "#BBF7D0"},
                ],
                "threshold": {
                    "line": {"color": "#1E3A5F", "width": 3},
                    "thickness": 0.8,
                    "value": score,
                },
            },
        )
    )
    fig.update_layout(height=320, margin=dict(t=60, b=20, l=30, r=30))
    st.plotly_chart(fig, use_container_width=True)


def pillar_bar_chart(pillars: dict) -> None:
    names = [k.title() for k in pillars]
    values = [pillars[k]["score"] for k in pillars]
    fig = go.Figure(go.Bar(x=names, y=values, marker_color="#1E3A5F", text=[f"{v:.0f}" for v in values], textposition="outside"))
    fig.update_layout(title="Pillar Scores (0–100)", yaxis_range=[0, 105], height=350, margin=dict(t=50))
    st.plotly_chart(fig, use_container_width=True)


def source_fetch_progress(sources: list[str]) -> None:
    import time

    progress = st.progress(0)
    status = st.empty()
    for i, source in enumerate(sources):
        status.info(f"Fetching {source.upper()} data via consent framework...")
        time.sleep(0.6)
        progress.progress((i + 1) / len(sources))
    status.success("All data sources connected successfully.")


def render_data_pull_summary(summaries: list[dict]) -> None:
    st.markdown("#### Data Pulled — Source Summary")
    cols = st.columns(2)
    for i, s in enumerate(summaries):
        with cols[i % 2]:
            status_icon = {"healthy": "🟢", "warning": "🟡", "risk": "🔴", "neutral": "⚪"}.get(s["status"], "⚪")
            with st.container(border=True):
                st.markdown(f"**{s['icon']} {s['source']}** {status_icon}")
                st.caption(f"{s['records']} · {s['headline']}")
                for h in s["highlights"]:
                    st.markdown(f"- {h}")


def render_score_drivers(boosters: list[dict], draggers: list[dict]) -> None:
    c1, c2 = st.columns(2)

    with c1:
        st.markdown("#### What's Pulling the Score **Up**")
        if boosters:
            for d in boosters:
                st.success(f"**+{d['score_points']} pts** — {d['factor']}  \n_{d['value']}_ · {d['pillar'].title()} pillar")
        else:
            st.info("No strong positive drivers identified.")

    with c2:
        st.markdown("#### What's Pulling the Score **Down**")
        if draggers:
            for d in draggers:
                st.error(f"**{d['score_points']} pts** — {d['factor']}  \n_{d['value']}_ · {d['pillar'].title()} pillar")
        else:
            st.info("No significant negative drivers — clean profile.")


def driver_impact_chart(boosters: list[dict], draggers: list[dict]) -> None:
    rows = boosters[:5] + draggers[:5]
    if not rows:
        return
    labels = [d["factor"][:28] for d in rows]
    values = [d["score_points"] for d in rows]
    colors = ["#22C55E" if v > 0 else "#EF4444" for v in values]
    fig = go.Figure(go.Bar(x=values, y=labels, orientation="h", marker_color=colors, text=[f"{v:+.0f}" for v in values], textposition="outside"))
    fig.update_layout(
        title="Top Score Drivers (points on 300–900 scale)",
        xaxis_title="Approx. score impact",
        height=max(280, len(rows) * 45),
        margin=dict(l=10, r=10, t=40),
    )
    st.plotly_chart(fig, use_container_width=True)
