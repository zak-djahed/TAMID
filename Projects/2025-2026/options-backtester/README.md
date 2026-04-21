# Options Trading Backtesting System

A comprehensive Python-based options trading backtesting framework that downloads options chain data, calculates option Greeks using Black-Scholes model, and backtests delta-neutral volatility trading strategies.

## Overview

This project implements a complete workflow for options trading analysis:

1. **Data Download**: Fetches real-time options chain data from Yahoo Finance
2. **Greeks Calculation**: Computes option Greeks (Delta, Gamma, Theta, Vega) using Black-Scholes pricing model
3. **Backtesting**: Simulates delta-neutral volatility trading strategies with realistic transaction costs
4. **Performance Analysis**: Evaluates strategy performance using risk-adjusted metrics (Sharpe ratio, Sortino ratio, max drawdown)

## Features

- **Options Data Download**: Automated download of options chains from Yahoo Finance
- **Greeks Calculation**: Full implementation of Black-Scholes Greeks (Delta, Gamma, Theta, Vega)
- **Delta-Neutral Strategy**: Automated hedging to maintain delta-neutral positions
- **Realistic Trading Costs**: Includes commissions, bid-ask spreads, and hedging costs
- **Performance Metrics**: Comprehensive risk and return analysis
- **Visualizations**: Automatic generation of PnL charts and exposure graphs

## Installation

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)

### Setup

1. **Clone or download this repository**

2. **Install required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the project** (see Configuration section below)

## Configuration

Before running the scripts, you need to configure the following:

### 1. Download Directory (`greeks_generator.py`)

Edit line 12 in `greeks_generator.py`:
```python
download_dir = "YOUR_DOWNLOAD_DIR"  # Change this to your desired directory
```

For example:
```python
download_dir = "/Users/oscar/Downloads"  # or "./data" for relative path
```

### 2. Backtest Directory (`run_options_backtest (1).py`)

Edit line 148 in `run_options_backtest.py`:
```python
download_dir = "/Users/oscar/Downloads"  # Change to your directory
```

### 3. Results Analysis Path (`results_analysis.ipynb`)

In the notebook, update the path in Cell 1:
```python
results_path = "backtest_results.csv"  # or full path if needed
```

### 4. Risk-Free Rate

The risk-free rate is set to 4% (0.04) in `greeks_generator.py` and 4.5% (0.045) in `results_analysis.ipynb`. Adjust these values based on your assumptions:
- `greeks_generator.py`: Line 10
- `results_analysis.ipynb`: Cell 0

### 5. Trading Symbol

Edit line 5 in `download_options_data.py` to change the stock symbol:
```python
symbol = "AAPL"  # Change to any valid ticker symbol
```

## Step-by-Step Workflow

### Step 1: Download Options Data

Run the data download script to fetch options chain data:

```bash
python "download_options_data.py"
```

**What it does:**
- Downloads options chain for the specified symbol (default: AAPL)
- Filters options by moneyness (80%-120% of spot price for liquidity)
- Saves data to `option_chain_[SYMBOL].csv`

**Output:**
- `option_chain_AAPL.csv` (or your symbol) containing:
  - Symbol, date, expiration, strike, option type (calls/puts)
  - Bid, ask, last price
  - Implied volatility, open interest
  - Underlying price

### Step 2: Calculate Option Greeks

Run the Greeks generator to compute option sensitivities:

```bash
python "greeks_generator.py"
```

**What it does:**
- Reads the latest options CSV file from the download directory
- Calculates Delta, Gamma, Theta, Vega for each option using Black-Scholes model
- Computes theoretical Black-Scholes prices
- Saves results to `option_chain_[SYMBOL]_with_greeks.csv`

**Output:**
- `option_chain_[SYMBOL]_with_greeks.csv` with additional columns:
  - `delta`: Price sensitivity to underlying moves
  - `gamma`: Sensitivity of delta to underlying moves
  - `theta`: Time decay (daily)
  - `vega`: Sensitivity to volatility changes
  - `bs_price`: Theoretical Black-Scholes price
  - `time_to_expiry`: Time to expiration in years
  - `sigma`: Normalized implied volatility

### Step 3: Run Backtest

Execute the backtesting engine:

```bash
python "run_options_backtest.py"
```

**What it does:**
- Loads options data with Greeks
- Implements delta-neutral volatility trading strategy:
  - **Signal**: Opens positions when implied volatility is low relative to realized volatility
  - **Position**: Buys at-the-money options
  - **Hedging**: Maintains delta-neutrality by trading underlying stock
  - **Costs**: Includes commissions ($2 per trade) and bid-ask slippage (5%)
- Tracks daily PnL, equity, delta, and vega exposures
- Generates visualization charts

**Output:**
- `backtest_results.csv`: Daily time series of:
  - Date, daily PnL, equity curve
  - Net delta and vega exposures
- `cumulative_pnl.png`: Chart of cumulative profit and loss
- `daily_pnl_breakdown.png`: Bar chart of daily PnL
- `daily_exposures.png`: Chart of delta and vega over time

**Strategy Logic:**
- Compares implied volatility to realized volatility (20-day rolling window)
- When IV < realized vol, opens long options positions
- Hedges delta by shorting/buying underlying stock
- Accounts for theta decay (time value loss)
- Tracks option mark-to-market and stock PnL

### Step 4: Analyze Results

Open and run the Jupyter notebook for performance analysis:

```bash
jupyter notebook results_analysis.ipynb
```

