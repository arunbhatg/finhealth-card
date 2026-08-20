"""Finn. brand assets, IDBI Bank co-branding, and Finndot app link."""

from __future__ import annotations

import base64
from pathlib import Path

import streamlit as st

FINNDOT_PLAY_URL = "https://play.google.com/store/apps/details?id=com.anomapro.finndot.prd"

FINN_BLACK = "#1A1A1A"
FINN_GREEN = "#22C55E"

_ROOT = Path(__file__).resolve().parents[2]
ASSETS_DIR = _ROOT / "assets"
IDBI_LOGO_PNG = ASSETS_DIR / "idbi-bank.png"
IDBI_LOGO_SVG = ASSETS_DIR / "idbi-bank.svg"

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
    for candidate in (IDBI_LOGO_PNG, Path.cwd() / "assets" / "idbi-bank.png", IDBI_LOGO_SVG):
        if candidate.exists():
            return candidate
    return None


def _idbi_data_uri() -> str | None:
    path = _idbi_logo_path()
    if path is None:
        return None
    mime = "image/png" if path.suffix.lower() == ".png" else "image/svg+xml"
    b64 = base64.b64encode(path.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def partner_logos_html(*, height_px: int = 36) -> str:
    uri = _idbi_data_uri()
    idbi = (
        f'<img src="{uri}" alt="IDBI Bank" '
        f'style="height:{height_px}px;width:auto;max-width:220px;display:block;'
        f'border-radius:4px;object-fit:contain;" />'
        if uri
        else '<span style="font-weight:700;color:#00836c;font-size:1.05rem;">IDBI BANK</span>'
    )
    return (
        '<div style="display:flex;align-items:center;gap:12px;flex-wrap:wrap;'
        'margin:0 0 0.4rem 0;">'
        f"{idbi}"
        '<span style="width:1px;height:28px;background:#CBD5E1;display:inline-block;"></span>'
        f"{finn_logo_html('medium')}"
        "</div>"
    )


def render_sidebar_branding() -> None:
    st.sidebar.markdown(partner_logos_html(height_px=30), unsafe_allow_html=True)
    st.sidebar.caption("FinHealth Card · IDBI × Finn.")


def render_app_header() -> None:
    """Main content hero — partner logos + product title above page navigation."""
    st.markdown(
        f"""
        {partner_logos_html(height_px=42)}
        <div class="finn-app-header">
            <div class="finn-app-title">{APP_TITLE_HTML}</div>
            <div class="finn-app-tagline">{APP_TAGLINE}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_page_header_branding() -> None:
    """Compact logo row for main content area (optional)."""
    st.markdown(partner_logos_html(height_px=28), unsafe_allow_html=True)


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
