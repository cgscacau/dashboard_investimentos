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

# CSS customizado melhorado
st.markdown("""
    <style>
    /* Estilo geral */
    .main {
        padding: 0rem 1rem;
    }
    
    /* Métricas */
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 20px;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .stMetric label {
        color: white !important;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .stMetric [data-testid="stMetricValue"] {
        color: white !important;
        font-size: 1.8rem;
        font-weight: 700;
    }
    
    .stMetric [data-testid="stMetricDelta"] {
        color: #90EE90 !important;
    }
    
    /* Títulos */
    h1 {
        color: #1f77b4;
        font-weight: 700;
        padding-bottom: 1rem;
        border-bottom: 3px solid #667eea;
    }
    
    h2 {
        color: #2ca02c;
        font-weight: 600;
        margin-top: 2rem;
    }
    
    h3 {
        color: #ff7f0e;
        font-weight: 600;
    }
    
    /* Sidebar */
    .css-1d391kg {
        background: linear-gradient(180deg, #667eea 0%, #764ba2 100%);
    }
    
    /* Botões */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        border-radius: 8px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 12px rgba(102, 126, 234, 0.4);
    }
    
    /* Input fields */
    .stTextInput > div > div > input {
        border-radius: 8px;
        border: 2px solid #667eea;
    }
    
    .stSelectbox > div > div > select {
        border-radius: 8px;
        border: 2px solid #667eea;
    }
    
    /* Cards de informação */
    .stAlert {
        border-radius: 10px;
        border-left: 4px solid #667eea;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f0f2f6;
        border-radius: 8px;
        font-weight: 600;
    }
    
    /* Tabelas */
    .dataframe {
        border-radius: 10px;
        overflow: hidden;
    }
    
    /* Gráficos */
    .js-plotly-plot {
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    /* Animações */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .element-container {
        animation: fadeIn 0.5s ease-out;
    }
    
    /* Radio buttons */
    .stRadio > div {
        background-color: white;
        padding: 1rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
    }
    
    /* Checkbox */
    .stCheckbox {
        padding: 0.5rem;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Função principal da aplicação."""
    
    # Sidebar
    with st.sidebar:
        # Logo/Header
        st.markdown("""
            <div style='text-align: center; padding: 1rem 0;'>
                <h1 style='color: white; margin: 0;'>📊</h1>
                <h2 style='color: white; margin: 0; font-size: 1.5rem;'>Dashboard</h2>
                <p style='color: white; margin: 0; font-size: 0.9rem;'>Investimentos</p>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Menu de navegação
        st.markdown("### 🧭 Navegação")
        pagina = st.radio(
            "Escolha uma opção:",
            ["📈 Análise de Ações", "💼 Análise de Fundos", "⚖️ Comparação"],
            label_visibility="collapsed"
        )
        
        st.markdown("---")
        
        # Informações adicionais
        with st.expander("ℹ️ Sobre o Dashboard"):
            st.markdown("""
            **Dashboard de Investimentos v2.0**
            
            🎯 **Recursos:**
            - ✅ Análise técnica completa
            - ✅ Gráficos interativos
            - ✅ Indicadores (RSI, MACD, BB)
            - ✅ Comparação de ativos
            - ✅ Cálculo de volatilidade
            
            📊 **Tecnologias:**
            - Streamlit
            - yFinance
            - Plotly
            - Pandas & NumPy
            """)
        
        with st.expander("📚 Guia Rápido"):
            st.markdown("""
            **🇧🇷 Ações Brasileiras:**
            ```
            PETR4.SA, VALE3.SA, ITUB4.SA
            ```
            
            **🇺🇸 Ações Internacionais:**
            ```
            AAPL, MSFT, GOOGL, TSLA
            ```
            
            **📊 ETFs:**
            ```
            BOVA11.SA, HASH11.SA, SPY, QQQ
            ```
            
            💡 **Dica:** Use o período de 1 ano para análises mais precisas.
            """)
        
        with st.expander("⚠️ Aviso Legal"):
            st.markdown("""
            <div style='background-color: #fff3cd; padding: 1rem; border-radius: 8px; border-left: 4px solid #ffc107;'>
                <strong>⚠️ IMPORTANTE</strong><br><br>
                Este dashboard é apenas para fins <strong>educacionais</strong>.<br><br>
                ❌ NÃO é recomendação de investimento<br>
                ❌ NÃO garante resultados<br>
                ✅ Consulte um profissional certificado
            </div>
            """, unsafe_allow_html=True)
        
        # Rodapé
        st.markdown("---")
        st.markdown("""
            <div style='text-align: center; color: white; font-size: 0.8rem;'>
                💡 Dados: Yahoo Finance<br>
                🚀 v2.0 - Português BR<br>
                ❤️ Feito com Streamlit
            </div>
        """, unsafe_allow_html=True)
    
    # Conteúdo principal
    if pagina == "📈 Análise de Ações":
        analise_acoes.show()
    elif pagina == "💼 Análise de Fundos":
        analise_fundos.show()
    elif pagina == "⚖️ Comparação":
        comparacao.show()


if __name__ == "__main__":
    main()
