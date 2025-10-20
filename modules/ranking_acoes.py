"""Módulo de ranking de ações."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from config import Config
from utils.scoring import rankear_ativos
from utils.formatters import formatar_moeda, formatar_percentual, traduzir_setor


def show():
    """Exibe a página de ranking de ações."""
    
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background: white; border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🏆</div>
            <h1 style='margin: 0; font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Ranking de Ações
            </h1>
            <p style='color: #64748b; font-size: 1.1rem; margin-top: 0.5rem;'>
                Descubra as melhores oportunidades de investimento
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Filtros
    with st.sidebar:
        st.markdown("### ⚙️ Filtros de Análise")
        
        # Selecionar mercado
        mercado = st.radio(
            "Mercado:",
            ["🇧🇷 Brasil", "🌎 Internacional", "🌍 Global"],
            index=0
        )
        
        # Período de análise
        periodo_label = st.selectbox(
            "Período de análise:",
            list(Config.PERIODOS.keys()),
            index=3
        )
        periodo = Config.PERIODOS[periodo_label]
        
        st.markdown("---")
        
        # Filtros avançados
        st.markdown("### 🎯 Filtros Avançados")
        
        score_minimo = st.slider(
            "Score mínimo:",
            0, 100, 50,
            help="Mostrar apenas ações com score acima deste valor"
        )
        
        filtrar_setor = st.multiselect(
            "Filtrar por setor:",
            ["Todos"] + list(Config.SETORES_PORTUGUES.values()),
            default=["Todos"]
        )
        
        st.markdown("---")
        
        # Botão de análise
        analisar = st.button("🚀 Analisar Ações", use_container_width=True, type="primary")
    
    # Determinar lista de ações
    if mercado == "🇧🇷 Brasil":
        lista_acoes = Config.ACOES_BRASILEIRAS
        titulo_mercado = "Mercado Brasileiro"
    elif mercado == "🌎 Internacional":
        lista_acoes = Config.ACOES_INTERNACIONAIS
        titulo_mercado = "Mercado Internacional"
    else:
        lista_acoes = Config.ACOES_BRASILEIRAS + Config.ACOES_INTERNACIONAIS
        titulo_mercado = "Mercado Global"
    
    # Executar análise
    if analisar or 'df_ranking' not in st.session_state:
        with st.spinner(f'🔄 Analisando {len(lista_acoes)} ações do {titulo_mercado}...'):
            # Barra de progresso
            progresso_bar = st.progress(0)
            status_text = st.empty()
            
            def atualizar_progresso(atual, total, ticker):
                progresso = atual / total
                progresso_bar.progress(progresso)
                status_text.text(f"Analisando {ticker}... ({atual}/{total})")
            
            # Rankear ações
            df_ranking = rankear_ativos(lista_acoes, periodo, atualizar_progresso)
            
            progresso_bar.empty()
            status_text.empty()
            
            if df_ranking.empty:
                st.error("❌ Não foi possível obter dados suficientes para análise.")
                return
            
            st.session_state.df_ranking = df_ranking
            st.success(f"✅ Análise concluída! {len(df_ranking)} ações analisadas.")
    
    # Recuperar dados
    if 'df_ranking' not in st.session_state:
        st.info("👆 Clique em 'Analisar Ações' para começar a análise.")
        return
    
    df = st.session_state.df_ranking.copy()
    
    # Aplicar filtros
    df = df[df['score_total'] >= score_minimo]
    
    if "Todos" not in filtrar_setor:
        setores_filtrados = [k for k, v in Config.SETORES_PORTUGUES.items() if v in filtrar_setor]
        df = df[df['setor'].isin(setores_filtrados + filtrar_setor)]
    
    if df.empty:
        st.warning("⚠️ Nenhuma ação encontrada com os filtros aplicados.")
        return
    
    # === SEÇÃO 1: RESUMO ===
    st.markdown("### 📊 Resumo da Análise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analisadas", len(st.session_state.df_ranking))
    
    with col2:
        top_10_pct = (len(df[df['score_total'] >= 70]) / len(df) * 100) if len(df) > 0 else 0
        st.metric("Top Performers", f"{top_10_pct:.1f}%")
    
    with col3:
        retorno_medio = df['retorno'].mean()
        st.metric("Retorno Médio", formatar_percentual(retorno_medio))
    
    with col4:
        melhor_acao = df.iloc[0]['ticker'] if len(df) > 0 else "N/A"
        st.metric("Melhor Ação", melhor_acao)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === SEÇÃO 2: TOP 10 ===
    st.markdown("### 🏆 Top 10 Melhores Ações")
    
    top_10 = df.head(10)
    
    for idx, row in top_10.iterrows():
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([0.5, 2, 1.5, 1.5, 1])
            
            with col1:
                st.markdown(f"<h2 style='color: {row['cor']};'>#{row['ranking']}</h2>", unsafe_allow_html=True)
            
            with col2:
                st.markdown(f"**{row['ticker']}**")
                st.caption(row['nome'][:40] + "..." if len(row['nome']) > 40 else row['nome'])
            
            with col3:
                st.markdown(f"<div style='background: {row['cor']}; color: white; padding: 0.5rem; border-radius: 10px; text-align: center;'>"
                           f"<strong>Score: {row['score_total']:.1f}</strong></div>", unsafe_allow_html=True)
                st.caption(row['classificacao'])
            
            with col4:
                st.metric("Retorno", formatar_percentual(row['retorno']), 
                         delta=formatar_percentual(row['retorno']))
            
            with col5:
                if st.button("📊 Detalhes", key=f"btn_{row['ticker']}", use_container_width=True):
                    st.session_state.ativo_selecionado = row['ticker']
                    st.session_state.pagina_atual = "🔍 Análise Detalhada"
                    st.rerun()
            
            st.markdown("---")
    
    # === SEÇÃO 3: TABELA COMPLETA ===
    with st.expander("📋 Ver Tabela Completa", expanded=False):
        # Preparar dados para exibição
        df_display = df[['ranking', 'ticker', 'nome', 'setor', 'score_total', 
                        'retorno', 'volatilidade', 'sharpe', 'tendencia', 'classificacao']].copy()
        
        df_display.columns = ['#', 'Código', 'Nome', 'Setor', 'Score', 
                             'Retorno %', 'Volatilidade %', 'Sharpe', 'Tendência', 'Classificação']
        
        # Formatar valores
        df_display['Retorno %'] = df_display['Retorno %'].apply(lambda x: f"{x:.2f}%")
        df_display['Volatilidade %'] = df_display['Volatilidade %'].apply(lambda x: f"{x:.2f}%")
        df_display['Sharpe'] = df_display['Sharpe'].apply(lambda x: f"{x:.2f}")
        df_display['Score'] = df_display['Score'].apply(lambda x: f"{x:.1f}")
        
        st.dataframe(df_display, use_container_width=True, hide_index=True, height=400)
    
    # === SEÇÃO 4: GRÁFICOS ===
    st.markdown("### 📈 Análise Visual")
    
    tab1, tab2, tab3 = st.tabs(["📊 Distribuição de Scores", "🎯 Retorno vs Volatilidade", "🏢 Por Setor"])
    
    with tab1:
        criar_grafico_distribuicao(df)
    
    with tab2:
        criar_grafico_scatter(df)
    
    with tab3:
        criar_grafico_setores(df)


def criar_grafico_distribuicao(df):
    """Cria gráfico de distribuição de scores."""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=df['score_total'],
        nbinsx=20,
        marker_color='#667eea',
        opacity=0.7,
        name='Distribuição'
    ))
    
    fig.update_layout(
        title='Distribuição de Scores',
        xaxis_title='Score Total',
        yaxis_title='Quantidade de Ações',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_scatter(df):
    """Cria gráfico de dispersão retorno vs volatilidade."""
    fig = px.scatter(
        df,
        x='volatilidade',
        y='retorno',
        size='score_total',
        color='score_total',
        hover_data=['ticker', 'nome'],
        labels={
            'volatilidade': 'Volatilidade (%)',
            'retorno': 'Retorno (%)',
            'score_total': 'Score'
        },
        title='Retorno vs Volatilidade',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(height=500, template='plotly_white')
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_setores(df):
    """Cria gráfico de performance por setor."""
    # Traduzir setores
    df_setores = df.copy()
    df_setores['setor_pt'] = df_setores['setor'].apply(
        lambda x: Config.SETORES_PORTUGUES.get(x, x)
    )
    
    # Agrupar por setor
    setores_agrupados = df_setores.groupby('setor_pt').agg({
        'score_total': 'mean',
        'retorno': 'mean',
        'ticker': 'count'
    }).reset_index()
    
    setores_agrupados.columns = ['Setor', 'Score Médio', 'Retorno Médio', 'Quantidade']
    setores_agrupados = setores_agrupados.sort_values('Score Médio', ascending=False)
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=setores_agrupados['Setor'],
        y=setores_agrupados['Score Médio'],
        marker_color='#667eea',
        text=setores_agrupados['Score Médio'].apply(lambda x: f"{x:.1f}"),
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Score Médio por Setor',
        xaxis_title='Setor',
        yaxis_title='Score Médio',
        height=400,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de setores
    st.dataframe(setores_agrupados, use_container_width=True, hide_index=True)

