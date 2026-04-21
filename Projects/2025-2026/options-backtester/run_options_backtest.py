import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import sys
import glob
import os
from pathlib import Path
from load_spx_data import load_spx_pickles

class OptionPosition:
    def __init__(self, row):
        self.strike = row['strike']
        self.expiry = row['expiration']
        self.type = row['option_type']
        self.iv = row['implied_vol']
        self.delta = row['delta']
        self.gamma = row['gamma']
        self.vega = row['vega']
        self.theta = row['theta']
        self.price = row['last']
        self.qty = 1

class Portfolio:
    def __init__(self, initial_cash=100000):
        self.initial_cash = initial_cash
        self.cash = initial_cash
        self.options = []
        self.stock_position = 0
        self.daily_pnl = []
        self.daily_delta = []
        self.daily_vega = []
        self.dates = []                           
        self.equity = []

    def update_greeks(self):
        total_delta = sum([opt.delta * opt.qty for opt in self.options])
        total_vega = sum([opt.vega * opt.qty for opt in self.options])
        self.daily_delta.append(total_delta + self.stock_position)
        self.daily_vega.append(total_vega)

def calculate_realized_vol(prices, window=20):
    """Calcula la volatilidad realizada usando retornos logarítmicos"""
    if len(prices) < 2:
        return 0.0
    returns = np.log(prices / prices.shift(1)).dropna()
    if len(returns) == 0:
        return 0.0
    return returns.std() * np.sqrt(252) * 100  # Convertir a porcentaje anual

def delta_neutral_vol_signal(df_day, historical_prices=None):
    spot = df_day['underlying_price'].iloc[0]
  
    df_day_sorted = df_day.iloc[(df_day['strike'] - spot).abs().argsort()]
    atm = df_day_sorted.head(2)
    
    if len(atm) == 0:
        return None
    
    if historical_prices is not None and len(historical_prices) > 1:
        realized_vol = calculate_realized_vol(historical_prices)
        implied_vol_mean = atm['implied_vol'].mean()
     
        if implied_vol_mean < realized_vol:
            return atm
    else:
        implied_vol_mean = atm['implied_vol'].mean()
        if implied_vol_mean < 30:  
            return atm
    return None

def run_backtest(df, commission=2.0, bid_ask_slip=0.05):
    port = Portfolio()
    prev_spot = None

    # Ensure dates are sorted and datetime
    df = df.sort_values('date').copy()
    df['date'] = pd.to_datetime(df['date'])

    # Build daily underlying close series from the df (purely daily)
    daily_spot = (
        df.groupby('date')['underlying_price']
          .first()
          .sort_index()
    )
    
    for day, group in df.groupby("date"):
        spot = group['underlying_price'].iloc[0]
      
        opt_pnl = 0
        if port.options:
            for opt in port.options:
                matching = group[(group['strike'] == opt.strike) & 
                                 (group['option_type'] == opt.type)]
                
                if len(matching) > 0:
                    current_price = matching['last'].iloc[0]
                    opt_pnl += (current_price - opt.price) * opt.qty
                    
                    opt.price = current_price
                    if 'delta' in matching.columns:
                        opt.delta = matching['delta'].iloc[0]
                    if 'theta' in matching.columns:
                        opt.theta = matching['theta'].iloc[0]
        
      
        stock_pnl = 0
        if prev_spot is not None:
            stock_pnl = port.stock_position * (spot - prev_spot)
        
       
        theta_decay = 0
        if port.options:
            theta_decay = sum([opt.theta * opt.qty for opt in port.options])
        
     
        port.cash -= theta_decay
        
   
        signal_options = delta_neutral_vol_signal(
            group,
            daily_spot.loc[:day]      # Series of spot up to current day
        )

        trading_cost = 0
        hedge_cost = 0
        if signal_options is not None and len(signal_options) > 0:
            for _, row in signal_options.iterrows():
                mid = (row['bid'] + row['ask']) / 2
                pos = OptionPosition(row)
                pos.price = mid
                port.options.append(pos)
                port.cash -= mid * pos.qty + commission + bid_ask_slip
                trading_cost += commission + bid_ask_slip
            
            net_opt_delta = sum([opt.delta * opt.qty for opt in port.options])
            delta_to_hedge = -net_opt_delta - port.stock_position
            port.stock_position += delta_to_hedge
            hedge_cost = abs(delta_to_hedge) * spot * 0.001
            port.cash -= hedge_cost
        
        daily_pnl = opt_pnl + stock_pnl - trading_cost - hedge_cost
        port.daily_pnl.append(daily_pnl)
        port.update_greeks()
        
        port.dates.append(day)

        # track equity
        if not port.equity:
            port.equity.append(port.initial_cash + daily_pnl)
        else:
            port.equity.append(port.equity[-1] + daily_pnl)

        prev_spot = spot
    
    return port

