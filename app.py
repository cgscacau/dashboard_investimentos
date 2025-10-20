"""
Dashboard de Investimentos - Ranking e Análise
Aplicação Streamlit para rankear e analisar as melhores ações e fundos
"""

import streamlit as st
from modules import ranking_acoes, ranking_fundos, analise_detalhada, comparacao

# Configuração da página
st.set_page_config(
    page_title="Dashboard de Investimentos - Ranking",
    page_icon="🏆",
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
        background: #f8fafc;
    }
    
    /* Sidebar moderna */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #0f172a 100%);
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
    /* Header da sidebar */
    .sidebar-header {
        text-align: center;
        padding: 2rem 1rem;
        background: rgba(255,255,255,0.05);
        border-radius: 15px;
        margin: 1rem;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .sidebar-title {
        font-size: 1.8rem;
        font-weight: 700;
        margin: 0.5rem 0;
        color: #ffffff !important;
        text-shadow: 0 2px 10px rgba(102, 126, 234, 0.5);
    }
    
    .sidebar-subtitle {
        font-size: 1rem;
        color: #94a3b8 !important;
        margin: 0;
    }
    
    /* Radio buttons modernos */
    .stRadio > div {
        background: rgba(255,255,255,0.05);
        padding: 1.5rem;
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255,255,255,0.1);
    }
    
    .stRadio label {
        font-weight: 600 !important;
        font-size: 1.1rem !important;
        padding: 0.8rem 1rem !important;
        margin: 0.5rem 0 !important;
        border-radius: 10px !important;
        transition: all 0.3s ease !important;
        cursor: pointer !important;
        color: #e2e8f0 !important;
    }
    
    .stRadio label:hover {
        background: rgba(102, 126, 234, 0.3) !important;
        transform: translateX(5px);
    }
    
    /* Expanders na sidebar */
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e2e8f0 !important;
    }
    
    [data-testid="stSidebar"] .streamlit-expanderHeader:hover {
        background: rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Cards de métricas */
    .metric-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        transition: all 0.3s ease;
        border: 1px solid rgba(0,0,0,0.05);
    }
    
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 15px 40px rgba(0,0,0,0.15);
    }
    
    /* Títulos */
    h1 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    h2 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    h3 {
        color: #334155 !important;
        font-weight: 600 !important;
    }
    
    /* Botões */
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
    
    /* Input fields */
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid #cbd5e1 !important;
        padding: 0.8rem 1rem !important;
        font-size: 1rem !important;
        transition: all 0.3s ease !important;
        background: white !important;
        color: #0f172a !important;
        font-weight: 500 !important;
    }
    
    .stTextInput > div > div > input:focus,
    .stSelectbox > div > div > select:focus {
        border-color: #667eea !important;
        box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.2) !important;
    }
    
    /* Tabs */
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
        color: #475569;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white !important;
    }
    
    /* Dataframes */
    .dataframe {
        border-radius: 15px !important;
        overflow: hidden !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
    }
    
    /* Alerts */
    .stAlert {
        border-radius: 15px !important;
        border: none !important;
        box-shadow: 0 4px 15px rgba(0,0,0,0.08) !important;
        padding: 1.5rem !important;
    }
    
    /* Progress bar */
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 12px;
        height: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
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
    
    /* Cards de feature */
    .feature-card {
        background: white;
        padding: 2rem;
        border-radius: 20px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        text-align: center;
        transition: all 0.3s ease;
        border-top: 4px solid;
    }
    
    .feature-card:hover {
        transform: translateY(-10px);
        box-shadow: 0 20px 40px rgba(0,0,0,0.15);
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Função principal da aplicação."""
    
    # Inicializar session state
    if 'ativo_selecionado' not in st.session_state:
        st.session_state.ativo_selecionado = None
    
    # Sidebar
    with st.sidebar:
        # Header da sidebar
        st.markdown("""
            <div class='sidebar-header'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🏆</div>
                <div class='sidebar-title'>Ranking</div>
                <div class='sidebar-subtitle'>Investimentos</div>
                <div style='margin-top: 1rem; padding: 0.5rem; background: rgba(102, 126, 234, 0.2); 
                            border-radius: 10px; font-size: 0.85rem;'>
                    Descubra as melhores oportunidades
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegação
        st.markdown("### 🧭 Menu Principal")
        pagina = st.radio(
            "Escolha uma opção:",
            [
                "🏆 Ranking de Ações",
                "💼 Ranking de Fundos",
                "🔍 Análise Detalhada",
                "⚖️ Comparação"
            ],
            label_visibility="collapsed"
        )
        
        st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        
        # Informações sobre o sistema de ranking
        with st.expander("ℹ️ Como Funciona o Ranking"):
            st.markdown("""
            **Sistema de Pontuação Inteligente**
            
            Cada ativo recebe um score de 0 a 100 baseado em 5 critérios:
            
            📈 **Retorno (30%)**
            - Performance no período selecionado
            
            📉 **Volatilidade (20%)**
            - Menor volatilidade = Maior score
            
            ⚡ **Sharpe Ratio (20%)**
            - Relação retorno/risco
            
            📊 **Tendência (15%)**
            - Análise de médias móveis
            
            🎯 **Momentum (15%)**
            - Indicador RSI
            
            ---
            
            **Classificação:**
            - ⭐⭐⭐⭐⭐ 80-100: Excelente
            - ⭐⭐⭐⭐ 70-79: Muito Bom
            - ⭐⭐⭐ 60-69: Bom
            - ⭐⭐ 50-59: Regular
            - ⭐ 0-49: Fraco
            """)
        
        with st.expander("📚 Glossário"):
            st.markdown("""
            **Termos Importantes:**
            
            **Sharpe Ratio**
            - Mede retorno ajustado ao risco
            - Quanto maior, melhor
            
            **Volatilidade**
            - Variação dos preços
            - Indica nível de risco
            
            **RSI (Índice de Força Relativa)**
            - 0-30: Sobrevendido
            - 70-100: Sobrecomprado
            
            **Beta**
            - Sensibilidade ao mercado
            - Beta > 1: Mais volátil que mercado
            - Beta < 1: Menos volátil
            
            **P/L (Preço/Lucro)**
            - Quantos anos para recuperar investimento
            - Menor geralmente é melhor
            
            **Dividend Yield**
            - Rendimento de dividendos
            - Quanto maior, melhor para renda
            """)
        
        with st.expander("🎯 Estratégias"):
            st.markdown("""
            **Perfis de Investidor:**
            
            🛡️ **Conservador**
            - Foco em menor volatilidade
            - Sharpe Ratio > 1
            - Ações de setores defensivos
            - ETFs de índices amplos
            
            ⚖️ **Moderado**
            - Score total > 60
            - Diversificação entre setores
            - Mix de ações e fundos
            
            🚀 **Agressivo**
            - Foco em maior retorno
            - Aceita alta volatilidade
            - Ações de crescimento
            - ETFs setoriais
            
            ---
            
            💡 **Dica:** Use o ranking como ponto de partida, mas sempre faça sua própria análise!
            """)
        
        with st.expander("⚠️ Aviso Legal"):
            st.markdown("""
            <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px; 
                        border-left: 4px solid #fbbf24;'>
                <strong style='color: #fbbf24;'>⚠️ IMPORTANTE</strong><br><br>
                
                Este dashboard é exclusivamente para fins <strong>educacionais</strong>.<br><br>
                
                ❌ NÃO é recomendação de investimento<br>
                ❌ NÃO garante resultados futuros<br>
                ❌ NÃO substitui análise profissional<br><br>
                
                ✅ Consulte um profissional certificado pela CVM<br>
                ✅ Investimentos envolvem riscos<br>
                ✅ Rentabilidade passada não garante retornos futuros<br><br>
                
                <strong>Dados fornecidos por Yahoo Finance</strong>
            </div>
            """, unsafe_allow_html=True)
        
        # Rodapé
        st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; font-size: 0.85rem; opacity: 0.8;'>
                🏆 <strong>Ranking Dashboard</strong><br>
                v3.0 - Sistema de Pontuação<br><br>
                
                💡 Dados em tempo real<br>
                📊 Análise automatizada<br>
                🚀 Atualização contínua<br><br>
                
                ❤️ Desenvolvido com<br>
                <strong>Streamlit + Python</strong>
            </div>
        """, unsafe_allow_html=True)
    
    # Conteúdo principal
    if pagina == "🏆 Ranking de Ações":
        ranking_acoes.show()
    elif pagina == "💼 Ranking de Fundos":
        ranking_fundos.show()
    elif pagina == "🔍 Análise Detalhada":
        analise_detalhada.show()
    elif pagina == "⚖️ Comparação":
        comparacao.show()
    else:
        # Página inicial (home)
        mostrar_home()


def mostrar_home():
    """Mostra página inicial com overview."""
    
    st.markdown("""
        <div style='text-align: center; padding: 3rem 0;'>
            <div style='font-size: 5rem; margin-bottom: 1rem;'>🏆</div>
            <h1 style='font-size: 3.5rem; margin: 0; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Dashboard de Ranking de Investimentos
            </h1>
            <p style='font-size: 1.3rem; color: #64748b; margin-top: 1rem;'>
                Descubra as melhores oportunidades do mercado com análise automatizada
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Features principais
    st.markdown("### 🎯 Funcionalidades Principais")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
            <div class='feature-card' style='border-top-color: #667eea;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🏆</div>
                <h3 style='color: #667eea;'>Ranking de Ações</h3>
                <p style='color: #64748b;'>
                    Descubra as ações com melhor performance e potencial de crescimento
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
            <div class='feature-card' style='border-top-color: #10b981;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>💼</div>
                <h3 style='color: #10b981;'>Ranking de Fundos</h3>
                <p style='color: #64748b;'>
                    Encontre os melhores ETFs e fundos para diversificar sua carteira
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
            <div class='feature-card' style='border-top-color: #f59e0b;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>🔍</div>
                <h3 style='color: #f59e0b;'>Análise Detalhada</h3>
                <p style='color: #64748b;'>
                    Análise técnica e fundamentalista completa de qualquer ativo
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
            <div class='feature-card' style='border-top-color: #ef4444;'>
                <div style='font-size: 3rem; margin-bottom: 1rem;'>⚖️</div>
                <h3 style='color: #ef4444;'>Comparação</h3>
                <p style='color: #64748b;'>
                    Compare múltiplos ativos lado a lado para tomar decisões informadas
                </p>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Como começar
    st.markdown("### 🚀 Como Começar")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <h3>📊 Para Iniciantes</h3>
            
            **1. Comece pelo Ranking de Fundos**
            - Menor risco
            - Diversificação automática
            - Mais simples de entender
            
            **2. Escolha fundos com:**
            - Score > 70
            - Sharpe Ratio > 1
            - Baixa volatilidade
            
            **3. Diversifique**
            - Combine diferentes ETFs
            - Balanceie Brasil e Internacional
            - Considere diferentes setores
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div style='background: white; padding: 2rem; border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1);'>
            <h3>🎯 Para Experientes</h3>
            
            **1. Use o Ranking de Ações**
            - Maiores oportunidades
            - Análise mais detalhada
            - Maior controle
            
            **2. Analise múltiplos fatores:**
            - Score total
            - Tendência técnica
            - Fundamentos da empresa
            - Correlação com carteira
            
            **3. Use Análise Detalhada**
            - Verifique indicadores técnicos
            - Avalie fundamentos
            - Compare com concorrentes
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    # Call to action
    st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 3rem; border-radius: 20px; text-align: center; color: white;
                    box-shadow: 0 20px 40px rgba(102, 126, 234, 0.3);'>
            <h2 style='color: white; margin: 0;'>Pronto para começar?</h2>
            <p style='font-size: 1.2rem; margin: 1rem 0 2rem 0; opacity: 0.9;'>
                Escolha uma opção no menu lateral e descubra as melhores oportunidades de investimento!
            </p>
            <div style='font-size: 2rem;'>👈</div>
        </div>
    """, unsafe_allow_html=True)


if __name__ == "__main__":
    main()
