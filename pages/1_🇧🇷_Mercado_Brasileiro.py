# pages/1_🇧🇷_Mercado_Brasileiro.py

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
from googletrans import Translator
import time # Importa a biblioteca de tempo

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Mercado Brasileiro", layout="wide")

# --- FUNÇÕES DE APOIO ---
SECTOR_TRANSLATIONS = {
    "Financial Services": "Serviços Financeiros", "Consumer Cyclical": "Consumo Cíclico",
    "Industrials": "Industrial", "Technology": "Tecnologia", "Healthcare": "Saúde",
    "Energy": "Energia", "Utilities": "Utilidades Públicas", "Basic Materials": "Materiais Básicos",
    "Consumer Defensive": "Consumo Defensivo", "Real Estate": "Imobiliário",
    "Communication Services": "Serviços de Comunicação", "Conglomerates": "Conglomerados"
}

@st.cache_data(ttl=86400)
def translate_text_safely(text):
    if not text or not isinstance(text, str): return "Descrição não disponível."
    try:
        translator = Translator(); return translator.translate(text, dest='pt').text
    except Exception: return text

@st.cache_data(ttl=3600)
def get_stock_data(ticker):
    ticker_yf = f"{ticker}.SA"
    stock = yf.Ticker(ticker_yf)
    try:
        info = stock.info
        # ✅ CORREÇÃO: Pausa adicionada para respeitar o limite da API
        time.sleep(0.2) 
        hist = stock.history(period="5y")
        if hist.empty or not info.get('longName'): return None, None
        try: hist.index = hist.index.tz_localize(None)
        except TypeError: pass
        return info, hist
    except Exception:
        return None, None
# ... (o restante do arquivo permanece idêntico) ...
def format_number(number, is_currency=True):
    if number is None: return "N/A"
    prefix = "R$ " if is_currency else ""
    if abs(number) >= 1e9: return f"{prefix}{number / 1e9:.2f} B"
    if abs(number) >= 1e6: return f"{prefix}{number / 1e6:.2f} M"
    return f"{prefix}{number}"
def calculate_rsi(data, period=14):
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))
def calculate_stochastic(data, period=14, k_smooth=3, d_smooth=3):
    low_min = data['Low'].rolling(window=period).min()
    high_max = data['High'].rolling(window=period).max()
    k = 100 * (data['Close'] - low_min) / (high_max - low_min)
    k_smoothed = k.rolling(window=k_smooth).mean()
    d_smoothed = k_smoothed.rolling(window=d_smooth).mean()
    return k_smoothed, d_smoothed
def calculate_willr(data, period=14):
    low_min = data['Low'].rolling(window=period).min()
    high_max = data['High'].rolling(window=period).max()
    return -100 * (high_max - data['Close']) / (high_max - low_min)
def calculate_obv(data):
    obv = (data['Volume'] * (~data['Close'].diff().le(0) * 2 - 1)).cumsum()
    return obv
def interpret_rsi(rsi_value):
    if rsi_value > 70: return "Sobrecomprado", "🔴"
    if rsi_value < 30: return "Sobrevendido", "🟢"
    return "Neutro", "⚪"
def interpret_stochastic(k, d):
    if k > 80 and d > 80: return "Sobrecomprado", "🔴"
    if k < 20 and d < 20: return "Sobrevendido", "🟢"
    if k > d: return "Sinal de Alta (K > D)", "🟢"
    return "Sinal de Baixa (K < D)", "🔴"
def interpret_willr(willr_value):
    if willr_value > -20: return "Sobrecomprado", "🔴"
    if willr_value < -80: return "Sobrevendido", "🟢"
    return "Neutro", "⚪"
def interpret_obv(obv_series):
    if len(obv_series) < 5: return "Dados insuficientes", "⚪"
    if obv_series.iloc[-1] > obv_series.iloc[-5]: return "Acumulação (Volume confirma alta)", "🟢"
    if obv_series.iloc[-1] < obv_series.iloc[-5]: return "Distribuição (Volume confirma baixa)", "🔴"
    return "Neutro", "⚪"
