# app.py
import streamlit as st

st.set_page_config(
    page_title="Análise de Investimentos",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Plataforma de Análise de Investimentos")
st.markdown("---")

st.markdown(
    """
    ## Bem-vindo à sua plataforma de análise de investimentos!

    Esta ferramenta foi construída para ajudar você a analisar diferentes classes de ativos
    de forma rápida e intuitiva, utilizando dados de mercado em tempo real.

    **O que você pode fazer aqui?**
    - **Análise de Ativos Brasileiros:** Acesse dados fundamentalistas, de valuation e gráficos técnicos para Ações, FIIs e ETFs da B3.
    - **Análise de Ativos Americanos:** Obtenha informações sobre Ações, REITs e ETFs do mercado americano.
    - **Análise de Criptomoedas:** Explore o universo das criptos com dados de mercado, métricas e gráficos.

    **Navegue pelas seções no menu à esquerda para começar!**


    """
)