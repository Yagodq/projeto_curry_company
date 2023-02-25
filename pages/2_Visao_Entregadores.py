#Bibliotecas ------------------------------------------------
import pandas as pd
import plotly.express as px
from haversine import haversine
import streamlit as st
from PIL import Image
import folium
from streamlit_folium import folium_static

#configuração da página
st.set_page_config( page_title='Visão Entregadores', layout='wide' )

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

# Tabela Avaliação media e desvio padrão por trânsito
def mean_std_trans( df1):
    """ Produz uma tabela de dados com a média e desvio padrão das avaliações de usuário por tipo de trânsito.
        imput:Dataframe
        output:Tabela(Dataframe)
    """
    #Seleção de colunas
    cols = ['Delivery_person_Ratings', 'Road_traffic_density']
    #Seleção de linha, agrupamento por tráfego e calculo da média e desvio padrão
    #Agregação = .agg(colunas : ['operação' , 'operação' ])
    df_mean_std = (df1.loc[:, cols].groupby('Road_traffic_density')
                               .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ))
    #renomeando colunas de média e desvio padrão
    df_mean_std.columns = ['Delivery_mean', 'Delivery_std']
    df_mean_std.reset_index()
    st.dataframe(df_mean_std, use_container_width=True)

    st.markdown('##### Avaliação media e desvio padrão por condição climática')
    #Seleção de colunas
    cols = ['Delivery_person_Ratings', 'Weatherconditions']
    #Seleção de linha, agrupamento por tráfego e calculo da média e desvio padrão
    #Agregação = .agg(colunas : ['operação' , 'operação' ])
    df_mean_std_wethe = (df1.loc[:, cols].groupby('Weatherconditions')
                               .agg( {'Delivery_person_Ratings': ['mean', 'std'] } ))
    #renomeando colunas de média e desvio padrão
    df_mean_std_wethe.columns = ['Delivery_mean', 'Delivery_std']
    #Reset do index
    df_mean_std_wethe.reset_index()
                
    return df_mean_std_wethe

#Devolve tabela com top 10 vendedores mais rapidos ou lentos, selecionados de acordo com o parametro 'top_asc'passado.
def top_entregadores( df1, top_asc):
    """ Produz uma tabela de dados com os top 10 entregadores mais rápidos ou lentos por tipo cidade.
        Parêmetro: top_asc=True (Retorna os entregadores mais rápidos), top_asc=False(Retorna os entregadores mais lentos)
        imput:Dataframe
        output:Tabela(Dataframe)
    """
    #Seleção de colunas
    cols = ['Delivery_person_ID','City', 'Time_taken(min)']
    #Agrupamento dos entregadores mais lentos por cidade (max)
    df2 = df1.loc[:, cols].groupby(['City', 'Delivery_person_ID']).max().sort_values( [ 'City', 'Time_taken(min)' ], ascending=top_asc).reset_index()
    #Selecionando os 10 primeiros por cidade
    df_aux01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    df_aux02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    df_aux03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)
    #Unindo as listas do top 10 
    df3 = pd.concat( [df_aux01, df_aux02, df_aux03 ] ).reset_index( drop=True )
                
    return df3

#-------------------------------------------------------------------------------------------------
#-------------------------------- Inicío da estrutura lógica do código ---------------------------
#Importando Dataset
df = pd.read_csv('train.csv')

#Limpando os dados
df1 = clean_code( df )

#Visão Entregadores ===========================================
#=========================================================
#Barra lateral Streamlit
#=========================================================
st.title( 'Marketplace - Visão Entregadores' )

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
    'Até qual data ?',
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
#Tab Visão gerencial
with tab1:
    #Criação de uma container com 4 colunas
    with st.container():
        st.markdown('### Metricas gerenciais')
        col1,col2,col3,col4 = st.columns( 4)
        with col1:
            #Maior idade entre os entregadores
            maior_idade = df1.loc[:, 'Delivery_person_Age'].max()
            col1.metric( 'Maior idade', maior_idade)
        with col2:
            #Menor idade entre os entregadores
            menor_idade = df1.loc[:, 'Delivery_person_Age'].min()
            col2.metric('Menor Idade', menor_idade)
        with col3:
            melhor_condicao = df1.loc[:, 'Vehicle_condition'].max()
            col3.metric('Melhor condição de veículo', melhor_condicao)
        with col4:
            pior_condicao = df1.loc[:, 'Vehicle_condition'].min()
            col4.metric('Pior condição de veículo', pior_condicao)
            
    #Criação de um container com duas colunas, uma inteira e uma com duas linhas        
    with st.container():
        st.markdown( """___""")
        st.markdown('### Volumes de avaliações')
        col1,col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Avaliação media por entregador')
            #Seleção de colunas
            cols = ['Delivery_person_Ratings', 'Delivery_person_ID' ]
            #Seleção de linhas, agrupamento por entregador e média da avaliação
            df_avg = df1.loc[:, cols].groupby(['Delivery_person_ID']).mean().reset_index()
            #Comando para exibição de dataframe no Streamlit
            st.dataframe( df_avg, use_container_width=True)
        with col2:
            st.markdown('##### Avaliação media e desvio padrão por trânsito')
            df_mean_std_wethe = mean_std_trans( df1)
            st.dataframe(df_mean_std_wethe, use_container_width=True)        
             
    #Criação de container com duas colunas, tabelas com top 10 vendedores mais rapidos e lentos
    with st.container():
        st.markdown( """___""")
        st.markdown('### Velocidade de entrega')
        col1,col2 = st.columns( 2 )
        with col1:
            st.markdown('##### Top 10 entregadores mais rapidos por cidade')
            df3 = top_entregadores( df1, top_asc=True)
            st.dataframe( df3, use_container_width=True)
        with col2:
            st.markdown('##### Top 10 entregadores mais lentos por cidade')
            df3 = top_entregadores( df1, top_asc=False)
            st.dataframe(df3, use_container_width=True)
            
           
            
            
        
        
        

