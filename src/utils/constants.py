"""Constants, sector data, and scoring weights."""

from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATA_DIR = PROJECT_ROOT / "data"
SYNTHETIC_DIR = DATA_DIR / "synthetic"
PROFILES_DIR = SYNTHETIC_DIR / "profiles"
MODELS_DIR = DATA_DIR / "models"

SCORE_MIN = 300
SCORE_MAX = 900

PILLAR_WEIGHTS = {
    "revenue": 0.30,
    "liquidity": 0.25,
    "risk": 0.25,
    "context": 0.10,
    "reputation": 0.10,
}

SOURCE_WEIGHTS = {
    "gst": 0.20,
    "upi": 0.12,
    "aa": 0.18,
    "epfo": 0.12,
    "google": 0.10,
    "bureau": 0.12,
    "courts": 0.08,
    "electricity": 0.08,
}

SECTOR_GROWTH = {
    "Manufacturing": 6.2,
    "Retail": 8.5,
    "Services": 7.1,
    "Agri-Input": 4.8,
    "Textiles": -1.5,
    "Pharma": 9.3,
    "Food Processing": 5.6,
    "Logistics": 7.8,
}

MACRO_INDICATORS = {
    "repo_rate": 6.50,
    "gdp_growth": 6.8,
    "manufacturing_pmi": 52.4,
    "inflation_cpi": 5.1,
    "msme_sentiment_index": 58.2,
}

GRADE_THRESHOLDS = [
    (750, "Excellent"),
    (650, "Good"),
    (550, "Fair"),
    (0, "Poor"),
]

FINN_SCORE_LABEL = "Finn. Alternative Score"

DEMO_PERSONAS = {
    "MSME001": {
        "name": "Sharma Precision Works",
        "story": "Healthy manufacturer — strong GST, stable payroll, excellent promoter credit",
        "sector": "Manufacturing",
        "city": "Pune",
        "state": "Maharashtra",
    },
    "MSME002": {
        "name": "Patel Kirana & General Store",
        "story": "Thriving retail — high UPI volume, glowing Google reviews",
        "sector": "Retail",
        "city": "Ahmedabad",
        "state": "Gujarat",
    },
    "MSME003": {
        "name": "Gupta Trading Company",
        "story": "Distressed trader — GST delays, litigation, weak promoter bureau",
        "sector": "Retail",
        "city": "Delhi",
        "state": "Delhi",
    },
    "MSME004": {
        "name": "Krishi Mitra Agro Supplies",
        "story": "Agri-input dealer — weather-favorable monsoon boosts sector outlook",
        "sector": "Agri-Input",
        "city": "Nagpur",
        "state": "Maharashtra",
    },
}
