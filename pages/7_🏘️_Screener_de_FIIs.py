# pages/7_🏘️_Screener_de_FIIs.py

import streamlit as st
import pandas as pd
import requests

# --- CONFIGURAÇÃO DA PÁGINA ---
st.set_page_config(page_title="Screener de FIIs", layout="wide")

# --- FUNÇÕES DE SCRAPING E CÁLCULO ---
@st.cache_data(ttl=3600)
def scrape_fundamentus_fiis():
    url = "https://www.fundamentus.com.br/fii_resultado.php"
    headers = {'User-Agent': 'Mozilla/5.0'}
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        df = pd.read_html(response.text, decimal=',', thousands='.')[0]
        return df
    except Exception as e:
        st.error(f"Erro ao acessar o Fundamentus: {e}")
        return pd.DataFrame()

def clean_and_prepare_data_fiis(df):
    df_clean = df.copy()
    for col in df_clean.columns:
        if col == 'Papel': continue
        if df_clean[col].dtype == 'object':
            had_percent = df_clean[col].str.contains('%', na=False).any()
            df_clean[col] = df_clean[col].str.replace('%', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
            df_clean[col] = pd.to_numeric(df_clean[col], errors='coerce')
            if had_percent:
                df_clean[col] = df_clean[col] / 100
    return df_clean

def rank_fiis(df, selected_indicators):
    # ✅ CORREÇÃO: Mapeamento de direção atualizado com os novos indicadores
    ranking_direction = {
        'Dividend Yield': False, 'P/VP': True, 'Liquidez': False, 
        'FFO Yield': False, 'Cap Rate': False, 'Vacância Média': True
    }
    rank_cols = []
    for indicator in selected_indicators:
        rank_col_name = f"Rank ({indicator})"
        df[rank_col_name] = df[indicator].rank(ascending=ranking_direction[indicator], na_option='bottom')
        rank_cols.append(rank_col_name)
    if rank_cols:
        df['🏆 Rank Final'] = df[rank_cols].sum(axis=1)
        df = df.sort_values(by='🏆 Rank Final')
    return df

# --- INTERFACE PRINCIPAL ---
st.title("🏘️ Screener de Fundos Imobiliários (FIIs)")
st.markdown("Crie seu próprio ranking de FIIs! Defina filtros, escolha seus indicadores favoritos e encontre os melhores fundos para sua estratégia de renda passiva.")
st.info("Quanto menor o **'🏆 Rank Final'**, melhor o FII segundo os seus critérios de ranking.")

# ✅ CORREÇÃO: Opções de indicadores atualizadas com os dados corretos do site
INDICATOR_MAP_FII = {
    'Dividend Yield 🔼': 'Dividend Yield', 'P/VP 🔽': 'P/VP', 'Liquidez 🔼': 'Liquidez',
    'FFO Yield 🔼': 'FFO Yield', 'Cap Rate 🔼': 'Cap Rate', 'Vacância Média 🔽': 'Vacância Média'
}
INDICATOR_LABELS_FII = list(INDICATOR_MAP_FII.keys())

st.subheader("1. Filtre o Universo de FIIs (Opcional)")
st.caption("Defina os intervalos desejados. Deixe os valores em 0 para não aplicar o filtro.")

with st.expander("Clique para abrir/fechar os filtros"):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        min_dy = c1.number_input("DY (%) Mínimo", value=5.0, step=0.5, format="%.2f") / 100
        min_ffo_yield = c1.number_input("FFO Yield (%) Mínimo", value=0.0, step=0.5, format="%.2f") / 100
    with c2:
        max_dy = c2.number_input("DY (%) Máximo", value=0.0, step=0.5, format="%.2f") / 100
        min_liquidez = c2.number_input("Liquidez Mínima (R$)", value=100000, step=10000, format="%d")
    with c3:
        min_pvp = c3.number_input("P/VP Mínimo", value=0.0, step=0.1, format="%.2f")
        max_vacancia = c3.number_input("Vacância Média Máxima (%)", value=20.0, step=1.0, format="%.2f") / 100
    with c4:
        max_pvp = c4.number_input("P/VP Máximo", value=1.1, step=0.1, format="%.2f")

st.subheader("2. Selecione os Indicadores para o Ranking")
selected_labels = st.multiselect(
    "Escolha os indicadores que irão compor o 'Rank Final':",
    options=INDICATOR_LABELS_FII,
    default=['Dividend Yield 🔼', 'P/VP 🔽', 'Liquidez 🔼']
)

if st.button("Gerar Ranking de FIIs"):
    selected_indicators = [INDICATOR_MAP_FII[label] for label in selected_labels]
    if not selected_indicators:
        st.warning("Por favor, selecione pelo menos um indicador para gerar o ranking.")
    else:
        with st.spinner("Buscando e processando todos os dados de FIIs do Fundamentus..."):
            raw_df = scrape_fundamentus_fiis()
        
        if not raw_df.empty:
            cleaned_df = clean_and_prepare_data_fiis(raw_df)
            
            filtered_df = cleaned_df.copy()
            if min_liquidez > 0: filtered_df = filtered_df[filtered_df['Liquidez'] >= min_liquidez]
            if min_dy > 0: filtered_df = filtered_df[filtered_df['Dividend Yield'] >= min_dy]
            if max_dy > 0: filtered_df = filtered_df[filtered_df['Dividend Yield'] <= max_dy]
            if min_pvp > 0: filtered_df = filtered_df[filtered_df['P/VP'] >= min_pvp]
            if max_pvp > 0: filtered_df = filtered_df[filtered_df['P/VP'] <= max_pvp]
            if max_vacancia > 0: filtered_df = filtered_df[filtered_df['Vacância Média'] <= max_vacancia]
            if min_ffo_yield > 0: filtered_df = filtered_df[filtered_df['FFO Yield'] >= min_ffo_yield]
            
            if filtered_df.empty:
                st.warning("Nenhum FII encontrado com os filtros definidos. Tente critérios menos restritivos.")
            else:
                ranked_df = rank_fiis(filtered_df, selected_indicators)
                display_cols = ['Papel', 'Segmento', 'Cotação', '🏆 Rank Final'] + selected_indicators
                st.success(f"Ranking gerado com sucesso para {len(ranked_df)} FIIs!")
                
                st.dataframe(
                    ranked_df[display_cols].style.format({
                        'Cotação': 'R$ {:.2f}', 'Dividend Yield': '{:.2%}', 'P/VP': '{:.2f}',
                        'Liquidez': 'R$ {:,.2f}', 'FFO Yield': '{:.2%}', 'Cap Rate': '{:.2%}', 
                        'Vacância Média': '{:.2%}'
                    }),
                    height=800, use_container_width=True, hide_index=True
                )
        else:
            st.error("Não foi possível carregar os dados de FIIs do Fundamentus.")