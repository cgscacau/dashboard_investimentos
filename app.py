"""
Dashboard de Investimentos
Aplicação Streamlit para análise de ações e fundos de investimento
"""

import streamlit as st
from modules import analise_acoes, analise_fundos, comparacao

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Investimentos",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS customizado
st.markdown("""
    <style>
    .main {
        padding: 0rem 1rem;
    }
    .stMetric {
        background-color: #f0f2f6;
        padding: 10px;
        border-radius: 5px;
    }
    h1 {
        color: #1f77b4;
    }
    h2 {
        color: #2ca02c;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Função principal da aplicação."""
    
    # Título principal
    st.sidebar.title("📊 Dashboard de Investimentos")
    st.sidebar.markdown("---")
    
    # Menu de navegação
    pagina = st.sidebar.radio(
        "Navegação",
        ["📈 Análise de Ações", "💼 Análise de Fundos", "⚖️ Comparação"],
        label_visibility="collapsed"
    )
    
    st.sidebar.markdown("---")
    
    # Informações adicionais
    with st.sidebar.expander("ℹ️ Sobre o Dashboard"):
        st.markdown("""
        **Dashboard de Investimentos**
        
        Ferramenta completa para análise técnica de:
        - ✅ Ações brasileiras e internacionais
        - ✅ Fundos de investimento e ETFs
        - ✅ Comparação entre múltiplos ativos
        
        **Recursos:**
        - Gráficos interativos
        - Indicadores técnicos (RSI, MACD, Bollinger)
        - Análise de correlação
        - Cálculo de volatilidade e Sharpe Ratio
        
        **Tecnologias:**
        - Streamlit
        - yFinance
        - Plotly
        - pandas-ta
        
        **Versão:** 2.0 (Português BR)
        """)
    
    with st.sidebar.expander("📚 Como Usar"):
        st.markdown("""
        **Ações Brasileiras:**
        - Use o sufixo .SA
        - Exemplos: PETR4.SA, VALE3.SA, ITUB4.SA
        
        **Ações Internacionais:**
        - Use o código direto
        - Exemplos: AAPL, MSFT, GOOGL
        
        **ETFs Brasileiros:**
        - BOVA11.SA (Ibovespa)
        - HASH11.SA (NASDAQ)
        - SMAL11.SA (Small Caps)
        
        **ETFs Internacionais:**
        - SPY (S&P 500)
        - QQQ (NASDAQ)
        - VOO (Vanguard S&P 500)
        
        **Dicas:**
        - 📊 Ajuste o período de análise conforme necessário
        - 📈 Use indicadores técnicos para identificar tendências
        - ⚖️ Compare múltiplos ativos para diversificação
        - 💡 Verifique a correlação entre ativos
        """)
    
    with st.sidebar.expander("⚠️ Aviso Legal"):
        st.markdown("""
        **IMPORTANTE:**
        
        Este dashboard é apenas para fins **educacionais** e **informativos**.
        
        ❌ **NÃO** constitui recomendação de investimento
        
        ❌ **NÃO** substitui análise profissional
        
        ❌ **NÃO** garante resultados futuros
        
        ✅ Consulte sempre um profissional certificado antes de investir
        
        ✅ Os dados são fornecidos pelo Yahoo Finance
        
        ✅ Investimentos envolvem riscos
        """)
    
    # Roteamento de páginas
    if pagina == "📈 Análise de Ações":
        analise_acoes.show()
    elif pagina == "💼 Análise de Fundos":
        analise_fundos.show()
    elif pagina == "⚖️ Comparação":
        comparacao.show()
    
    # Rodapé
    st.sidebar.markdown("---")
    st.sidebar.markdown(
        """
        <div style='text-align: center; color: gray; font-size: 0.8em;'>
        💡 Dados fornecidos por Yahoo Finance<br>
        📊 Dashboard v2.0 - Português BR<br>
        ⚠️ Apenas para fins educacionais<br>
        <br>
        Desenvolvido com ❤️ usando Streamlit
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
