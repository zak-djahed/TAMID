# We honestly probably don't need this file anymore nor greeks_generator.py

'''
import yahooquery
from yahooquery import Ticker
import pandas as pd
import pytz

symbol = "AAPL"
tkr = Ticker(symbol)

chain = tkr.option_chain
chain_df = chain.reset_index()

expirations = chain_df['expiration'].unique()
expiry = expirations[0] if len(expirations) > 0 else None

if expiry:
    chain_df = chain_df[chain_df['expiration'] == expiry]

calls = chain_df[chain_df['optionType'] == 'calls']
puts = chain_df[chain_df['optionType'] == 'puts']

def clean_option(row, symbol, underlying_price):
    return {
        "symbol": symbol,
        "date": pd.Timestamp.now().strftime('%Y-%m-%d'),
        "expiration": row['expiration'],
        "strike": row['strike'],
        "option_type": row['optionType'],
        "bid": row['bid'],
        "ask": row['ask'],
        "last": row['lastPrice'],
        "implied_vol": row['impliedVolatility'],
        "open_interest": row['openInterest'],
        "underlying_price": underlying_price
    }

underlying_price = tkr.price[symbol]['regularMarketPrice']

calls_df = calls.apply(lambda row: clean_option(row, symbol, underlying_price), axis=1).apply(pd.Series)
puts_df = puts.apply(lambda row: clean_option(row, symbol, underlying_price), axis=1).apply(pd.Series)
options_df = pd.concat([calls_df, puts_df], ignore_index=True)

# Liquidity / moneyness filter
lower_strike = 0.8 * underlying_price
upper_strike = 1.2 * underlying_price

options_df = options_df[
    (options_df["strike"] >= lower_strike) &
    (options_df["strike"] <= upper_strike)
].copy()

print(f"Filtered to strikes between {lower_strike:.2f} and {upper_strike:.2f}")
print(f"Remaining rows: {len(options_df)}")

# Save cleaned, filtered option chain
options_df.to_csv("option_chain_AAPL.csv", index=False)

print(options_df.head())

'''