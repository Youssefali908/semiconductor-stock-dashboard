"""CPS*5745 semiconductor stock comparison dashboard by Youssef Ali."""
from datetime import date, timedelta
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
import yfinance as yf
from analytics import compute_metrics, strongest_return_correlation

st.set_page_config(page_title="Semiconductor Market Lens | Youssef Ali", page_icon="📈", layout="wide")
st.title("Semiconductor Market Lens")
st.caption("Youssef Ali  •  Developed for CPS*5745")
st.markdown("Compare semiconductor companies with six interactive Plotly charts, shared filters, and recent Yahoo Finance prices.")
COMPANIES = {"NVDA":"NVIDIA","AMD":"Advanced Micro Devices","INTC":"Intel","AVGO":"Broadcom","QCOM":"Qualcomm","TSM":"Taiwan Semiconductor"}
with st.sidebar:
    st.header("Shared filters")
    st.write("Youssef Ali · Developed for CPS*5745")
    symbols = st.multiselect("Companies (select at least 3)", list(COMPANIES), default=["NVDA","AMD","INTC"],format_func=lambda x:f"{COMPANIES[x]} ({x})")
    start = st.date_input("Start date", date.today()-timedelta(days=365),max_value=date.today())
    end = st.date_input("End date",date.today(),max_value=date.today())
    refresh = st.button("Refresh market data")
    st.caption("Source: Yahoo Finance via yfinance. Daily prices may be delayed.")
@st.cache_data(ttl=900)
def load(tickers, start_date, end_date):
    adjusted, dollars, failures = {},{},[]
    for ticker in tickers:
        try:
            hist=yf.download(ticker,start=start_date.isoformat(),end=(end_date+timedelta(days=1)).isoformat(),auto_adjust=False,progress=False,threads=False,timeout=20)
            if hist.empty:
                failures.append(ticker)
                continue
            if isinstance(hist.columns,pd.MultiIndex):
                hist.columns=hist.columns.get_level_values(0)
            adj="Adj Close" if "Adj Close" in hist else "Close"
            index=pd.to_datetime(hist.index).tz_localize(None).normalize() if hist.index.tz is not None else pd.to_datetime(hist.index).normalize()
            adjusted[ticker]=pd.Series(hist[adj].to_numpy().reshape(-1),index=index)
            dollars[ticker]=pd.Series((hist["Close"]*hist["Volume"]).to_numpy().reshape(-1),index=index)
        except Exception:
            failures.append(ticker)
    return (pd.concat(adjusted,axis=1) if adjusted else pd.DataFrame(),
            pd.concat(dollars,axis=1) if dollars else pd.DataFrame(),failures)
if refresh:
    load.clear()
if len(symbols)<3:
    st.warning("Select at least three publicly traded companies.")
    st.stop()
if start>=end:
    st.warning("Start date must be earlier than end date.")
    st.stop()
with st.spinner("Fetching market history…"):
    adjusted,dollars,failures=load(tuple(symbols),start,end)
if failures or any(t not in adjusted for t in symbols):
    st.error("Market history could not be retrieved for: "+", ".join(failures)+". Refresh or retry later. No synthetic prices are used.")
    st.stop()
try:
    m=compute_metrics(adjusted[symbols])
except ValueError as exc:
    st.error(str(exc))
    st.stop()
