# pages/4_🏆_Top_Ativos.py

import streamlit as st
import pandas as pd
import requests
import yfinance as yf

# ✅ MUDANÇA: Importando as listas completas do nosso novo arquivo de configuração
from ativos_config import IBOVESPA_TICKERS, SP100_TICKERS

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Top Ativos por Mercado", layout="wide")

# --- CABEÇALHO PARA API COINGECKO ---
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36'}

# --- FUNÇÕES DE BUSCA DE DADOS ---

@st.cache_data(ttl=3600) # Cache de 1 hora
def get_top_100_coins():
    """Busca a lista das top 100 moedas da CoinGecko."""
    url = "https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=100&page=1"
    try:
        response = requests.get(url, headers=HEADERS)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Erro ao acessar a API da CoinGecko: {e}")
        return None

@st.cache_data(ttl=1800) # Cache de 30 minutos
def get_multiple_stock_info(tickers, suffix=""):
    """Busca informações básicas para uma lista de tickers de ações."""
    data_list = []
    full_tickers_str = " ".join([t + suffix for t in tickers])
    
    data = yf.download(tickers=full_tickers_str, period='1d', group_by='ticker')
    
    for ticker_name in tickers:
        ticker_yf_name = ticker_name + suffix
        try:
            # Para o preço, pegamos o último fechamento do download em massa
            last_close = data[ticker_yf_name]['Close'].iloc[-1]
            
            # Buscamos o info para os outros dados
            info = yf.Ticker(ticker_yf_name).info
            
            # Pega os dados essenciais para a tabela
            data_list.append({
                'Ticker': info.get('symbol', ticker_yf_name),
                'Nome': info.get('shortName', 'N/A'),
                'Preço': last_close,
                'Variação (24h)': ((last_close / info.get('previousClose', 0)) - 1) * 100 if info.get('previousClose', 0) > 0 else 0,
                'Market Cap': info.get('marketCap', 0),
                'P/L': info.get('trailingPE')
            })
        except Exception:
            continue
            
    return pd.DataFrame(data_list)

# --- FUNÇÕES DE ESTILO ---

def format_number(number):
    if number is None or not isinstance(number, (int, float)) or pd.isna(number): return "N/A"
    if abs(number) >= 1e12: return f"{number / 1e12:.2f} T"
    if abs(number) >= 1e9: return f"{number / 1e9:.2f} B"
    if abs(number) >= 1e6: return f"{number / 1e6:.2f} M"
    return f"{number:,.2f}"

def style_change(val):
    """Colore a variação em vermelho para negativo e verde para positivo."""
    if not isinstance(val, (int, float)) or pd.isna(val): return ''
    color = 'red' if val < 0 else 'green'
    return f'color: {color}'

# --- INTERFACE PRINCIPAL ---

st.title("🏆 Top Ativos por Mercado")
st.markdown("Uma visão geral dos principais ativos em cada categoria de mercado.")

tab1, tab2, tab3 = st.tabs(["🪙 **Criptomoedas (Top 100)**", "🇧🇷 **Ações Brasil (Ibovespa)**", "🇺🇸 **Ações EUA (S&P 100)**"])

# --- ABA DE CRIPTOMOEDAS ---
with tab1:
    with st.spinner("Buscando dados das Top 100 Criptomoedas..."):
        crypto_data = get_top_100_coins()

    if crypto_data:
        df_crypto = pd.DataFrame(crypto_data)
        df_crypto_display = df_crypto[[
            'market_cap_rank', 'name', 'symbol', 'current_price',
            'price_change_percentage_24h', 'market_cap', 'total_volume'
        ]].copy()
        df_crypto_display.columns = ['Rank', 'Nome', 'Ticker', 'Preço (USD)', 'Variação (24h)', 'Market Cap', 'Volume (24h)']
        df_crypto_display['Ticker'] = df_crypto_display['Ticker'].str.upper()

        styled_df_crypto = df_crypto_display.style.format({
            'Preço (USD)': "${:,.4f}",
            'Variação (24h)': "{:.2f}%",
            'Market Cap': lambda x: f"$ {format_number(x)}",
            'Volume (24h)': lambda x: f"$ {format_number(x)}"
        }).applymap(style_change, subset=['Variação (24h)'])
        
        st.dataframe(styled_df_crypto, use_container_width=True, hide_index=True, height=600)
    else:
        st.error("Não foi possível carregar os dados das criptomoedas no momento.")

# --- ABA DE AÇÕES BRASIL ---
with tab2:
    # ✅ MUDANÇA: Usando a lista completa do Ibovespa
    with st.spinner("Buscando dados das principais ações brasileiras..."):
        df_br = get_multiple_stock_info(IBOVESPA_TICKERS, suffix=".SA")
    
    if not df_br.empty:
        df_br_display = df_br.sort_values(by='Market Cap', ascending=False)
        styled_df_br = df_br_display.style.format({
            'Preço': "R$ {:,.2f}", 'Variação (24h)': "{:.2f}%",
            'Market Cap': lambda x: f"R$ {format_number(x)}", 'P/L': "{:.2f}"
        }).applymap(style_change, subset=['Variação (24h)'])
        st.dataframe(styled_df_br, use_container_width=True, hide_index=True, height=600)
        st.caption("Nota: Lista baseada nos componentes do índice Ibovespa.")
    else:
        st.error("Não foi possível carregar os dados das ações brasileiras no momento.")

# --- ABA DE AÇÕES EUA ---
with tab3:
    # ✅ MUDANÇA: Usando a lista completa do S&P 100
    with st.spinner("Buscando dados das principais ações americanas..."):
        df_us = get_multiple_stock_info(SP100_TICKERS)
    
    if not df_us.empty:
        df_us_display = df_us.sort_values(by='Market Cap', ascending=False)
        styled_df_us = df_us_display.style.format({
            'Preço': "$ {:,.2f}", 'Variação (24h)': "{:.2f}%",
            'Market Cap': lambda x: f"$ {format_number(x)}", 'P/L': "{:.2f}"
        }).applymap(style_change, subset=['Variação (24h)'])
        st.dataframe(styled_df_us, use_container_width=True, hide_index=True, height=600)
        st.caption("Nota: Lista baseada nos componentes do índice S&P 100.")
    else:
        st.error("Não foi possível carregar os dados das ações americanas no momento.")