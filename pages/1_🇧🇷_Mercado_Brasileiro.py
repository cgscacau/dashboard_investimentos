# pages/1_🇧🇷_Mercado_Brasileiro.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import requests
from datetime import datetime, timedelta

st.set_page_config(page_title="Mercado Brasileiro", layout="wide")

# Tradução de setores
SECTOR_TRANSLATIONS = {
    "Financial Services": "Serviços Financeiros", "Consumer Cyclical": "Consumo Cíclico",
    "Industrials": "Industrial", "Technology": "Tecnologia", "Healthcare": "Saúde",
    "Energy": "Energia", "Utilities": "Utilidades Públicas", "Basic Materials": "Materiais Básicos",
    "Consumer Defensive": "Consumo Defensivo", "Real Estate": "Imobiliário",
    "Communication Services": "Serviços de Comunicação", "Conglomerates": "Conglomerados"
}

# ====== 🔥 Funções Auxiliares 🔥 ======

@st.cache_data(ttl=1800)
def get_stock_data(ticker):
    try:
        url = f"https://brapi.dev/api/quote/{ticker}?range=5y&interval=1d&fundamental=true"
        response = requests.get(url)
        if response.status_code != 200:
            return None, None
        data = response.json()['results'][0]

        info = {
            'longName': data.get('longName', ''),
            'symbol': data.get('symbol', ''),
            'currentPrice': data.get('regularMarketPrice'),
            'previousClose': data.get('regularMarketPreviousClose'),
            'fiftyTwoWeekHigh': data.get('fiftyTwoWeekHigh'),
            'fiftyTwoWeekLow': data.get('fiftyTwoWeekLow'),
            'marketCap': data.get('marketCap'),
            'trailingPE': data.get('priceEarnings'),
            'priceToBook': data.get('priceToBook'),
            'trailingAnnualDividendYield': data.get('dividendYield'),
            'returnOnEquity': data.get('roe'),
            'debtToEquity': data.get('debtToEquity'),
            'sector': data.get('sector'),
            'industry': data.get('sector'),
            'longBusinessSummary': data.get('description'),
        }

        candles = data.get('historicalDataPrice', [])
        hist = pd.DataFrame(candles)
        hist['date'] = pd.to_datetime(hist['date'])
        hist.set_index('date', inplace=True)
        hist.rename(columns={
            'open': 'Open', 'close': 'Close',
            'high': 'High', 'low': 'Low',
            'volume': 'Volume', 'dividends': 'Dividends'
        }, inplace=True)
        hist = hist.sort_index()

        return info, hist
    except Exception as e:
        st.error(f"Erro ao buscar dados: {e}")
        return None, None

def format_number(number, is_currency=True):
    if number is None:
        return "N/A"
    prefix = "R$ " if is_currency else ""
    if abs(number) >= 1e9:
        return f"{prefix}{number / 1e9:.2f} B"
    if abs(number) >= 1e6:
        return f"{prefix}{number / 1e6:.2f} M"
    return f"{prefix}{number:.2f}"

# ====== 🔥 Indicadores Técnicos 🔥 ======

def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_stochastic(data, period=14, k_smooth=3, d_smooth=3):
    low_min = data['Low'].rolling(window=period).min()
    high_max = data['High'].rolling(window=period).max()
    k = 100 * (data['Close'] - low_min) / (high_max - low_min)
    return k.rolling(window=k_smooth).mean(), k.rolling(window=k_smooth).mean().rolling(window=d_smooth).mean()

def calculate_willr(data, period=14):
    low_min = data['Low'].rolling(window=period).min()
    high_max = data['High'].rolling(window=period).max()
    return -100 * (high_max - data['Close']) / (high_max - low_min)

def calculate_obv(data):
    return (data['Volume'] * (~data['Close'].diff().le(0) * 2 - 1)).cumsum()

# ====== 🔥 Interpretações 🔥 ======

def interpret_rsi(rsi_value):
    if rsi_value > 70:
        return "Sobrecomprado", "🔴"
    if rsi_value < 30:
        return "Sobrevendido", "🟢"
    return "Neutro", "⚪"

def interpret_stochastic(k, d):
    if k is None or d is None:
        return "N/A", "⚪"
    if k > 80 and d > 80:
        return "Sobrecomprado", "🔴"
    if k < 20 and d < 20:
        return "Sobrevendido", "🟢"
    if k > d:
        return "Sinal de Alta", "🟢"
    return "Sinal de Baixa", "🔴"

def interpret_willr(willr_value):
    if willr_value > -20:
        return "Sobrecomprado", "🔴"
    if willr_value < -80:
        return "Sobrevendido", "🟢"
    return "Neutro", "⚪"

def interpret_obv(obv_series):
    if len(obv_series) < 5:
        return "Dados insuficientes", "⚪"
    if obv_series.iloc[-1] > obv_series.iloc[-5]:
        return "Acumulação", "🟢"
    if obv_series.iloc[-1] < obv_series.iloc[-5]:
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
        return "Convergência de Sinais de ALTA.", "Sugere uma possível ZONA DE COMPRA."
    if score <= -2:
        return "Convergência de Sinais de BAIXA.", "Sugere uma possível ZONA DE VENDA."
    return "Sinais DIVERGENTES ou Neutros.", "Sugere INDEFINIÇÃO ou movimento lateral."

# ========================================

# 🔥 Interface Streamlit 🔥
st.title("🇧🇷 Análise de Ativos Brasileiros (Ações, FIIs, ETFs)")
st.markdown("Pesquise um ativo da B3 (ex: PETR4, ITSA4, BBAS3)")

