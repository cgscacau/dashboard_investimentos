# pages/5_🔎_Explorador_de_Dividendos.py

import streamlit as st
import pandas as pd
import yfinance as yf

# ✅ MUDANÇA: Importando AMBAS as listas de dividendos do nosso arquivo de configuração
from ativos_config import BRAZIL_DIVIDEND_STOCKS, US_DIVIDEND_STOCKS

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Explorador de Dividendos", layout="wide")

# --- FUNÇÕES DE BUSCA DE DADOS ---

# ✅ MUDANÇA: Simplificamos para usar apenas uma função robusta com yfinance
@st.cache_data(ttl=1800) # Cache de 30 minutos
def get_stock_details(tickers, suffix=""):
    """Busca informações detalhadas para uma lista de tickers usando yfinance."""
    data_list = []
    
    for ticker in tickers:
        try:
            info = yf.Ticker(ticker + suffix).info
            # Pega os dados essenciais para a tabela de dividendos
            data_list.append({
                'Ticker': info.get('symbol', ticker),
                'Nome': info.get('shortName', 'N/A'),
                'Setor': info.get('sector', 'N/A'),
                'Preço': info.get('currentPrice', 0),
                'Dividend Yield (%)': (info.get('trailingAnnualDividendYield', 0) * 100),
                'P/L': info.get('trailingPE')
            })
        except Exception:
            continue
            
    return pd.DataFrame(data_list)

# --- FUNÇÕES DE ESTILO ---
def style_yield(val):
    """Colore o yield baseado no seu valor."""
    if not isinstance(val, (int, float)): return ''
    if val > 8: color = 'green'
    elif val > 4: color = 'orange'
    else: color = 'black'
    return f'color: {color}; font-weight: bold;'

# --- INTERFACE PRINCIPAL ---

st.title("🔎 Explorador de Boas Pagadoras de Dividendos")
st.markdown("Descubra ativos com histórico de bom pagamento de dividendos em diferentes mercados.")

tab1, tab2 = st.tabs(["🇺🇸 **Ações EUA (Lista Curada)**", "🇧🇷 **Ações Brasil (Lista Curada)**"])

# --- ABA DE AÇÕES EUA ---
with tab1:
    st.subheader("Principais Empresas Pagadoras de Dividendos dos EUA")
    st.markdown("A lista abaixo é uma **seleção curada** de empresas americanas conhecidas pelo bom histórico de pagamento de dividendos (ex: 'Dividend Aristocrats').")

    # ✅ MUDANÇA: Usando nossa lista curada e a função estável get_stock_details
    with st.spinner("Buscando dados das ações americanas..."):
        df_us = get_stock_details(US_DIVIDEND_STOCKS)
    
    if df_us is not None and not df_us.empty:
        df_us_display = df_us.sort_values(by='Dividend Yield (%)', ascending=False)

        styled_df_us = df_us_display.style.format({
            'Preço': "$ {:,.2f}",
            'Dividend Yield (%)': "{:.2f}%",
            'P/L': "{:.2f}"
        }).applymap(style_yield, subset=['Dividend Yield (%)'])

        st.dataframe(styled_df_us, use_container_width=True, hide_index=True, height=600)
    else:
        st.error("Não foi possível carregar os dados das ações americanas no momento.")

# --- ABA DE AÇÕES BRASIL ---
with tab2:
    st.subheader("Principais Empresas Pagadoras de Dividendos do Brasil")
    st.markdown("A lista abaixo é uma **seleção curada** de empresas brasileiras conhecidas pelo bom histórico de pagamento de dividendos.")

    with st.spinner("Buscando dados das ações brasileiras..."):
        df_br = get_stock_details(BRAZIL_DIVIDEND_STOCKS, suffix=".SA")
    
    if not df_br.empty:
        df_br_display = df_br.sort_values(by='Dividend Yield (%)', ascending=False)

        styled_df_br = df_br_display.style.format({
            'Preço': "R$ {:,.2f}",
            'Dividend Yield (%)': "{:.2f}%",
            'P/L': "{:.2f}"
        }).applymap(style_yield, subset=['Dividend Yield (%)'])

        st.dataframe(styled_df_br, use_container_width=True, hide_index=True, height=600)
    else:
        st.error("Não foi possível carregar os dados das ações brasileiras no momento.")
