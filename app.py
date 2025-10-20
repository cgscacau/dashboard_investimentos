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

# CSS customizado premium (mantém o mesmo CSS anterior)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700&display=swap');
    
    * {
        font-family: 'Inter', sans-serif;
    }
    
    .main {
        padding: 0rem 2rem;
        background: #f8fafc;
    }
    
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1f36 0%, #0f172a 100%);
        box-shadow: 4px 0 20px rgba(0,0,0,0.3);
    }
    
    [data-testid="stSidebar"] * {
        color: #e2e8f0 !important;
    }
    
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
    
    [data-testid="stSidebar"] .streamlit-expanderHeader {
        background: rgba(255,255,255,0.05) !important;
        border-radius: 10px !important;
        padding: 1rem !important;
        font-weight: 600 !important;
        border: 1px solid rgba(255,255,255,0.1) !important;
        color: #e2e8f0 !important;
    }
    
    h1 {
        color: #0f172a !important;
        font-weight: 700 !important;
    }
    
    h2 {
        color: #1e293b !important;
        font-weight: 600 !important;
    }
    
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
        font-weight: 600 !important;
        transition: all 0.3s ease !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
    }
    
    .stButton > button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.4) !important;
    }
    
    .stTextInput > div > div > input,
    .stSelectbox > div > div > select {
        border-radius: 12px !important;
        border: 2px solid #cbd5e1 !important;
        padding: 0.8rem 1rem !important;
        background: white !important;
        color: #0f172a !important;
    }
    
    .stProgress > div > div > div > div {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%) !important;
    }
    
    ::-webkit-scrollbar {
        width: 12px;
    }
    
    ::-webkit-scrollbar-track {
        background: #f1f5f9;
        border-radius: 10px;
    }
    
    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border-radius: 10px;
    }
    </style>
    """, unsafe_allow_html=True)


def main():
    """Função principal da aplicação."""
    
    # Inicializar session state
    if 'pagina_atual' not in st.session_state:
        st.session_state.pagina_atual = "🏆 Ranking de Ações"
    
    if 'ativo_selecionado' not in st.session_state:
        st.session_state.ativo_selecionado = None
    
    # Sidebar
    with st.sidebar:
        # Header da sidebar
        st.markdown("""
            <div class='sidebar-header'>
                <div style='font-size: 3rem; margin-bottom: 0.5rem;'>🏆</div>
                <div class='sidebar-title'>Ranking</div>
                <div style='color: #94a3b8 !important; font-size: 1rem;'>Investimentos</div>
                <div style='margin-top: 1rem; padding: 0.5rem; background: rgba(102, 126, 234, 0.2); 
                            border-radius: 10px; font-size: 0.85rem;'>
                    Descubra as melhores oportunidades
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        # Menu de navegação
        st.markdown("### 🧭 Menu Principal")
        
        # Usar botões ao invés de radio para melhor controle
        if st.button("🏆 Ranking de Ações", use_container_width=True, 
                    type="primary" if st.session_state.pagina_atual == "🏆 Ranking de Ações" else "secondary"):
            st.session_state.pagina_atual = "🏆 Ranking de Ações"
            st.session_state.ativo_selecionado = None
            st.rerun()
        
        if st.button("💼 Ranking de Fundos", use_container_width=True,
                    type="primary" if st.session_state.pagina_atual == "💼 Ranking de Fundos" else "secondary"):
            st.session_state.pagina_atual = "💼 Ranking de Fundos"
            st.session_state.ativo_selecionado = None
            st.rerun()
        
        if st.button("🔍 Análise Detalhada", use_container_width=True,
                    type="primary" if st.session_state.pagina_atual == "🔍 Análise Detalhada" else "secondary"):
            st.session_state.pagina_atual = "🔍 Análise Detalhada"
            st.rerun()
        
        if st.button("⚖️ Comparação", use_container_width=True,
                    type="primary" if st.session_state.pagina_atual == "⚖️ Comparação" else "secondary"):
            st.session_state.pagina_atual = "⚖️ Comparação"
            st.rerun()
        
        st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        
        # Informações
        with st.expander("ℹ️ Como Funciona o Ranking"):
            st.markdown("""
            **Sistema de Pontuação Inteligente**
            
            Cada ativo recebe um score de 0 a 100 baseado em:
            
            📈 **Retorno (30%)** - Performance no período
            
            📉 **Volatilidade (20%)** - Menor = Melhor
            
            ⚡ **Sharpe Ratio (20%)** - Relação retorno/risco
            
            📊 **Tendência (15%)** - Médias móveis
            
            🎯 **Momentum (15%)** - Indicador RSI
            
            ---
            
            **Classificação:**
            - ⭐⭐⭐⭐⭐ 80-100: Excelente
            - ⭐⭐⭐⭐ 70-79: Muito Bom
            - ⭐⭐⭐ 60-69: Bom
            - ⭐⭐ 50-59: Regular
            - ⭐ 0-49: Fraco
            """)
        
        with st.expander("⚠️ Aviso Legal"):
            st.markdown("""
            <div style='background: rgba(255,255,255,0.1); padding: 1rem; border-radius: 10px;'>
                <strong style='color: #fbbf24;'>⚠️ IMPORTANTE</strong><br><br>
                
                Este dashboard é apenas para fins <strong>educacionais</strong>.<br><br>
                
                ❌ NÃO é recomendação de investimento<br>
                ❌ NÃO garante resultados<br>
                ✅ Consulte um profissional certificado
            </div>
            """, unsafe_allow_html=True)
        
        # Rodapé
        st.markdown("<hr style='margin: 2rem 0; opacity: 0.3;'>", unsafe_allow_html=True)
        st.markdown("""
            <div style='text-align: center; font-size: 0.85rem; opacity: 0.8;'>
                🏆 <strong>Ranking Dashboard</strong><br>
                v3.0 - Sistema de Pontuação<br><br>
                💡 Dados: Yahoo Finance<br>
                🚀 Análise automatizada<br><br>
                ❤️ Feito com Streamlit
            </div>
        """, unsafe_allow_html=True)
    
    # Conteúdo principal - roteamento baseado em session_state
    pagina = st.session_state.pagina_atual
    
    if pagina == "🏆 Ranking de Ações":
        ranking_acoes.show()
    elif pagina == "💼 Ranking de Fundos":
        ranking_fundos.show()
    elif pagina == "🔍 Análise Detalhada":
        analise_detalhada.show()
    elif pagina == "⚖️ Comparação":
        comparacao.show()


if __name__ == "__main__":
    main()
