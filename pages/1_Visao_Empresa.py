#Bibliotecas ------------------------------------------------
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

#configuração da página
st.set_page_config( page_title='Visão Empresa', layout='wide' )

#============================================================
# Funções ---------------------------------------------------
#============================================================

#Limpeza do Dataframe ---------------------------------------
def clean_code( df1 ):
    """ Esta função tem a responsabilidade de limpar o dataframe
        tipos de limpeza:
        Remoção dos dados NaN
        Mudança do tipo da coluna de dados
        Remoção do espaços da variaveis de texto
        Formatação da coluna de dadas
        Limpeza da coluna de tempo(remoção do texto da variavel numérica)
        Imput:Dataframe
        Output:Dataframe
    """
    #Cópia do dataframe original
    df1 = df.copy()
    #1 Excluindo as linhas NaN na coluna Age
    linhas_vazias = df1['Delivery_person_Age'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    linhas_vazias = df1['Festival'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]
    #1.2 Conversao de texto/categoria/string para numeros inteiros
    df1['Delivery_person_Age'] = df1['Delivery_person_Age'].astype( int )

    #2 Convertendo a coluna Ratings de texto para decimal
    df1['Delivery_person_Ratings'] = df1['Delivery_person_Ratings'].astype( float )

    #3 Convetendo a coluna Order_Data de texto para data
    df1['Order_Date'] = pd.to_datetime( df1['Order_Date'], format='%d-%m-%Y' )

    #4 Remove as linhas da coluna multiple_deliveries que tenham o 
    # conteudo igual a 'NaN '
    linhas_vazias = df1['multiple_deliveries'] != 'NaN '
    df1 = df1.loc[linhas_vazias, :]

    #4.1Convertendo os valores da coluna Multiple_deliveries para numero inteiro 
    df1['multiple_deliveries'] = df1['multiple_deliveries'].astype( int )

    #6 Removendo os espaços dentro de strings/texto/objeto nas colunas
    df1.loc[:, 'ID'] = df1.loc[:, 'ID'].str.strip()
    df1.loc[:, 'Road_traffic_density'] = df1.loc[:, 'Road_traffic_density'].str.strip()
    df1.loc[:, 'Type_of_order'] = df1.loc[:, 'Type_of_order'].str.strip()
    df1.loc[:, 'Type_of_vehicle'] = df1.loc[:, 'Type_of_vehicle'].str.strip()
    df1.loc[:, 'City'] = df1.loc[:, 'City'].str.strip()
    df1.loc[:, 'Festival'] = df1.loc[:, 'Festival'].str.strip()

    #7 Remove as linhas da coluna Road_traffic_density que tenham o 
    # conteudo igual a 'NaN '
    df1 = df1.loc[df1['Road_traffic_density'] != 'NaN', :]
    df1 = df1.loc[df1['City'] != 'NaN', :]

    #8 Limpeza da coluna time, retira do (min)
    df1['Time_taken(min)'] = df1['Time_taken(min)'].apply( lambda x: x.split('(min) ')[1] )
    df1['Time_taken(min)'] = df1['Time_taken(min)'].astype(int)
    
    return df1

#PLota Gráfico de pedido por dia
def pedidos_dia( df1 ):
    """ Produz um gráfico de barras, demonstrando o volume de pedidos por dia.
        imput:Dataframe
        output:Gráfico de barras
    """
    # Seleção de colunas
    cols = ['ID', 'Order_Date']
    # Seleção de linhas,agrupamento por Data e contagem por dia
    df_aux = df1.loc[:, cols].groupby(['Order_Date']).count().reset_index()
    #desenhar gráfico de colunas
    fig = px.bar(df_aux, x='Order_Date', y='ID')

    return fig

#PLota gráfico de pedidos por tráfego
def pedido_trafego( df1):
    """ Produz um gráfico de pizza, demonstrando o volume de pedidos por tipo de tráfego.
        imput:Dataframe
        output:Gráfico de pizza
    """
    #Seleção de colunas
    cols = ['ID', 'Road_traffic_density']
    #Seleção de linhas,agrupamento e contagem por tipo de tráfego
    df_aux = df1.loc[:, cols].groupby(['Road_traffic_density']).count().reset_index()
    #Criando coluna de percentual de entrega por tipo de trafégo 
    df_aux['entregas_perc'] = df_aux['ID'] / df_aux['ID'].sum()
    #Desenhar gráfico de pizza
    fig = px.pie(df_aux, values= 'entregas_perc', names= 'Road_traffic_density')
    
    return fig

#PLata gráfico de pedido por cidade e tipo de tráfego
def pedido_cid_traf ( df1):
    """ Produz um gráfico de bolha, demonstrando o volume de pedidos por cidade e tipo de tráfego.
        imput:Dataframe
        output:Gráfico de bolha
    """
    #Seleção de colunas
    cols = ['ID', 'City', 'Road_traffic_density']
    #Seleção de linhas, agrupamento e contagem por cidade e tipo de tráfego
    df_aux = df1.loc[:,cols].groupby(['City', 'Road_traffic_density']).count().reset_index()
    #Desenhar gráfico de bolha
    fig = px.scatter(df_aux, x='City', y='Road_traffic_density', size='ID', color='City')
    
    return fig

#Linhas, Pedidos por semana
def pedido_semana( df1):
    """ Produz um gráfico de linhas, demonstrando o volume de pedidos por semana.
        imput:Dataframe
        output:Gráfico de linhas
    """
    #Criar coluna semana
    df1['Week_of_year'] = df1['Order_Date'].dt.strftime( '%U' )
    #Seleção de colunas
    cols = ['ID', 'Week_of_year']
    #Seleção de linhas, agrupamento e contagem por semana
    df_aux = df1.loc[:, cols].groupby(['Week_of_year']).count().reset_index()
    #Desenhar gráfico de linhas
    fig = px.line(df_aux , x= 'Week_of_year', y= 'ID')
        
    return fig

#Linhas, pedido por entregado por semana
def pedido_entreg_semana( df1):
    """ Produz um gráfico de linhas, demonstrando o volume de pedidos por entregador e por semana.
        imput:Dataframe
        output:Gráfico de linhas
    """
    #Pedidos totais na semana
    df_aux01 = df1.loc[:, ['ID', 'Week_of_year']].groupby(['Week_of_year']).count().reset_index()
    #Quantidade de entregadore unicos por semana
    df_aux02 = df1.loc[:, ['Delivery_person_ID', 'Week_of_year']].groupby(['Week_of_year']).nunique().reset_index()
    #Juntando colunas
    df_aux03 = pd.merge( df_aux01, df_aux02, how='inner' )
    #Calculando pedidos por entregador em cada semana 
    df_aux03['order_by_delivery'] = df_aux01['ID'] / df_aux03['Delivery_person_ID']
    #Desenhar gráfico de linhas
    fig = px.line(df_aux03, x='Week_of_year', y='order_by_delivery' )
    
    return fig

#Mapa de localizações centrais de cada cidade por tráfego
def mapa_cidade( df1):
    """ Retorna um mapa com as localizações centrais de cada cidade pelo tipo de tráfego.
        imput:Dataframe
        output:Gráfico de linhas
    """
    #Seleciona colunas
    cols = ['City', 'Road_traffic_density', 'Delivery_location_latitude', 'Delivery_location_longitude']
    #Seleciona pontos centrais da cidade por utilizando mediana, por tipo de tráfego e cidade
    df_aux = df1.loc[:,cols].groupby(['City', 'Road_traffic_density']).median().reset_index()
    #Criação de uma mapa
    map = folium.Map()
    #Marcação dos pontos no mapa criado
    #For para ler de ponto em ponto do mapa, Iterrows transforme para folium reconhecer, Folium.Marker marca as latitudes e longitudes no mapa e add.to() adiciona tudo a um mapa criado
    for index, location_info in df_aux.iterrows():
        folium.Marker( [location_info['Delivery_location_latitude'],
                               location_info['Delivery_location_longitude']],
                               popup=location_info[['City', 'Road_traffic_density']] ).add_to( map )

    #Comando para exibição de mapa no Streamlit
    folium_static( map, width=1024, height=600)

#-------------------------------------------------------------------------------------------------
#-------------------------------- Inicío da estrutura lógica do código ---------------------------
#Importando Dataset
df = pd.read_csv('train.csv')

#Limpando os dados
df1 = clean_code( df )

#Visão Empresa ===========================================

#=========================================================
#Barra lateral Streamlit
#=========================================================
st.title( 'Marketplace - Visão Empresa' )

#Adicionando Imagem a barra lateral
image_path = 'logo.jpg'
image =Image.open( image_path)
st.sidebar.image( image, width=280)

#Criando Barra lateral com filtros
st.sidebar.markdown( '### Curry Company' )
st.sidebar.markdown( '## Fastest Delivery in Town' )
st.sidebar.markdown( """___""")

#Filtro data
st.sidebar.markdown( '## Selecione uma data limite:')
data_slider = st.sidebar.slider(
    'Até que valor?',
    value=pd.datetime(2022, 4, 13),
    min_value= pd.datetime(2022, 2, 11),
    max_value= pd.datetime(2022, 4 ,6),
    format= 'DD-MM-YYYY' )

st.sidebar.markdown( """___""")

#Filtro trânsito
st.sidebar.markdown( '## Selecione uma condição de trâfego:')
traffic_options = st.sidebar.multiselect(
    'Quais as condiçoes de trânsito:',
    ['Low', 'Medium', 'High', 'Jam'],
    default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown( """___""")
st.sidebar.markdown( '### Powered by Comunidade DS')

#Integração dos Filtros
#Filtro de data
linhas_selecionadas = df1['Order_Date'] < data_slider
df1 = df1.loc[linhas_selecionadas, :]

#Filtro de Trãnsito
#Usado o comando isin, passando que as opções do filtro estão em algum lugar
linhas_selecionadas = df1['Road_traffic_density'].isin( traffic_options )
df1 = df1.loc[linhas_selecionadas, :]

#=========================================================
#Layout Streamlit
#=========================================================
#Criação de páginas e separação em visões
tab1, tab2, tab3= st.tabs( ['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'] )
# Tab Visão gerencial
with tab1:
    
    #Criação de container alocação do conteúdo
    #Pedidos por dia
    with st.container():
        st.markdown( '### Quantidade pedidos por dia' )
        #Chamando o funções que plota o gráfico
        fig = pedidos_dia( df1 )
        #Comando para exibição de gráficos da biblioteca Streamlit
        st.plotly_chart( fig, user_container_width=True)
        
    #Criação de container e divisão do container em duas colunas para alocação de 2 gráficos
    with st.container():
        col1,col2 = st.columns( 2 )
        
        with col1:
            #Pizza Pedido por tráfego
            st.markdown('### Volume de Pedidos por tipo de tráfego')
            fig = pedido_trafego( df1 )
            st.plotly_chart( fig, use_container_width=True)
            
        with col2:
            #Bolha Volume de pedido por cidade e tipo de tráfego
            st.markdown('### Volume de pedidos por cidade e tipo de tráfego')
            fig = pedido_cid_traf( df1 )
            st.plotly_chart( fig, use_container_width=True)
                    
# Tab Visão Tática      
with tab2:
    with st.container():
        #Linhas, pedidos por semana
        st.markdown( '### Volume de pedidos por semana')
        fig = pedido_semana( df1 )
        st.plotly_chart( fig, user_container_width=True)
        
    with st.container():
        #Linhas, pedido por entregado por semana
        st.markdown( '### Volume de pedidos por entregador por semana')
        fig = pedido_entreg_semana( df1 )
        st.plotly_chart( fig, user_container_width=True)
         
# Tab Visão Geográfica
with tab3:
    with st.container():
        #Mapa de localizações centrais de cada cidade por tráfego
        st.markdown( '### Mapa de localização central de cada cidade por tipo de trâfego')
        mapa_cidade( df1 )