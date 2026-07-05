# FinHealth Card

AI/ML-driven **Financial Health Card** for MSME credit assessment using alternative data.

## Features

- **10 alternative data connectors**: GST, UPI, Account Aggregator, EPFO, Google Reviews (NLP sentiment), Promoter Bureau, Court Cases, Electricity, Macro/Sector, Investment
- **Hybrid scoring**: Rule-based explainability + LightGBM calibration
- **5-pillar breakdown**: Revenue, Liquidity, Risk, Context, Reputation
- **4 demo personas**: Healthy manufacturer, retail kirana, distressed trader, agri dealer
- **Loan simulation** with eligibility and pricing
- **Streamlit dashboard** — deployable to Streamlit Community Cloud (free)

## Quick Start

```bash
# Install dependencies
pip install -r requirements.txt

# Generate synthetic data (75 MSME profiles)
python scripts/generate_data.py

# Train ML model
python scripts/train_model.py

# Run the app
streamlit run app/main.py
```

## Deploy (Free)

1. Push this repo to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect repo, set main file: `app/main.py`
4. Deploy — no credit card required

## Demo Flow

1. Open **Demo Gallery** → pick a persona
2. View **Health Card** with score gauge (300–900)
3. Explore **Score Breakdown** for explainability
4. Check **Data Insights** charts per source
5. Run **Loan Simulation**

## Architecture

```
Streamlit UI → Connectors (mock) → Feature Engineering → Rule Engine + LightGBM → Health Score
```

## Project Structure

```
app/           Streamlit UI
src/connectors Mock data fetchers
src/features   Feature engineering
src/scoring    Rules, ML model, loan sim
data/synthetic Generated MSME profiles
scripts/       Data generation & training
```
