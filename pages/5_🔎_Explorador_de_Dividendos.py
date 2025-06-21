# pages/5_🔎_Explorador_de_Dividendos.py

import streamlit as st
import pandas as pd
import yfinance as yf
import time
from ativos_config import BRAZIL_DIVIDEND_STOCKS, US_DIVIDEND_STOCKS

st.set_page_config(page_title="Explorador de Dividendos", layout="wide")

# ✅ CORREÇÃO: Função que usa a mesma lógica otimizada
@st.cache_data(ttl=1800)
def get_stock_details(tickers, suffix=""):
    data_list = []
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker + suffix).info
            data_list.append({
                'Ticker': info.get('symbol', ticker), 'Nome': info.get('shortName', 'N/A'),
                'Setor': info.get('sector', 'N/A'), 'Preço': info.get('currentPrice', 0),
                'Dividend Yield (%)': (info.get('trailingAnnualDividendYield', 0) * 100),
                'P/L': info.get('trailingPE')
            })
            time.sleep(1) # Pausa de segurança um pouco maior aqui
        except Exception:
            continue
    return pd.DataFrame(data_list)

def style_yield(val):
    if not isinstance(val, (int, float)): return ''
    if val > 8: color = 'green'
    elif val > 4: color = 'orange'
    else: color = 'black'
    return f'color: {color}; font-weight: bold;'

st.title("🔎 Explorador de Boas Pagadoras de Dividendos")
st.markdown("Descubra ativos com histórico de bom pagamento de dividendos em diferentes mercados.")
tab1, tab2 = st.tabs(["🇺🇸 **Ações EUA (Lista Curada)**", "🇧🇷 **Ações Brasil (Lista Curada)**"])

with tab1:
    st.subheader("Principais Empresas Pagadoras de Dividendos dos EUA")
    st.markdown("A lista abaixo é uma **seleção curada** de empresas americanas conhecidas pelo bom histórico de pagamento de dividendos (ex: 'Dividend Aristocrats').")
    with st.spinner("Buscando dados das ações americanas..."):
        df_us = get_stock_details(US_DIVIDEND_STOCKS)
    if df_us is not None and not df_us.empty:
        df_us_display = df_us.sort_values(by='Dividend Yield (%)', ascending=False)
        styled_df_us = df_us_display.style.format({'Preço': "$ {:,.2f}", 'Dividend Yield (%)': "{:.2f}%", 'P/L': "{:.2f}"}).map(style_yield, subset=['Dividend Yield (%)'])
        st.dataframe(styled_df_us, use_container_width=True, hide_index=True, height=600)
    else: st.error("Não foi possível carregar os dados das ações americanas no momento.")

with tab2:
    st.subheader("Principais Empresas Pagadoras de Dividendos do Brasil")
    st.markdown("A lista abaixo é uma **seleção curada** de empresas brasileiras conhecidas pelo bom histórico de pagamento de dividendos.")
    with st.spinner("Buscando dados das ações brasileiras..."):
        df_br = get_stock_details(BRAZIL_DIVIDEND_STOCKS, suffix=".SA")
    if not df_br.empty:
        df_br_display = df_br.sort_values(by='Dividend Yield (%)', ascending=False)
        styled_df_br = df_br_display.style.format({'Preço': "R$ {:,.2f}", 'Dividend Yield (%)': "{:.2f}%", 'P/L': "{:.2f}"}).map(style_yield, subset=['Dividend Yield (%)'])
        st.dataframe(styled_df_br, use_container_width=True, hide_index=True, height=600)
    else: st.error("Não foi possível carregar os dados das ações brasileiras no momento.")
