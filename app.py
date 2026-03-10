import streamlit as st
import yfinance as yf
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(page_title="Comparateur Boursier Pro", layout="wide")

# --- Sidebar ---
st.sidebar.title("📊 Comparaison d'Actifs")
main_ticker = st.sidebar.text_input("Action Principale", "NVDA").upper()
comp_ticker = st.sidebar.text_input("Action à Comparer", "AAPL").upper()
period = st.sidebar.selectbox("Période", ["1mo", "6mo", "1y", "2y", "5y"])

# --- Fonction de récupération ---
@st.cache_data
def get_comparison_data(ticker1, ticker2, period):
    data1 = yf.download(ticker1, period=period)
    data2 = yf.download(ticker2, period=period)
    
    # Calcul du rendement cumulé : (Prix / Premier Prix - 1) * 100
    data1['Pct_Change'] = (data1['Close'] / data1['Close'].iloc[0] - 1) * 100
    data2['Pct_Change'] = (data2['Close'] / data2['Close'].iloc[0] - 1) * 100
    return data1, data2

df1, df2 = get_comparison_data(main_ticker, comp_ticker, period)

# --- Affichage ---
st.title(f"Performance Relative : {main_ticker} vs {comp_ticker}")

# Création du graphique de comparaison
fig = go.Figure()

# Ligne Action 1
fig.add_trace(go.Scatter(
    x=df1.index, 
    y=df1['Pct_Change'],
    name=main_ticker,
    line=dict(color='#00ffcc', width=2)
))

# Ligne Action 2
fig.add_trace(go.Scatter(
    x=df2.index, 
    y=df2['Pct_Change'],
    name=comp_ticker,
    line=dict(color='#ff3366', width=2)
))

# Style du graphique
fig.update_layout(
    title=f"Croissance cumulée (%) sur la période {period}",
    xaxis_title="Date",
    yaxis_title="Variation en %",
    template="plotly_dark",
    hovermode="x unified",
    height=600
)

st.plotly_chart(fig, use_container_width=True)

# --- Métriques de performance ---
perf1 = df1['Pct_Change'].iloc[-1]
perf2 = df2['Pct_Change'].iloc[-1]

c1, c2 = st.columns(2)
c1.metric(f"Performance {main_ticker}", f"{perf1:.2f} %", delta=f"{perf1:.2f}%")
c2.metric(f"Performance {comp_ticker}", f"{perf2:.2f} %", delta=f"{perf2:.2f}%")




st.write("---")
st.subheader(f"📰 Dernières actualités pour {main_ticker}")

# Récupération des news via yfinance
ticker_obj = yf.Ticker(main_ticker)
news = ticker_obj.news[:5] # On prend les 5 dernières

if news:
    for item in news:
        with st.container():
            col_img, col_txt = st.columns([1, 4])
            # Si une image est disponible
            if 'thumbnail' in item and item['thumbnail'].get('resolutions'):
                col_img.image(item['thumbnail']['resolutions'][0]['url'])
            
            col_txt.markdown(f"**[{item['title']}]({item['link']})**")
            col_txt.caption(f"Source: {item['publisher']} | Publié le: {datetime.fromtimestamp(item['providerPublishTime']).strftime('%d/%m/%Y')}")
            st.write("")
else:
    st.info("Aucune actualité récente trouvée.")