if __name__ == "__main__":
    project_root = Path(__file__).resolve().parents[0]
    data_dir = project_root / "data" / "spx" / "with_iv_greeks"

    print(f"Loading SPX pickle data from: {data_dir}")
    df = load_spx_pickles(
        data_dir,
        moneyness_band=(0.8, 1.2),
        strike_scale=1000,  # adjust if Strike scale changes
    )

    key_counts = (
        df.groupby(["date", "expiration", "strike", "option_type"])
          .size()
    )
    max_per_key = key_counts.max()
    print(f"Max rows per (date, expiration, strike, type): {max_per_key}")
    assert max_per_key == 1, "Found multiple rows per contract per day (intraday data?)"

    # Per-day underlying_price uniqueness (one SPX close per date)
    u_counts = df.groupby("date")["underlying_price"].nunique()
    max_u = u_counts.max()
    print(f"Max unique underlying prices per date: {max_u}")
    assert max_u == 1, "More than one underlying_price per date; data is not pure daily close"

    print(f"Total records: {len(df)}")
    print(f"Date range: {df['date'].min().date()} to {df['date'].max().date()}")
    print(f"Unique expirations: {df['expiration'].nunique()}")

    results = run_backtest(df)

    
    print(f"\n✓ Backtest completed")
    print(f"✓ Days processed: {len(results.daily_pnl)}")
    print(f"✓ Total PnL: ${sum(results.daily_pnl):.2f}")
    print(f"✓ Final cash: ${results.cash:.2f}")
    print(f"✓ Option positions: {len(results.options)}")
    print(f"✓ Stock position: {results.stock_position:.2f}")

    output_dir = project_root / "outputs"
    os.makedirs(output_dir, exist_ok=True)

    
    # save daily time series to CSV for analysis
    results_df = pd.DataFrame({
        "date": results.dates,
        "daily_pnl": results.daily_pnl,
        "equity": results.equity,
        "delta": results.daily_delta,
        "vega": results.daily_vega,
    })
    results_df.sort_values("date", inplace=True)

    results_csv = f"{output_dir}/backtest_results.csv"
    results_df.to_csv(results_csv, index=False)
    print(f"Saved daily results to: {results_csv}")


    if len(results.daily_pnl) > 0:
        cumulative_pnl = np.cumsum(results.daily_pnl)
        days = np.arange(1, len(results.daily_pnl) + 1)
        
      
        plt.figure(figsize=(12, 6))
        plt.plot(days, cumulative_pnl, marker='o', linewidth=2, markersize=8, color='#2ecc71')
        plt.title("Cumulative PnL", fontsize=16, fontweight='bold')
        plt.xlabel("Day", fontsize=12)
        plt.ylabel("PnL ($)", fontsize=12)
        plt.grid(True, alpha=0.3)
        
    
        for i, (day, pnl) in enumerate(zip(days, cumulative_pnl)):
            plt.annotate(f'${pnl:.2f}', (day, pnl), 
                        textcoords="offset points", xytext=(0,10), ha='center', fontsize=9)
        
       
        plt.axhline(y=0, color='r', linestyle='--', alpha=0.5, linewidth=1)
        
    
        if len(cumulative_pnl) == 1:
            plt.xlim(0.5, 1.5)
            margin = max(abs(cumulative_pnl[0]) * 0.2, 50)
            plt.ylim(cumulative_pnl[0] - margin, cumulative_pnl[0] + margin)
        
        plt.tight_layout()
        pnl_file = f"{output_dir}/cumulative_pnl.png"
        plt.savefig(pnl_file, dpi=150, bbox_inches='tight')
        print(f"Graph saved: {pnl_file}")
        plt.close()
        

        if len(results.daily_delta) > 0 and len(results.daily_vega) > 0:
            plt.figure(figsize=(12, 6))
            plt.plot(days, results.daily_delta, marker='o', linewidth=2, markersize=8, 
                    label="Net Delta", color='#3498db')
            plt.plot(days, results.daily_vega, marker='s', linewidth=2, markersize=8, 
                    label="Net Vega", color='#e74c3c')
            
            for i, day in enumerate(days):
                if i < len(results.daily_delta):
                    plt.annotate(f'{results.daily_delta[i]:.3f}', 
                               (day, results.daily_delta[i]), 
                               textcoords="offset points", xytext=(0,10), 
                               ha='center', fontsize=8, color='#3498db')
                if i < len(results.daily_vega):
                    plt.annotate(f'{results.daily_vega[i]:.4f}', 
                               (day, results.daily_vega[i]), 
                               textcoords="offset points", xytext=(0,-15), 
                               ha='center', fontsize=8, color='#e74c3c')
            
            plt.legend(fontsize=11, loc='best')
            plt.title("Daily Exposures (Delta & Vega)", fontsize=16, fontweight='bold')
            plt.xlabel("Day", fontsize=12)
            plt.ylabel("Exposure", fontsize=12)
            plt.grid(True, alpha=0.3)
            plt.axhline(y=0, color='black', linestyle='--', alpha=0.3, linewidth=1)
        
            if len(days) == 1:
                plt.xlim(0.5, 1.5)
            
            plt.tight_layout()
            exposures_file = f"{output_dir}/daily_exposures.png"
            plt.savefig(exposures_file, dpi=150, bbox_inches='tight')
            print(f"Graph saved: {exposures_file}")
            plt.close()
        
        if len(results.daily_pnl) > 0:
            plt.figure(figsize=(12, 6))
            colors = ['#2ecc71' if pnl >= 0 else '#e74c3c' for pnl in results.daily_pnl]
            bars = plt.bar(days, results.daily_pnl, color=colors, alpha=0.7, edgecolor='black', linewidth=1.5)
            plt.title("Daily PnL", fontsize=16, fontweight='bold')
            plt.xlabel("Day", fontsize=12)
            plt.ylabel("PnL ($)", fontsize=12)
            plt.grid(True, alpha=0.3, axis='y')
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.5, linewidth=1)
            
       
            for bar, pnl in zip(bars, results.daily_pnl):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height,
                        f'${pnl:.2f}',
                        ha='center', va='bottom' if height >= 0 else 'top', fontsize=10, fontweight='bold')
            
            if len(days) == 1:
                plt.xlim(0.5, 1.5)
            
            plt.tight_layout()
            daily_pnl_file = f"{output_dir}/daily_pnl_breakdown.png"
            plt.savefig(daily_pnl_file, dpi=150, bbox_inches='tight')
            print(f"Graph saved: {daily_pnl_file}")
            plt.close()
        
 
        plt.figure(figsize=(12, 6))
        plt.plot(days, cumulative_pnl, marker='o', linewidth=2, markersize=8, color='#2ecc71')
        plt.title("Cumulative PnL", fontsize=16, fontweight='bold')
        plt.xlabel("Day", fontsize=12)
        plt.ylabel("PnL ($)", fontsize=12)
        plt.grid(True, alpha=0.3)
        for i, (day, pnl) in enumerate  (zip(days, cumulative_pnl)):
            plt.annotate(f'${pnl:.2f}', (day, pnl), 
                        textcoords="offset points", xytext=(0,10), ha='center', fontsize=10)
        plt.axhline(y=0, color='r', linestyle='--', alpha=0.5)
        if len(cumulative_pnl) == 1:
            plt.xlim(0.5, 1.5)
            margin = max(abs(cumulative_pnl[0]) * 0.2, 50)
            plt.ylim(cumulative_pnl[0] - margin, cumulative_pnl[0] + margin)
        plt.tight_layout()
        plt.show()
    else:
        print("Warning: No data to plot")