**What it does:**
- Calculates performance metrics:
  - **Annualized Return**: Compounded annual return
  - **Annualized Volatility**: Risk measure (standard deviation)
  - **Sharpe Ratio**: Risk-adjusted return metric
  - **Sortino Ratio**: Downside risk-adjusted return
  - **Max Drawdown**: Largest peak-to-trough decline
  - **Average Exposures**: Mean delta and vega
- Visualizes:
  - Equity curve over time
  - Rolling Sharpe ratio (60-day window)

## File Descriptions

### `download_options_data (1).py`
- **Purpose**: Downloads options chain data from Yahoo Finance
- **Inputs**: Stock symbol (hardcoded)
- **Outputs**: `option_chain_[SYMBOL].csv`
- **Key Features**: Moneyness filtering (80%-120% of spot)

### `greeks_generator (1).py`
- **Purpose**: Calculates option Greeks using Black-Scholes model
- **Inputs**: Options CSV file from download step
- **Outputs**: `option_chain_[SYMBOL]_with_greeks.csv`
- **Key Features**: 
  - Black-Scholes pricing
  - Greeks calculation (Delta, Gamma, Theta, Vega)
  - Implied volatility normalization
  - Time-to-expiry calculation

### `run_options_backtest (1).py`
- **Purpose**: Backtests delta-neutral volatility trading strategy
- **Inputs**: Options CSV with Greeks
- **Outputs**: 
  - `backtest_results.csv`
  - Visualization PNG files
- **Key Features**:
  - Portfolio management (cash, options, stock positions)
  - Delta-neutral hedging
  - Transaction cost modeling
  - Daily PnL tracking
  - Visualization generation

### `results_analysis.ipynb`
- **Purpose**: Performance analysis and visualization
- **Inputs**: `backtest_results.csv`
- **Outputs**: Metrics and charts
- **Key Features**:
  - Risk-adjusted performance metrics
  - Equity curve visualization
  - Rolling Sharpe ratio analysis

## Output Files

### CSV Files
- `option_chain_[SYMBOL].csv`: Raw options data
- `option_chain_[SYMBOL]_with_greeks.csv`: Options data with calculated Greeks
- `backtest_results.csv`: Daily backtest results and metrics

### Visualization Files
- `cumulative_pnl.png`: Cumulative profit and loss chart
- `daily_pnl_breakdown.png`: Daily PnL bar chart
- `daily_exposures.png`: Delta and vega exposure charts

## Performance Metrics Explained

### Annualized Return
The compounded annual return of the strategy, calculated as:
```
(1 + mean_daily_return)^252 - 1
```

### Annualized Volatility
The annualized standard deviation of returns:
```
daily_std * sqrt(252)
```

### Sharpe Ratio
Risk-adjusted return metric:
```
(annual_return - risk_free_rate) / annual_volatility
```
Higher is better. Typically:
- < 1: Poor
- 1-2: Good
- > 2: Excellent

### Sortino Ratio
Similar to Sharpe but only penalizes downside volatility:
```
(annual_return - risk_free_rate) / downside_volatility
```

### Max Drawdown
The largest peak-to-trough decline in equity, expressed as a percentage. Lower (less negative) is better.

## Strategy Parameters

### Trading Costs
- **Commission**: $2.00 per options trade (configurable in `run_options_backtest.py` line 69)
- **Bid-Ask Slippage**: 5% of mid price (line 69)
- **Hedge Cost**: 0.1% of notional for stock hedging (line 128)

### Risk-Free Rate
- **Greeks Calculation**: 4% annual (0.04)
- **Performance Analysis**: 4.5% annual (0.045)

### Volatility Signal
- **Realized Vol Window**: 20 trading days
- **IV Threshold**: Implied volatility compared to realized volatility
- **Fallback Threshold**: 30% if historical prices unavailable

### Moneyness Filter
- Options filtered to strikes between 80% and 120% of spot price
- Ensures adequate liquidity and relevance

## Troubleshooting

### Common Issues

1. **"No CSV files found" error**
   - Ensure `download_dir` is correctly configured in `greeks_generator.py`
   - Verify that Step 1 completed successfully and generated a CSV file

2. **"Module not found" error**
   - Install missing dependencies: `pip install -r requirements.txt`
   - Ensure you're using the correct Python environment

3. **Empty or incomplete data**
   - Check internet connection for Yahoo Finance API
   - Verify the stock symbol is valid and has options data
   - Some symbols may have limited options availability

4. **Greeks calculation errors**
   - Check for invalid implied volatility values (should be between 1% and 500%)
   - Verify dates are correctly formatted
   - Ensure time-to-expiry is positive

5. **Backtest produces no trades**
   - Adjust volatility thresholds in `delta_neutral_vol_signal()` function
   - Check that implied volatility data is valid
   - Verify historical price data is available

## Future Enhancements

Potential improvements to consider:

- [ ] Support for multiple symbols and portfolio optimization
- [ ] Advanced volatility models (Heston, Local Volatility)
- [ ] Additional Greeks (Rho, Charm, etc.)
- [ ] More sophisticated hedging strategies
- [ ] Real-time data integration
- [ ] Web dashboard for visualization
- [ ] Machine learning for signal generation
- [ ] Options chain surface analysis
- [ ] Greeks surface visualization

## Dependencies

See `requirements.txt` for complete list. Key dependencies:
- `pandas`: Data manipulation and analysis
- `numpy`: Numerical computations
- `scipy`: Statistical functions (normal distribution)
- `yahooquery`: Yahoo Finance API access
- `matplotlib`: Visualization and plotting
- `jupyter`: Notebook interface for analysis

## License

This project is provided as-is for educational and research purposes.

## Disclaimer

This software is for educational purposes only. Options trading involves substantial risk of loss. Past performance does not guarantee future results. Always consult with a qualified financial advisor before making investment decisions.
