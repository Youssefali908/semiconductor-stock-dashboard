# Semiconductor Market Lens — Youssef Ali

**Developed for CPS*5745** — Visualization Design and Development.

An original Streamlit/Plotly Python stock comparison dashboard using recent daily Yahoo Finance market history through `yfinance`. Default comparison: NVIDIA (NVDA), AMD (AMD), and Intel (INTC). The user can select any three or more of six semiconductor companies and change the start/end dates; each chart updates with the same filters.

## Six comparison visualizations
1. Indexed adjusted stock performance (line; first common adjusted close = 100)
2. Selected-period adjusted-price return (horizontal bar; %)
3. Distribution of daily adjusted-price returns (box; %)
4. Return versus annualized daily-return volatility (scatter; %)
5. Correlation of daily adjusted returns (heatmap; Pearson r from -1 to +1)
6. Average daily traded US-dollar value per month (grouped bars; billions USD per trading day)

The app generates a short, data-driven comparison showing the strongest and weakest adjusted-price returns, highest annualized daily-return volatility, and strongest pairwise return correlation.

## Run locally

```bash
python -m pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud
1. Visit https://share.streamlit.io/ and authenticate with GitHub.
2. Create a new app from `Youssefali908/semiconductor-stock-dashboard`, branch `main`, main file `app.py`.
3. Wait for installation and verify that all six charts load with actual recent market history.
4. Open the public `*.streamlit.app` link in an incognito window to confirm that viewers do not need to sign in.
5. Submit this **live Streamlit link**, plus readable screenshots showing the author, filters, and each visualization in your CPS*5745 Canvas quiz. GitHub alone is not the live dashboard URL.

## Data methodology
Historical adjusted prices are used for returns and comparisons and aligned to common trading sessions; historical market data can be delayed. Volatility is the sample standard deviation of daily percentage returns multiplied by √252. The correlation metric is Pearson correlation of daily returns. Approximate daily traded dollar value uses *raw* closing price times unadjusted traded shares; that is not market capitalization. Refresh the data through the button or wait for the 15-minute cache. Do not substitute synthetic prices when data requests fail.

## AI-use acknowledgment
ChatGPT assisted with initial code generation, layout, testing, and documentation. The student should verify the deployed site and its outputs before submitting.

## Project files
- `app.py`: Streamlit UI, 6 Plotly charts, shared filters, live market download
- `analytics.py`: analytics functions
- `requirements.txt`: Python dependencies
- `.streamlit/config.toml`: color theme
- `tests/test_analytics.py`: calculation unit tests
