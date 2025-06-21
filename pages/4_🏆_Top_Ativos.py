# pages/4_🏆_Top_Ativos.py

import streamlit as st
import pandas as pd
import requests
import yfinance as yf
import time # Importa a biblioteca de tempo

from ativos_config import IBOVESPA_TICKERS, SP100_TICKERS

st.set_page_config(page_title="Top Ativos por Mercado", layout="wide")

HEADERS = {'User-Agent': 'Mozilla/5.0'}

@st.cache_data(ttl=3600)
def get_top_100_coins():
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao acessar a API da CoinGecko: {e}")
        return None

@st.cache_data(ttl=1800)
def get_multiple_stock_info(tickers, suffix=""):
    data_list = []
    
    for ticker_name in tickers:
        ticker_yf_name = ticker_name + suffix
        try:
            info = yf.Ticker(ticker_yf_name).info
            data_list.append({
                'Ticker': info.get('symbol', ticker_yf_name),
                'Nome': info.get('shortName', 'N/A'),
                'Preço': info.get('currentPrice', 0),
                'Variação (24h)': info.get('regularMarketChangePercent', 0) * 100,
                'Market Cap': info.get('marketCap', 0),
                'P/L': info.get('trailingPE')
            })
            # ✅ CORREÇÃO: Pausa de 0.1 segundos para não sobrecarregar a API
            time.sleep(0.1)
        except Exception:
            continue
            
    return pd.DataFrame(data_list)

def format_number(number):
    if number is None or not isinstance(number, (int, float)) or pd.isna(number): return "N/A"
    if abs(number) >= 1e12: return f"{number / 1e12:.2f} T"
    if abs(number) >= 1e9: return f"{number / 1e9:.2f} B"
    if abs(number) >= 1e6: return f"{number / 1e6:.2f} M"
    return f"{number:,.2f}"

def style_change(val):
    if not isinstance(val, (int, float)) or pd.isna(val): return ''
    color = 'red' if val < 0 else 'green'
    return f'color: {color}'

st.title("🏆 Top Ativos por Mercado")
st.markdown("Uma visão geral dos principais ativos em cada categoria de mercado.")

tab1, tab2, tab3 = st.tabs(["🪙 **Criptomoedas (Top 100)**", "🇧🇷 **Ações Brasil (Ibovespa)**", "🇺🇸 **Ações EUA (S&P 100)**"])

with tab1:
    with st.spinner("Buscando dados das Top 100 Criptomoedas..."): crypto_data = get_top_100_coins()
    if crypto_data:
        df_crypto = pd.DataFrame(crypto_data); df_crypto_display = df_crypto[['market_cap_rank', 'name', 'symbol', 'current_price', 'price_change_percentage_24h', 'market_cap', 'total_volume']].copy(); df_crypto_display.columns = ['Rank', 'Nome', 'Ticker', 'Preço (USD)', 'Variação (24h)', 'Market Cap', 'Volume (24h)']; df_crypto_display['Ticker'] = df_crypto_display['Ticker'].str.upper()
        styled_df_crypto = df_crypto_display.style.format({'Preço (USD)': "${:,.4f}", 'Variação (24h)': "{:.2f}%", 'Market Cap': lambda x: f"$ {format_number(x)}", 'Volume (24h)': lambda x: f"$ {format_number(x)}"}).applymap(style_change, subset=['Variação (24h)'])
        st.dataframe(styled_df_crypto, use_container_width=True, hide_index=True, height=600)
    else: st.error("Não foi possível carregar os dados das criptomoedas no momento.")

with tab2:
    with st.spinner("Buscando dados das principais ações brasileiras..."): df_br = get_multiple_stock_info(IBOVESPA_TICKERS, suffix=".SA")
    if not df_br.empty:
        df_br_display = df_br.sort_values(by='Market Cap', ascending=False); styled_df_br = df_br_display.style.format({'Preço': "R$ {:,.2f}", 'Variação (24h)': "{:.2f}%", 'Market Cap': lambda x: f"R$ {format_number(x)}", 'P/L': "{:.2f}"}).applymap(style_change, subset=['Variação (24h)'])
        st.dataframe(styled_df_br, use_container_width=True, hide_index=True, height=600); st.caption("Nota: Lista baseada nos componentes do índice Ibovespa.")
    else: st.error("Não foi possível carregar os dados das ações brasileiras no momento.")

with tab3:
    with st.spinner("Buscando dados das principais ações americanas..."): df_us = get_multiple_stock_info(SP100_TICKERS)
    if not df_us.empty:
        df_us_display = df_us.sort_values(by='Market Cap', ascending=False); styled_df_us = df_us_display.style.format({'Preço': "$ {:,.2f}", 'Variação (24h)': "{:.2f}%", 'Market Cap': lambda x: f"$ {format_number(x)}", 'P/L': "{:.2f}"}).applymap(style_change, subset=['Variação (24h)'])
        st.dataframe(styled_df_us, use_container_width=True, hide_index=True, height=600); st.caption("Nota: Lista baseada nos componentes do índice S&P 100.")
    else: st.error("Não foi possível carregar os dados das ações americanas no momento.")
