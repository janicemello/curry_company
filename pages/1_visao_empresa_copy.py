#Visão empresa
#Import Libraries 
import numpy as np 
import pandas as pd 
import plotly.express as px 
import plotly.offline as py
import folium
from haversine import haversine
import streamlit as st 
from PIL import Image
from streamlit_folium import folium_static


#import dataset
df = pd.read_csv(r'food_delivery_train.csv')
#print(df)

#==================
#   FUNÇÕES
#==================
#____________________

#Cleaning
#____________________
def clean_cod(df):
#    """Esta função tem a responsabilidade de limpar o dataframe 
#    tipos de limpeza:
#    1- remoção dos dados NA
#    2- Mudança do tipo da coluna de dados 
#    3- remoção dos espaços das váriaveis de texto 
#    4- formatação da data 
#       5- limpeza da coluna de tempo """

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
    #print(df)


    #Excluindo a o texto do horario 
    df["Time_taken(min)"] = df["Time_taken(min)"].apply(lambda x: x.split("(min) ")[1])
    df["Time_taken(min)"] = df["Time_taken(min)"].astype(int)
    #print(df)
    #print(df.head())
    return df
df = clean_cod(df)

#======================================
#Barra Lateral
#======================================
st.header('Marketplace -Visão Empresa')
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
#___________
# GRÁFICO   
#__________


 #ORDER METRIC

         
def order_metric(df):
    #Order Metric
    #quantidade de pedidos por dia 
    st.header('Quantidade de pedidos por dia')
    cools = ["ID", "Order_Date"]
    #seleção de linhas
    df_aux = df.loc[:, cools].groupby("Order_Date").count().reset_index()
    #grafico
    fig1 = px.bar(df_aux, x="Order_Date", y="ID")
    return fig1


#TRAFIC_ORDER_SHARE
def traffic_order_share(df):
#Distribuição de pedidos por tipo de tráfego
    df_aux3 = df.loc[:, ["ID","Road_traffic_density"]].groupby("Road_traffic_density").count().reset_index()
    df_aux3["perc_ID"] = 100*(df_aux3["ID"]/df_aux3['ID'].sum())
#gráfico 
    fig2 = px.pie(df_aux3, values="perc_ID", names="Road_traffic_density")
    return fig2

#TRAFFIC_ORDER_CITY
def traffic_order_City(df):

    #Comparação do volume de pedidos por cidade e tipo de tráfego.
    df_aux4 = df.loc[:, ["ID", "City", "Road_traffic_density"]].groupby(["City", "Road_traffic_density"]).count().reset_index()
    #gráfico
    fig3 = px.scatter(df_aux4, x="City", y="Road_traffic_density", size="ID")
    return fig3


#WEEK_OF_YEARR
def week_of_year(df):

#    #quantidade de pedidos por semana 
    df["Week_of_year"] = df["Order_Date"].dt.strftime("%u")
    df_aux2 = df.loc[:,["ID", "Week_of_year"]].groupby("Week_of_year").count().reset_index()
    #gráfico 
    fig4 = px.line(df_aux2, x="Week_of_year", y="ID")
    return fig4 


#ORDER SHARE BY WEEK 
def order_share_by_week(df):
    #quantas entregas por semana/ quantos entregadores por semana
    df_aux5 = df.loc[:, ["ID", "Week_of_year"]].groupby("Week_of_year").count().reset_index()
    df_aux6 = df.loc[:,["Delivery_person_ID", "Week_of_year"]].groupby("Week_of_year").nunique().reset_index()
    df_aux7 = pd.merge(df_aux5,df_aux6, how="inner")
    df_aux7["order_by_delivery"] = df_aux7["ID"]/df_aux7["Delivery_person_ID"]
    #gráfico 
    fig5=px.line(df_aux7, x="Week_of_year", y="order_by_delivery")
    return fig5


#COUNTRY MAPS
def country_maps(df):

        #A localização central de cada cidade por tipo de tráfego.
        data_plot = df.loc[:, ["City", "Road_traffic_density", "Delivery_location_latitude", "Delivery_location_longitude"]].groupby(["City", "Road_traffic_density"]).median().reset_index()
        data_plot = data_plot[data_plot["City"] != "NaN "]
        data_plot = data_plot[data_plot["Road_traffic_density"] != "NaN "]
#        #gráfico 
        map = folium.Map()
        for index, location_info in data_plot.iterrows(): 
            folium.Marker([location_info["Delivery_location_latitude"], 
                           location_info["Delivery_location_longitude"]], popup= location_info[["City","Road_traffic_density" ]]).add_to(map)
        
#fazendo a visualização do gráfico
        folium_static(map,width=1024 , height= 600)
        return None




#======================================
#Layout streamlit 
#======================================

#criando abas 
tab1, tab2, tab3 = st.tabs(['Visão Gerencial', 'Visão Tática', 'Visão Geográfica'])

#usando clasula com with 
with tab1: 
    #criando um container
    with st.container():
        #ORDER METRIC
            #Order Metric
        st.markdown('# Orders by date')
        fig1 = order_metric(df)
        st.plotly_chart(fig1, use_container_width=True)

    with st.container():
#criando colunas próximo gráfico
        col1, col2 = st.columns(2)
        with col1: 
            st.header('Distribuição de pedidos por tipo de tráfego')
            fig2 = traffic_order_share(df)
            st.plotly_chart(fig2, use_container_width=True)

        with col2: 
            st.header('Comparação do volume de pedidos por cidade e tipo de tráfego')
            fig3 = traffic_order_City(df)
            st.plotly_chart(fig3, use_container_width=True)

#=======================
#  VISÃO TÁTICA
#=======================
with tab2: 
    with st.container():
        st.markdown('# Quantidade de pedidos por semana')
        fig4 = week_of_year(df)
        st.plotly_chart(fig4, use_container_width=True)

    with st.container():
        st.markdown('# Quantidade de entregas por semana')
        fig5 = order_share_by_week(df)
        st.plotly_chart(fig5, use_container_width=True)



#===================================
#        VISÃO GEOGRÁFICA
#===================================
with tab3: 
    st.markdown('#Localização central de cada cidade por tipo de tráfico')
    country_maps(df)
#    map.save('index,html')

