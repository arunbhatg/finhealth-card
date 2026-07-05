"""Streamlit views for FinHealth Card."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from app.components.widgets import pillar_bar_chart, render_score_gauge, source_fetch_progress
from src.connectors.base import load_profile
from src.connectors.data_summary import build_data_pull_summary
from src.connectors.sources import ALL_CONNECTORS, fetch_all_sources
from src.features.feature_engineering import extract_features
from src.scoring.explainability import build_score_narrative, extract_score_drivers
from src.scoring.loan_simulator import simulate_loan
from src.scoring.model import compute_final_score
from src.utils.constants import DEMO_PERSONAS, MACRO_INDICATORS
from src.utils.helpers import score_to_grade


def build_score_result(
    features: dict,
    profile: dict | None = None,
    sources: list[str] | None = None,
) -> dict:
    """Build score result in app layer to avoid stale module-cache issues."""
    result = compute_final_score(features)

    if "boosters" not in result:
        drivers = extract_score_drivers(result["pillars"])
        result["boosters"] = drivers["boosters"]
        result["draggers"] = drivers["draggers"]
        result["narrative"] = build_score_narrative(
            result["final_score"],
            drivers["boosters"],
            drivers["draggers"],
        )

    if profile is not None:
        result["data_summary"] = build_data_pull_summary(profile, sources)

    return result


def render_data_pull_summary(summaries: list[dict]) -> None:
    st.markdown("#### Data Pulled — Source Summary")
    cols = st.columns(2)
    for i, summary in enumerate(summaries):
        with cols[i % 2]:
            status_icon = {"healthy": "🟢", "warning": "🟡", "risk": "🔴", "neutral": "⚪"}.get(
                summary["status"],
                "⚪",
            )
            with st.container(border=True):
                st.markdown(f"**{summary['icon']} {summary['source']}** {status_icon}")
                st.caption(f"{summary['records']} · {summary['headline']}")
                for highlight in summary["highlights"]:
                    st.markdown(f"- {highlight}")


def render_score_drivers(boosters: list[dict], draggers: list[dict]) -> None:
    col_up, col_down = st.columns(2)

    with col_up:
        st.markdown("#### What's Pulling the Score **Up**")
        if boosters:
            for driver in boosters:
                st.success(
                    f"**+{driver['score_points']} pts** — {driver['factor']}  \n"
                    f"_{driver['value']}_ · {driver['pillar'].title()} pillar"
                )
        else:
            st.info("No strong positive drivers identified.")

    with col_down:
        st.markdown("#### What's Pulling the Score **Down**")
        if draggers:
            for driver in draggers:
                st.error(
                    f"**{driver['score_points']} pts** — {driver['factor']}  \n"
                    f"_{driver['value']}_ · {driver['pillar'].title()} pillar"
                )
        else:
            st.info("No significant negative drivers — clean profile.")


def driver_impact_chart(boosters: list[dict], draggers: list[dict]) -> None:
    rows = boosters[:5] + draggers[:5]
    if not rows:
        return

    labels = [driver["factor"][:28] for driver in rows]
    values = [driver["score_points"] for driver in rows]
    colors = ["#22C55E" if value > 0 else "#EF4444" for value in values]
    fig = go.Figure(
        go.Bar(
            x=values,
            y=labels,
            orientation="h",
            marker_color=colors,
            text=[f"{value:+.0f}" for value in values],
            textposition="outside",
        )
    )
    fig.update_layout(
        title="Top Score Drivers (points on 300–900 scale)",
        xaxis_title="Approx. score impact",
        height=max(280, len(rows) * 45),
        margin=dict(l=10, r=10, t=40),
    )
    st.plotly_chart(fig, use_container_width=True)


PAGES = [
    "Home",
    "Onboarding",
    "Consent & Fetch",
    "Health Card",
    "Score Breakdown",
    "Data Insights",
    "Loan Simulation",
    "Demo Gallery",
]


def init_session():
    defaults = {
        "page": "Home",
        "msme_id": None,
        "profile": None,
        "features": None,
        "score_result": None,
        "consent_sources": [],
        "fetched": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def sidebar_nav():
    st.sidebar.title("FinHealth Card")
    st.sidebar.caption("Alternative-data MSME underwriting")
    page = st.sidebar.radio("Navigate", PAGES, index=PAGES.index(st.session_state.page))
    st.session_state.page = page
    if st.session_state.msme_id:
        st.sidebar.divider()
        st.sidebar.markdown(f"**Active MSME:** {st.session_state.msme_id}")
        if st.session_state.profile:
            st.sidebar.markdown(st.session_state.profile.get("business_name", ""))


def page_home():
    st.title("FinHealth Card")
    st.subheader("Credit visibility for the credit-invisible")
    st.markdown(
        """
        Many MSMEs are rejected for loans despite being financially healthy — they simply lack
        traditional financial documents. **FinHealth Card** assesses MSME creditworthiness using
        **18+ alternative data signals** across:

        - GST compliance & turnover
        - UPI transaction patterns
        - Account Aggregator bank data
        - EPFO payroll signals
        - Google Business sentiment (NLP)
        - Promoter bureau & litigation
        - Electricity consumption
        - Sector macro & weather overlays
        """
    )
    col1, col2, col3 = st.columns(3)
    col1.metric("Data Sources", "10+", "connectors")
    col2.metric("Score Range", "300–900", "CIBIL-like")
    col3.metric("Time to Score", "< 5 sec", "near real-time")

    st.info("Start with **Demo Gallery** for instant results, or **Onboarding** for a full walkthrough.")
    if st.button("Go to Demo Gallery", type="primary"):
        st.session_state.page = "Demo Gallery"
        st.rerun()


def page_onboarding():
    st.title("MSME Onboarding")
    st.markdown("Enter business details to begin alternative-data assessment.")

    master_path = ROOT / "data" / "synthetic" / "msme_master.csv"
    if master_path.exists():
        master = pd.read_csv(master_path)
    else:
        st.warning("Synthetic data not generated yet. Run `python scripts/generate_data.py` first.")
        return

    with st.form("onboard_form"):
        c1, c2 = st.columns(2)
        with c1:
            business_name = st.text_input("Business Name", "Sharma Precision Works")
            pan = st.text_input("PAN", "AABCS1234D")
            sector = st.selectbox("Sector", master["sector"].unique())
        with c2:
            gstin = st.text_input("GSTIN", "27AABCU9603R1ZM")
            city = st.text_input("City", "Pune")
            state = st.selectbox("State", master["state"].unique())

        submitted = st.form_submit_button("Continue to Consent", type="primary")

    if submitted:
        match = master[
            (master["sector"] == sector) & (master["state"] == state)
        ]
        msme_id = match.iloc[0]["msme_id"] if not match.empty else "MSME001"
        st.session_state.msme_id = msme_id
        st.session_state.profile = load_profile(msme_id)
        st.session_state.page = "Consent & Fetch"
        st.session_state.fetched = False
        st.rerun()


def page_consent():
    st.title("Consent & Data Connect")
    if not st.session_state.msme_id:
        st.warning("Complete onboarding first.")
        return

    profile = st.session_state.profile or load_profile(st.session_state.msme_id)
    st.markdown(f"**{profile['business_name']}** — grant consent to fetch alternative data.")

    sources = {
        "gst": "GST Returns (GSTR-1/3B)",
        "upi": "UPI Merchant Transactions",
        "aa": "Account Aggregator — Bank Statements",
        "epfo": "EPFO Establishment Data",
        "google": "Google Business Profile & Reviews",
        "bureau": "Promoter Credit Bureau",
        "courts": "Court Cases & Litigation",
        "electricity": "Electricity Consumption (Discom)",
        "macro": "Sector Macro Indicators",
        "investment": "R&D / CapEx / Investment",
    }

    selected = []
    cols = st.columns(2)
    for i, (key, label) in enumerate(sources.items()):
        with cols[i % 2]:
            if st.checkbox(label, value=True, key=f"consent_{key}"):
                selected.append(key)

    st.session_state.consent_sources = selected

    if st.button("Connect & Fetch Data", type="primary"):
        source_fetch_progress(selected)
        fetch_all_sources(st.session_state.msme_id, selected)
        features = extract_features(profile)
        score_result = build_score_result(features, profile=profile, sources=selected)
        st.session_state.features = features
        st.session_state.score_result = score_result
        st.session_state.fetched = True
        st.session_state.page = "Health Card"
        st.rerun()


def page_health_card():
    st.title("Financial Health Card")
    if not st.session_state.fetched or not st.session_state.score_result:
        st.warning("Fetch data first via Consent & Fetch.")
        return

    profile = st.session_state.profile
    result = st.session_state.score_result
    score = result["final_score"]
    grade = score_to_grade(score)

    st.markdown(f"### {profile['business_name']}")
    st.caption(f"{profile['sector']} · {profile['city']}, {profile['state']} · GSTIN: {profile['gstin']}")

    c1, c2 = st.columns([1, 1])
    with c1:
        render_score_gauge(score, grade)
    with c2:
        st.markdown("#### Assessment Summary")
        st.metric("Final Score", int(score), delta=result["blend_note"])
        st.metric("Rule Score", int(result["rule_score"]))
        if result["ml_score"]:
            st.metric("ML Calibrated Score", int(result["ml_score"]))
        st.success(f"**{grade}** — {'Eligible for unsecured MSME loan' if score >= 550 else 'Requires further review'}")

    st.markdown("---")
    st.markdown("#### Before vs After Alternative Data")
    b1, b2 = st.columns(2)
    with b1:
        st.error("Traditional Credit: **Rejected** — No audited financials, no bureau track record")
    with b2:
        st.success(f"Alt-Data Score: **{int(score)}** — Creditworthy based on digital footprint")

    if result.get("narrative"):
        st.info(result["narrative"])

    if result.get("data_summary"):
        st.markdown("---")
        render_data_pull_summary(result["data_summary"])

    if result.get("boosters") or result.get("draggers"):
        st.markdown("---")
        driver_impact_chart(result.get("boosters", []), result.get("draggers", []))
        render_score_drivers(result.get("boosters", []), result.get("draggers", []))


def page_breakdown():
    st.title("Score Breakdown")
    if not st.session_state.score_result:
        st.warning("No score available.")
        return

    result = st.session_state.score_result
    pillars = result["pillars"]

    st.markdown(result.get("narrative", ""))
    st.markdown("---")

    if result.get("boosters") or result.get("draggers"):
        driver_impact_chart(result.get("boosters", []), result.get("draggers", []))
        render_score_drivers(result.get("boosters", []), result.get("draggers", []))
        st.markdown("---")

    pillar_bar_chart(pillars)

    if result.get("data_summary"):
        render_data_pull_summary(result["data_summary"])
        st.markdown("---")

    st.markdown("#### Detailed Pillar Drivers")
    for pillar, data in pillars.items():
        with st.expander(f"{pillar.title()} — {data['score']:.0f}/100", expanded=pillar == "revenue"):
            for d in data["drivers"]:
                impact = d["impact"]
                color = "normal" if impact >= 50 else "inverse"
                st.metric(d["factor"], d["value"], delta=f"{impact:.0f} pts", delta_color=color)


def page_insights():
    st.title("Data Insights")
    if not st.session_state.msme_id:
        st.warning("No MSME selected.")
        return

    profile = load_profile(st.session_state.msme_id)
    tabs = st.tabs(["GST", "UPI", "Bank (AA)", "EPFO", "Google", "Electricity", "Macro"])

    with tabs[0]:
        gst = profile["gst"]
        df = pd.DataFrame({"Turnover (₹L)": gst["monthly_turnover_lakhs"]})
        st.plotly_chart(px.line(df, markers=True, title="Monthly GST Turnover"), use_container_width=True)
        st.write(f"Filing compliance issues: **{gst['payment_delays_count']}** delays")

    with tabs[1]:
        upi = profile["upi"]
        df = pd.DataFrame({"Volume (₹L)": upi["monthly_volume_lakhs"]})
        st.plotly_chart(px.bar(df, title="Monthly UPI Volume"), use_container_width=True)

    with tabs[2]:
        aa = profile["aa"]
        df = pd.DataFrame({"Credits": aa["monthly_credits_lakhs"], "Debits": aa["monthly_debits_lakhs"]})
        st.plotly_chart(px.line(df, markers=True, title="Monthly Cash Flow"), use_container_width=True)
        st.metric("ABB (3M avg)", f"₹{aa['abb_lakhs']}L")

    with tabs[3]:
        epfo = profile["epfo"]
        df = pd.DataFrame({"Employees": epfo["employee_count"], "Wage Bill (₹L)": epfo["monthly_wage_bill_lakhs"]})
        st.plotly_chart(px.line(df, markers=True, title="Payroll Trends"), use_container_width=True)

    with tabs[4]:
        google = profile["google"]
        st.metric("Google Rating", f"{google['rating']} ★", f"{google['review_count']} reviews")
        for r in google["reviews"][:5]:
            st.markdown(f"- **{r['rating']}★** ({r['sentiment']}): _{r['text']}_")

    with tabs[5]:
        elec = profile["electricity"]
        df = pd.DataFrame({"kWh": elec["monthly_kwh"]})
        st.plotly_chart(px.area(df, title="Electricity Consumption"), use_container_width=True)

    with tabs[6]:
        macro = profile["macro"]
        c1, c2, c3 = st.columns(3)
        c1.metric("Repo Rate", f"{MACRO_INDICATORS['repo_rate']}%")
        c2.metric("Sector Growth", f"{macro.get('sector_growth_pct', 'N/A')}%")
        c3.metric("Monsoon Index", f"{macro.get('monsoon_index_pct', 100)}%")


def page_loan_sim():
    st.title("Loan Simulation")
    if not st.session_state.score_result:
        st.warning("Complete assessment first.")
        return

    score = st.session_state.score_result["final_score"]
    turnover = st.session_state.features["gst_avg_monthly_turnover"]
    amount = st.slider("Requested Loan Amount (₹ Lakhs)", 5, 50, 15)

    result = simulate_loan(score, amount, turnover)

    if result["eligible"]:
        st.success(f"Eligible — Approved up to ₹{result['approved_lakhs']}L")
    else:
        st.error(result["reason"])

    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Grade", result["grade"])
    c2.metric("Approved", f"₹{result.get('approved_lakhs', 0)}L")
    c3.metric("Interest Rate", f"{result.get('interest_rate_pct', 'N/A')}%")
    c4.metric("Tenure", f"{result.get('tenure_months', 'N/A')} months")


def page_demo_gallery():
    st.title("Demo Gallery")
    st.markdown("Explore pre-built MSME personas showcasing different financial health profiles.")

    cols = st.columns(2)
    for i, (msme_id, meta) in enumerate(DEMO_PERSONAS.items()):
        with cols[i % 2]:
            st.markdown(f"### {meta['name']}")
            st.caption(meta["story"])
            st.write(f"{meta['sector']} · {meta['city']}, {meta['state']}")
            if st.button(f"Assess {msme_id}", key=f"demo_{msme_id}"):
                profile = load_profile(msme_id)
                features = extract_features(profile)
                score_result = build_score_result(
                    features,
                    profile=profile,
                    sources=list(ALL_CONNECTORS.keys()),
                )
                st.session_state.msme_id = msme_id
                st.session_state.profile = profile
                st.session_state.features = features
                st.session_state.score_result = score_result
                st.session_state.fetched = True
                st.session_state.page = "Health Card"
                st.rerun()


def run_app():
    st.set_page_config(page_title="FinHealth Card", page_icon="📊", layout="wide")

    with st.spinner("Initializing FinHealth Card..."):
        from src.bootstrap import ensure_ready

        ensure_ready()

    init_session()
    sidebar_nav()

    pages = {
        "Home": page_home,
        "Onboarding": page_onboarding,
        "Consent & Fetch": page_consent,
        "Health Card": page_health_card,
        "Score Breakdown": page_breakdown,
        "Data Insights": page_insights,
        "Loan Simulation": page_loan_sim,
        "Demo Gallery": page_demo_gallery,
    }
    pages[st.session_state.page]()


run_app()
