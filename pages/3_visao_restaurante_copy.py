#Import Libraries 
import numpy as np 
import pandas as pd 
import plotly.express as px 
import plotly.offline as py
import plotly.graph_objects as go 
import re
import folium
from haversine import haversine
import streamlit as st 
from PIL import Image
from streamlit_folium import folium_static


#import dataset
df = pd.read_csv(r'/home/janice/Downloads/DATA SCIENCE(1)/FTC/food_delivery_train.csv')
#print(df)


#=====================================
#           FUNÇÕES
#=====================================
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

        #Excluindo a o texto do horario 
    df["Time_taken(min)"] = df["Time_taken(min)"].apply(lambda x: x.split("(min) ")[1])
    df["Time_taken(min)"] = df["Time_taken(min)"].astype(int)

    return df 
df = cleaning_code(df)
#======================================
    #Barra Lateral
#======================================
st.header('Marketplace -Visão Restaurantes')
#image_path = "/home/janice/Downloads/DATA SCIENCE(1)/FTC/logo.png"
image = Image.open('logo.png')
st.sidebar.image(image, width=120)


st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

#st.sidebar.markdown('## Selecione uma data limite')

data_slider = st.sidebar.slider(
    'Até qual valor?',
    value=pd.datetime(2022, 4, 13),
    min_value=pd.datetime(2022, 2, 11),
    max_value=pd.datetime(2022, 4, 6),
    format='DD-MM-YYYY')

st.header(data_slider)
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


#==========================
#       FUNÇÃO LAYOUT
#=========================


#DISTANCE 
def distance(df, fig):
    if fig == False:
        cools = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['distance'] = df.loc[:, cools].apply(lambda x:haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        avg_distance = np.round(df['distance'].mean(), 2)
        return avg_distance
    else:
        cools = ['Restaurant_latitude', 'Restaurant_longitude', 'Delivery_location_latitude', 'Delivery_location_longitude']
        df['distance'] = df.loc[:, cools].apply(lambda x:haversine((x['Restaurant_latitude'], x['Restaurant_longitude']), (x['Delivery_location_latitude'], x['Delivery_location_longitude'])), axis=1)
        distance = df.loc[:, ['City', 'distance']].groupby('City').mean().reset_index()
        fig = go.Figure(data = [go.Pie(labels = distance['City'], values= distance['distance'], pull=[0, 0.1 ,0])])
        return fig 

#AVG_STD_TIME_DELIVERY 
def avg_std_time_delivery(df, festival, op):
#ESTA FUNÇÃO CALCULA O TEMPO MÉDIO E O DESVIO PADRÃO DO TEMPO DE ENTREGA."
#PARAMETROS 
# IMPUT: DF: DATAFRAME COM OS DADOS NECESSÁRIOS PARA O CALCULO 
# OP: Tipo de operação que precisa ser calculada
#      'avg_time': Calcula o tempo médio 
#       'std_time': Calcula o desvio padrão do tempo de entega
#OUTPUT: DAtaframe com 2 colunas e 1 linha
    cools = ['Time_taken(min)', 'Festival']
    df_aux = df.loc[:, cools].groupby('Festival').agg({'Time_taken(min)':['mean', 'std']})
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()
    #filtrando só o Yes 
    linhas_selec = df_aux['Festival'] == festival
    df_aux = np.round(df_aux.loc[linhas_selec, op],2)

    return df_aux

#AVG_STD_TIME_GRAPH
def avg_std_time_graph(df):
    df_aux = df.loc[:, ['City', 'Time_taken(min)']].groupby( 'City' ).agg( {'Time_taken(min)': ['mean', 'std']} )
    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = go.Figure() 
    fig.add_trace( go.Bar( name='Control', x=df_aux['City'], y=df_aux['avg_time'], error_y=dict(type='data', array=df_aux['std_time']))) 
    fig.update_layout(barmode='group') 
    return fig 

#AVG_STD_TIME_ON_TRAFFIC
def avg_std_time_on_traffic(df):
    df_aux = ( df.loc[:, ['City', 'Time_taken(min)', 'Road_traffic_density']]
    .groupby( ['City', 'Road_traffic_density'] )
    .agg( {'Time_taken(min)': ['mean', 'std']} ) )

    df_aux.columns = ['avg_time', 'std_time']
    df_aux = df_aux.reset_index()

    fig = px.sunburst(df_aux, path=['City', 'Road_traffic_density'], values='avg_time',
        color='std_time', color_continuous_scale='RdBu',
        color_continuous_midpoint=np.average(df_aux['std_time'] ) )
    return fig 

#======================================
#        Layout 
#=====================================
tab1, tab2,tab3 = st.tabs(['Visão Genrencial', '-', '_'])

with tab1: 
    with st.container():  
        st.title('Overal Metrics')
        col1,col2,col3,col4,col5,col6 = st.columns(6)

        with col1:
            delivery_unique = len(df.loc[:, 'Delivery_person_ID'].unique())
            col1.metric('Entregadores únicos', delivery_unique)


        with col2: 
            avg_distance = distance(df, fig= False)
            col2.metric("Distância média",avg_distance)

        with col3:
            df_aux = avg_std_time_delivery(df, 'Yes ','avg_time')
            col3.metric('STD da entrega com festival', df_aux)   

        with col4:
            df_aux = avg_std_time_delivery(df, 'Yes ','std_time')
            col4.metric('AVG da entrega com festival', df_aux)     

        with col5: 
            df_aux = avg_std_time_delivery(df, 'No ','avg_time')
            col5.metric('AVG da entrega sem festival', df_aux) 
        with col6:
            df_aux = avg_std_time_delivery(df, 'No ','std_time')
            col6.metric('STD da entrega sem festival', df_aux) 


    with st.container():
        col1, col2 = st.columns(2)
        with col1: 
            st.title('Distribuição da distância')
            cools = ['City', 'Time_taken(min)', 'Type_of_order']
            desv_med = df.loc[:, cools].groupby(['City', 'Type_of_order']).agg({'Time_taken(min)':['mean', 'std']})
            desv_med.columns = ['avg_time', 'std_time']
            desv_med = desv_med.reset_index()
            st.dataframe(desv_med)

        with col2: 
#            st.markdown("TIME GRAPH")
            fig = avg_std_time_graph(df)
            st.plotly_chart( fig )
    #        cools = ['City', 'Time_taken(min)']
    #        desv_med = df.loc[:, cools].groupby('City').agg({'Time_taken(min)':['mean', 'std']})
    #        desv_med.columns = ['avg_time', 'std_time']
    #        desv_med = desv_med.reset_index()
    #        fig = go.Figure()
    #        fig.add_trace(go.bar(name = 'Control', x=desv_med['City'], y=desv_med['avg_time'], error_y=dict(type='data', array=desv_med['std_time'])))
    #        fig.update_layout(barmode='group')
    #        st.plotly_chart(fig)


    with st.container():
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("""---""")
            st.title('Tempo médio de entrega por cidade')
            fig= distance(df, fig=True)
            st.plotly_chart(fig)

        with col2: 
            st.markdown("""---""")
            st.title('Distribuição do tempo')
            fig = avg_std_time_on_traffic(df)
            st.plotly_chart( fig )


    
    
