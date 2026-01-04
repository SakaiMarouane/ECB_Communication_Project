import os
from pathlib import Path
import yfinance as yf
import pandas as pd
import numpy as np

# --- Force working directory to project root ---
ROOT_DIR = Path(__file__).resolve().parent.parent
os.chdir(ROOT_DIR)

OUT_PATH = Path("data/market/eurostoxx50_daily.csv")
OUT_PATH.parent.mkdir(parents=True, exist_ok=True)

ticker = "^STOXX50E"

df = yf.download(
    ticker,
    start="1998-01-01",
    progress=False,
    auto_adjust=True  # makes behavior explicit
)

# Handle multi-level columns from newer yfinance versions
if isinstance(df.columns, pd.MultiIndex):
    df.columns = df.columns.get_level_values(0)

df = df.reset_index()

# Handle different column name formats (Date vs date, etc.)
df.columns = [c.lower() if isinstance(c, str) else c for c in df.columns]

# With auto_adjust=True, "Close" is already adjusted
if "close" in df.columns:
    df = df[["date", "close"]].rename(columns={"close": "price"})
elif "Close" in df.columns:
    df = df[["date", "Close"]].rename(columns={"Close": "price"})
else:
    raise ValueError(f"Could not find Close column. Columns: {df.columns.tolist()}")

df["date"] = pd.to_datetime(df["date"])
df = df.sort_values("date").reset_index(drop=True)

# ✅ log returns (as in the paper)
df["return"] = np.log(df["price"]).diff()

df = df.dropna()

df.to_csv(OUT_PATH, index=False)

print(df.head())
print(df.tail())
print("Saved:", OUT_PATH.resolve())
print("Start date:", df["date"].min(), "End date:", df["date"].max(), "Rows:", len(df))
