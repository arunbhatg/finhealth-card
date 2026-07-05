import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.connectors.base import load_profile
from src.connectors.sources import ALL_CONNECTORS
from src.features.feature_engineering import extract_features
from src.scoring.model import compute_final_score

for mid in ["MSME001", "MSME003"]:
    profile = load_profile(mid)
    f = extract_features(profile)
    r = compute_final_score(f, profile=profile, sources=list(ALL_CONNECTORS.keys()))
    print(f"\n=== {mid} score={int(r['final_score'])} ===")
    print(r["narrative"])
    print("UP:", [f"+{b['score_points']} {b['factor']}" for b in r["boosters"][:3]])
    print("DOWN:", [f"{d['score_points']} {d['factor']}" for d in r["draggers"][:3]])