def analyze_convergence(signals):
    score = 0
    for signal, _ in signals.values():
        if "Sobrecomprado" in signal or "Baixa" in signal or "Distribuição" in signal: score -= 1
        if "Sobrevendido" in signal or "Alta" in signal or "Acumulação" in signal: score += 1
    if score >= 2: return "Convergência de Sinais de ALTA.", "Sugere uma possível ZONA DE COMPRA."
    if score <= -2: return "Convergência de Sinais de BAIXA.", "Sugere uma possível ZONA DE VENDA."
    return "Sinais DIVERGENTES ou Neutros.", "Sugere INDEFINIÇÃO ou movimento lateral."
def get_valuation_models(info, current_price):
    results = {}
    try:
        eps = info.get('trailingEps'); bvps = info.get('bookValue')
        if not eps and info.get('trailingPE') and info['trailingPE'] > 0: eps = current_price / info['trailingPE']
        if not bvps and info.get('priceToBook') and info['priceToBook'] > 0: bvps = current_price / info['priceToBook']
        if eps and bvps and eps > 0 and bvps > 0: results['Benjamin Graham'] = (22.5 * eps * bvps) ** 0.5
    except Exception: results['Benjamin Graham'] = None
    return results
def create_valuation_gauge(avg_fair_price, current_price):
    if not avg_fair_price or avg_fair_price <= 0: return None
    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta", value=current_price, title={'text': "Preço Atual vs. Preço Justo", 'font': {'size': 20}},
        delta={'reference': avg_fair_price, 'increasing': {'color': "red"}, 'decreasing': {'color': "green"}},
        gauge={'axis': {'range': [None, avg_fair_price * 1.5]},
               'steps': [{'range': [0, avg_fair_price * 0.8], 'color': "lightgreen"}, {'range': [avg_fair_price * 0.8, avg_fair_price * 1.2], 'color': "lightyellow"}, {'range': [avg_fair_price * 1.2, avg_fair_price * 1.5], 'color': "lightcoral"}],
               'threshold': {'line': {'color': "black", 'width': 4}, 'thickness': 0.75, 'value': avg_fair_price}}))
    fig.update_layout(height=300, margin=dict(t=50, b=50))
    return fig
