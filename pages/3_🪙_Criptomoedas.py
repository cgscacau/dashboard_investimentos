# pages/3_🪙_Criptomoedas.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import pandas_ta as ta
import yfinance as yf
from datetime import datetime, timedelta

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Criptomoedas", layout="wide")

# Lista de principais criptos para o selectbox
CRYPTO_LIST = {
    "Bitcoin": "BTC-USD", "Ethereum": "ETH-USD", "Tether": "USDT-USD", "BNB": "BNB-USD",
    "Solana": "SOL-USD", "XRP": "XRP-USD", "Cardano": "ADA-USD", "Dogecoin": "DOGE-USD",
    "Shiba Inu": "SHIB-USD", "Avalanche": "AVAX-USD", "Polkadot": "DOT-USD", "Chainlink": "LINK-USD"
}

# ✅ CORREÇÃO: Voltando para a função de busca da yfinance, que é mais estável
@st.cache_data(ttl=900)
def get_crypto_data(ticker):
    stock = yf.Ticker(ticker)
    try:
        info = stock.info
        hist = stock.history(period="5y")
        # Validação simples e robusta: se não há histórico, o ticker é inválido.
        if hist.empty:
            return None, None
        try: hist.index = hist.index.tz_localize(None)
        except TypeError: pass
        return info, hist
    except Exception:
        return None, None

def format_number(number, is_currency=True):
    if number is None: return "N/A"
    prefix = "$ " if is_currency else ""
    if abs(number) >= 1e12: return f"{prefix}{number / 1e12:.2f} T"
    if abs(number) >= 1e9: return f"{prefix}{number / 1e9:.2f} B"
    if abs(number) >= 1e6: return f"{prefix}{number / 1e6:.2f} M"
    return f"{prefix}{number}"

def format_crypto_price(price):
    if price is None: return "N/A"
    if price >= 1.0: return f"$ {price:,.2f}"
    if price < 1.0 and price > 0.001: return f"$ {price:,.4f}"
    return f"$ {price:,.8f}"

# --- FUNÇÕES DE ANÁLISE TÉCNICA (idênticas) ---
def interpret_rsi(rsi_value):
    if rsi_value > 70: return "Sobrecomprado", "🔴"
    if rsi_value < 30: return "Sobrevendido", "🟢"
    return "Neutro", "⚪"

def interpret_stochastic(k, d):
    if k > 80 and d > 80: return "Sobrecomprado", "🔴"
    if k < 20 and d < 20: return "Sobrevendido", "🟢"
    if k > d: return "Sinal de Alta (K > D)", "🟢"
    return "Sinal de Baixa (K < D)", "🔴"
    
def interpret_willr(willr_value):
    if willr_value > -20: return "Sobrecomprado", "🔴"
    if willr_value < -80: return "Sobrevendido", "🟢"
    return "Neutro", "⚪"

def interpret_obv(obv_series):
    if len(obv_series) < 5: return "Dados insuficientes", "⚪"
    if obv_series.iloc[-1] > obv_series.iloc[-5]: return "Acumulação (Volume confirma alta)", "🟢"
    if obv_series.iloc[-1] < obv_series.iloc[-5]: return "Distribuição (Volume confirma baixa)", "🔴"
    return "Neutro", "⚪"

def analyze_convergence(signals):
    score = 0
    for signal, _ in signals.values():
        if "Sobrecomprado" in signal or "Baixa" in signal or "Distribuição" in signal: score -= 1
        if "Sobrevendido" in signal or "Alta" in signal or "Acumulação" in signal: score += 1
    if score >= 2: return "Convergência de Sinais de ALTA.", "Sugere uma possível ZONA DE COMPRA ou continuação de tendência de alta."
    if score <= -2: return "Convergência de Sinais de BAIXA.", "Sugere uma possível ZONA DE VENDA ou continuação de tendência de baixa."
    return "Sinais DIVERGENTES ou Neutros.", "Sugere INDEFINIÇÃO ou movimento lateral do mercado. Cautela é recomendada."

