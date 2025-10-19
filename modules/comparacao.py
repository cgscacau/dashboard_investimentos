"""Módulo de comparação entre múltiplas ações/fundos."""

import streamlit as st
import plotly.graph_objects as go
import pandas as pd
from config import Config
from utils.data_fetcher import fetch_multiple_stocks, normalize_prices


def show():
    """Exibe a página de comparação."""
    st.title("⚖️ Comparação de Ativos")
    
    st.info("""
    **Como usar:**
    - Digite os tickers separados por vírgula
    - Use .SA para ações brasileiras (ex: PETR4.SA, VALE3.SA)
    - Máximo de 5 ativos por comparação
    """)
    
    # Sidebar com controles
    with st.sidebar:
        st.header("Configurações")
        
        tickers_input = st.text_area(
            "Digite os tickers (separados por vírgula):",
            value="PETR4.SA, VALE3.SA, ITUB4.SA",
            help="Ex: PETR4.SA, VALE3.SA, ITUB4.SA"
        )
        
        periodo_label = st.selectbox(
            "Período de análise:",
            options=list(Config.PERIODOS.keys()),
            index=3
        )
        periodo = Config.PERIODOS[periodo_label]
        
        normalizar = st.checkbox(
            "Normalizar preços (base 100)",
            value=True,
            help="Facilita a comparação de ativos com preços muito diferentes"
        )
    
    # Processar tickers
    tickers = [t.strip().upper() for t in tickers_input.split(',') if t.strip()]
    
    if len(tickers) == 0:
        st.warning("⚠️ Por favor, insira pelo menos um ticker.")
        return
    
    if len(tickers) > 5:
        st.warning("⚠️ Máximo de 5 ativos por comparação. Usando apenas os 5 primeiros.")
        tickers = tickers[:5]
    
    # Buscar dados
    with st.spinner("Carregando dados dos ativos..."):
        dados_dict = fetch_multiple_stocks(tickers, periodo)
    
    if not dados_dict:
        st.error("❌ Não foi possível obter dados para nenhum dos tickers informados.")
        return
    
    # Verificar quais tickers falharam
    tickers_sucesso = list(dados_dict.keys())
    tickers_falha = [t for t in tickers if t not in tickers_sucesso]
    
    if tickers_falha:
        st.warning(f"⚠️ Não foi possível obter dados para: {', '.join(tickers_falha)}")
    
    if not tickers_sucesso:
        st.error("❌ Nenhum dado válido foi encontrado.")
        return
    
    st.success(f"✅ Dados carregados para: {', '.join(tickers_sucesso)}")
    
    # Métricas comparativas
    mostrar_metricas_comparativas(dados_dict)
    
    # Gráfico de evolução
    if normalizar:
        criar_grafico_normalizado(dados_dict)
    else:
        criar_grafico_absoluto(dados_dict)
    
    # Gráfico de retornos
    criar_grafico_retornos_comparativo(dados_dict)
    
    # Correlação
    criar_matriz_correlacao(dados_dict)
    
    # Tabela comparativa
    with st.expander("📊 Tabela Comparativa Detalhada"):
        mostrar_tabela_comparativa(dados_dict, periodo)


def mostrar_metricas_comparativas(dados_dict):
    """Mostra métricas comparativas dos ativos."""
    st.subheader("📊 Métricas Comparativas")
    
    metricas = []
    
    for ticker, dados in dados_dict.items():
        if dados.empty:
            continue
        
        preco_inicial = dados['Close'].iloc[0]
        preco_final = dados['Close'].iloc[-1]
        variacao = ((preco_final - preco_inicial) / preco_inicial) * 100
        volatilidade = dados['Close'].pct_change().std() * (252 ** 0.5) * 100
        
        metricas.append({
            'Ticker': ticker,
            'Preço Inicial': f"R$ {preco_inicial:.2f}",
            'Preço Atual': f"R$ {preco_final:.2f}",
            'Variação': f"{variacao:.2f}%",
            'Volatilidade': f"{volatilidade:.2f}%"
        })
    
    df_metricas = pd.DataFrame(metricas)
    st.dataframe(df_metricas, use_container_width=True, hide_index=True)


