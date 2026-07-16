"""Streamlit entry — clean 3-step underwriter flow."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import streamlit as st

# Startup-safe copy — duplicated in src/utils/ui_text.py for other modules.
FINN_GREEN = "#22C55E"
FINN_DOT_HTML = f'Finn<span style="color:{FINN_GREEN}">.</span>'
APP_TITLE = "Finn. Alternative Score System"
APP_TITLE_HTML = f"{FINN_DOT_HTML} Alternative Score System"
APP_TAGLINE = "NTC MSME underwriting · powered by Finndot alternative data"
FINN_SCORE_LABEL = "Finn. Alternative Score"
FINN_SCORE_LABEL_HTML = f"{FINN_DOT_HTML} Alternative Score"

PAGE_ORDER = ("Cases", "Assessment", "Details")


def _run_page(name: str) -> None:
    if name == "Cases":
        from app.views.cases import page_cases

        page_cases()
    elif name == "Assessment":
        from app.views.assessment import page_assessment

        page_assessment()
    elif name == "Details":
        from app.views.details import page_details

        page_details()


def init_session():
    defaults = {
        "page": "Cases",
        "msme_id": None,
        "profile": None,
        "features": None,
        "score_result": None,
        "source_status": None,
        "fetched": False,
        "_bootstrapped": False,
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def bootstrap_once():
    if st.session_state._bootstrapped:
        return
    with st.spinner("Starting…"):
        from src.bootstrap import ensure_ready

        ensure_ready()
    st.session_state._bootstrapped = True


def _sidebar_branding() -> None:
    try:
        from app.components.branding import render_sidebar_branding

        render_sidebar_branding()
    except Exception:
        st.sidebar.markdown(
            f'<span style="font-weight:700;font-size:1.2rem">{FINN_DOT_HTML}</span>',
            unsafe_allow_html=True,
        )
        st.sidebar.caption("FinHealth Card")


def _sidebar_footer_link() -> None:
    try:
        from app.components.branding import render_sidebar_footer_link

        render_sidebar_footer_link()
    except Exception:
        st.sidebar.markdown("---")
        st.sidebar.caption("[Try Finndot AI app](https://play.google.com/store/apps/details?id=com.anomapro.finndot.prd)")


def sidebar():
    _sidebar_branding()

    if st.session_state.fetched and st.session_state.profile:
        p = st.session_state.profile
        score = int(st.session_state.score_result["final_score"]) if st.session_state.score_result else "—"
        st.sidebar.markdown(
            f"**{p['business_name'][:26]}**  \n"
            f"<span class='finn-muted'>{p['sector']} · {FINN_SCORE_LABEL_HTML}: {score}</span>",
            unsafe_allow_html=True,
        )
        if st.sidebar.button("Change case", width="stretch"):
            st.session_state.page = "Cases"
            st.rerun()
    else:
        st.sidebar.caption("Pick a case to begin")

    _sidebar_footer_link()


def top_nav():
    labels = list(PAGE_ORDER) if st.session_state.fetched and st.session_state.score_result else ["Cases"]

    idx = labels.index(st.session_state.page) if st.session_state.page in labels else 0
    st.markdown('<div class="finn-nav">', unsafe_allow_html=True)
    page = st.radio(
        "Navigate",
        labels,
        index=idx,
        horizontal=True,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    if page != st.session_state.page:
        st.session_state.page = page
        st.rerun()


def app_header():
    st.markdown(
        f"""
        <div class="finn-app-header">
            <div class="finn-app-title">{APP_TITLE_HTML}</div>
            <div class="finn-app-tagline">{APP_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _footer_branding() -> None:
    try:
        from app.components.branding import render_footer_branding

        render_footer_branding()
    except Exception:
        st.markdown(
            '<div style="margin-top:2rem;padding-top:1rem;border-top:1px solid #E2E8F0;'
            f'text-align:center;font-size:0.78rem;color:#94A3B8;">Powered by {FINN_DOT_HTML}</div>',
            unsafe_allow_html=True,
        )


def run_app():
    from app.components.styles import inject_styles

    st.set_page_config(
        page_title="FinHealth Card | Finn.",
        page_icon="🟢",
        layout="wide",
        initial_sidebar_state="expanded",
    )

    inject_styles()
    init_session()
    bootstrap_once()
    sidebar()
    app_header()
    top_nav()
    _run_page(st.session_state.page)
    _footer_branding()


run_app()
