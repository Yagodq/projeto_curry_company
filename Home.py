#Bibliotecas
import streamlit as st
from PIL import Image

#Comando para juntar as páginas
st.set_page_config( page_title="Home", layout='wide')

#Adicionando imagem
image_path = 'logo.jpg'
image = Image.open( image_path )
st.sidebar.image( image, width=280)

#Criando Barra lateral com filtros
st.sidebar.markdown( '### Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""")

#Cria título da página home
st.write( '# Curry Company Growth Dashboard')

#Cria descrição no home de como usar o Dashboard
st.markdown(
""" Growth Dashboard foi construído para acompanhar as métricas de crescimento da Empresa, Entregadores e Restaurantes.
    ### Como Utilizar este Dashboard?
    - Visão empresa:
        - Visão Gerencial: Métricas gerais de comportamento.
        - Visão Tática: Indicadores semanais de crescimento.
        - Visão Geográfica: Insights de geolocalização.
    - Visão Entregadores:
        - Acompanhamento dos indicadores semanais de crescimento.
    - Visão Restaurantes:
        - Indicadores semanais de crescimento dos restaurantes.
    
""")