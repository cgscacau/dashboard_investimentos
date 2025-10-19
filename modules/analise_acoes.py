"""Módulo de análise de ações individuais."""

import streamlit as st
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from config import Config
from utils.data_fetcher import fetch_stock_data, get_stock_info
from utils.indicators import calculate_all_indicators, get_signal_interpretation


def show():
    """Exibe a página de análise de ações."""
    st.title("📈 Análise de Ações")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("Configurações")
        
        # Input do ticker
        ticker = st.text_input(
            "Digite o ticker da ação:",
            value="PETR4.SA",
            help="Ex: PETR4.SA (Brasil) ou AAPL (EUA)"
        ).upper()
        
        # Seleção de período
        periodo_label = st.selectbox(
            "Período de análise:",
            options=list(Config.PERIODOS.keys()),
            index=3  # 1 ano como padrão
        )
        periodo = Config.PERIODOS[periodo_label]
        
        # Seleção de indicadores
        st.subheader("Indicadores Técnicos")
        mostrar_rsi = st.checkbox("RSI", value=True)
        mostrar_macd = st.checkbox("MACD", value=True)
        mostrar_bb = st.checkbox("Bandas de Bollinger", value=True)
        mostrar_volume = st.checkbox("Volume", value=True)
        mostrar_sma = st.checkbox("Médias Móveis", value=True)
    
    # Buscar dados
    with st.spinner(f"Carregando dados de {ticker}..."):
        dados = fetch_stock_data(ticker, periodo)
    
    if dados is None or dados.empty:
        st.error(f"❌ Não foi possível obter dados para o ticker {ticker}")
        st.info("💡 Verifique se o ticker está correto. Para ações brasileiras, use o sufixo .SA (ex: PETR4.SA)")
        return
    
    # Normalizar dados se tiver multi-index
    dados = normalizar_dados(dados)
    
    # Verificar se tem dados válidos
    if 'Close' not in dados.columns or dados['Close'].isna().all():
        st.error("❌ Dados inválidos recebidos")
        return
    
    # Informações da ação
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        preco_atual = float(dados['Close'].iloc[-1])
        preco_inicial = float(dados['Close'].iloc[0])
        maxima = float(dados['High'].max())
        minima = float(dados['Low'].min())
        variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100
        
        with col1:
            st.metric("Preço Atual", f"R$ {preco_atual:.2f}")
        
        with col2:
            st.metric("Variação no Período", f"{variacao:.2f}%", delta=f"{variacao:.2f}%")
        
        with col3:
            st.metric("Máxima", f"R$ {maxima:.2f}")
        
        with col4:
            st.metric("Mínima", f"R$ {minima:.2f}")
    
    except (ValueError, TypeError, IndexError) as e:
        st.error(f"❌ Erro ao processar métricas: {str(e)}")
        return
    
    # Calcular indicadores
    with st.spinner("Calculando indicadores técnicos..."):
        indicators = calculate_all_indicators(dados)
    
    # Criar gráfico principal
    criar_grafico_principal(dados, indicators, ticker, mostrar_bb, mostrar_sma)
    
    # Gráficos de indicadores
    if mostrar_rsi and 'RSI' in indicators:
        criar_grafico_rsi(indicators['RSI'], ticker)
    
    if mostrar_macd and 'MACD' in indicators:
        criar_grafico_macd(indicators, ticker)
    
    if mostrar_volume and 'Volume' in dados.columns:
        criar_grafico_volume(dados, ticker)
    
    # Análise e sinais
    st.header("📊 Análise Técnica")
    signals = get_signal_interpretation(indicators)
    
    if signals:
        for indicator, signal in signals.items():
            st.write(f"**{indicator}:** {signal}")
    else:
        st.info("Não há sinais disponíveis no momento.")
    
    # Estatísticas adicionais
    with st.expander("📈 Estatísticas Detalhadas"):
        mostrar_estatisticas(dados, indicators)
    
    # Informações da empresa
    with st.expander("🏢 Informações da Empresa"):
        mostrar_info_empresa(ticker)