def criar_grafico_normalizado(dados_dict):
    """Cria gráfico com preços normalizados."""
    st.subheader("📈 Evolução Normalizada (Base 100)")
    
    dados_normalizados = normalize_prices(dados_dict)
    
    if dados_normalizados.empty:
        st.warning("Não foi possível normalizar os dados.")
        return
    
    fig = go.Figure()
    
    cores = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, ticker in enumerate(dados_normalizados.columns):
        fig.add_trace(go.Scatter(
            x=dados_normalizados.index,
            y=dados_normalizados[ticker],
            mode='lines',
            name=ticker,
            line=dict(color=cores[i % len(cores)], width=2)
        ))
    
    fig.update_layout(
        title='Comparação de Performance (Base 100)',
        yaxis_title='Valor Normalizado',
        xaxis_title='Data',
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_absoluto(dados_dict):
    """Cria gráfico com preços absolutos."""
    st.subheader("📈 Evolução de Preços Absolutos")
    
    fig = go.Figure()
    
    cores = ['blue', 'red', 'green', 'orange', 'purple']
    
    for i, (ticker, dados) in enumerate(dados_dict.items()):
        if dados.empty:
            continue
        
        fig.add_trace(go.Scatter(
            x=dados.index,
            y=dados['Close'],
            mode='lines',
            name=ticker,
            line=dict(color=cores[i % len(cores)], width=2)
        ))
    
    fig.update_layout(
        title='Comparação de Preços Absolutos',
        yaxis_title='Preço (R$)',
        xaxis_title='Data',
        height=600,
        hovermode='x unified',
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        )
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_grafico_retornos_comparativo(dados_dict):
    """Cria gráfico comparativo de retornos."""
    st.subheader("📊 Comparação de Retornos")
    
    retornos_data = {}
    
    for ticker, dados in dados_dict.items():
        if not dados.empty:
            preco_inicial = dados['Close'].iloc[0]
            preco_final = dados['Close'].iloc[-1]
            retorno = ((preco_final - preco_inicial) / preco_inicial) * 100
            retornos_data[ticker] = retorno
    
    fig = go.Figure()
    
    tickers = list(retornos_data.keys())
    retornos = list(retornos_data.values())
    cores = ['green' if r >= 0 else 'red' for r in retornos]
    
    fig.add_trace(go.Bar(
        x=tickers,
        y=retornos,
        marker_color=cores,
        text=[f"{r:.2f}%" for r in retornos],
        textposition='outside'
    ))
    
    fig.update_layout(
        title='Retornos no Período',
        yaxis_title='Retorno (%)',
        xaxis_title='Ticker',
        height=400,
        showlegend=False
    )
    
    st.plotly_chart(fig, use_container_width=True)


def criar_matriz_correlacao(dados_dict):
    """Cria matriz de correlação entre os ativos."""
    st.subheader("🔗 Matriz de Correlação")
    
    # Criar DataFrame com todos os preços de fechamento
    df_precos = pd.DataFrame()
    
    for ticker, dados in dados_dict.items():
        if not dados.empty:
            df_precos[ticker] = dados['Close']
    
    if df_precos.empty or len(df_precos.columns) < 2:
        st.info("É necessário pelo menos 2 ativos para calcular a correlação.")
        return
    
    # Calcular matriz de correlação
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
        textfont={"size": 12},
        colorbar=dict(title="Correlação")
    ))
    
    fig.update_layout(
        title='Matriz de Correlação entre Ativos',
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    st.info("""
    **Interpretação:**
    - **1.0:** Correlação perfeita positiva
    - **0.0:** Sem correlação
    - **-1.0:** Correlação perfeita negativa
    
    Ativos com baixa correlação podem ajudar na diversificação da carteira.
    """)


def mostrar_tabela_comparativa(dados_dict, periodo):
    """Mostra tabela comparativa detalhada."""
    comparacao = []
    
    for ticker, dados in dados_dict.items():
        if dados.empty:
            continue
        
        retornos = dados['Close'].pct_change().dropna()
        
        preco_inicial = dados['Close'].iloc[0]
        preco_final = dados['Close'].iloc[-1]
        variacao = ((preco_final - preco_inicial) / preco_inicial) * 100
        
        volatilidade = retornos.std() * (252 ** 0.5) * 100
        retorno_medio = retornos.mean() * 252 * 100
        
        # Sharpe Ratio
        sharpe = (retorno_medio - 10) / volatilidade if volatilidade != 0 else 0
        
        # Drawdown máximo
        cumulative = (1 + retornos).cumprod()
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        comparacao.append({
            'Ticker': ticker,
            'Preço Inicial (R$)': f"{preco_inicial:.2f}",
            'Preço Final (R$)': f"{preco_final:.2f}",
            'Variação (%)': f"{variacao:.2f}",
            'Retorno Anualizado (%)': f"{retorno_medio:.2f}",
            'Volatilidade Anual (%)': f"{volatilidade:.2f}",
            'Sharpe Ratio': f"{sharpe:.2f}",
            'Drawdown Máximo (%)': f"{max_drawdown:.2f}"
        })
    
    df_comparacao = pd.DataFrame(comparacao)
    st.dataframe(df_comparacao, use_container_width=True, hide_index=True)