# --- INTERFACE PRINCIPAL ---
st.title("🪙 Análise de Criptomoedas")
st.markdown("Selecione uma criptomoeda da lista para ver a análise.")

crypto_name = st.selectbox("Selecione a Criptomoeda:", list(CRYPTO_LIST.keys()))
ticker_input = CRYPTO_LIST[crypto_name]

if ticker_input:
    with st.spinner(f"Buscando dados para {crypto_name}..."):
        crypto_info, hist_data = get_crypto_data(ticker_input)

    if crypto_info and not hist_data.empty:
        current_price = crypto_info.get('regularMarketPrice') or hist_data['Close'].iloc[-1]
        hist_2y = hist_data.loc[hist_data.index > (datetime.now() - timedelta(days=730))].copy()

        change_pct_manual = None
        previous_close = crypto_info.get('regularMarketPreviousClose')
        if previous_close and current_price and previous_close > 0:
            change_pct_manual = ((current_price / previous_close) - 1)
        delta_text = f"{change_pct_manual * 100:.2f}%" if change_pct_manual is not None else ""
        
        st.header(f"{crypto_info.get('name', crypto_name)} ({crypto_info.get('symbol', ticker_input)})", divider='rainbow')
        cols_header = st.columns(4)
        cols_header[0].metric("Preço Atual", format_crypto_price(current_price), delta=delta_text)
        cols_header[1].metric("Market Cap", format_number(crypto_info.get('marketCap')))
        cols_header[2].metric("Volume (24h)", format_number(crypto_info.get('volume24Hr')))
        cols_header[3].metric("Rank (Market Cap)", f"#{crypto_info.get('marketCapRank', 'N/A')}")

        tab1, tab2, tab3 = st.tabs(["📜 Visão Geral & Métricas", "📊 Análise Técnica", "📄 Dados Completos"])

        with tab1:
            st.subheader("Principais Métricas")
            col_m1, col_m2, col_m3 = st.columns(3)
            col_m1.metric("Fornecimento Circulante", format_number(crypto_info.get('circulatingSupply'), is_currency=False))
            col_m2.metric("Fornecimento Total", format_number(crypto_info.get('totalSupply'), is_currency=False))
            if crypto_info.get('maxSupply'):
                col_m3.metric("Fornecimento Máximo", format_number(crypto_info.get('maxSupply'), is_currency=False))
            
            circ_supply = crypto_info.get('circulatingSupply')
            total_supply = crypto_info.get('totalSupply')
            if circ_supply and total_supply and total_supply > 0:
                st.subheader("Distribuição do Fornecimento")
                supply_data = pd.DataFrame({'Categoria': ['Em Circulação', 'Não Circulante'], 'Valor': [circ_supply, total_supply - circ_supply]})
                fig_pie = go.Figure(data=[go.Pie(labels=supply_data['Categoria'], values=supply_data['Valor'], hole=.3)])
                fig_pie.update_layout(title_text='Fornecimento Circulante vs. Total', height=350)
                st.plotly_chart(fig_pie, use_container_width=True)
            else:
                st.info("Gráfico de distribuição indisponível por falta de dados de fornecimento (circulante e/ou total) na API.")

            st.subheader("Descrição")
            description_text = crypto_info.get('description')
            if description_text and description_text.strip():
                st.info(description_text)
            else:
                st.info("Descrição não disponível para esta criptomoeda.")
            
        with tab2:
            hist_2y.ta.stoch(append=True); hist_2y.ta.willr(append=True); hist_2y.ta.obv(append=True)
            hist_2y['RSI'] = ta.rsi(hist_2y['Close'], length=14)
            hist_2y['SMA20'] = ta.sma(hist_2y['Close'], length=20); hist_2y['SMA50'] = ta.sma(hist_2y['Close'], length=50)

            fig_price = go.Figure(data=[go.Candlestick(x=hist_2y.index, open=hist_2y['Open'], high=hist_2y['High'], low=hist_2y['Low'], close=hist_2y['Close'], name='Candlestick')])
            fig_price.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['SMA20'], mode='lines', name='MMS 20', line=dict(color='orange', width=1.5)))
            fig_price.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['SMA50'], mode='lines', name='MMS 50', line=dict(color='purple', width=1.5)))
            fig_price.update_layout(title=f'Gráfico de Preços para {crypto_name} (Últimos 2 Anos)', yaxis_title='Preço ($)', xaxis_rangeslider_visible=False, height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1))
            st.plotly_chart(fig_price, use_container_width=True)

            col_ind1, col_ind2 = st.columns(2)
            with col_ind1:
                fig_rsi = go.Figure(); fig_rsi.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['RSI'], name='RSI', line=dict(color='royalblue'))); fig_rsi.add_hline(y=70, line_dash="dash", line_color="red"); fig_rsi.add_hline(y=30, line_dash="dash", line_color="green"); fig_rsi.update_layout(title="Índice de Força Relativa (RSI)", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_rsi, use_container_width=True)
                fig_stoch = go.Figure(); fig_stoch.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['STOCHk_14_3_3'], name='%K', line=dict(color='blue'))); fig_stoch.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['STOCHd_14_3_3'], name='%D', line=dict(color='red'))); fig_stoch.add_hline(y=80, line_dash="dash", line_color="red"); fig_stoch.add_hline(y=20, line_dash="dash", line_color="green"); fig_stoch.update_layout(title="Oscilador Estocástico", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_stoch, use_container_width=True)

            with col_ind2:
                fig_willr = go.Figure(); fig_willr.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['WILLR_14'], name='Williams %R', line=dict(color='purple'))); fig_willr.add_hline(y=-20, line_dash="dash", line_color="red"); fig_willr.add_hline(y=-80, line_dash="dash", line_color="green"); fig_willr.update_layout(title="Williams %R", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_willr, use_container_width=True)
                fig_obv = go.Figure(); fig_obv.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['OBV'], name='OBV', line=dict(color='green'))); fig_obv.update_layout(title="On-Balance Volume (OBV)", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_obv, use_container_width=True)
            
            st.markdown("---")
            st.subheader("Interpretação e Convergência dos Indicadores")
            signals = {"RSI": interpret_rsi(hist_2y['RSI'].iloc[-1]), "Estocástico": interpret_stochastic(hist_2y['STOCHk_14_3_3'].iloc[-1], hist_2y['STOCHd_14_3_3'].iloc[-1]),"Williams %R": interpret_willr(hist_2y['WILLR_14'].iloc[-1]),"OBV": interpret_obv(hist_2y['OBV'])}
            cols_interp = st.columns(4)
            for i, (indicator, (text, emoji)) in enumerate(signals.items()): cols_interp[i].metric(label=f"{indicator} {emoji}", value=text)
            
            conclusion, recommendation = analyze_convergence(signals)
            st.markdown(f"### Conclusão da Análise Técnica: {conclusion}")
            st.markdown(f"<p style='font-size: 20px;'>{recommendation}</p>", unsafe_allow_html=True)
            st.caption("Atenção: Esta é uma análise técnica automatizada e não constitui uma recomendação de investimento.")
        
        with tab3:
            st.subheader("Dados Gerais (JSON)")
            st.info("Estes são todos os dados gerais sobre o ativo retornados pela API yfinance.")
            st.json(crypto_info)

            st.subheader("Histórico de Preços (Tabela)")
            st.info("Tabela completa com o histórico dos últimos 5 anos.")
            st.dataframe(hist_data.sort_index(ascending=False), use_container_width=True)
            
    else:
        st.error(f"Não foi possível encontrar dados para o ticker '{ticker_input}'. Verifique se o ticker está correto ou tente novamente.")
