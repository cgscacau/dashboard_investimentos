"""Módulo de análise de fundos de investimento."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import Config
from utils.data_fetcher import fetch_stock_data


def show():
    """Exibe a página de análise de fundos."""
    st.title("💼 Análise de Fundos de Investimento")
    
    st.info("""
    **Como usar:**
    - Para fundos brasileiros, use o ticker com sufixo .SA (ex: HASH11.SA para ETFs)
    - Para fundos internacionais, use o ticker direto (ex: SPY, QQQ)
    """)
    
    # Sidebar com controles
    with st.sidebar:
        st.header("Configurações")
        
        ticker = st.text_input(
            "Digite o ticker do fundo:",
            value="HASH11.SA",
            help="Ex: HASH11.SA (ETF brasileiro) ou SPY (ETF americano)"
        ).upper()
        
        periodo_label = st.selectbox(
            "Período de análise:",
            options=list(Config.PERIODOS.keys()),
            index=3
        )
        periodo = Config.PERIODOS[periodo_label]
    
    # Buscar dados
    with st.spinner(f"Carregando dados de {ticker}..."):
        dados = fetch_stock_data(ticker, periodo)
    
    if dados is None or dados.empty:
        st.error(f"❌ Não foi possível obter dados para o fundo {ticker}")
        st.info("💡 Verifique se o ticker está correto.")
        return
    
    # Métricas principais
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        preco_atual = dados['Close'].iloc[-1]
        st.metric("Valor Atual", f"R$ {preco_atual:.2f}")
    
    with col2:
        variacao = ((dados['Close'].iloc[-1] - dados['Close'].iloc[0]) / dados['Close'].iloc[0]) * 100
        st.metric("Rentabilidade", f"{variacao:.2f}%", delta=f"{variacao:.2f}%")
    
    with col3:
        volatilidade = dados['Close'].pct_change().std() * (252 ** 0.5) * 100
        st.metric("Volatilidade Anual", f"{volatilidade:.2f}%")
    
    with col4:
        sharpe = calcular_sharpe_ratio(dados)
        st.metric("Sharpe Ratio", f"{sharpe:.2f}")
    
    # Gráfico de evolução
    criar_grafico_evolucao(dados, ticker)
    
    # Gráfico de retornos
    criar_grafico_retornos(dados, ticker)
    
    # Análise de performance
    with st.expander("📊 Análise de Performance"):
        mostrar_analise_performance(dados)
    
    # Estatísticas
    with st.expander("📈 Estatísticas Detalhadas"):
        mostrar_estatisticas_fundo(dados)


def calcular_sharpe_ratio(dados, risk_free_rate=0.1):
    """Calcula o Sharpe Ratio."""
    try:
        retornos = dados['Close'].pct_change().dropna()
        retorno_medio = retornos.mean() * 252
        volatilidade = retornos.std() * (252 ** 0.5)
        
        if volatilidade == 0:
            return 0
        
        sharpe = (retorno_medio - risk_free_rate) / volatilidade
        return sharpe
    except Exception:
        return 0


def criar_grafico_evolucao(dados, ticker):
    """Cria gráfico de evolução do fundo."""
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dados.index,
        y=dados['Close'],
        mode='lines',
        name='Valor da Cota',
        line=dict(color='blue', width=2),
        fill='tozeroy',
        fillcolor='rgba(0, 100, 255, 0.1)'
    ))
    
    # Adicionar SMA 50
    sma_50 = dados['Close'].rolling(window=50).mean()
    fig.add_trace(go.Scatter(
        x=dados.index,
        y=sma_50,
        mode='lines',
        name='SMA 50',
        line=dict(color='red', width=1, dash='dash')
    ))
    
    fig.update_layout(
        title=f'Evolução do Valor - {ticker}',
        yaxis_title='Valor (R$)',
        xaxis_title='Data',
        height=500,
        hovermode='x unified'
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_retornos(dados, ticker):
    """Cria gráfico de distribuição de retornos."""
    retornos = dados['Close'].pct_change().dropna() * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=retornos,
        nbinsx=50,
        name='Retornos Diários',
        marker_color='blue',
        opacity=0.7
    ))
    
    fig.update_layout(
        title=f'Distribuição de Retornos Diários - {ticker}',
        xaxis_title='Retorno (%)',
        yaxis_title='Frequência',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def mostrar_analise_performance(dados):
    """Mostra análise de performance do fundo."""
    retornos = dados['Close'].pct_change().dropna()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Retornos")
        st.write(f"**Retorno Diário Médio:** {retornos.mean()*100:.3f}%")
        st.write(f"**Retorno Mensal Médio:** {retornos.mean()*21*100:.2f}%")
        st.write(f"**Retorno Anual (252 dias):** {retornos.mean()*252*100:.2f}%")
        
        # Melhor e pior dia
        melhor_dia = retornos.max() * 100
        pior_dia = retornos.min() * 100
        st.write(f"**Melhor Dia:** +{melhor_dia:.2f}%")
        st.write(f"**Pior Dia:** {pior_dia:.2f}%")
    
    with col2:
        st.subheader("Risco")
        st.write(f"**Volatilidade Diária:** {retornos.std()*100:.3f}%")
        st.write(f"**Volatilidade Mensal:** {retornos.std()*(21**0.5)*100:.2f}%")
        st.write(f"**Volatilidade Anual:** {retornos.std()*(252**0.5)*100:.2f}%")
        
        # Drawdown
        cumulative = (1 + retornos).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        st.write(f"**Drawdown Máximo:** {max_drawdown:.2f}%")


def mostrar_estatisticas_fundo(dados):
    """Mostra estatísticas detalhadas do fundo."""
    st.subheader("Estatísticas de Preço")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.write(f"**Mínimo:** R$ {dados['Close'].min():.2f}")
        st.write(f"**Máximo:** R$ {dados['Close'].max():.2f}")
        st.write(f"**Amplitude:** R$ {dados['Close'].max() - dados['Close'].min():.2f}")
    
    with col2:
        st.write(f"**Média:** R$ {dados['Close'].mean():.2f}")
        st.write(f"**Mediana:** R$ {dados['Close'].median():.2f}")
        st.write(f"**Desvio Padrão:** R$ {dados['Close'].std():.2f}")
    
    with col3:
        percentil_25 = dados['Close'].quantile(0.25)
        percentil_75 = dados['Close'].quantile(0.75)
        st.write(f"**Percentil 25%:** R$ {percentil_25:.2f}")
        st.write(f"**Percentil 75%:** R$ {percentil_75:.2f}")
        st.write(f"**IQR:** R$ {percentil_75 - percentil_25:.2f}")
