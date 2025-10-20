"""Módulo de análise detalhada de um ativo específico."""

import streamlit as st
import plotly.graph_objects as go
from utils.data_fetcher import fetch_stock_data, get_stock_info
from utils.indicators import calculate_all_indicators, get_signal_interpretation
from utils.scoring import calcular_score_ativo
from utils.formatters import formatar_moeda, formatar_percentual, traduzir_setor, obter_simbolo_moeda


def show():
    """Exibe análise detalhada de um ativo."""
    
    st.markdown("""
        <div style='text-align: center; padding: 2rem 0; background: white; border-radius: 20px; 
                    box-shadow: 0 10px 30px rgba(0,0,0,0.1); margin-bottom: 2rem;'>
            <div style='font-size: 4rem; margin-bottom: 1rem;'>🔍</div>
            <h1 style='margin: 0; font-size: 2.5rem; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                       -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
                Análise Detalhada
            </h1>
            <p style='color: #64748b; font-size: 1.1rem; margin-top: 0.5rem;'>
                Análise técnica e fundamentalista completa
            </p>
        </div>
    """, unsafe_allow_html=True)
    
    # Sidebar - Seleção de ativo
    with st.sidebar:
        st.markdown("### 🎯 Selecionar Ativo")
        
        # Usar valor do session_state se existir
        valor_padrao = st.session_state.get('ativo_selecionado', 'PETR4.SA')
        
        ticker = st.text_input(
            "Digite o código:",
            value=valor_padrao,
            help="Ex: PETR4.SA, AAPL, BOVA11.SA"
        ).upper()
        
        # Atualizar session_state
        st.session_state.ativo_selecionado = ticker
        
        periodo_label = st.selectbox(
            "Período:",
            ['1 mês', '3 meses', '6 meses', '1 ano', '2 anos'],
            index=3
        )
        
        periodos_map = {
            '1 mês': '1mo',
            '3 meses': '3mo',
            '6 meses': '6mo',
            '1 ano': '1y',
            '2 anos': '2y'
        }
        periodo = periodos_map[periodo_label]
        
        analisar = st.button("🔍 Analisar", use_container_width=True, type="primary")
    
    # Analisar automaticamente se vier de um ranking
    if ticker and (analisar or valor_padrao != 'PETR4.SA'):
        analisar_ativo(ticker, periodo)
    elif not analisar:
        st.info("👆 Digite um código de ativo e clique em 'Analisar' para começar.")

