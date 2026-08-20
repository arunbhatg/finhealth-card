"""Finn. brand assets, IDBI Bank co-branding, and Finndot app link."""

from __future__ import annotations

from pathlib import Path

import streamlit as st
from PIL import Image

FINNDOT_PLAY_URL = "https://play.google.com/store/apps/details?id=com.anomapro.finndot.prd"

FINN_BLACK = "#1A1A1A"
FINN_GREEN = "#22C55E"

_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = _ROOT / "assets"
IDBI_LOGO_PNG = ASSETS_DIR / "idbi-bank.png"

# Inline mark — inherits surrounding text color; period is always green.
FINN_DOT_HTML = f'Finn<span style="color:{FINN_GREEN}">.</span>'
FINN_SCORE_LABEL_HTML = f"{FINN_DOT_HTML} Alternative Score"
APP_TITLE_HTML = f"{FINN_DOT_HTML} Alternative Score System"
APP_TAGLINE = "NTC MSME underwriting · IDBI Bank × Finndot alternative data"


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


def _idbi_logo_path() -> Path | None:
    for candidate in (
        IDBI_LOGO_PNG,
        Path.cwd() / "assets" / "idbi-bank.png",
        Path("/mount/src/finhealth-card/assets/idbi-bank.png"),
    ):
        if candidate.exists():
            return candidate
    return None


def _idbi_image() -> Image.Image | None:
    path = _idbi_logo_path()
    if path is None:
        return None
    return Image.open(path).convert("RGB")


def _render_partner_row(*, idbi_width: int, finn_size: str) -> None:
    img = _idbi_image()
    left, mid, right = st.columns([2.4, 0.12, 1.1])
    with left:
        if img is not None:
            st.image(img, width=idbi_width, caption="IDBI Bank")
        else:
            st.markdown("**IDBI BANK**")
    with mid:
        st.markdown(
            '<div style="border-left:1px solid #CBD5E1;height:32px;margin-top:8px;"></div>',
            unsafe_allow_html=True,
        )
    with right:
        st.markdown(finn_logo_html(finn_size), unsafe_allow_html=True)


def render_sidebar_branding() -> None:
    img = _idbi_image()
    if img is not None:
        st.sidebar.image(img, width=180, caption="IDBI Bank")
    else:
        st.sidebar.markdown("**IDBI BANK**")
    st.sidebar.markdown(finn_logo_html("small"), unsafe_allow_html=True)
    st.sidebar.caption("FinHealth Card · IDBI × Finn.")


def render_app_header() -> None:
    """Main content hero — partner logos + product title above page navigation."""
    _render_partner_row(idbi_width=210, finn_size="medium")
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
    _render_partner_row(idbi_width=160, finn_size="small")


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
