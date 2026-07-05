"""Train ML scoring model on synthetic data."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.scoring.model import train_model

if __name__ == "__main__":
    metrics = train_model()
    print(f"Model trained — RMSE: {metrics['rmse']:.2f}, R²: {metrics['r2']:.3f}")
