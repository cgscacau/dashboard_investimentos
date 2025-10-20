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

# CSS customizado premium
st.markdown("""
    <style>
    /* Importar fonte moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    /* Reset e base */
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 0rem 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1e3c72 0%, #2a5298 100%);
        box-shadow: 4px 0 15px rgba(0,0,0,0.1);
    }
    
    [data-testid="stSidebar"] * {
        color: white !important;
    }
    
    /* Header da sidebar */
    .sidebar-header {
        text-align: center;
        padding: 2rem 1rem;
        background: rgba(255,255,255,0.1);
        border-radius: 15px;
        margin: 1rem;
        backdrop-filter: blur(10px);
    }
    
    .sidebar-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
        background: linear-gradient(90deg, #fff, #a8dadc);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    
    /* Radio buttons modernos */
    .stRadio > div {
        background: rgba(255,255,255,0.1);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.2);
    }
    
    .stRadio label {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 0.8rem !important;
        margin: 0.5rem 0 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
    }
    
    .stRadio label:hover {
        background: rgba(255,255,255,0.2) !important;
        transform: translateX(5px);
    }
    
    /* Expanders na sidebar */
    .streamlit-expanderHeader {
        background: rgba(255,255,255,0.1) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255,255,255,0.2) !important;
    }
    
    .streamlit-expanderHeader:hover {
        background: rgba(255,255,255,0.2) !important;
    }
    
    /* Cards de métricas premium */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
        position: relative;
        overflow: hidden;
    }
    
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 5px;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
    }
    
    .metric-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    
    .metric-label {
        color: #64748b;
        font-size: 0.9rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 0.5rem;
    }
    
    .metric-value {
        color: #1e293b;
        font-size: 2.5rem;
        font-weight: 700;
        margin: 0.5rem 0;
    }
    
    .metric-change {
        font-size: 0.9rem;
        font-weight: 600;
        padding: 0.3rem 0.8rem;
        border-radius: 20px;
        display: inline-block;
        margin-top: 0.5rem;
    }
    
    .metric-change.positive {
        background: rgba(34, 197, 94, 0.1);
        color: #16a34a;
    }
    
    .metric-change.negative {
        background: rgba(239, 68, 68, 0.1);
        color: #dc2626;
    }
    
    /* Títulos elegantes */
    h1 {
        color: #1e293b;
        font-weight: 700;
        font-size: 3rem;
        margin-bottom: 2rem;
        text-align: center;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }
    
    h2 {
        color: #334155;
        font-weight: 600;
        font-size: 1.8rem;
        margin: 2rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 3px solid #667eea;
        display: inline-block;
    }
    
    h3 {
        color: #475569;
        font-weight: 600;
        font-size: 1.4rem;
        margin: 1.5rem 0 1rem 0;
    }
    
    /* Badges de sinal premium */
    .signal-badge {
        background: white;
        padding: 1.5rem;
        border-radius: 15px;
        box-shadow: 0 5px 15px rgba(0,0,0,0.08);
        margin: 1rem 0;
        border-left: 5px solid;
        transition: all 0.3s ease;
    }
    
    .signal-badge:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
    }
    
    .signal-badge.success {
        border-left-color: #22c55e;
        background: linear-gradient(135deg, #ffffff 0%, #f0fdf4 100%);
    }
    
    .signal-badge.warning {
        border-left-color: #f59e0b;
        background: linear-gradient(135deg, #ffffff 0%, #fffbeb 100%);
    }
    
    .signal-badge.danger {
        border-left-color: #ef4444;
        background: linear-gradient(135deg, #ffffff 0%, #fef2f2 100%);
    }
    
    .signal-title {
        color: #1e293b;
        font-size: 1.1rem;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    
    .signal-text {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.6;
    }
    
    /* Input fields modernos */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid #e2e8f0 !important;
        padding: 0.8rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: white !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1) !important;
    }
    
    /* Botões premium */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        width: 100% !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    /* Tabs modernas */
    .stTabs [data-baseweb="tab-list"] {
        gap: 1rem;
        background: white;
        padding: 1rem;
        border-radius: 15px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    .stTabs [data-baseweb="tab"] {
        padding: 1rem 2rem;
        border-radius: 10px;
        font-weight: 600;
        transition: all 0.3s ease;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Alerts premium */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        padding: 1.5rem !important;
    }
    
    /* Expanders do conteúdo */
    .main .streamlit-expanderHeader {
        background: white !important;
        color: #1e293b !important;
        border-radius: 12px !important;
        padding: 1.2rem !important;
        font-weight: 600 !important;
        border: 2px solid #e2e8f0 !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05) !important;
    }
    
    .main .streamlit-expanderHeader:hover {
        border-color: #667eea !important;
        background: #f8fafc !important;
    }
    
    /* Tabelas modernas */
    .dataframe {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
    }
    
    .dataframe thead tr th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        font-weight: 600 !important;
        padding: 1rem !important;
    }
    
    .dataframe tbody tr:hover {
        background: #f8fafc !important;
    }
    
    /* Gráficos */
    .js-plotly-plot {
        border-radius: 15px !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        background: white !important;
        padding: 1rem !important;
    }
    
    /* Animações */
    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(30px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    
    .element-container {
        animation: slideIn 0.5s ease-out;
    }
    
    /* Scrollbar customizada */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb:hover {
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%);
    }
    
    /* Checkbox personalizado */
    .stCheckbox {
        padding: 0.5rem;
        transition: all 0.3s ease;
    }
    
    .stCheckbox:hover {
        background: rgba(102, 126, 234, 0.05);
        border-radius: 8px;
    }
    
    /* Spinner customizado */
    .stSpinner > div {
        border-top-color: #667eea !important;
    }
    
    /* Divider elegante */
    hr {
        margin: 2rem 0;
        border: none;
        height: 2px;
        background: linear-gradient(90deg, transparent, #667eea, transparent);
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Função principal da aplicação."""
    
    # Sidebar
    with st.sidebar:
        # Header da sidebar
        st.markdown("""
            <div class='sidebar-header'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>📊</div>
                <div class='sidebar-title'>Dashboard</div>
                <div style='font-size: 1.1rem; opacity: 0.9;'>Investimentos Pro</div>
            </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegação
        st.markdown("### 🧭 Navegação")
        pagina = st.radio(
            "Escolha uma opção:",
            ["📈 Análise de Ações", "💼 Análise de Fundos", "⚖️ Comparação"],
            label_visibility="collapsed"
        )
        
        st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        
        # Informações adicionais
        with st.expander("ℹ️ Sobre o Dashboard"):
            st.markdown("""
            **Dashboard de Investimentos v2.0**
            
            🎯 **Recursos Premium:**
            - ✅ Análise técnica avançada
            - ✅ Gráficos interativos HD
            - ✅ Indicadores profissionais
            - ✅ Comparação múltipla
            - ✅ Alertas inteligentes
            
            📊 **Tecnologias:**
            - Streamlit Pro
            - yFinance API
            - Plotly Graphics
            - Pandas & NumPy
            
            🚀 **Performance:**
            - Cache otimizado
            - Atualização em tempo real
            - Interface responsiva
            """)
        
        with st.expander("📚 Guia Rápido"):
            st.markdown("""
            **🇧🇷 Ações Brasileiras:**
            ```
            PETR4.SA  - Petrobras
            VALE3.SA  - Vale
            ITUB4.SA  - Itaú
            BBDC4.SA  - Bradesco
            ```
            
            **🇺🇸 Ações Internacionais:**
            ```
            AAPL  - Apple
            MSFT  - Microsoft
            GOOGL - Google
            TSLA  - Tesla
            ```
            
            **📊 ETFs Populares:**
            ```
            BOVA11.SA - Ibovespa
            HASH11.SA - NASDAQ
            SPY       - S&P 500
            QQQ       - NASDAQ-100
            ```
            
            💡 **Dica:** Use períodos maiores (1 ano+) para análises mais precisas e confiáveis.
            """)
        
        with st.expander("⚠️ Aviso Legal"):
            st.markdown("""
            <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; border-left: 4px solid #fbbf24;'>
                <strong style='color: #fbbf24;'>⚠️ IMPORTANTE</strong><br><br>
                Este dashboard é exclusivamente para fins <strong>educacionais e informativos</strong>.<br><br>
                ❌ NÃO constitui recomendação de investimento<br>
                ❌ NÃO garante resultados futuros<br>
                ❌ NÃO substitui assessoria profissional<br><br>
                ✅ Sempre consulte um profissional certificado pela CVM antes de investir<br>
                ✅ Investimentos envolvem riscos de perda
            </div>
            """, unsafe_allow_html=True)
        
        # Rodapé
        st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; font-size: 0.85rem; opacity: 0.8;'>
                💡 Dados fornecidos por<br>
                <strong>Yahoo Finance API</strong><br><br>
                🚀 Dashboard v2.0<br>
                Português Brasil<br><br>
                ❤️ Desenvolvido com<br>
                <strong>Streamlit</strong>
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