ticker_input = st.text_input("Digite o Ticker do Ativo:", "ITSA4").upper()

if ticker_input:
    with st.spinner(f"Buscando dados para {ticker_input}..."):
        stock_info, hist_data = get_stock_data(ticker_input)

    if stock_info and not hist_data.empty:
        current_price = stock_info.get('currentPrice') or hist_data['Close'].iloc[-1]
        sector_pt = SECTOR_TRANSLATIONS.get(
            stock_info.get('industry', stock_info.get('sector', 'N/A')),
            stock_info.get('industry', stock_info.get('sector', 'N/A'))
        )

        hist_2y = hist_data.loc[hist_data.index > (datetime.now() - timedelta(days=730))].copy()

        previous_close = stock_info.get('previousClose')
        change_pct_manual = None
        if previous_close and current_price and previous_close > 0:
            change_pct_manual = ((current_price / previous_close) - 1)

        delta_text = f"{change_pct_manual * 100:.2f}%" if change_pct_manual is not None else ""

        st.header(f"{stock_info.get('longName', 'N/A')} ({stock_info.get('symbol', 'N/A')})", divider='rainbow')
        cols_header = st.columns(4)
        cols_header[0].metric("Preço Atual", f"R$ {current_price:.2f}", delta=delta_text)
        cols_header[1].metric("Setor", sector_pt)
        cols_header[2].metric("Mín. 52 Semanas", f"R$ {stock_info.get('fiftyTwoWeekLow', 0):.2f}")
        cols_header[3].metric("Máx. 52 Semanas", f"R$ {stock_info.get('fiftyTwoWeekHigh', 0):.2f}")

        # ==== 🔥 ABA DE ANÁLISE TÉCNICA 🔥 ====
        st.subheader("📊 Análise Técnica Avançada")

        hist_2y['RSI'] = calculate_rsi(hist_2y)
        hist_2y['STOCHk'], hist_2y['STOCHd'] = calculate_stochastic(hist_2y)
        hist_2y['WILLR'] = calculate_willr(hist_2y)
        hist_2y['OBV'] = calculate_obv(hist_2y)
        hist_2y['SMA20'] = hist_2y['Close'].rolling(window=20).mean()
        hist_2y['SMA50'] = hist_2y['Close'].rolling(window=50).mean()

        fig_price = go.Figure(data=[
            go.Candlestick(
                x=hist_2y.index,
                open=hist_2y['Open'],
                high=hist_2y['High'],
                low=hist_2y['Low'],
                close=hist_2y['Close'],
                name='Candlestick'
            ),
            go.Scatter(x=hist_2y.index, y=hist_2y['SMA20'], mode='lines', name='MMS 20'),
            go.Scatter(x=hist_2y.index, y=hist_2y['SMA50'], mode='lines', name='MMS 50')
        ])

        fig_price.update_layout(
            title=f'Gráfico de Preços para {ticker_input} (Últimos 2 Anos)',
            yaxis_title='Preço (R$)',
            xaxis_rangeslider_visible=False,
            height=400
        )
        st.plotly_chart(fig_price, use_container_width=True)

        col_ind1, col_ind2 = st.columns(2)

        with col_ind1:
            fig_rsi = go.Figure()
            fig_rsi.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['RSI'], name='RSI'))
            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
            fig_rsi.update_layout(title="Índice de Força Relativa (RSI)", height=250)
            st.plotly_chart(fig_rsi, use_container_width=True)

            fig_stoch = go.Figure()
            fig_stoch.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['STOCHk'], name='%K'))
            fig_stoch.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['STOCHd'], name='%D'))
            fig_stoch.add_hline(y=80, line_dash="dash", line_color="red")
            fig_stoch.add_hline(y=20, line_dash="dash", line_color="green")
            fig_stoch.update_layout(title="Oscilador Estocástico", height=250)
            st.plotly_chart(fig_stoch, use_container_width=True)

        with col_ind2:
            fig_willr = go.Figure()
            fig_willr.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['WILLR'], name='Williams %R'))
            fig_willr.add_hline(y=-20, line_dash="dash", line_color="red")
            fig_willr.add_hline(y=-80, line_dash="dash", line_color="green")
            fig_willr.update_layout(title="Williams %R", height=250)
            st.plotly_chart(fig_willr, use_container_width=True)

            fig_obv = go.Figure()
            fig_obv.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['OBV'], name='OBV'))
            fig_obv.update_layout(title="On-Balance Volume (OBV)", height=250)
            st.plotly_chart(fig_obv, use_container_width=True)

        st.markdown("---")
        st.subheader("Interpretação e Convergência dos Indicadores")

        signals = {
            "RSI": interpret_rsi(hist_2y['RSI'].iloc[-1]),
            "Estocástico": interpret_stochastic(hist_2y['STOCHk'].iloc[-1], hist_2y['STOCHd'].iloc[-1]),
            "Williams %R": interpret_willr(hist_2y['WILLR'].iloc[-1]),
            "OBV": interpret_obv(hist_2y['OBV'])
        }

        cols_interp = st.columns(4)
        _ = [cols_interp[i].metric(label=f"{indicator} {emoji}", value=text) for i, (indicator, (text, emoji)) in enumerate(signals.items())]

        conclusion, recommendation = analyze_convergence(signals)
        st.markdown(f"### Conclusão da Análise Técnica: {conclusion}")
        st.markdown(f"<p style='font-size: 20px;'>{recommendation}</p>", unsafe_allow_html=True)

    else:
        st.error(f"Não foi possível encontrar dados para '{ticker_input}'. Verifique o ticker e tente novamente.")
