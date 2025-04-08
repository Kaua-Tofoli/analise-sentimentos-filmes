# Importando bibliotecas necessárias
import csv
import os
from textblob import TextBlob
import pandas as pd
import streamlit as st
from deep_translator import GoogleTranslator

# Caminho do arquivo CSV com os dados
arquivo_csv = "dados.csv"  # O arquivo deve estar no mesmo diretório do app

# Função para ler o CSV e transformar em um DataFrame
def ler_csv_para_df(nome_arquivo):
    if not os.path.exists(nome_arquivo):
        st.error(f"O arquivo '{nome_arquivo}' não existe.")
        return pd.DataFrame()

    # Lê o CSV e mantém apenas as colunas necessárias
    df = pd.read_csv(nome_arquivo, delimiter=';', encoding='latin1')
    df = df[["Nome do Filme (em Português)", "Comentários"]].dropna()
    df.columns = ["filme", "comentario"]
    return df

# Função para traduzir e analisar o sentimento do comentário
def analisar_sentimento(comentario):
    try:
        # Traduz para inglês, pois o TextBlob funciona melhor com esse idioma
        comentario_en = GoogleTranslator(source='auto', target='en').translate(comentario)
        polaridade = TextBlob(comentario_en).sentiment.polarity
    except Exception as e:
        polaridade = 0.0  # Caso dê erro, retorna neutro
        print(f"Erro ao traduzir: {e} | Comentário: {comentario}")

    # Classifica o sentimento com base na polaridade
    if polaridade > 0.1:
        return "Bom", polaridade
    elif polaridade < -0.1:
        return "Ruim", polaridade
    else:
        return "Neutro", polaridade

# --- INTERFACE STREAMLIT ---
st.set_page_config(page_title="Análise de Sentimentos de Filmes", layout="wide")
st.title("🎬 Análise de Sentimentos de Comentários de Filmes")

# Carrega os dados
df = ler_csv_para_df(arquivo_csv)

if not df.empty:
    # Aplica a análise de sentimento para cada comentário
    df["Sentimento"], df["Polaridade"] = zip(*df["comentario"].apply(analisar_sentimento))

    # Exibe os dados originais
    with st.expander("📄 Ver dados brutos"):
        st.dataframe(df)

    # Gráfico de sentimentos por filme
    st.subheader("📊 Distribuição de Sentimentos por Filme")
    grafico = df.groupby(["filme", "Sentimento"]).size().unstack().fillna(0)
    st.bar_chart(grafico)

    # Filtro por filme e exibição dos comentários
    st.subheader("🔎 Comentários por Filme")
    filmes = df["filme"].unique()
    filme_selecionado = st.selectbox("Escolha um filme:", filmes)

    comentarios_filme = df[df["filme"] == filme_selecionado]
    st.write(comentarios_filme[["comentario", "Sentimento", "Polaridade"]])
else:
    st.warning("Nenhum dado foi carregado.")