prices=m["prices"]; daily=m["daily_returns"]; period=m["period_return_pct"]; vol=m["annualized_volatility_pct"]
indexed=m["indexed"]; correlation=m["correlation"]
st.caption(f"Compared stocks: {', '.join(symbols)} | Shared trading dates: {prices.index[0].date()} to {prices.index[-1].date()} | {len(prices)} sessions")
a,b,c=st.columns(3)
leader=period.idxmax(); laggard=period.idxmin(); most_volatile=vol.idxmax()
a.metric("Highest period return",f"{leader}: {period[leader]:+.1f}%")
b.metric("Lowest period return",f"{laggard}: {period[laggard]:+.1f}%")
c.metric("Highest annualized volatility",f"{most_volatile}: {vol[most_volatile]:.1f}%")
strongest=strongest_return_correlation(correlation)
st.subheader("Key differences")
message=(f"From {prices.index[0].date()} to {prices.index[-1].date()}, {COMPANIES[leader]} had the highest adjusted-price return "
         f"({period[leader]:+.1f}%), while {COMPANIES[laggard]} had the lowest ({period[laggard]:+.1f}%). "
         f"{COMPANIES[most_volatile]} exhibited the largest annualized variation in daily returns ({vol[most_volatile]:.1f}%).")
if strongest:
    message+=f" The strongest absolute daily-return correlation was {strongest[0]} versus {strongest[1]} (r={strongest[2]:+.2f})."
st.info(message)
st.subheader("Six interactive comparison charts")
indexed_long=indexed.reset_index().melt(id_vars=indexed.index.name or "index",var_name="Company",value_name="Indexed adjusted price")
indexed_long=indexed_long.rename(columns={indexed_long.columns[0]:"Date"})
fig1=px.line(indexed_long,x="Date",y="Indexed adjusted price",color="Company",title="01 · Indexed performance (start = 100)",labels={"Indexed adjusted price":"Adjusted-price index (initial = 100)"})
fig2=px.bar(x=period.sort_values().values,y=period.sort_values().index,orientation="h",title="02 · Selected-period adjusted return",labels={"x":"Total return over selected window (%)","y":"Company"})
daily_pct=daily.mul(100)
daily_long=daily_pct.reset_index().melt(id_vars=daily_pct.index.name or "index",var_name="Company",value_name="Daily return (%)")
fig3=px.box(daily_long,x="Company",y="Daily return (%)",color="Company",points="outliers",title="03 · Daily-return distribution")
fig4=px.scatter(x=vol.values,y=period.values,text=period.index,color=period.index,title="04 · Risk versus period return",labels={"x":"Annualized volatility of daily returns (%)","y":"Selected-period return (%)"},size_max=20)
fig4.update_traces(marker_size=17,textposition="top center")
fig5=px.imshow(correlation.loc[symbols,symbols],zmin=-1,zmax=1,color_continuous_scale="RdBu_r",text_auto=".2f",title="05 · Daily-return Pearson correlation",labels={"color":"Pearson r"})
aligned_dollars=dollars.reindex(index=prices.index,columns=symbols)
monthly=aligned_dollars.resample("MS").mean().div(1e9)
activity=monthly.reset_index().melt(id_vars=monthly.index.name or "index",var_name="Company",value_name="Average daily traded USD (billions)")
activity=activity.rename(columns={activity.columns[0]:"Month"})
fig6=px.bar(activity,x="Month",y="Average daily traded USD (billions)",color="Company",barmode="group",title="06 · Average daily dollar trading activity by month")
for fig in (fig1,fig2,fig3,fig4,fig5,fig6):
    fig.update_layout(template="plotly_dark",height=380,margin=dict(l=20,r=15,t=65,b=40))
for first,second in ((fig1,fig2),(fig3,fig4),(fig5,fig6)):
    l,r=st.columns(2)
    with l: st.plotly_chart(first,use_container_width=True)
    with r: st.plotly_chart(second,use_container_width=True)
st.caption("Methodology: adjusted closes for indexed performance and returns; 252-trading-day annualized daily-return standard deviation for volatility; Pearson correlation for daily returns. Estimated daily dollar volume = unadjusted Close × share Volume. Historical figures are descriptive, not predictions.")
st.caption("AI-use disclosure: ChatGPT assisted with drafting code, visual design, and documentation. Final deployment and results should be independently checked.")
st.download_button("Export aligned adjusted prices (CSV)",prices.to_csv().encode(),file_name="youssef_ali_prices.csv",mime="text/csv")
