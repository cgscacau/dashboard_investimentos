import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta
import numpy as np

st.set_page_config(page_title="Mercado Brasileiro", layout="wide")

# ============================== Funções ==============================

@st.cache_data(ttl=1800)
def get_stock_data(ticker):
    url = f"https://brapi.dev/api/quote/{ticker}?range=5y&interval=1d&fundamental=true"
    r = requests.get(url)
    if r.status_code != 200:
        return None, None
    data = r.json()
    if not data.get('results'):
        return None, None
    info = data['results'][0]

    prices = info.get('historicalDataPrice', [])
    if not prices:
        return info, None

    df = pd.DataFrame(prices)
    df['date'] = pd.to_datetime(df['date'])
    df = df.set_index('date').sort_index()
    return info, df


def format_number(value):
    if value is None:
        return "N/A"
    if value >= 1e9:
        return f"R$ {value/1e9:.2f} B"
    if value >= 1e6:
        return f"R$ {value/1e6:.2f} M"
    return f"R$ {value:.2f}"


def calculate_rsi(data, period=14):
    delta = data['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))


def calculate_stochastic(data, period=14):
    low_min = data['low'].rolling(window=period).min()
    high_max = data['high'].rolling(window=period).max()
    k = 100 * (data['close'] - low_min) / (high_max - low_min)
    d = k.rolling(window=3).mean()
    return k, d


def calculate_willr(data, period=14):
    high_max = data['high'].rolling(window=period).max()
    low_min = data['low'].rolling(window=period).min()
    return -100 * (high_max - data['close']) / (high_max - low_min)


def calculate_obv(data):
    direction = np.sign(data['close'].diff().fillna(0))
    return (direction * data['volume']).cumsum()


def calculate_sma(data, period):
    return data['close'].rolling(window=period).mean()


def interpret_rsi(value):
    if value > 70:
        return "Sobrecomprado", "🔴"
    if value < 30:
        return "Sobrevendido", "🟢"
    return "Neutro", "⚪"


def interpret_stochastic(k, d):
    if k > 80 and d > 80:
        return "Sobrecomprado", "🔴"
    if k < 20 and d < 20:
        return "Sobrevendido", "🟢"
    if k > d:
        return "Sinal de Alta", "🟢"
    return "Sinal de Baixa", "🔴"


def interpret_willr(value):
    if value > -20:
        return "Sobrecomprado", "🔴"
    if value < -80:
        return "Sobrevendido", "🟢"
    return "Neutro", "⚪"


def interpret_obv(obv):
    if len(obv) < 5:
        return "Dados insuficientes", "⚪"
    if obv.iloc[-1] > obv.iloc[-5]:
        return "Acumulação", "🟢"
    if obv.iloc[-1] < obv.iloc[-5]:
        return "Distribuição", "🔴"
    return "Neutro", "⚪"


def analyze_convergence(signals):
    score = 0
    for signal, _ in signals.values():
        if "Sobrecomprado" in signal or "Baixa" in signal or "Distribuição" in signal:
            score -= 1
        if "Sobrevendido" in signal or "Alta" in signal or "Acumulação" in signal:
            score += 1
    if score >= 2:
        return "🔼 Convergência de Sinais de ALTA", "🟢 Possível zona de COMPRA"
    if score <= -2:
        return "🔽 Convergência de Sinais de BAIXA", "🔴 Possível zona de VENDA"
    return "⏸️ Sinais neutros ou divergentes", "⚪ Mercado indefinido"


def get_valuation(info, price):
    eps = info.get('earningsPerShare')
    bvps = info.get('bookValue')
    if eps and bvps:
        fair_value = (22.5 * eps * bvps) ** 0.5
        return fair_value
    return None


# ============================ Interface ==============================

st.title("🇧🇷 Mercado Brasileiro — Análise Completa")

ticker = st.text_input("Digite o ticker (Ex.: ITSA4, PETR4, BBAS3, EGIE3):", "ITSA4").upper()

if ticker:
    with st.spinner(f"Buscando dados de {ticker}..."):
        info, df = get_stock_data(ticker)

    if info:
        # ========= Dados Básicos =========
        current_price = info.get("regularMarketPrice")
        long_name = info.get("longName", ticker)
        sector = info.get("sector", "N/A")
        dy = info.get("dividendYield") or 0
        market_cap = info.get("marketCap")
        week52high = info.get("fiftyTwoWeekHigh")
        week52low = info.get("fiftyTwoWeekLow")

        st.header(f"{long_name} ({ticker})", divider="rainbow")

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Preço Atual", f"R$ {current_price:.2f}" if current_price else "N/A")
        col2.metric("Setor", sector)
        col3.metric("Dividend Yield", f"{dy:.2f}%" if dy else "N/A")
        col4.metric("Valor de Mercado", format_number(market_cap))

        col5, col6 = st.columns(2)
        col5.metric("Mín. 52 Semanas", f"R$ {week52low:.2f}" if week52low else "N/A")
        col6.metric("Máx. 52 Semanas", f"R$ {week52high:.2f}" if week52high else "N/A")

        tab1, tab2, tab3 = st.tabs(["📈 Gráfico de Preço", "📊 Análise Técnica", "📜 Dados Fundamentais"])

        # ========= Gráfico =========
        with tab1:
            if df is not None:
                df['SMA20'] = calculate_sma(df, 20)
                df['SMA50'] = calculate_sma(df, 50)

                fig = go.Figure()
                fig.add_trace(go.Candlestick(
                    x=df.index,
                    open=df['open'],
                    high=df['high'],
                    low=df['low'],
                    close=df['close'],
                    name='Candlestick'
                ))
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['SMA20'], name="Média 20", line=dict(color='blue')
                ))
                fig.add_trace(go.Scatter(
                    x=df.index, y=df['SMA50'], name="Média 50", line=dict(color='orange')
                ))

                fig.update_layout(title=f'{ticker} — Últimos 5 anos',
                                  xaxis_rangeslider_visible=False,
                                  height=500)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("Histórico não disponível para este ativo.")

        # ========= Análise Técnica =========
        with tab2:
            if df is not None:
                df['RSI'] = calculate_rsi(df)
                df['STOCHk'], df['STOCHd'] = calculate_stochastic(df)
                df['WILLR'] = calculate_willr(df)
                df['OBV'] = calculate_obv(df)

                signals = {
                    "RSI": interpret_rsi(df['RSI'].iloc[-1]),
                    "Estocástico": interpret_stochastic(df['STOCHk'].iloc[-1], df['STOCHd'].iloc[-1]),
                    "Williams %R": interpret_willr(df['WILLR'].iloc[-1]),
                    "OBV": interpret_obv(df['OBV']),
                }

                cols = st.columns(4)
                for i, (ind, (text, emoji)) in enumerate(signals.items()):
                    cols[i].metric(ind, text, emoji)

                conclusion, recommendation = analyze_convergence(signals)
                st.subheader(conclusion)
                st.markdown(f"### {recommendation}")

            else:
                st.warning("Dados insuficientes para análise técnica.")

        # ========= Dados Fundamentais =========
        with tab3:
            st.subheader("📜 Dados Fundamentais")
            st.json(info)

            fair_value = get_valuation(info, current_price)
            if fair_value:
                upside = (fair_value / current_price - 1) * 100
                st.subheader("📊 Valuation - Benjamin Graham")
                st.write(f"Valor Justo: **R$ {fair_value:.2f}**")
                st.write(f"Potencial: **{'🔼' if upside > 0 else '🔽'} {upside:.2f}%**")
            else:
                st.info("Não foi possível calcular valuation com os dados disponíveis.")

    else:
        st.error(f"Não foi possível obter dados para o ticker {ticker}. Verifique se está correto.")
