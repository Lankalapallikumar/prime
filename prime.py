import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Market Sentiment vs Trader Performance", layout="wide")
st.title("📊 Market Sentiment vs Trader Performance Dashboard")

sentiment_file = st.file_uploader("Upload Bitcoin Market Sentiment CSV", type=['csv'])
trader_file = st.file_uploader("Upload Historical Trader Data CSV", type=['csv'])

if sentiment_file and trader_file:
    sentiment_df = pd.read_csv(sentiment_file)
    trader_df = pd.read_csv(trader_file)

    sentiment_df['date'] = pd.to_datetime(sentiment_df['date'])
    trader_df['Timestamp IST'] = pd.to_datetime(trader_df['Timestamp IST'], format='%d-%m-%Y %H:%M')
    trader_df['date'] = pd.to_datetime(trader_df['Timestamp IST'].dt.date)

    merged_df = pd.merge(trader_df, sentiment_df[['date', 'classification']], on='date', how='left')
    merged_df = merged_df.dropna(subset=['classification'])

    st.subheader("📈 PnL by Sentiment")
    fig1, ax1 = plt.subplots()
    sns.boxplot(data=merged_df, x='classification', y='Closed PnL', ax=ax1)
    st.pyplot(fig1)

    st.subheader("⚖️ Leverage (Start Position) by Sentiment")
    fig2, ax2 = plt.subplots()
    sns.violinplot(data=merged_df, x='classification', y='Start Position', ax=ax2)
    st.pyplot(fig2)

    st.subheader("🧭 Trade Side Distribution")
    side_sentiment = merged_df.groupby(['classification', 'Side']).size().reset_index(name='count')
    fig3, ax3 = plt.subplots()
    sns.barplot(data=side_sentiment, x='classification', y='count', hue='Side', ax=ax3)
    st.pyplot(fig3)

    avg_pnl = merged_df.groupby('classification')['Closed PnL'].mean()
    leverage_stats = merged_df.groupby('classification')['Start Position'].describe()
    side_dist = merged_df.groupby(['classification', 'Side']).size().unstack(fill_value=0)

    st.subheader("💡 Insights for Smarter Strategies")

    if avg_pnl['Greed'] > avg_pnl['Fear']:
        st.success(f"Higher PnL on Greed days: {avg_pnl['Greed']:.2f} vs Fear: {avg_pnl['Fear']:.2f}")
        st.write("💡 Strategy: Consider more aggressive long positions on Greed days.")
    else:
        st.success(f"Higher PnL on Fear days: {avg_pnl['Fear']:.2f} vs Greed: {avg_pnl['Greed']:.2f}")
        st.write("💡 Strategy: Consider contrarian or defensive strategies on Greed days.")

    if leverage_stats.loc['Greed']['mean'] > leverage_stats.loc['Fear']['mean']:
        st.info("Traders use higher leverage on Greed days. Caution recommended to avoid large losses.")
    else:
        st.info("Higher leverage observed on Fear days. May indicate panic trading; caution advised.")

    buy_greed = side_dist.loc['Greed'].get('BUY', 0)
    sell_greed = side_dist.loc['Greed'].get('SELL', 0)
    buy_fear = side_dist.loc['Fear'].get('BUY', 0)
    sell_fear = side_dist.loc['Fear'].get('SELL', 0)

    st.write(f"Greed Days — BUY: {buy_greed}, SELL: {sell_greed}")
    st.write(f"Fear Days — BUY: {buy_fear}, SELL: {sell_fear}")

    st.subheader("🏆 Top Performing Accounts by Sentiment")
    top_traders = merged_df.groupby(['Account', 'classification'])['Closed PnL'].sum().reset_index()
    for sentiment in ['Fear', 'Greed']:
        st.markdown(f"**{sentiment} Days**")
        st.dataframe(
            top_traders[top_traders['classification'] == sentiment]
            .sort_values('Closed PnL', ascending=False).head(3)
        )

    csv = merged_df.to_csv(index=False).encode('utf-8')
    st.download_button("📥 Download Merged Dataset", data=csv, file_name="merged_trader_sentiment.csv")
