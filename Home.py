#Bibliotecas 
import streamlit as st
from PIL import Image 

#st.set_page_config(page_tittle = "Home")


#==========================
#   BARRA LATERAL 
#==========================

#image_path = "/home/janice/Downloads/DATA SCIENCE(1)/FTC/logo.png"
image = Image.open('logo.png')
st.sidebar.image(image, width=140)

st.sidebar.markdown('### Curry Company')
st.sidebar.markdown('## Fastest Delivery in Town')
st.sidebar.markdown("""---""")

st.write('# Curry Company Growth Dashboard')

st.markdown("""
    Growth Dashboard foi contruído para acompanhar as métricas de crescimento dos entregadores e Restaurantes.
    VISÕES:
    - Empresa: 
         Visão Gerencial: Métricas gerais de comportamento.
         Visão Tática: Indicadores semanais e crescimento. 
         Visão Geográfica: Indicadores de geolocalização. 
    - Entregador: 
        Acompanhamento dos indicadores semanais e de cresciemento. 
    - Restaurante: 
        Acompanhamento dos indicadores semanais do crescimento do restaurante. 
""")
