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
    with st.sidebar.expander("ℹ️ Sobre"):
        st.markdown("""
        **Dashboard de Investimentos**
        
        Ferramenta para análise técnica de:
        - Ações brasileiras e internacionais
        - Fundos de investimento
        - Comparação entre múltiplos ativos
        
        **Desenvolvido com:**
        - Streamlit
        - yFinance
        - Plotly
        - pandas-ta
        
        **Versão:** 2.0
        """)
    
    with st.sidebar.expander("📚 Como Usar"):
        st.markdown("""
        **Ações Brasileiras:**
        - Use o sufixo .SA (ex: PETR4.SA)
        
        **Ações Internacionais:**
        - Use o ticker direto (ex: AAPL)
        
        **ETFs:**
        - Brasil: HASH11.SA, BOVA11.SA
        - EUA: SPY, QQQ, VOO
        
        **Dicas:**
        - Ajuste o período de análise
        - Compare múltiplos ativos
        - Use indicadores técnicos
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
        ⚠️ Este dashboard é apenas para fins educacionais
        </div>
        """,
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
