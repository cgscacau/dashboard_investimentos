"""Módulo de análise de ações individuais."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
import numpy as np
from config import Config
from utils.data_fetcher import fetch_stock_data, get_stock_info
from utils.indicators import calculate_all_indicators, get_signal_interpretation
from utils.formatters import formatar_moeda, formatar_percentual, traduzir_setor, obter_simbolo_moeda


def show():
    """Exibe a página de análise de ações."""
    st.title("📈 Análise de Ações")
    
    # Sidebar com controles
    with st.sidebar:
        st.header("Configurações")
        
        # Input do ticker
        ticker = st.text_input(
            "Digite o código da ação:",
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
        st.error(f"❌ Não foi possível obter dados para o código {ticker}")
        st.info("💡 Verifique se o código está correto. Para ações brasileiras, use o sufixo .SA (ex: PETR4.SA)")
        return
    
    # Normalizar dados
    dados = normalizar_dados(dados)
    
    # Verificar se tem dados válidos
    if 'Close' not in dados.columns or dados['Close'].isna().all():
        st.error("❌ Dados inválidos recebidos")
        return
    
    # Obter símbolo da moeda
    moeda = obter_simbolo_moeda(ticker)
    
    # Informações da ação
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        preco_atual = float(dados['Close'].iloc[-1])
        preco_inicial = float(dados['Close'].iloc[0])
        maxima = float(dados['High'].max())
        minima = float(dados['Low'].min())
        variacao = ((preco_atual - preco_inicial) / preco_inicial) * 100
        
        with col1:
            st.metric("Preço Atual", formatar_moeda(preco_atual, moeda))
        
        with col2:
            st.metric("Variação no Período", formatar_percentual(variacao), 
                     delta=formatar_percentual(variacao))
        
        with col3:
            st.metric("Máxima", formatar_moeda(maxima, moeda))
        
        with col4:
            st.metric("Mínima", formatar_moeda(minima, moeda))
    
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
        mostrar_estatisticas(dados, indicators, moeda)
    
    # Informações da empresa
    with st.expander("🏢 Informações da Empresa"):
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


def criar_grafico_principal(dados, indicators, ticker, mostrar_bb, mostrar_sma):
    """Cria o gráfico principal de candlestick com indicadores."""
    fig = go.Figure()
    
    fig.add_trace(go.Candlestick(
        x=dados.index,
        open=dados['Open'],
        high=dados['High'],
        low=dados['Low'],
        close=dados['Close'],
        name='Preço'
    ))
    
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
    
    if mostrar_sma:
        if 'SMA_20' in indicators and not indicators['SMA_20'].isna().all():
            fig.add_trace(go.Scatter(
                x=dados.index,
                y=indicators['SMA_20'],
                name='Média 20',
                line=dict(color='orange', width=1)
            ))
        if 'SMA_50' in indicators and not indicators['SMA_50'].isna().all():
            fig.add_trace(go.Scatter(
                x=dados.index,
                y=indicators['SMA_50'],
                name='Média 50',
                line=dict(color='red', width=1)
            ))
        if 'SMA_200' in indicators and not indicators['SMA_200'].isna().all():
            fig.add_trace(go.Scatter(
                x=dados.index,
                y=indicators['SMA_200'],
                name='Média 200',
                line=dict(color='purple', width=1)
            ))
    
    fig.update_layout(
        title=f'Gráfico de Candlestick - {ticker}',
        yaxis_title='Preço',
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
    
    fig.add_hline(y=70, line_dash="dash", line_color="red", annotation_text="Sobrecomprado")
    fig.add_hline(y=30, line_dash="dash", line_color="green", annotation_text="Sobrevendido")
    fig.add_hline(y=50, line_dash="dot", line_color="gray")
    
    fig.update_layout(
        title=f'RSI (Índice de Força Relativa) - {ticker}',
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
            name='Sinal',
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
        title=f'MACD (Convergência/Divergência de Médias Móveis) - {ticker}',
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


def mostrar_estatisticas(dados, indicators, moeda):
    """Mostra estatísticas detalhadas."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Estatísticas de Preço")
        try:
            st.write(f"**Média:** {formatar_moeda(dados['Close'].mean(), moeda)}")
            st.write(f"**Mediana:** {formatar_moeda(dados['Close'].median(), moeda)}")
            st.write(f"**Desvio Padrão:** {formatar_moeda(dados['Close'].std(), moeda)}")
            volatilidade = (dados['Close'].std() / dados['Close'].mean() * 100)
            st.write(f"**Volatilidade:** {formatar_percentual(volatilidade)}")
        except (ValueError, TypeError):
            st.warning("Erro ao calcular estatísticas")
    
    with col2:
        st.subheader("Indicadores Atuais")
        try:
            if 'RSI' in indicators and not indicators['RSI'].isna().all():
                st.write(f"**RSI:** {float(indicators['RSI'].iloc[-1]):.2f}")
            if 'SMA_20' in indicators and not indicators['SMA_20'].isna().all():
                st.write(f"**Média 20:** {formatar_moeda(indicators['SMA_20'].iloc[-1], moeda)}")
            if 'SMA_50' in indicators and not indicators['SMA_50'].isna().all():
                st.write(f"**Média 50:** {formatar_moeda(indicators['SMA_50'].iloc[-1], moeda)}")
            if 'SMA_200' in indicators and not indicators['SMA_200'].isna().all():
                st.write(f"**Média 200:** {formatar_moeda(indicators['SMA_200'].iloc[-1], moeda)}")
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
                setor_pt = traduzir_setor(info['sector'])
                st.write(f"**Setor:** {setor_pt}")
            if 'industry' in info:
                st.write(f"**Indústria:** {info['industry']}")
        
        with col2:
            if 'marketCap' in info and info['marketCap']:
                try:
                    from utils.formatters import formatar_numero_grande
                    market_cap = formatar_numero_grande(info['marketCap'])
                    moeda = obter_simbolo_moeda(ticker)
                    st.write(f"**Valor de Mercado:** {moeda} {market_cap}")
                except (ValueError, TypeError):
                    pass
            
            # Dividend Yield com cálculo manual se necessário
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
    else:
        st.info("Informações da empresa não disponíveis.")
