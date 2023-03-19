#Import Libraries 
import numpy as np 
import pandas as pd 
import plotly.express as px 
import plotly.offline as py
import re
import folium
from haversine import haversine
import streamlit as st 
from PIL import Image
from streamlit_folium import folium_static


#import dataset
df = pd.read_csv('food_delivery_train.csv')
#print(df)
#======================
#      FUNÇÕES 
#======================
def cleaning_code(df):
    #Cleaning
    #convertendo texto/categoria/strings para números decimais 
    #print(df.dtypes)
    df['Delivery_person_Ratings'] = df["Delivery_person_Ratings"].astype(float)


    #excluindo linhas vazias 
    linhas_vazias = df["Delivery_person_Age"] != "NaN "
    df = df.loc[linhas_vazias,:]
    #print(df)
    linhas_vazias2 = df["multiple_deliveries"] != "NaN "
    df = df.loc[linhas_vazias2,:]

    linhas_vazias3 = df["City"] != "NaN "
    df=df.loc[linhas_vazias3, :]

    linhas_vazias4 = df["Road_traffic_density"] != "NaN "
    df=df.loc[linhas_vazias4, :]

    linhas_vazias4 = df["Festival"] != "NaN "
    df=df.loc[linhas_vazias4, :]

    #print(df)

    #convertendo obj para int 
    df["Delivery_person_Age"] = df["Delivery_person_Age"].astype(int)
    #print(df.dtypes)

    df["multiple_deliveries"] = df["multiple_deliveries"].astype(int)
    #print(df.dtypes)

    #Convertento obj para date 
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], format= '%d-%m-%Y' )
    #print(df.dtypes)
    #print(df)

    #excluindo index
    df = df.reset_index(drop=True)

    #excluindo espaços vazios 
    for i in range(len(df)):
        df.loc[i,"ID"] = df.loc[i,"ID"].strip()
        df.loc[i,"Delivery_person_ID"] = df.loc[i,"Delivery_person_ID"].strip()
        df.loc[i,"Road_traffic_density"] = df.loc[i,"Road_traffic_density"].strip()
        df.loc[i,"City"] = df.loc[i,"City"].strip()
    #print(df)


    #Excluindo a o texto do horario 
    df["Time_taken(min)"] = df["Time_taken(min)"].apply(lambda x: x.split("(min) ")[1])
    df["Time_taken(min)"] = df["Time_taken(min)"].astype(int)
    #print(df)
    #print(df.head())


    #print(df.head())

    
    return df
df = cleaning_code(df)

#======================================
#Barra Lateral
#======================================
st.header('Marketplace -Visão Entregadores')
#image_path = "/home/janice/Downloads/DATA SCIENCE(1)/FTC/logo.png"
image = Image.open('logo.png')
st.sidebar.image(image, width=120)


st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

#st.header(data_slider)
st.sidebar.markdown("""---""")

traffic_options = st.sidebar.multiselect("Quais as condições do trânsito", ['Low', 'Medium', 'High', 'Jam'], default=['Low', 'Medium', 'High', 'Jam'])

st.sidebar.markdown("""---""")
st.sidebar.markdown("Powered by Janice Melo")

#achando a data min
#st.dataframe(df)
#print(df["Road_traffic_density"].unique())

#criando os filtros das datas
linhas_selecionadas = df['Order_Date'] < data_slider
df = df.loc[linhas_selecionadas, :]
#df["Road_traffic_density"].head()
#filtro de transito 
linhas_selecionadas2 = df['Road_traffic_density'].isin(traffic_options)
df = df.loc[linhas_selecionadas2, :]


#para ver se o filtro ta funcionando
#st.dataframe(df.head())

#==================================
#      FUNÇÕES LAYOUT
#===================================

#TOP DELIVERYS MAIS RÁPIDOS 
def top_deliverys(df, top_asc):
    df2 = df.loc[:, ['Delivery_person_ID','City', 'Time_taken(min)']].groupby(['City', 'Delivery_person_ID']).min().sort_values(['City', 'Time_taken(min)'], ascending = top_asc).reset_index()
    top10_01 = df2.loc[df2['City'] == 'Metropolitian', :].head(10)
    top10_02 = df2.loc[df2['City'] == 'Urban', :].head(10)
    top10_03 = df2.loc[df2['City'] == 'Semi-Urban', :].head(10)

    df3 = pd.concat([top10_01, top10_02, top10_03]).reset_index()
    return df3 





#======================================
#        Layout 
#=====================================

#criando abas 
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', '-', '-'])

with tab1: 
    with st.container():
        st.title('Overall Metrics')

        col1, col2, col3, col4 = st.columns(4, gap='large')
        with col1: 
            #st.subheader('Maior de idade')
            maior_idade = df.loc[:, "Delivery_person_Age"].max()
            col1.metric('Maior idade', maior_idade)
            
        with col2: 
            #st.subheader('Menor idade')
            menor_idade = df.loc[:, "Delivery_person_Age"].min()
            col2.metric('Menor idade', menor_idade)

        with col3: 
            #st.subheader('Melhor condição de veiculos')
            melhor_cond = df.loc[:,"Vehicle_condition"].max()
            col3.metric('Melhor condição', melhor_cond)

        with col4: 
            #st.subheader('Pior condição de veículos')
            pior_cond = df.loc[:, "Vehicle_condition"].min()
            col4.metric('Pior conndição', pior_cond)

    with st.container():
        st.markdown("""---""")
        st. title('Avaliações')
        col1, col2 = st.columns(2)
        with col1: 
            st.markdown('##### Avaliação média por entregador')
            avalia_media_entregador = df.loc[:, ["Delivery_person_ID","Delivery_person_Ratings"]].groupby("Delivery_person_ID").mean().reset_index()
            st.dataframe(avalia_media_entregador)
        with col2: 
#            #Avaliação Média por trânsito
#            #A avaliação média e o desvio padrão por tipo de tráfego.
            st.markdown('###### Avaliação Média por trânsito')
            avaliacao_media_std_traffic = (df.loc[:,["Delivery_person_Ratings","Road_traffic_density"]].groupby("Road_traffic_density")
                                            .agg({"Delivery_person_Ratings": ["mean", "std"]}))
#            #mudança de nome das colunas                                 
            avaliacao_media_std_traffic.columns = ["Delivery_Mean", "Delivery_STD"]
#            #reset do index 
            avaliacao_media_std_traffic = avaliacao_media_std_traffic.reset_index()
            st.dataframe(avaliacao_media_std_traffic)
            
            #Avaliação média por clima
            st.markdown('###### Avaliação média por clima')
            avaliacao_media_std_weather = (df.loc[:,["Delivery_person_Ratings","Weatherconditions"]].groupby("Weatherconditions")
                                .agg({"Delivery_person_Ratings": ["mean", "std"]}))
#            #mudança de nome das colunas                                 
            avaliacao_media_std_weather.columns = ["Delivery_Mean", "Delivery_STD"]
            #reset do index 
            avaliacao_media_std_weather = avaliacao_media_std_weather.reset_index()
            st.dataframe(avaliacao_media_std_weather)

    with st.container():
        st.markdown("""---""")
        st.title('Velocidade de entrega')

        col1, col2 = st.columns(2)
        with col1: 
            st.markdown('##### Top entregadores mais rápidos')
            df3 = top_deliverys(df, top_asc=True)
            st.dataframe(df3)

        with col2:
            st.markdown('##### Top entregadores mais lentos')
            df3 = top_deliverys(df,top_asc=False)
            st.dataframe(df3)
#print(df.dtypes)
#print(df)
