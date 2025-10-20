"""Módulo de ranking de fundos de investimento e ETFs."""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from config import Config
from utils.scoring import rankear_ativos
from utils.formatters import formatar_moeda, formatar_percentual, formatar_numero_grande


def show():
    """Exibe a página de ranking de fundos."""
    
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background: white; border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>💼</div>
            <h1 style='margin: 0; font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Ranking de Fundos e ETFs
            </h1>
            <p style='color: #64748b; font-size: 1.1rem; margin-top: 0.5rem;'>
                Encontre os melhores fundos para diversificar sua carteira
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
            help="Mostrar apenas fundos com score acima deste valor"
        )
        
        ordenar_por = st.selectbox(
            "Ordenar por:",
            ["Score Total", "Retorno", "Sharpe Ratio", "Menor Volatilidade"],
            index=0
        )
        
        st.markdown("---")
        
        # Informação sobre ETFs
        with st.expander("ℹ️ Sobre ETFs"):
            st.markdown("""
            **ETFs (Exchange Traded Funds)**
            
            São fundos que replicam índices e podem ser negociados como ações.
            
            **Vantagens:**
            - ✅ Diversificação instantânea
            - ✅ Baixo custo
            - ✅ Liquidez
            - ✅ Transparência
            
            **Exemplos:**
            - **BOVA11**: Ibovespa
            - **HASH11**: NASDAQ
            - **SPY**: S&P 500
            """)
        
        # Botão de análise
        analisar = st.button("🚀 Analisar Fundos", use_container_width=True, type="primary")
    
    # Determinar lista de fundos
    if mercado == "🇧🇷 Brasil":
        lista_fundos = Config.FUNDOS_BRASILEIROS
        titulo_mercado = "Fundos Brasileiros"
    elif mercado == "🌎 Internacional":
        lista_fundos = Config.FUNDOS_INTERNACIONAIS
        titulo_mercado = "ETFs Internacionais"
    else:
        lista_fundos = Config.FUNDOS_BRASILEIROS + Config.FUNDOS_INTERNACIONAIS
        titulo_mercado = "Fundos Globais"
    
    # Executar análise
    if analisar or 'df_ranking_fundos' not in st.session_state:
        with st.spinner(f'🔄 Analisando {len(lista_fundos)} fundos...'):
            # Barra de progresso
            progresso_bar = st.progress(0)
            status_text = st.empty()
            
            def atualizar_progresso(atual, total, ticker):
                progresso = atual / total
                progresso_bar.progress(progresso)
                status_text.text(f"Analisando {ticker}... ({atual}/{total})")
            
            # Rankear fundos
            df_ranking = rankear_ativos(lista_fundos, periodo, atualizar_progresso)
            
            progresso_bar.empty()
            status_text.empty()
            
            if df_ranking.empty:
                st.error("❌ Não foi possível obter dados suficientes para análise.")
                return
            
            st.session_state.df_ranking_fundos = df_ranking
            st.success(f"✅ Análise concluída! {len(df_ranking)} fundos analisados.")
    
    # Recuperar dados
    if 'df_ranking_fundos' not in st.session_state:
        st.info("👆 Clique em 'Analisar Fundos' para começar a análise.")
        return
    
    df = st.session_state.df_ranking_fundos.copy()
    
    # Aplicar filtros
    df = df[df['score_total'] >= score_minimo]
    
    # Ordenar
    if ordenar_por == "Retorno":
        df = df.sort_values('retorno', ascending=False)
    elif ordenar_por == "Sharpe Ratio":
        df = df.sort_values('sharpe', ascending=False)
    elif ordenar_por == "Menor Volatilidade":
        df = df.sort_values('volatilidade', ascending=True)
    else:
        df = df.sort_values('score_total', ascending=False)
    
    df = df.reset_index(drop=True)
    df['ranking'] = range(1, len(df) + 1)
    
    if df.empty:
        st.warning("⚠️ Nenhum fundo encontrado com os filtros aplicados.")
        return
    
    # === SEÇÃO 1: RESUMO ===
    st.markdown("### 📊 Resumo da Análise")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Analisados", len(st.session_state.df_ranking_fundos))
    
    with col2:
        melhor_retorno = df['retorno'].max()
        st.metric("Melhor Retorno", formatar_percentual(melhor_retorno))
    
    with col3:
        sharpe_medio = df['sharpe'].mean()
        st.metric("Sharpe Médio", f"{sharpe_medio:.2f}")
    
    with col4:
        menor_vol = df['volatilidade'].min()
        st.metric("Menor Volatilidade", formatar_percentual(menor_vol))
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === SEÇÃO 2: PÓDIO ===
    st.markdown("### 🏆 Pódio - Top 3 Fundos")
    
    if len(df) >= 3:
        col1, col2, col3 = st.columns(3)
        
        # 2º Lugar
        with col1:
            criar_card_podio(df.iloc[1], 2, "🥈", "#C0C0C0")
        
        # 1º Lugar
        with col2:
            criar_card_podio(df.iloc[0], 1, "🥇", "#FFD700")
        
        # 3º Lugar
        with col3:
            criar_card_podio(df.iloc[2], 3, "🥉", "#CD7F32")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === SEÇÃO 3: LISTA COMPLETA ===
    st.markdown("### 📋 Lista Completa de Fundos")
    
    for idx, row in df.iterrows():
        criar_card_fundo(row)
    
    # === SEÇÃO 4: COMPARAÇÃO VISUAL ===
    st.markdown("### 📊 Comparação Visual")
    
    tab1, tab2, tab3, tab4 = st.tabs([
        "📈 Retornos", 
        "🎯 Eficiência (Sharpe)", 
        "📉 Volatilidade",
        "🔄 Correlação"
    ])
    
    with tab1:
        criar_grafico_retornos(df)
    
    with tab2:
        criar_grafico_sharpe(df)
    
    with tab3:
        criar_grafico_volatilidade(df)
    
    with tab4:
        criar_grafico_correlacao(df)
    
    # === SEÇÃO 5: RECOMENDAÇÕES ===
    st.markdown("### 💡 Recomendações Personalizadas")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                    padding: 2rem; border-radius: 15px; color: white;'>
            <h3 style='color: white; margin-top: 0;'>🛡️ Perfil Conservador</h3>
            <p>Para investidores que buscam menor risco e volatilidade.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Fundos mais estáveis
        fundos_conservadores = df.nsmallest(3, 'volatilidade')
        for _, fundo in fundos_conservadores.iterrows():
            st.markdown(f"""
            - **{fundo['ticker']}** - Volatilidade: {fundo['volatilidade']:.2f}%
            """)
    
    with col2:
        st.markdown("""
        <div style='background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%); 
                    padding: 2rem; border-radius: 15px; color: white;'>
            <h3 style='color: white; margin-top: 0;'>🚀 Perfil Agressivo</h3>
            <p>Para investidores que buscam máximo retorno.</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Fundos com maior retorno
        fundos_agressivos = df.nlargest(3, 'retorno')
        for _, fundo in fundos_agressivos.iterrows():
            st.markdown(f"""
            - **{fundo['ticker']}** - Retorno: {fundo['retorno']:.2f}%
            """)


def criar_card_podio(row, posicao, emoji, cor):
    """Cria card do pódio."""
    st.markdown(f"""
        <div style='background: white; padding: 2rem; border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); text-align: center;
                    border-top: 5px solid {cor};'>
            <div style='font-size: 3rem; margin-bottom: 1rem;'>{emoji}</div>
            <h2 style='color: {cor}; margin: 0;'>{posicao}º Lugar</h2>
            <h3 style='margin: 0.5rem 0; color: #1e293b;'>{row['ticker']}</h3>
            <p style='color: #64748b; font-size: 0.9rem; margin: 0.5rem 0;'>
                {row['nome'][:40]}...
            </p>
            <div style='margin: 1rem 0; padding: 1rem; background: #f8fafc; border-radius: 10px;'>
                <div style='font-size: 2rem; font-weight: 700; color: {row['cor']};'>
                    {row['score_total']:.1f}
                </div>
                <div style='font-size: 0.8rem; color: #64748b;'>SCORE</div>
            </div>
            <div style='display: flex; justify-content: space-around; margin-top: 1rem;'>
                <div>
                    <div style='font-weight: 700; color: #10b981;'>{row['retorno']:.2f}%</div>
                    <div style='font-size: 0.8rem; color: #64748b;'>Retorno</div>
                </div>
                <div>
                    <div style='font-weight: 700; color: #667eea;'>{row['sharpe']:.2f}</div>
                    <div style='font-size: 0.8rem; color: #64748b;'>Sharpe</div>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def criar_card_fundo(row):
    """Cria card de fundo na lista."""
    with st.container():
        col1, col2, col3, col4, col5, col6 = st.columns([0.5, 2, 1, 1, 1, 0.8])
        
        with col1:
            st.markdown(f"<h3 style='color: {row['cor']};'>#{row['ranking']}</h3>", unsafe_allow_html=True)
        
        with col2:
            st.markdown(f"**{row['ticker']}**")
            st.caption(row['nome'][:50] + "..." if len(row['nome']) > 50 else row['nome'])
        
        with col3:
            st.markdown(f"""
                <div style='background: {row['cor']}; color: white; padding: 0.5rem; 
                            border-radius: 10px; text-align: center;'>
                    <strong>{row['score_total']:.1f}</strong>
                </div>
            """, unsafe_allow_html=True)
            st.caption(row['classificacao'])
        
        with col4:
            st.metric("Retorno", formatar_percentual(row['retorno']), 
                     delta=formatar_percentual(row['retorno']))
        
        with col5:
            st.metric("Sharpe", f"{row['sharpe']:.2f}")
            st.caption(f"Vol: {row['volatilidade']:.1f}%")
        
        with col6:
            with col6:
                if st.button("📊", key=f"btn_fundos_{row['ticker']}", use_container_width=True):
                    st.session_state.ativo_selecionado = row['ticker']
                    st.session_state.pagina_atual = "🔍 Análise Detalhada"
                    st.rerun()
        
        st.markdown("---")


def criar_grafico_retornos(df):
    """Cria gráfico de barras com retornos."""
    fig = go.Figure()
    
    colors = ['#10b981' if x >= 0 else '#ef4444' for x in df['retorno']]
    
    fig.add_trace(go.Bar(
        x=df['ticker'],
        y=df['retorno'],
        marker_color=colors,
        text=df['retorno'].apply(lambda x: f"{x:.2f}%"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Retorno: %{y:.2f}%<extra></extra>'
    ))
    
    fig.update_layout(
        title='Retorno no Período por Fundo',
        xaxis_title='Fundo',
        yaxis_title='Retorno (%)',
        height=500,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_sharpe(df):
    """Cria gráfico do Sharpe Ratio."""
    fig = go.Figure()
    
    colors = df['sharpe'].apply(lambda x: '#10b981' if x > 1 else '#f59e0b' if x > 0 else '#ef4444')
    
    fig.add_trace(go.Bar(
        x=df['ticker'],
        y=df['sharpe'],
        marker_color=colors,
        text=df['sharpe'].apply(lambda x: f"{x:.2f}"),
        textposition='outside',
        hovertemplate='<b>%{x}</b><br>Sharpe: %{y:.2f}<extra></extra>'
    ))
    
    # Linha de referência (Sharpe > 1 é bom)
    fig.add_hline(y=1, line_dash="dash", line_color="gray", 
                  annotation_text="Sharpe = 1 (Bom)")
    
    fig.update_layout(
        title='Índice Sharpe por Fundo',
        xaxis_title='Fundo',
        yaxis_title='Sharpe Ratio',
        height=500,
        template='plotly_white',
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Interpretação do Sharpe Ratio:**
    - 🟢 **> 1.0**: Excelente relação retorno/risco
    - 🟡 **0.5 - 1.0**: Boa relação retorno/risco
    - 🔴 **< 0.5**: Relação retorno/risco não atrativa
    """)


def criar_grafico_volatilidade(df):
    """Cria gráfico de volatilidade."""
    fig = px.scatter(
        df,
        x='volatilidade',
        y='retorno',
        size='score_total',
        color='sharpe',
        hover_data=['ticker', 'nome'],
        labels={
            'volatilidade': 'Volatilidade (Risco) %',
            'retorno': 'Retorno %',
            'sharpe': 'Sharpe Ratio',
            'score_total': 'Score'
        },
        title='Retorno vs Risco (Volatilidade)',
        color_continuous_scale='RdYlGn'
    )
    
    fig.update_layout(height=500, template='plotly_white')
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Como interpretar:**
    - 🎯 **Ideal**: Alto retorno + Baixa volatilidade (canto superior esquerdo)
    - ⚠️ **Evitar**: Baixo retorno + Alta volatilidade (canto inferior direito)
    - O tamanho da bolha representa o score total
    """)


def criar_grafico_correlacao(df):
    """Cria matriz de correlação entre fundos."""
    from utils.data_fetcher import fetch_multiple_stocks
    
    st.info("🔄 Calculando correlação entre os fundos...")
    
    # Buscar dados de todos os fundos
    periodo = '6mo'  # 6 meses para correlação
    dados_fundos = fetch_multiple_stocks(df['ticker'].tolist(), periodo)
    
    if not dados_fundos:
        st.warning("Não foi possível calcular a correlação.")
        return
    
    # Criar DataFrame com preços de fechamento
    df_precos = pd.DataFrame()
    for ticker, dados in dados_fundos.items():
        if not dados.empty:
            df_precos[ticker] = dados['Close']
    
    if df_precos.empty or len(df_precos.columns) < 2:
        st.warning("Dados insuficientes para calcular correlação.")
        return
    
    # Calcular correlação
    correlacao = df_precos.corr()
    
    # Criar heatmap
    fig = go.Figure(data=go.Heatmap(
        z=correlacao.values,
        x=correlacao.columns,
        y=correlacao.columns,
        colorscale='RdBu',
        zmid=0,
        text=correlacao.values.round(2),
        texttemplate='%{text}',
        textfont={"size": 10},
        colorbar=dict(title="Correlação")
    ))
    
    fig.update_layout(
        title='Matriz de Correlação entre Fundos',
        height=600,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Interpretação da Correlação:**
    - 🔴 **Próximo de 1**: Fundos se movem juntos (alta correlação)
    - ⚪ **Próximo de 0**: Fundos independentes (sem correlação)
    - 🔵 **Próximo de -1**: Fundos se movem em direções opostas (correlação negativa)
    
    💡 **Dica**: Para diversificação, escolha fundos com baixa correlação entre si!
    """)

