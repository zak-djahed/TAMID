import os
from pathlib import Path
import pandas as pd

def load_spx_pickles(
    data_dir: Path,
    moneyness_band=(0.8, 1.2),
    strike_scale=None,
) -> pd.DataFrame:
    """
    Load all SPX option pickle files from `data_dir`, combine them into a single
    daily DataFrame, filter by moneyness, and return columns that the
    backtester expects.
    """

    frames = []
    for fname in os.listdir(data_dir):
        if fname.endswith(".pkl"):
            fpath = data_dir / fname
            df = pd.read_pickle(fpath)
            frames.append(df)

    if not frames:
        raise ValueError(f"No .pkl files found in {data_dir}")

    df = pd.concat(frames, ignore_index=False)  # keep Date index

    # Make a proper 'date' column from the index, index is already datetime-like
    if not isinstance(df.index, pd.DatetimeIndex):
        # fallback if something changes later
        df.index = pd.to_datetime(df.index)

    df = df.reset_index().rename(columns={"Date": "date"})  # index to 'date'

    # Parse expiration from the integer yyyymmdd in 'Expiration'
    df["expiration"] = pd.to_datetime(df["Expiration"].astype(int).astype(str),
                                      format="%Y%m%d")

    # Map to the names your backtester uses
    df = df.rename(columns={
        "Strike": "strike_raw",
        "CallPut": "option_type",          
        "BestBid": "bid",
        "BestOffer": "ask",
        "ImpliedVolatility": "implied_vol",
        "Delta": "delta",
        "Gamma": "gamma",
        "Theta": "theta",
        "Vega": "vega",
        "SPX_AdjClose": "underlying_price",
    })

    # Optionally scale strikes if needed
    if strike_scale is not None:
        df["strike"] = df["strike_raw"] / strike_scale
    else:
        df["strike"] = df["strike_raw"]

    df["symbol"] = "^SPX"

    # Compute midprice if needed
    df["midprice"] = (df["bid"] + df["ask"]) / 2.0

    # Filter by moneyness band around underlying_price
    lower, upper = moneyness_band
    df = df[
        (df["strike"] >= lower * df["underlying_price"]) &
        (df["strike"] <= upper * df["underlying_price"])
    ].copy()

    # Ensure date is a Timestamp (not just date object)
    df["date"] = pd.to_datetime(df["date"])

    return df
