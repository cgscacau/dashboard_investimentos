"""Módulo de análise de ações individuais - versão melhorada."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from config import Config
from utils.data_fetcher import fetch_stock_data, get_stock_info
from utils.indicators import calculate_all_indicators, get_signal_interpretation
from utils.formatters import formatar_moeda, formatar_percentual, traduzir_setor, obter_simbolo_moeda


def show():
    """Exibe a página de análise de ações."""
    
    # CSS específico da página
    st.markdown("""
        <style>
        /* Cards de métricas personalizados */
        .metric-card {
            padding: 20px;
            border-radius: 15px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
        }
        
        .metric-label {
            color: white;
            font-size: 0.9rem;
            margin: 0;
            font-weight: 600;
        }
        
        .metric-value {
            color: white;
            font-size: 2rem;
            margin: 10px 0;
            font-weight: 700;
        }
        
        /* Badge de sinal */
        .signal-badge {
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
            margin: 10px 0;
        }
        
        .signal-title {
            color: white;
            margin: 0;
            font-weight: 600;
            font-size: 1.1rem;
        }
        
        .signal-text {
            color: white;
            margin: 10px 0 0 0;
            font-size: 0.9rem;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Título com ícone
    st.markdown("""
        <h1 style='text-align: center; color: #667eea; padding: 20px 0;'>
            📈 Análise Técnica de Ações
        </h1>
    """, unsafe_allow_html=True)
    
    # Sidebar com controles
    with st.sidebar:
        st.markdown("### ⚙️ Configurações de Análise")
        
        # Input do ticker com sugestões
        st.markdown("**📊 Código da Ação**")
        
        # Tabs para ações brasileiras e internacionais
        tab_br, tab_int = st.tabs(["🇧🇷 Brasil", "🌎 Internacional"])
        
        with tab_br:
            ticker_sugestao = st.selectbox(
                "Ações populares:",
                [""] + Config.TICKERS_BRASILEIROS_POPULARES,
                key="ticker_br"
            )
        
        with tab_int:
            ticker_sugestao_int = st.selectbox(
                "Ações populares:",
                [""] + Config.TICKERS_INTERNACIONAIS_POPULARES,
                key="ticker_int"
            )
        
        # Input manual
        ticker_manual = st.text_input(
            "Ou digite o código:",
            value=ticker_sugestao or ticker_sugestao_int or "PETR4.SA",
            help="Ex: PETR4.SA (Brasil) ou AAPL (EUA)"
        ).upper()
        
        ticker = ticker_manual
        
        st.markdown("---")
        
        # Seleção de período
        st.markdown("**📅 Período de Análise**")
        periodo_label = st.selectbox(
            "Selecione o período:",
            options=list(Config.PERIODOS.keys()),
            index=3,  # 1 ano como padrão
            label_visibility="collapsed"
        )
        periodo = Config.PERIODOS[periodo_label]
        
        st.markdown("---")
        
        # Seleção de indicadores
        st.markdown("**📊 Indicadores Técnicos**")
        
        col_ind1, col_ind2 = st.columns(2)
        
        with col_ind1:
            mostrar_rsi = st.checkbox("RSI", value=True)
            mostrar_macd = st.checkbox("MACD", value=True)
            mostrar_bb = st.checkbox("Bollinger", value=True)
        
        with col_ind2:
            mostrar_volume = st.checkbox("Volume", value=True)
            mostrar_sma = st.checkbox("Médias", value=True)
            mostrar_ema = st.checkbox("EMA", value=False)
        
        st.markdown("---")
        
        # Botão de atualizar
        if st.button("🔄 Atualizar Análise", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
    
    # Buscar dados com animação
    with st.spinner(f'🔄 Carregando dados de {ticker}...'):
        dados = fetch_stock_data(ticker, periodo)
    
    if dados is None or dados.empty:
        st.error(f"""
            ### ❌ Não foi possível obter dados para {ticker}
            
            **Possíveis causas:**
            - Código incorreto
            - Ativo não disponível
            - Problemas de conexão
            
            **💡 Dicas:**
            - Para ações brasileiras, use .SA (ex: PETR4.SA)
            - Para ações americanas, use o código direto (ex: AAPL)
            - Verifique se o código está correto
        """)
        return
    
    # Normalizar dados
    dados = normalizar_dados(dados)
    
    # Verificar se tem dados válidos
    if 'Close' not in dados.columns or dados['Close'].isna().all():
        st.error("❌ Dados inválidos recebidos")
        return
    
    # Obter símbolo da moeda
    moeda = obter_simbolo_moeda(ticker)
    
    # === SEÇÃO 1: MÉTRICAS PRINCIPAIS ===
    st.markdown("### 📊 Resumo do Ativo")
    
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        preco_atual = float(dados['Close'].iloc[-1])
        preco_inicial = float(dados['Close'].iloc[0])
        maxima = float(dados['High'].max())
        minima = float(dados['Low'].min())
        variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100
        
        with col1:
            st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);'>
                    <p class='metric-label'>💰 Preço Atual</p>
                    <h2 class='metric-value'>{formatar_moeda(preco_atual, moeda)}</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            cor_variacao = "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)" if variacao >= 0 else "linear-gradient(135deg, #eb3349 0%, #f45c43 100%)"
            icone_variacao = "📈" if variacao >= 0 else "📉"
            st.markdown(f"""
                <div class='metric-card' style='background: {cor_variacao};'>
                    <p class='metric-label'>{icone_variacao} Variação</p>
                    <h2 class='metric-value'>{formatar_percentual(variacao)}</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col3:
            st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #FA8BFF 0%, #2BD2FF 100%);'>
                    <p class='metric-label'>⬆️ Máxima</p>
                    <h2 class='metric-value'>{formatar_moeda(maxima, moeda)}</h2>
                </div>
            """, unsafe_allow_html=True)
        
        with col4:
            st.markdown(f"""
                <div class='metric-card' style='background: linear-gradient(135deg, #FF6B6B 0%, #FFE66D 100%);'>
                    <p class='metric-label'>⬇️ Mínima</p>
                    <h2 class='metric-value'>{formatar_moeda(minima, moeda)}</h2>
                </div>
            """, unsafe_allow_html=True)
    
    except (ValueError, TypeError, IndexError) as e:
        st.error(f"❌ Erro ao processar métricas: {str(e)}")
        return
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === SEÇÃO 2: CALCULAR INDICADORES ===
    with st.spinner('🧮 Calculando indicadores técnicos...'):
        indicators = calculate_all_indicators(dados)
    
    # === SEÇÃO 3: GRÁFICO PRINCIPAL ===
    st.markdown("### 📈 Gráfico de Candlestick")
    criar_grafico_principal(dados, indicators, ticker, mostrar_bb, mostrar_sma, mostrar_ema, moeda)
    
    # === SEÇÃO 4: INDICADORES TÉCNICOS ===
    st.markdown("### 📊 Indicadores Técnicos")
    
    # Criar tabs para os indicadores
    tabs = []
    if mostrar_rsi and 'RSI' in indicators:
        tabs.append("RSI")
    if mostrar_macd and 'MACD' in indicators:
        tabs.append("MACD")
    if mostrar_volume and 'Volume' in dados.columns:
        tabs.append("Volume")
    
    if tabs:
        tab_objects = st.tabs(tabs)
        
        tab_index = 0
        if mostrar_rsi and 'RSI' in indicators:
            with tab_objects[tab_index]:
                criar_grafico_rsi(indicators['RSI'], ticker)
            tab_index += 1
        
        if mostrar_macd and 'MACD' in indicators:
            with tab_objects[tab_index]:
                criar_grafico_macd(indicators, ticker)
            tab_index += 1
        
        if mostrar_volume and 'Volume' in dados.columns:
            with tab_objects[tab_index]:
                criar_grafico_volume(dados, ticker)
    
    # === SEÇÃO 5: ANÁLISE E SINAIS ===
    st.markdown("### 🎯 Sinais de Trading")
    
    signals = get_signal_interpretation(indicators)
    
    if signals:
        num_signals = len(signals)
        cols = st.columns(min(num_signals, 3))  # Máximo 3 colunas
        
        for i, (indicator, signal) in enumerate(signals.items()):
            col_index = i % 3
            
            with cols[col_index]:
                # Determinar cor e ícone do badge
                if "🟢" in signal:
                    cor = "linear-gradient(135deg, #11998e 0%, #38ef7d 100%)"
                    icone = "✅"
                elif "🔴" in signal:
                    cor = "linear-gradient(135deg, #eb3349 0%, #f45c43 100%)"
                    icone = "⚠️"
                else:
                    cor = "linear-gradient(135deg, #FFD89B 0%, #19547B 100%)"
                    icone = "ℹ️"
                
                # Remover emoji do texto do sinal
                texto_sinal = signal.replace("🟢", "").replace("🔴", "").replace("🟡", "").strip()
                
                st.markdown(f"""
                    <div class='signal-badge' style='background: {cor};'>
                        <h4 class='signal-title'>{icone} {indicator}</h4>
                        <p class='signal-text'>{texto_sinal}</p>
                    </div>
                """, unsafe_allow_html=True)
    else:
        st.info("💡 Não há sinais disponíveis no momento. Aguarde mais dados históricos.")
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    # === SEÇÃO 6: ESTATÍSTICAS E INFORMAÇÕES ===
    col_left, col_right = st.columns(2)
    
    with col_left:
        with st.expander("📈 Estatísticas Detalhadas", expanded=False):
            mostrar_estatisticas(dados, indicators, moeda)
    
    with col_right:
        with st.expander("🏢 Informações da Empresa", expanded=False):
            mostrar_info_empresa(ticker)


def normalizar_dados(dados):
    """Normaliza o DataFrame removendo multi-index se existir."""
    if dados.empty:
        return dados
    
    if isinstance(dados.columns, pd.MultiIndex):
        dados.columns = dados.columns.get_level_values(0)
    
    colunas_esperadas = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in colunas_esperadas:
        if col not in dados.columns:
            for dados_col in dados.columns:
                if col.lower() == str(dados_col).lower():
                    dados.rename(columns={dados_col: col}, inplace=True)
                    break
    
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in dados.columns:
            dados[col] = pd.to_numeric(dados[col], errors='coerce')
    
    dados = dados.dropna(subset=['Close'])
    
    return dados


def criar_grafico_principal(dados, indicators, ticker, mostrar_bb, mostrar_sma, mostrar_ema, moeda):
    """Cria o gráfico principal de candlestick com indicadores."""
    
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=dados.index,
        open=dados['Open'],
        high=dados['High'],
        low=dados['Low'],
        close=dados['Close'],
        name='Preço',
        increasing_line_color='#26a69a',
        decreasing_line_color='#ef5350'
    ))
    
    # Bandas de Bollinger
    if mostrar_bb and all(k in indicators for k in ['BB_upper', 'BB_middle', 'BB_lower']):
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=indicators['BB_upper'],
            name='BB Superior',
            line=dict(color='rgba(250, 250, 250, 0.3)', dash='dash', width=1),
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=indicators['BB_middle'],
            name='BB Média',
            line=dict(color='rgba(100, 181, 246, 0.5)', dash='dash', width=1),
            showlegend=True
        ))
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=indicators['BB_lower'],
            name='BB Inferior',
            line=dict(color='rgba(250, 250, 250, 0.3)', dash='dash', width=1),
            fill='tonexty',
            fillcolor='rgba(100, 181, 246, 0.1)',
            showlegend=True
        ))
    
    # Médias Móveis Simples
    if mostrar_sma:
        cores_sma = {
            'SMA_20': '#FF6B6B',
            'SMA_50': '#4ECDC4',
            'SMA_200': '#95E1D3'
        }
        
        for sma_name, cor in cores_sma.items():
            if sma_name in indicators and not indicators[sma_name].isna().all():
                periodo = sma_name.split('_')[1]
                fig.add_trace(go.Scatter(
                    x=dados.index,
                    y=indicators[sma_name],
                    name=f'Média {periodo}',
                    line=dict(color=cor, width=2),
                    showlegend=True
                ))
    
    # Médias Móveis Exponenciais
    if mostrar_ema:
        cores_ema = {
            'EMA_12': '#FFD93D',
            'EMA_26': '#6BCB77'
        }
        
        for ema_name, cor in cores_ema.items():
            if ema_name in indicators and not indicators[ema_name].isna().all():
                periodo = ema_name.split('_')[1]
                fig.add_trace(go.Scatter(
                    x=dados.index,
                    y=indicators[ema_name],
                    name=f'EMA {periodo}',
                    line=dict(color=cor, width=2, dash='dot'),
                    showlegend=True
                ))
    
    # Layout do gráfico
    fig.update_layout(
        title={
            'text': f'<b>{ticker}</b> - Análise de Candlestick',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 24, 'color': '#667eea'}
        },
        yaxis_title=f'Preço ({moeda})',
        xaxis_title='Data',
        height=650,
        xaxis_rangeslider_visible=False,
        hovermode='x unified',
        template='plotly_white',
        plot_bgcolor='rgba(240, 242, 246, 0.5)',
        paper_bgcolor='white',
        font=dict(size=12, family='Arial'),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            bgcolor='rgba(255, 255, 255, 0.8)',
            bordercolor='#667eea',
            borderwidth=1
        ),
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            showline=True,
            linecolor='#667eea'
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(200, 200, 200, 0.3)',
            showline=True,
            linecolor='#667eea'
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_rsi(rsi, ticker):
    """Cria o gráfico do RSI."""
    if rsi.isna().all():
        st.warning("⚠️ RSI não disponível para este período")
        return
    
    fig = go.Figure()
    
    # Linha do RSI
    fig.add_trace(go.Scatter(
        x=rsi.index,
        y=rsi,
        name='RSI',
        line=dict(color='#667eea', width=3),
        fill='tozeroy',
        fillcolor='rgba(102, 126, 234, 0.1)'
    ))
    
    # Linhas de referência
    fig.add_hline(
        y=70, 
        line_dash="dash", 
        line_color="#f45c43", 
        line_width=2,
        annotation_text="Sobrecomprado (70)",
        annotation_position="right"
    )
    fig.add_hline(
        y=30, 
        line_dash="dash", 
        line_color="#38ef7d", 
        line_width=2,
        annotation_text="Sobrevendido (30)",
        annotation_position="right"
    )
    fig.add_hline(
        y=50, 
        line_dash="dot", 
        line_color="gray", 
        line_width=1,
        annotation_text="Neutro (50)",
        annotation_position="right"
    )
    
    # Colorir áreas
    fig.add_hrect(
        y0=70, y1=100, 
        fillcolor="red", opacity=0.1,
        line_width=0
    )
    fig.add_hrect(
        y0=0, y1=30, 
        fillcolor="green", opacity=0.1,
        line_width=0
    )
    
    fig.update_layout(
        title={
            'text': f'<b>RSI - Índice de Força Relativa</b><br><sub>{ticker}</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title='RSI',
        xaxis_title='Data',
        height=400,
        hovermode='x unified',
        template='plotly_white',
        yaxis=dict(range=[0, 100])
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretação atual
    ultimo_rsi = float(rsi.iloc[-1])
    if ultimo_rsi > 70:
        st.warning(f"⚠️ **RSI atual: {ultimo_rsi:.2f}** - Ativo sobrecomprado, possível correção")
    elif ultimo_rsi < 30:
        st.success(f"✅ **RSI atual: {ultimo_rsi:.2f}** - Ativo sobrevendido, possível recuperação")
    else:
        st.info(f"ℹ️ **RSI atual: {ultimo_rsi:.2f}** - Ativo em zona neutra")


def criar_grafico_macd(indicators, ticker):
    """Cria o gráfico do MACD."""
    if 'MACD' not in indicators or indicators['MACD'].isna().all():
        st.warning("⚠️ MACD não disponível para este período")
        return
    
    fig = go.Figure()
    
    # Linha MACD
    if 'MACD' in indicators:
        fig.add_trace(go.Scatter(
            x=indicators['MACD'].index,
            y=indicators['MACD'],
            name='MACD',
            line=dict(color='#2196F3', width=2)
        ))
    
    # Linha de Sinal
    if 'MACD_signal' in indicators:
        fig.add_trace(go.Scatter(
            x=indicators['MACD_signal'].index,
            y=indicators['MACD_signal'],
            name='Sinal',
            line=dict(color='#FF9800', width=2)
        ))
    
    # Histograma
    if 'MACD_hist' in indicators:
        colors = ['#26a69a' if val >= 0 else '#ef5350' for val in indicators['MACD_hist']]
        fig.add_trace(go.Bar(
            x=indicators['MACD_hist'].index,
            y=indicators['MACD_hist'],
            name='Histograma',
            marker_color=colors,
            opacity=0.5
        ))
    
    # Linha zero
    fig.add_hline(y=0, line_dash="dash", line_color="gray", line_width=1)
    
    fig.update_layout(
        title={
            'text': f'<b>MACD - Convergência/Divergência de Médias</b><br><sub>{ticker}</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title='MACD',
        xaxis_title='Data',
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Interpretação
    if 'MACD' in indicators and 'MACD_signal' in indicators:
        ultimo_macd = float(indicators['MACD'].iloc[-1])
        ultimo_sinal = float(indicators['MACD_signal'].iloc[-1])
        
        if ultimo_macd > ultimo_sinal:
            st.success(f"✅ **MACD acima do sinal** - Tendência de alta")
        else:
            st.warning(f"⚠️ **MACD abaixo do sinal** - Tendência de baixa")


def criar_grafico_volume(dados, ticker):
    """Cria o gráfico de volume."""
    if 'Volume' not in dados.columns or dados['Volume'].isna().all():
        st.warning("⚠️ Volume não disponível para este período")
        return
    
    fig = go.Figure()
    
    # Cores baseadas no fechamento
    colors = ['#26a69a' if dados['Close'].iloc[i] >= dados['Open'].iloc[i] else '#ef5350' 
              for i in range(len(dados))]
    
    fig.add_trace(go.Bar(
        x=dados.index,
        y=dados['Volume'],
        name='Volume',
        marker_color=colors,
        opacity=0.7,
        showlegend=False
    ))
    
    # Média de volume
    volume_ma = dados['Volume'].rolling(window=20).mean()
    fig.add_trace(go.Scatter(
        x=dados.index,
        y=volume_ma,
        name='Média 20 dias',
        line=dict(color='#FFA726', width=2, dash='dash')
    ))
    
    fig.update_layout(
        title={
            'text': f'<b>Volume de Negociação</b><br><sub>{ticker}</sub>',
            'x': 0.5,
            'xanchor': 'center'
        },
        yaxis_title='Volume',
        xaxis_title='Data',
        height=400,
        hovermode='x unified',
        template='plotly_white'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Estatísticas de volume
    col1, col2, col3 = st.columns(3)
    
    with col1:
        volume_medio = dados['Volume'].mean()
        st.metric("Volume Médio", f"{volume_medio:,.0f}")
    
    with col2:
        volume_atual = dados['Volume'].iloc[-1]
        st.metric("Volume Atual", f"{volume_atual:,.0f}")
    
    with col3:
        variacao_volume = ((volume_atual - volume_medio) / volume_medio) * 100
        st.metric("Variação vs Média", f"{variacao_volume:+.1f}%")


def mostrar_estatisticas(dados, indicators, moeda):
    """Mostra estatísticas detalhadas."""
    
    st.markdown("#### 📊 Estatísticas de Preço")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write(f"**Média:** {formatar_moeda(dados['Close'].mean(), moeda)}")
        st.write(f"**Mediana:** {formatar_moeda(dados['Close'].median(), moeda)}")
        st.write(f"**Desvio Padrão:** {formatar_moeda(dados['Close'].std(), moeda)}")
    
    with col2:
        volatilidade = (dados['Close'].std() / dados['Close'].mean() * 100)
        st.write(f"**Volatilidade:** {formatar_percentual(volatilidade)}")
        
        # Amplitude
        amplitude = dados['High'].max() - dados['Low'].min()
        st.write(f"**Amplitude:** {formatar_moeda(amplitude, moeda)}")
        
        # Retorno total
        retorno_total = ((dados['Close'].iloc[-1] - dados['Close'].iloc[0]) / dados['Close'].iloc[0]) * 100
        st.write(f"**Retorno Total:** {formatar_percentual(retorno_total)}")
    
    st.markdown("---")
    st.markdown("#### 📈 Indicadores Atuais")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if 'RSI' in indicators and not indicators['RSI'].isna().all():
            st.write(f"**RSI:** {float(indicators['RSI'].iloc[-1]):.2f}")
        
        if 'SMA_20' in indicators and not indicators['SMA_20'].isna().all():
            st.write(f"**Média 20:** {formatar_moeda(indicators['SMA_20'].iloc[-1], moeda)}")
        
        if 'SMA_50' in indicators and not indicators['SMA_50'].isna().all():
            st.write(f"**Média 50:** {formatar_moeda(indicators['SMA_50'].iloc[-1], moeda)}")
    
    with col2:
        if 'SMA_200' in indicators and not indicators['SMA_200'].isna().all():
            st.write(f"**Média 200:** {formatar_moeda(indicators['SMA_200'].iloc[-1], moeda)}")
        
        if 'MACD' in indicators and not indicators['MACD'].isna().all():
            st.write(f"**MACD:** {float(indicators['MACD'].iloc[-1]):.4f}")
        
        # Volume médio
        if 'Volume' in dados.columns:
            vol_medio = dados['Volume'].mean()
            st.write(f"**Vol. Médio:** {vol_medio:,.0f}")


def mostrar_info_empresa(ticker):
    """Mostra informações da empresa."""
    
    with st.spinner('Carregando informações da empresa...'):
        info = get_stock_info(ticker)
    
    if info:
        st.markdown("#### 🏢 Informações Gerais")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if 'longName' in info:
                st.write(f"**Nome:** {info['longName']}")
            if 'sector' in info:
                setor_pt = traduzir_setor(info['sector'])
                st.write(f"**Setor:** {setor_pt}")
            if 'industry' in info:
                st.write(f"**Indústria:** {info['industry']}")
            if 'country' in info:
                st.write(f"**País:** {info['country']}")
        
        with col2:
            if 'marketCap' in info and info['marketCap']:
                try:
                    from utils.formatters import formatar_numero_grande
                    market_cap = formatar_numero_grande(info['marketCap'])
                    moeda = obter_simbolo_moeda(ticker)
                    st.write(f"**Valor de Mercado:** {moeda} {market_cap}")
                except (ValueError, TypeError):
                    pass
            
            if 'dividendYield' in info and info['dividendYield']:
                try:
                    div_yield = float(info['dividendYield']) * 100
                    st.write(f"**Dividend Yield:** {div_yield:.2f}%")
                except (ValueError, TypeError):
                    st.write("**Dividend Yield:** N/A")
            else:
                st.write("**Dividend Yield:** N/A")
            
            if 'beta' in info and info['beta']:
                try:
                    st.write(f"**Beta:** {float(info['beta']):.2f}")
                except (ValueError, TypeError):
                    pass
            
            if 'trailingPE' in info and info['trailingPE']:
                try:
                    st.write(f"**P/L:** {float(info['trailingPE']):.2f}")
                except (ValueError, TypeError):
                    pass
        
        # Descrição da empresa
        if 'longBusinessSummary' in info:
            st.markdown("---")
            st.markdown("#### 📝 Sobre a Empresa")
            with st.expander("Ver descrição completa"):
                st.write(info['longBusinessSummary'])
    
    else:
        st.info("ℹ️ Informações da empresa não disponíveis no momento.")
