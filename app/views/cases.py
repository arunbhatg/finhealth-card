"""Demo case selection — entry point for underwriters."""

import streamlit as st

from app.components.underwriter import render_demo_card
from app.views._helpers import assess_msme, load_case
from src.connectors.base import load_profile
from src.features.feature_engineering import extract_features
from src.scoring.model import compute_final_score
from src.scoring.summary_data import borrower_identity_table, score_summary_table
from src.scoring.underwriter_insights import get_demo_preview
from src.utils.constants import DEMO_PERSONAS


def page_select_case():
    st.title("Select MSME Case")
    st.caption("Choose a demo borrower — click **Preview actuals** for identity & score values.")

    st.markdown(
        """
        | Case | What it demonstrates |
        |------|---------------------|
        | **MSME001** | Manufacturer approved on GST + payroll + promoter quality |
        | **MSME002** | Retail kirana — strong UPI + customer sentiment |
        | **MSME003** | Trader declined — compliance, litigation, weak bureau |
        | **MSME004** | Agri dealer — sector/macro overlay |
        """
    )

    cols = st.columns(2)
    for i, (msme_id, meta) in enumerate(DEMO_PERSONAS.items()):
        profile = load_profile(msme_id)
        features = extract_features(profile)
        score = compute_final_score(features)["final_score"]
        preview = get_demo_preview(msme_id, features, profile, score)

        with cols[i % 2]:
            if render_demo_card(preview, meta, f"case_{msme_id}"):
                load_case(msme_id)
                st.session_state.page = "② Credit Decision"
                st.rerun()
            with st.popover("Preview actuals"):
                bundle = assess_msme(msme_id, profile)
                st.dataframe(borrower_identity_table(profile), use_container_width=True, hide_index=True)
                st.dataframe(score_summary_table(bundle["score_result"]), use_container_width=True, hide_index=True)

    st.divider()
    st.caption("Tip: Compare MSME001 (approve) vs MSME003 (decline).")
