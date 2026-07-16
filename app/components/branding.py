"""Finn. brand assets and Finndot app link."""

import streamlit as st

FINNDOT_PLAY_URL = "https://play.google.com/store/apps/details?id=com.anomapro.finndot.prd"

FINN_BLACK = "#1A1A1A"
FINN_GREEN = "#22C55E"

# Inline mark — inherits surrounding text color; period is always green.
FINN_DOT_HTML = f'Finn<span style="color:{FINN_GREEN}">.</span>'
FINN_SCORE_LABEL_HTML = f"{FINN_DOT_HTML} Alternative Score"
APP_TITLE_HTML = f"{FINN_DOT_HTML} Alternative Score System"
APP_TAGLINE = "NTC MSME underwriting · powered by Finndot alternative data"


def finn_logo_html(size: str = "medium") -> str:
    sizes = {"small": "1.25rem", "medium": "1.85rem", "large": "2.5rem"}
    font_size = sizes.get(size, "1.85rem")
    return (
        f'<span style="font-family: Segoe UI, system-ui, -apple-system, sans-serif; '
        f'font-weight: 700; font-size: {font_size}; letter-spacing: -0.03em; '
        f'line-height: 1.1; white-space: nowrap;">'
        f'<span style="color: {FINN_BLACK};">Finn</span>'
        f'<span style="color: {FINN_GREEN};">.</span>'
        f"</span>"
    )


def render_sidebar_branding() -> None:
    st.sidebar.markdown(finn_logo_html("medium"), unsafe_allow_html=True)
    st.sidebar.caption("FinHealth Card")


def render_app_header() -> None:
    """Main content hero — product title above page navigation."""
    st.markdown(
        f"""
        <div class="finn-app-header">
            <div class="finn-app-title">{APP_TITLE_HTML}</div>
            <div class="finn-app-tagline">{APP_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header_branding() -> None:
    """Compact logo row for main content area (optional)."""
    col_logo, col_spacer = st.columns([1, 4])
    with col_logo:
        st.markdown(finn_logo_html("small"), unsafe_allow_html=True)


def render_footer_branding() -> None:
    """Subtle footer — not prime placement; includes Finndot app link."""
    st.markdown(
        f"""
        <div style="margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #E2E8F0;
                    text-align: center; font-size: 0.78rem; color: #94A3B8;">
            Powered by {finn_logo_html("small")}
            &nbsp;·&nbsp;
            <a href="{FINNDOT_PLAY_URL}" target="_blank" rel="noopener noreferrer"
               style="color: #64748B; text-decoration: none;">
               try finndot ai app
            </a>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_sidebar_footer_link() -> None:
    """Very subtle link at bottom of sidebar."""
    st.sidebar.markdown("---")
    st.sidebar.caption(
        f"[Try Finndot AI app]({FINNDOT_PLAY_URL})"
    )
