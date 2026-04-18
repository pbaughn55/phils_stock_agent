import streamlit as st
import yfinance as yf
from datetime import datetime

st.set_page_config(page_title="Stock Analysis Agent", page_icon="🚀", layout="wide")

st.title("🚀 Stock Analysis Agent")
st.markdown("**Professional insights • Analyst targets • Timelines**")

ticker_input = st.text_input("Enter ticker symbol", value="AMZN", key="ticker")

@st.cache_data(ttl=600, show_spinner=False)   # Cache for 10 minutes
def get_stock_data(symbol: str):
    """Fetch and return only serializable data"""
    ticker = yf.Ticker(symbol.upper())
    return {
        "info": ticker.info,
        "history": ticker.history(period="1y"),
        "news": ticker.news[:5] if ticker.news else [],
        "calendar": ticker.calendar
    }

if st.button("Analyze Stock", type="primary", use_container_width=True):
    with st.spinner(f"Fetching latest data for {ticker_input.upper()}..."):
        try:
            # Get cached data
            data = get_stock_data(ticker_input)
            info = data["info"]
            hist = data["history"]
            news = data["news"]
            calendar = data["calendar"]

            current_price = info.get('currentPrice') or info.get('regularMarketPrice')
            target_low = info.get('targetLowPrice')
            target_mean = info.get('targetMeanPrice')
            target_high = info.get('targetHighPrice')
            target_median = info.get('targetMedianPrice')
            num_analysts = info.get('numberOfAnalystOpinions')
            recommendation = info.get('recommendationKey', 'N/A')

            sma50 = hist['Close'].rolling(50).mean().iloc[-1] if not hist.empty else None
            sma200 = hist['Close'].rolling(200).mean().iloc[-1] if not hist.empty else None

            def fmt_price(val):
                return f"${val:.2f}" if val is not None else "N/A"
            def fmt_num(val, decimals=2):
                if val is None: return "N/A"
                try: return f"{float(val):.{decimals}f}"
                except: return "N/A"

            # Clean earnings date
            if isinstance(calendar, dict) and 'Earnings Date' in calendar:
                earnings_date = str(calendar.get('Earnings Date'))
            elif hasattr(calendar, 'empty') and not calendar.empty:
                earnings_date = str(calendar.iloc[0].get('Earnings Date', 'N/A'))
            else:
                earnings_date = "Check Yahoo Finance"
            earnings_date = earnings_date.replace("datetime.date(", "").replace(")", "").replace("[", "").replace("]", "")

            st.success(f"✅ Analysis for {ticker_input.upper()} complete")

            col1, col2 = st.columns([3, 2])

            with col1:
                st.subheader("📊 Analyst Consensus & Targeted Values")
                st.markdown(f"""
- **Mean Target Price:** {fmt_price(target_mean)}
- **Low / High Range:** {fmt_price(target_low)} — {fmt_price(target_high)}
- **Median Target:** {fmt_price(target_median)}
- **Number of Analysts:** {num_analysts or 'N/A'}
- **Recommendation:** **{recommendation.upper()}**
- **Expected Timeline:** 12 months
                """)

                st.subheader("📈 Key Metrics & Technicals")
                st.markdown(f"""
- **Current Price:** {fmt_price(current_price)}
- **52-Week Range:** {fmt_price(info.get('fiftyTwoWeekLow'))} — {fmt_price(info.get('fiftyTwoWeekHigh'))}
- **50-day SMA:** {fmt_price(sma50)}
- **200-day SMA:** {fmt_price(sma200)}
- **Market Cap:** ${info.get('marketCap', 0) / 1e9:.1f}B
- **Trailing P/E:** {fmt_num(info.get('trailingPE'))}
- **Forward P/E:** {fmt_num(info.get('forwardPE'))}
- **EPS (TTM):** ${fmt_num(info.get('trailingEps'))}
                """)

            with col2:
                st.subheader("📰 Recent News")
                added = False
                if news:
                    for item in news:
                        title = item.get('title')
                        publisher = item.get('publisher') or "Unknown"
                        link = item.get('link') or f"https://finance.yahoo.com/quote/{ticker_input}"
                        if title and title.lower() != "none":
                            st.markdown(f"- **{title}**  \n({publisher}) — [Read]({link})")
                            added = True
                if not added:
                    st.info(f"View live news → [Yahoo Finance](https://finance.yahoo.com/quote/{ticker_input}/news)")

                st.subheader("💡 Agent Insights")
                st.markdown(f"""
**Business Summary**  
{info.get('longBusinessSummary', 'N/A')[:500]}...

**Next catalysts**  
Next earnings ≈ {earnings_date}
                """)

            st.caption("**Disclaimer:** Educational/entertainment only. Not financial advice.")

        except Exception as e:
            if "Too Many Requests" in str(e) or "rate limit" in str(e).lower():
                st.error("⏳ Yahoo Finance is rate-limiting us right now.")
                st.info("Wait 30–60 seconds and try again.")
            else:
                st.error(f"❌ Error: {e}")

else:
    st.info("👆 Click **Analyze Stock** to get the full report")

st.markdown("---")
st.caption("Built for Phil • Powered by yfinance + Streamlit")