def normalizar_dados(dados):
    """
    Normaliza o DataFrame removendo multi-index se existir.
    
    Args:
        dados: DataFrame com dados de ações
        
    Returns:
        DataFrame normalizado
    """
    if dados.empty:
        return dados
    
    # Se as colunas forem MultiIndex, flatten
    if isinstance(dados.columns, pd.MultiIndex):
        dados.columns = dados.columns.get_level_values(0)
    
    # Garantir que as colunas esperadas existem
    colunas_esperadas = ['Open', 'High', 'Low', 'Close', 'Volume']
    for col in colunas_esperadas:
        if col not in dados.columns:
            # Tentar encontrar coluna similar (case insensitive)
            for dados_col in dados.columns:
                if col.lower() == str(dados_col).lower():
                    dados.rename(columns={dados_col: col}, inplace=True)
                    break
    
    # Converter para numérico
    for col in ['Open', 'High', 'Low', 'Close', 'Volume']:
        if col in dados.columns:
            dados[col] = pd.to_numeric(dados[col], errors='coerce')
    
    # Remover linhas com NaN em Close
    dados = dados.dropna(subset=['Close'])
    
    return dados


def criar_grafico_principal(dados, indicators, ticker, mostrar_bb, mostrar_sma):
    """Cria o gráfico principal de candlestick com indicadores."""
    fig = go.Figure()
    
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=dados.index,
        open=dados['Open'],
        high=dados['High'],
        low=dados['Low'],
        close=dados['Close'],
        name='Preço'
    ))
    
    # Bandas de Bollinger
    if mostrar_bb and all(k in indicators for k in ['BB_upper', 'BB_middle', 'BB_lower']):
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=indicators['BB_upper'],
            name='BB Superior',
            line=dict(color='gray', dash='dash'),
            opacity=0.5
        ))
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=indicators['BB_middle'],
            name='BB Média',
            line=dict(color='blue', dash='dash'),
            opacity=0.5
        ))
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=indicators['BB_lower'],
            name='BB Inferior',
            line=dict(color='gray', dash='dash'),
            fill='tonexty',
            opacity=0.3
        ))
    
    # Médias Móveis
    if mostrar_sma:
        if 'SMA_20' in indicators and not indicators['SMA_20'].isna().all():
            fig.add_trace(go.Scatter(
                x=dados.index,
                y=indicators['SMA_20'],
                name='SMA 20',
                line=dict(color='orange', width=1)
            ))
        if 'SMA_50' in indicators and not indicators['SMA_50'].isna().all():
            fig.add_trace(go.Scatter(
                x=dados.index,
                y=indicators['SMA_50'],
                name='SMA 50',
                line=dict(color='red', width=1)
            ))
        if 'SMA_200' in indicators and not indicators['SMA_200'].isna().all():
            fig.add_trace(go.Scatter(
                x=dados.index,
                y=indicators['SMA_200'],
                name='SMA 200',
                line=dict(color='purple', width=1)
            ))
    
    fig.update_layout(
        title=f'Gráfico de Candlestick - {ticker}',
        yaxis_title='Preço (R$)',
        xaxis_title='Data',
        height=600,
        xaxis_rangeslider_visible=False,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_rsi(rsi, ticker):
    """Cria o gráfico do RSI."""
    if rsi.isna().all():
        st.warning("RSI não disponível para este período")
        return
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=rsi.index,
        y=rsi,
        name='RSI',
        line=dict(color='purple', width=2)
    ))
    
    # Linhas de referência
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Sobrecomprado")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Sobrevendido")
    fig.add_hline(y=50, line_dash="dot", line_color="gray")
    
    fig.update_layout(
        title=f'RSI (Relative Strength Index) - {ticker}',
        yaxis_title='RSI',
        xaxis_title='Data',
        height=300,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_macd(indicators, ticker):
    """Cria o gráfico do MACD."""
    if 'MACD' not in indicators or indicators['MACD'].isna().all():
        st.warning("MACD não disponível para este período")
        return
    
    fig = go.Figure()
    
    if 'MACD' in indicators:
        fig.add_trace(go.Scatter(
            x=indicators['MACD'].index,
            y=indicators['MACD'],
            name='MACD',
            line=dict(color='blue', width=2)
        ))
    
    if 'MACD_signal' in indicators:
        fig.add_trace(go.Scatter(
            x=indicators['MACD_signal'].index,
            y=indicators['MACD_signal'],
            name='Signal',
            line=dict(color='red', width=2)
        ))
    
    if 'MACD_hist' in indicators:
        colors = ['green' if val >= 0 else 'red' for val in indicators['MACD_hist']]
        fig.add_trace(go.Bar(
            x=indicators['MACD_hist'].index,
            y=indicators['MACD_hist'],
            name='Histograma',
            marker_color=colors,
            opacity=0.3
        ))
    
    fig.update_layout(
        title=f'MACD (Moving Average Convergence Divergence) - {ticker}',
        yaxis_title='MACD',
        xaxis_title='Data',
        height=300,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_volume(dados, ticker):
    """Cria o gráfico de volume."""
    if 'Volume' not in dados.columns or dados['Volume'].isna().all():
        st.warning("Volume não disponível para este período")
        return
    
    fig = go.Figure()
    
    colors = ['green' if dados['Close'].iloc[i] >= dados['Open'].iloc[i] else 'red' 
              for i in range(len(dados))]
    
    fig.add_trace(go.Bar(
        x=dados.index,
        y=dados['Volume'],
        name='Volume',
        marker_color=colors,
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f'Volume de Negociação - {ticker}',
        yaxis_title='Volume',
        xaxis_title='Data',
        height=300,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def mostrar_estatisticas(dados, indicators):
    """Mostra estatísticas detalhadas."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estatísticas de Preço")
        try:
            st.write(f"**Média:** R$ {float(dados['Close'].mean()):.2f}")
            st.write(f"**Mediana:** R$ {float(dados['Close'].median()):.2f}")
            st.write(f"**Desvio Padrão:** R$ {float(dados['Close'].std()):.2f}")
            st.write(f"**Volatilidade:** {float(dados['Close'].std() / dados['Close'].mean() * 100):.2f}%")
        except (ValueError, TypeError):
            st.warning("Erro ao calcular estatísticas")
    
    with col2:
        st.subheader("Indicadores Atuais")
        try:
            if 'RSI' in indicators and not indicators['RSI'].isna().all():
                st.write(f"**RSI:** {float(indicators['RSI'].iloc[-1]):.2f}")
            if 'SMA_20' in indicators and not indicators['SMA_20'].isna().all():
                st.write(f"**SMA 20:** R$ {float(indicators['SMA_20'].iloc[-1]):.2f}")
            if 'SMA_50' in indicators and not indicators['SMA_50'].isna().all():
                st.write(f"**SMA 50:** R$ {float(indicators['SMA_50'].iloc[-1]):.2f}")
            if 'SMA_200' in indicators and not indicators['SMA_200'].isna().all():
                st.write(f"**SMA 200:** R$ {float(indicators['SMA_200'].iloc[-1]):.2f}")
        except (ValueError, TypeError, IndexError):
            st.warning("Alguns indicadores não estão disponíveis")


def mostrar_info_empresa(ticker):
    """Mostra informações da empresa."""
    info = get_stock_info(ticker)
    
    if info:
        col1, col2 = st.columns(2)
        
        with col1:
            if 'longName' in info:
                st.write(f"**Nome:** {info['longName']}")
            if 'sector' in info:
                st.write(f"**Setor:** {info['sector']}")
            if 'industry' in info:
                st.write(f"**Indústria:** {info['industry']}")
        
        with col2:
            if 'marketCap' in info:
                try:
                    st.write(f"**Market Cap:** R$ {float(info['marketCap']):,.0f}")
                except (ValueError, TypeError):
                    pass
            if 'dividendYield' in info and info['dividendYield']:
                try:
                    st.write(f"**Dividend Yield:** {float(info['dividendYield'])*100:.2f}%")
                except (ValueError, TypeError):
                    pass
            if 'beta' in info:
                try:
                    st.write(f"**Beta:** {float(info['beta']):.2f}")
                except (ValueError, TypeError):
                    pass
    else:
        st.info("Informações da empresa não disponíveis.")
