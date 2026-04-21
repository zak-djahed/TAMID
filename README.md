# TAMID

A collection of quantitative finance projects completed as part of TAMID at the University of Miami.  
These projects focus on portfolio construction, factor modeling, and optimization techniques inspired by modern asset pricing theory.

---

## 📚 Projects

### 1. **Beta, Size, and Portfolio Sorting**
- **Objective:** Test whether stock beta is a significant predictor of returns by constructing portfolios sorted on **beta** and then further on **size**.  
- **Process:**
  - Collected 500 stocks from a chosen index (2021–2023).
  - Estimated **betas** using linear regression against the market.
  - Sorted into quintiles by beta, then further into quintiles by **market capitalization (size)**.
  - Tracked performance of these double-sorted portfolios over 2024–present.
- **Key Insight:** Connects directly to the Fama–French framework — evaluating whether returns are driven by beta or by other shared characteristics such as firm size.

---

### 2. **Factor Models and Portfolio Optimization**
- **Objective:** Apply factor models to construct covariance matrices, then use them for **portfolio optimization**.  
- **Part 1: Monte Carlo Simulation**
  - Selected 20 stocks and estimated their historical expected returns & variances.
  - Generated **10,000 random portfolios** with weights summing to 1.
  - Plotted the **risk-return frontier**, showing the parabolic efficient frontier shape.
- **Part 2: Minimum-Variance Portfolio**
  - Used `scipy.optimize.minimize` to solve for the **global minimum variance portfolio** subject to weights summing to 1.
  - Compared its performance against the market portfolio (2018–2024).
- **Key Insight:** Demonstrated how factor model-derived covariance matrices allow construction of efficient portfolios that outperform naive diversification.

---

### 3. **Testing Optimized vs Random Portfolios**
- **Objective:** Evaluate whether optimized portfolios actually outperform naive/random portfolios in practice.  
- **Process:**
  - Selected 5 sets of 20 stocks (2016–2020 or later).
  - Constructed and compared:
    - **Equal-weighted (1/n) portfolios**
    - **Random-weight portfolios**
    - **Minimum-variance portfolios**
    - **Mean-variance portfolios**
    - **Max-Sharpe portfolios**
  - Plotted risk-return outcomes for each across multiple subsets.
- **Key Insight:** Explored whether optimization techniques consistently generate superior portfolios compared to simple random or equal-weight strategies.

---

### 4. **Options Backtesting System**
- [**View Project**](https://github.com/zak-djahed/TAMID/tree/main/Projects/2025-2026/options-backtester)  
- **Objective:** Build an end-to-end options research pipeline enabling fully automated and repeatable strategy testing on SPX data.
- **Process:**
  - Designed a systematic **delta-neutral volatility strategy** that shorts options when implied volatility exceeds realized volatility and hedges dynamically.
  - Incorporated realistic trading mechanics: transaction costs, delta hedging, and position-level risk tracking.
  - Engineered a Greeks calculation engine (Black-Scholes delta, gamma, theta, vega) and aligned all signals to end-of-day realized volatility.
- **Key Results:**
  - Generated **$59K+ in cumulative PnL** and **$159K in equity** over the backtest period.
  - Produced a reusable framework for testing any volatility-based options strategy with full audit trail.

---

### 5. **Portfolio Dashboard**
- [**View Repo**](https://github.com/zak-djahed/TAMID_Portfolio_Dashboard)  
- **Description:** A lightweight dashboard that displays quick price data for a sample of blue-chip stocks, including Apple (AAPL), Microsoft (MSFT), and Tesla (TSLA).  
- **Purpose:** Serves as a convenient front-end tool for tracking real-time movements of major equities alongside deeper quantitative research from the projects above.

---

## 🧪 Tech Stack
- **Languages:** Python (3.11)  
- **Libraries:** `pandas`, `numpy`, `matplotlib`, `statsmodels`, `scipy`, `yfinance`, `py_vollib`, `yahooquery`

---

## ▶️ How to Run
1. Clone the repository:
   ```bash
   git clone https://github.com/zak-djahed/TAMID.git
   cd TAMID
2. Create environment & install dependencies:
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt
3. Open any notebook:
   jupyter notebook homework_X.ipynb

