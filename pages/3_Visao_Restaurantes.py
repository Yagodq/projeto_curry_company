#Bibliotecas ------------------------------------------------
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from haversine import haversine
import streamlit as st
import pandas as pd
from PIL import Image
import numpy as np

#configuração da página
st.set_page_config( page_title='Visão Restaurantes', layout='wide' )

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

#Retorna a distancia média de haversine
def distancia( df1 ):
    """ Calcula a distancia média entre os restaurante e os pontos de entrega.
        imput:Dataframe
        output:Métrica
    """
    #Selecionando as colunas
    cols = ['Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    #Calculo da distancia por meio da biblioteca haversine, utilizando apply lambda para aplicar a solução linha por linha
    df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine(
                                                 ( x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                 ( x['Delivery_location_latitude'], x['Delivery_location_longitude']) ) , axis=1)
     #Média final
    avg_distance = np.round(df1['distance'].mean(), 2)
    
    return avg_distance

#Função que calcula tempo médio e desvio padrão do tempo de entrega
def avg_std_tempo_entreg ( df1, festival, op):
    """ Está função calcula o tempo médio e desvio padrão do tempo de entrega.
    Parêmetros:
    imput:DF1: Dataframe com os dados
            festival: Se teve ou não festival 
                "Yes": Teve festival
                "No": Não teve festival
            op : Tipo de operação que vai ser calculada
                "avg_time": Calcula a médio do tempo
                "std_time": Calcula o desvio padrão do tempo
            
            output:Dataframe
    """
    #Calculos e agrupamento por cidade e densidade de trafego
    df_aux = df1.loc[:,['Time_taken(min)', 'Festival']].groupby(['Festival']).agg( { 'Time_taken(min)': ['mean', 'std'] })
    #Renomeando colunas e organizando index
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    #Filtro para recuperar dado especifico
    df_aux = np.round(df_aux.loc[df_aux['Festival'] == festival, op ], 2)
                
    return df_aux

#Plota gráfico de pizza 
def pizza_avg_city( df1 ): 
    """ Produz um gráfico de pizza com média de entrega por cidade.
        imput:Dataframe
        output:Gráfico pizza
    """
    #Selecionando as colunas
    cols = ['Restaurant_latitude','Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
    #Calculo da distancia por meio da biblioteca haversine, utilizando apply lambda para aplicar a solução linha por linha
    df1['distance'] = df1.loc[:, cols].apply( lambda x: haversine(
                                                         ( x['Restaurant_latitude'], x['Restaurant_longitude']), 
                                                         ( x['Delivery_location_latitude'], x['Delivery_location_longitude']) ) , axis=1)
    #Agrupamento da distancia média por cidade
    avg_distance = df1.loc[:, ['City', 'distance']].groupby(['City']).mean().reset_index()
    #Criação do gráfico de pizza
    fig = go.Figure( data = [ go.Pie( labels= avg_distance['City'], values= avg_distance['distance'], pull=[0, 0, 0.1])])
            
    return fig

#Plota gráfico de barras de tempo médio e desvio padrão por cidade das entregas
def avg_std_city( df1 ):
    """ Retorna um gráfico de barras com a média e desvio padrão das entregas por cidade.
        imput:Dataframe
        output:Gráfico barra
    """
    #Calculos e agrupamento por cidade
    df_aux = df1.loc[:, ['Time_taken(min)', 'City'] ].groupby(['City']).agg( { 'Time_taken(min)': ['mean', 'std'] } )
    #Renomeando colunas e organizando index
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    #Criando gráfico de barra na biblioteca GO
    fig = go.Figure()
    fig.add_trace( go.Bar(name='Controle',
                            x=df_aux['City'],
                            y=df_aux['avg_time'],
                                  error_y=dict( type= 'data', array=df_aux[ 'std_time'] ) ) )
    fig.update_layout( barmode= 'group')
            
    return fig

#Plota gráfico sunburst de tempo médio e desvio padrão das entregas por cidade e tráfego
def sunburst_city_traf( df1 ):
    """ Retorna um gráfico de sunburst com a média e desvio padrão das entregas por cidade e tipo de tráfego.
        imput:Dataframe
        output:Gráfico barra
    """
    #Selecionando as colunas
    cols = ['Time_taken(min)', 'City', 'Road_traffic_density' ]
    #Calculos e agrupamento por cidade e densidade de trafego
    df_aux = df1.loc[:, cols].groupby(['City', 'Road_traffic_density']).agg( { 'Time_taken(min)': ['mean', 'std'] })
    #Renomeando colunas e organizando index
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    #Criando gráfico SunBurst
    fig = px.sunburst( df_aux, path=['City', 'Road_traffic_density'], values='avg_time', color='std_time', color_continuous_scale='RdBu', color_continuous_midpoint=np.average(df_aux['std_time'] ) )
            
    return fig

#-------------------------------------------------------------------------------------------------
#-------------------------------- Inicío da estrutura lógica do código ---------------------------
#Importando Dataset
df = pd.read_csv('train.csv')

#Limpando os dados
df1 = clean_code( df )

#Visão Restaurantes ===========================================
#=========================================================
#Barra lateral Streamlit
#=========================================================
st.title( 'Marketplace - Visão Restaurantes' )

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

#Filtro Clima
st.sidebar.markdown( '## Selecione uma condição de clima:')
Weatherconditions_options = st.sidebar.multiselect(
    'Quais as condiçoes de clima:',
    ['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'],
    default=['conditions Cloudy', 'conditions Fog', 'conditions Sandstorms', 'conditions Stormy', 'conditions Sunny', 'conditions Windy'])

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

#Filtro de clima
#Usado o comando isin, passando que as opções do filtro estão em algum lugar
linhas_selecionadas = df1['Weatherconditions'].isin( Weatherconditions_options )
df1 = df1.loc[linhas_selecionadas, :]

#=========================================================
#Layout Streamlit
#=========================================================
#Criação de páginas para separação do contéudo
tab1,tab2 = st.tabs( ['Visão gerencial','.'])
with tab1:
    #Criação dos 4 container para divisão do conteúdo
    with st.container():
        st.markdown('### Metricas gerais')
        #Criação de 6 colunas para divisão dos métricas
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        #Coluna entregadores únicos
        with col1:
            unique_delivery = len(df1.loc[:,'Delivery_person_ID' ].unique())
            col1.metric('Entregadores únicos', unique_delivery)
        #Colunas Distancia média entregas
        with col2:
            avg_distance = distancia( df1 )
            col2.metric('A distancia média da entregas', avg_distance)      
        #Média tempo com festival
        with col3:
            df_aux = avg_std_tempo_entreg(df1, "Yes", "avg_time")
            col3.metric('Tempo médio com festival', df_aux)    
        with col4: 
            df_aux = avg_std_tempo_entreg(df1, "Yes", "std_time" )
            col4.metric('Desvio padrão com festival', df_aux)
        with col5:
            df_aux = avg_std_tempo_entreg(df1, "No", "avg_time")
            col5.metric('Tempo médio sem festival', df_aux)
        with col6: 
            df_aux = avg_std_tempo_entreg(df1, "No", "std_time")
            col6.metric('Desvio padrão sem festival', df_aux)
            
    #Container com distancia média por cidade (Gráfico pizza) e tabela de tempo médio por cidade e pedido     
    with st.container():
        #Criando colunas
        col1,col2 = st.columns(2)
        # Coluna com distancia média por cidade (Gráfico pizza)
        with col1:
            st.markdown( """___""")
            st.markdown('#### Distancia média por cidade')
            fig = pizza_avg_city( df1 ) 
            st.plotly_chart( fig, use_container_width=True)    
        with col2:
            st.markdown( """___""")
            st.markdown('#### Tempo médio por cidade e tipo de pedido')
            #Calculos e agrupamento por cidade e tipo de pedido
            df_aux = df1.loc[:, ['Time_taken(min)', 'City', 'Type_of_order' ]].groupby(['City', 'Type_of_order']).agg( { 'Time_taken(min)': ['mean', 'std'] })
            #Renomeando colunas e organizando index
            df_aux.columns = ['avg_time', 'std_time']
            df_aux = df_aux.reset_index()
            st.dataframe(df_aux, use_container_width=True)
        
    #Container com 2 gráficos de tempo em colunas diferentes
    with st.container():
        st.markdown( """___""")
        #Criação das colunas
        col1,col2 = st.columns(2)
        with col1:
            st.markdown(' #### Tempo médio e desvio por cidade')
            fig = avg_std_city( df1 )
            st.plotly_chart( fig,  use_container_width=True)
        with col2:
            st.markdown(' #### Tempo médio e desvio por cidade e trâfego')
            fig = sunburst_city_traf( df1 )
            st.plotly_chart( fig, use_container_width=True)
            
           
            
    