st.title("🇧🇷 Análise de Ativos Brasileiros (Ações, FIIs, ETFs)"); st.markdown("Use o campo abaixo para pesquisar um ativo da B3 (ex: PETR4, ITSA4, BBAS3)")
ticker_input = st.text_input("Digite o Ticker do Ativo:", "ITSA4").upper()
if ticker_input:
    with st.spinner(f"Buscando e analisando dados para {ticker_input}..."): stock_info, hist_data = get_stock_data(ticker_input)
    if stock_info and not hist_data.empty:
        current_price = stock_info.get('currentPrice') or hist_data['Close'].iloc[-1]
        sector_pt = SECTOR_TRANSLATIONS.get(stock_info.get('industry', stock_info.get('sector', 'N/A')), stock_info.get('industry', stock_info.get('sector', 'N/A')))
        hist_2y = hist_data.loc[hist_data.index > (datetime.now() - timedelta(days=730))].copy()
        summary_translated = translate_text_safely(stock_info.get('longBusinessSummary'))
        change_pct_manual = None; previous_close = stock_info.get('previousClose')
        if previous_close and current_price and previous_close > 0: change_pct_manual = ((current_price / previous_close) - 1)
        delta_text = f"{change_pct_manual * 100:.2f}%" if change_pct_manual is not None else ""
        dy_value = f"{(stock_info.get('trailingAnnualDividendYield', 0) * 100):.2f}%" if stock_info.get('trailingAnnualDividendYield') else "N/A"
        st.header(f"{stock_info.get('longName', 'N/A')} ({stock_info.get('symbol', 'N/A')})", divider='rainbow')
        cols_header = st.columns(4)
        cols_header[0].metric("Preço Atual", f"R$ {current_price:.2f}", delta=delta_text)
        cols_header[1].metric("Setor", sector_pt)
        cols_header[2].metric("Mín. 52 Semanas", f"R$ {stock_info.get('fiftyTwoWeekLow', 0):.2f}")
        cols_header[3].metric("Máx. 52 Semanas", f"R$ {stock_info.get('fiftyTwoWeekHigh', 0):.2f}")
        tab1, tab2, tab3 = st.tabs(["📜 Análise Fundamentalista", "📊 Análise Técnica Avançada", "📄 Dados Completos"])
        with tab1:
            st.subheader("Principais Indicadores")
            fund_data = {"P/L": f"{stock_info.get('trailingPE'):.2f}" if stock_info.get('trailingPE') else "N/A", "P/VP": f"{stock_info.get('priceToBook'):.2f}" if stock_info.get('priceToBook') else "N/A", "Dividend Yield (12M)": dy_value, "ROE (%)": f"{stock_info.get('returnOnEquity', 0) * 100:.2f}%" if stock_info.get('returnOnEquity') else "N/A", "Valor de Mercado": format_number(stock_info.get('marketCap')), "Dívida/Patrimônio": f"{stock_info.get('debtToEquity'):.2f}" if stock_info.get('debtToEquity') else "N/A"}
            cols_fund = st.columns(3)
            for i, (key, value) in enumerate(fund_data.items()): cols_fund[i % 3].metric(key, value)
            st.markdown("---"); st.subheader("Análise de Valuation")
            valuation_results = get_valuation_models(stock_info, current_price); valid_models = {k: v for k, v in valuation_results.items() if v is not None and v > 0}
            if valid_models:
                avg_fair_price = sum(valid_models.values()) / len(valid_models); upside = ((avg_fair_price / current_price) - 1) * 100; col_val1, col_val2 = st.columns([1, 2])
                with col_val1: gauge_fig = create_valuation_gauge(avg_fair_price, current_price); st.plotly_chart(gauge_fig, use_container_width=True)
                with col_val2: st.markdown(f"##### Preço Justo Médio: <font color='blue'>R$ {avg_fair_price:.2f}</font>", unsafe_allow_html=True); st.markdown(f"##### Potencial de Valorização: <font color='{'green' if upside > 0 else 'red'}'>{upside:.2f}%</font>", unsafe_allow_html=True); st.markdown("---"); st.write("**Modelos Utilizados:**");_ = [st.write(f"- {model}: **R$ {price:.2f}**") for model, price in valid_models.items()]
            else: st.warning("Não foi possível calcular um preço justo para este ativo com os dados disponíveis.")
            st.markdown("---"); st.subheader("Histórico de Dividendos (Últimos Anos)")
            dividends_past = hist_data[(hist_data['Dividends'] > 0) & (hist_data.index <= datetime.now())]
            if not dividends_past.empty:
                annual_dividends = dividends_past.groupby(dividends_past.index.year)['Dividends'].sum(); annual_close_price = hist_data.groupby(hist_data.index.year)['Close'].last(); texts = []
                for year in annual_dividends.index:
                    dividend_value = annual_dividends.get(year, 0); close_price = annual_close_price.get(year); text = f"R$ {dividend_value:.2f}"
                    if close_price and close_price > 0 and dividend_value > 0: yield_value = (dividend_value / close_price) * 100; text += f"<br>{yield_value:.2f}%"
                    texts.append(text)
                fig_div = go.Figure(); fig_div.add_trace(go.Bar(x=annual_dividends.index, y=annual_dividends.values, text=texts, textposition='auto', name='Dividendos')); fig_div.update_xaxes(type='category'); fig_div.update_layout(title_text='Dividendos Pagos por Ano (Valor e % Yield)', height=350, uniformtext_minsize=8, uniformtext_mode='hide'); st.plotly_chart(fig_div, use_container_width=True)
            else: st.info("Este ativo não registrou pagamento de dividendos nos últimos 5 anos.")
            st.subheader("Descrição da Empresa")
            if summary_translated and summary_translated != "Descrição não disponível.": st.markdown(f"<p style='font-size: 20px;'>{summary_translated}</p>", unsafe_allow_html=True)
            else: st.info("A descrição da empresa não foi fornecida pela fonte de dados.")
        with tab2:
            hist_2y['RSI'] = calculate_rsi(hist_2y); hist_2y['STOCHk'], hist_2y['STOCHd'] = calculate_stochastic(hist_2y); hist_2y['WILLR'] = calculate_willr(hist_2y); hist_2y['OBV'] = calculate_obv(hist_2y)
            hist_2y['SMA20'] = hist_2y['Close'].rolling(window=20).mean(); hist_2y['SMA50'] = hist_2y['Close'].rolling(window=50).mean()
            fig_price = go.Figure(data=[go.Candlestick(x=hist_2y.index, open=hist_2y['Open'], high=hist_2y['High'], low=hist_2y['Low'], close=hist_2y['Close'], name='Candlestick')]); fig_price.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['SMA20'], mode='lines', name='MMS 20', line=dict(color='orange', width=1.5))); fig_price.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['SMA50'], mode='lines', name='MMS 50', line=dict(color='purple', width=1.5))); fig_price.update_layout(title=f'Gráfico de Preços para {ticker_input} (Últimos 2 Anos)', yaxis_title='Preço (R$)', xaxis_rangeslider_visible=False, height=400, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)); st.plotly_chart(fig_price, use_container_width=True)
            col_ind1, col_ind2 = st.columns(2)
            with col_ind1:
                fig_rsi = go.Figure(); fig_rsi.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['RSI'], name='RSI', line=dict(color='royalblue'))); fig_rsi.add_hline(y=70, line_dash="dash", line_color="red"); fig_rsi.add_hline(y=30, line_dash="dash", line_color="green"); fig_rsi.update_layout(title="Índice de Força Relativa (RSI)", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_rsi, use_container_width=True)
                fig_stoch = go.Figure(); fig_stoch.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['STOCHk'], name='%K', line=dict(color='blue'))); fig_stoch.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['STOCHd'], name='%D', line=dict(color='red'))); fig_stoch.add_hline(y=80, line_dash="dash", line_color="red"); fig_stoch.add_hline(y=20, line_dash="dash", line_color="green"); fig_stoch.update_layout(title="Oscilador Estocástico", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_stoch, use_container_width=True)
            with col_ind2:
                fig_willr = go.Figure(); fig_willr.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['WILLR'], name='Williams %R', line=dict(color='purple'))); fig_willr.add_hline(y=-20, line_dash="dash", line_color="red"); fig_willr.add_hline(y=-80, line_dash="dash", line_color="green"); fig_willr.update_layout(title="Williams %R", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_willr, use_container_width=True)
                fig_obv = go.Figure(); fig_obv.add_trace(go.Scatter(x=hist_2y.index, y=hist_2y['OBV'], name='OBV', line=dict(color='green'))); fig_obv.update_layout(title="On-Balance Volume (OBV)", height=250, margin=dict(t=30, b=30)); st.plotly_chart(fig_obv, use_container_width=True)
            st.markdown("---"); st.subheader("Interpretação e Convergência dos Indicadores")
            signals = {"RSI": interpret_rsi(hist_2y['RSI'].iloc[-1]), "Estocástico": interpret_stochastic(hist_2y['STOCHk'].iloc[-1], hist_2y['STOCHd'].iloc[-1]), "Williams %R": interpret_willr(hist_2y['WILLR'].iloc[-1]), "OBV": interpret_obv(hist_2y['OBV'])}
            cols_interp = st.columns(4)
            for i, (indicator, (text, emoji)) in enumerate(signals.items()): cols_interp[i].metric(label=f"{indicator} {emoji}", value=text)
            conclusion, recommendation = analyze_convergence(signals)
            st.markdown(f"### Conclusão da Análise Técnica: {conclusion}"); st.markdown(f"<p style='font-size: 20px;'>{recommendation}</p>", unsafe_allow_html=True); st.caption("Atenção: Esta é uma análise técnica automatizada e não constitui uma recomendação de investimento.")
        with tab3:
            st.subheader("Dados Fundamentais Completos (JSON)"); st.info("Estes são todos os dados brutos sobre o ativo retornados pela API yfinance."); st.json(stock_info)
            st.subheader("Histórico de Preços e Dividendos (Tabela)"); st.info("Tabela completa com o histórico dos últimos 5 anos."); st.dataframe(hist_data.sort_index(ascending=False), use_container_width=True)
    else:
        st.error(f"Não foi possível encontrar dados para o ticker '{ticker_input}'. Verifique se o ticker está correto ou tente novamente.")
