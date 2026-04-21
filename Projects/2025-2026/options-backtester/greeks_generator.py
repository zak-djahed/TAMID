# I don't think we need this anymore nor the download_options_data


'''
import numpy as np
from scipy.stats import norm
import pandas as pd
import os
import math as math
from datetime import datetime
import glob
import sys

r = 0.04

download_dir = "YOUR_DOWNLOAD_DIR"

def black_scholes_price(S, K, T, r, sigma, option_type='C') :
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T) 
    if option_type == "C":
        return (S * norm.cdf(d1)) - (K * np.exp(-r * T) * norm.cdf(d2))
    else:
        return (K * np.exp(-r * T) * norm.cdf(-d2)) - (S * norm.cdf(-d1)) 

def delta(S, K, T, r, sigma, option_type = 'C'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    if option_type == 'C':
        return norm.cdf(d1)
    else:
        return norm.cdf(d1) - 1
def gamma(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    pdf_d1 = norm.pdf(d1)
    gamma = pdf_d1 / (S * sigma * np.sqrt(T))
    return gamma
def theta(S, K, T, r, sigma, option_type = 'C'):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)

    first = - (S * norm.pdf(d1) * sigma) / (2 * np.sqrt(T))

    if option_type == 'C':
        theta_val = first - r * K * np.exp(-r * T) * norm.cdf(d2)
    else:  # put
        theta_val = first + r * K * np.exp(-r * T) * norm.cdf(-d2)

    return theta_val / 365
def vega(S, K, T, r, sigma):
    d1 = (np.log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    vega = S * norm.pdf(d1) * np.sqrt(T)

    return vega / 100

def inflexion_point(S, K, T, r) :
    m = S / (K * np.exp(-r * T))
    return np.sqrt(2 * abs(np.log(m) / T))


def implied_vol(S, K, T, r, market_price, option_type="C", x0=0.2, tol=10**-8, max_iter=100):

    for i in range(max_iter):
        p = black_scholes_price(S, K, T, r, x0, option_type)
        v = vega(S, K, T, r, x0)
        
        if abs(v) < tol:
            break
            
        diff = (p - market_price) / v
        x0 = x0 - diff
        
        if abs(diff) < tol:
            break
    
    return x0

def calculate_greeks_for_row(row, r):
  
    S = row['underlying_price']
    K = row['strike']
    
    date = pd.to_datetime(row['date'])
    expiration = pd.to_datetime(row['expiration'])
    T = (expiration - date).days / 365.0
    

    if T <= 0:
        T = 1/365.0
    
    option_type = 'C' if row['option_type'] == 'calls' else 'P'
    
    sigma = row['implied_vol'] / 100
    
    if sigma < 0.01 or sigma > 5.0:
        sigma = 0.2  
    
    delta_val = delta(S, K, T, r, sigma, option_type)
    gamma_val = gamma(S, K, T, r, sigma)
    theta_val = theta(S, K, T, r, sigma, option_type)
    vega_val = vega(S, K, T, r, sigma)
    
    bs_price = black_scholes_price(S, K, T, r, sigma, option_type)
    
    return pd.Series({
        'delta': delta_val,
        'gamma': gamma_val,
        'theta': theta_val,
        'vega': vega_val,
        'bs_price': bs_price,
        'time_to_expiry': T,
        'sigma': sigma
    })

csv_files = [f for f in glob.glob(f"{download_dir}/option_chain_*.csv") 
             if "_with_greeks" not in f]
if not csv_files:
    print(f"Error: No se encontraron archivos CSV sin Greeks en {download_dir}")
    sys.exit(1)

latest_file = max(csv_files, key=os.path.getctime)
print(f"Leyendo archivo: {latest_file}")

df = pd.read_csv(latest_file)

df['date'] = pd.to_datetime(df['date'])
df['expiration'] = pd.to_datetime(df['expiration'])

print("Calculando Greeks...")
greeks_df = df.apply(lambda row: calculate_greeks_for_row(row, r), axis=1)

result_df = pd.concat([df, greeks_df], axis=1)

output_filename = latest_file.replace('.csv', '_with_greeks.csv')
result_df.to_csv(output_filename, index=False)

print(f"\n✓ Archivo con Greeks guardado: {output_filename}")
print(f"✓ Total de opciones procesadas: {len(result_df)}")
print(f"✓ Tasa libre de riesgo (r): {r*100}%")
print(f"\nColumnas añadidas: delta, gamma, theta, vega, bs_price, time_to_expiry, sigma")
print(f"\nPrimeras filas del resultado:")
display_cols = ['symbol', 'strike', 'option_type', 'underlying_price', 'delta', 'gamma', 'theta', 'vega', 'bs_price', 'last', 'time_to_expiry']
print(result_df[display_cols].head(10))
'''