def analisar_ativo(ticker, periodo):
    """Realiza análise completa do ativo."""
    
    # Buscar dados
    with st.spinner(f'Carregando dados de {ticker}...'):
        dados = fetch_stock_data(ticker, periodo)
        info = get_stock_info(ticker)
    
    if dados is None or dados.empty:
        st.error(f"❌ Não foi possível obter dados para {ticker}")
        return
    
    moeda = obter_simbolo_moeda(ticker)
    
    # Calcular score
    score_data = calcular_score_ativo(dados, info)
    
    if score_data is None:
        st.error("❌ Erro ao calcular score do ativo")
        return
    
    # === HEADER COM SCORE ===
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        nome = info.get('longName', ticker) if info else ticker
        st.markdown(f"## {ticker}")
        st.markdown(f"**{nome}**")
        if info and 'sector' in info:
            setor = traduzir_setor(info['sector'])
            st.caption(f"Setor: {setor}")
    
    with col2:
        st.markdown(f"""
            <div style='background: {score_data['cor']}; color: white; padding: 2rem; 
                        border-radius: 15px; text-align: center;'>
                <div style='font-size: 3rem; font-weight: 700;'>{score_data['total']}</div>
                <div style='font-size: 0.9rem;'>SCORE TOTAL</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div style='background: white; border: 3px solid {score_data['cor']}; 
                        padding: 2rem; border-radius: 15px; text-align: center;'>
                <div style='font-size: 1.5rem; color: {score_data['cor']};'>
                    {score_data['classificacao']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === MÉTRICAS PRINCIPAIS ===
    st.markdown("### 📊 Indicadores de Performance")
    
    col1, col2, col3, col4, col5 = st.columns(5)
    
    with col1:
        criar_metrica_score("📈 Retorno", score_data['retorno'], 
                           formatar_percentual(score_data['retorno_valor']))
    
    with col2:
        criar_metrica_score("📉 Volatilidade", score_data['volatilidade'], 
                           formatar_percentual(score_data['volatilidade_valor']))
    
    with col3:
        criar_metrica_score("⚡ Sharpe", score_data['sharpe'], 
                           f"{score_data['sharpe_valor']:.2f}")
    
    with col4:
        criar_metrica_score("📊 Tendência", score_data['tendencia'], 
                           score_data['tendencia_sinal'])
    
    with col5:
        criar_metrica_score("🎯 RSI", score_data['momento'], 
                           f"{score_data['rsi_valor']:.1f}")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === GRÁFICO DE RADAR ===
    st.markdown("### 🎯 Análise Multidimensional")
    criar_grafico_radar(score_data)
    
    # === ANÁLISE TÉCNICA ===
    st.markdown("### 📈 Análise Técnica")
    
    indicators = calculate_all_indicators(dados)
    signals = get_signal_interpretation(indicators)
    
    if signals:
        cols = st.columns(len(signals))
        for i, (indicator, signal) in enumerate(signals.items()):
            with cols[i]:
                if "🟢" in signal:
                    cor = "#10b981"
                    icone = "✅"
                elif "🔴" in signal:
                    cor = "#ef4444"
                    icone = "⚠️"
                else:
                    cor = "#f59e0b"
                    icone = "ℹ️"
                
                texto_sinal = signal.replace("🟢", "").replace("🔴", "").replace("🟡", "").strip()
                
                st.markdown(f"""
                    <div style='background: white; border-left: 5px solid {cor}; 
                                padding: 1rem; border-radius: 10px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                        <h4 style='color: {cor}; margin: 0;'>{icone} {indicator}</h4>
                        <p style='color: #64748b; margin: 0.5rem 0 0 0;'>{texto_sinal}</p>
                    </div>
                """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === INFORMAÇÕES FUNDAMENTALISTAS ===
    if info:
        st.markdown("### 🏢 Informações Fundamentalistas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Informações Gerais**")
            if 'sector' in info:
                st.write(f"• **Setor:** {traduzir_setor(info['sector'])}")
            if 'industry' in info:
                st.write(f"• **Indústria:** {info['industry']}")
            if 'country' in info:
                st.write(f"• **País:** {info['country']}")
            if 'marketCap' in info and info['marketCap']:
                from utils.formatters import formatar_numero_grande
                market_cap = formatar_numero_grande(info['marketCap'])
                st.write(f"• **Valor de Mercado:** {moeda} {market_cap}")
        
        with col2:
            st.markdown("**Indicadores Financeiros**")
            if 'trailingPE' in info and info['trailingPE']:
                st.write(f"• **P/L:** {info['trailingPE']:.2f}")
            if 'dividendYield' in info and info['dividendYield']:
                div_yield = info['dividendYield'] * 100
                st.write(f"• **Dividend Yield:** {div_yield:.2f}%")
            if 'beta' in info and info['beta']:
                st.write(f"• **Beta:** {info['beta']:.2f}")
            if 'profitMargins' in info and info['profitMargins']:
                margin = info['profitMargins'] * 100
                st.write(f"• **Margem de Lucro:** {margin:.2f}%")
    
    # === RECOMENDAÇÃO FINAL ===
    st.markdown("### 💡 Recomendação")
    
    if score_data['total'] >= 75:
        st.success(f"""
        **🟢 FORTE COMPRA**
        
        {ticker} apresenta excelentes indicadores técnicos e fundamentalistas. 
        Score de {score_data['total']:.1f} indica uma oportunidade atrativa de investimento.
        
        **Pontos Fortes:**
        - Retorno consistente no período
        - Boa relação risco/retorno (Sharpe)
        - Tendência técnica favorável
        """)
    elif score_data['total'] >= 60:
        st.info(f"""
        **🟡 COMPRA MODERADA**
        
        {ticker} apresenta bons indicadores, mas com alguns pontos de atenção. 
        Score de {score_data['total']:.1f} sugere potencial, mas com cautela.
        
        **Recomendação:** Adequado para carteiras diversificadas.
        """)
    else:
        st.warning(f"""
        **🔴 AGUARDAR**
        
        {ticker} não apresenta indicadores favoráveis no momento. 
        Score de {score_data['total']:.1f} sugere aguardar melhores oportunidades.
        
        **Sugestão:** Monitorar e aguardar melhora nos indicadores técnicos.
        """)


def criar_metrica_score(titulo, score, valor):
    """Cria card de métrica com score."""
    cor = "#10b981" if score >= 70 else "#f59e0b" if score >= 50 else "#ef4444"
    
    st.markdown(f"""
        <div style='background: white; padding: 1.5rem; border-radius: 15px; 
                    box-shadow: 0 4px 12px rgba(0,0,0,0.1); text-align: center;
                    border-top: 4px solid {cor};'>
            <div style='color: #64748b; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem;'>
                {titulo}
            </div>
            <div style='color: {cor}; font-size: 2rem; font-weight: 700; margin: 0.5rem 0;'>
                {score:.0f}
            </div>
            <div style='color: #94a3b8; font-size: 0.9rem;'>
                {valor}
            </div>
        </div>
    """, unsafe_allow_html=True)


def criar_grafico_radar(score_data):
    """Cria gráfico de radar com os scores."""
    
    categorias = ['Retorno', 'Volatilidade', 'Sharpe', 'Tendência', 'Momento']
    valores = [
        score_data['retorno'],
        score_data['volatilidade'],
        score_data['sharpe'],
        score_data['tendencia'],
        score_data['momento']
    ]
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatterpolar(
        r=valores,
        theta=categorias,
        fill='toself',
        fillcolor='rgba(102, 126, 234, 0.3)',
        line=dict(color='#667eea', width=3),
        name='Score'
    ))
    
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickvals=[0, 25, 50, 75, 100],
                gridcolor='#e2e8f0'
            ),
            angularaxis=dict(
                gridcolor='#e2e8f0'
            ),
            bgcolor='white'
        ),
        showlegend=False,
        height=500,
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)

