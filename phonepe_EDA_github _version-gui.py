import pandas as pd
import json
import os
import requests
import subprocess
import streamlit as st
from streamlit_option_menu import option_menu
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from IPython.display import display 

# Connection
conn=psycopg2.connect(host="localhost", user="user", password="password", database="database")
cursor=conn.cursor()

# DataFrames

# agg_trans
cursor.execute('''select * from Aggregate_Transaction;''')
conn.commit()
t1=cursor.fetchall()
agg_trans=pd.DataFrame(t1,columns=["state","year","quarter","transaction_type","transaction_count","transaction_amount"])

# agg_user
cursor.execute('''select * from Aggregate_user;''')
conn.commit()
t2=cursor.fetchall()
agg_user=pd.DataFrame(t2,columns=["state","year","quarter","brands","count","percentage"])

# map_trans
cursor.execute('''select * from Map_Transaction;''')
conn.commit()
t3=cursor.fetchall()
map_trans=pd.DataFrame(t3,columns=["state","year","quarter","district","transaction_count","transaction_amount"])

# map_user
cursor.execute('''select * from Map_user;''')
conn.commit()
t4=cursor.fetchall()
Map_user=pd.DataFrame(t4,columns=["state","year","quarter","district","registeredUsers","appOpens"])

# top_trans
cursor.execute('''select * from Top_Transaction;''')
conn.commit()
t5=cursor.fetchall()
Top_trans=pd.DataFrame(t5,columns=["state","year","quarter","pincode","count","amount"])

# top_user
cursor.execute('''select * from Top_user;''')
conn.commit()
t6=cursor.fetchall()
Top_user=pd.DataFrame(t6,columns=["state","year","quarter","pincode","registeredUser"])

#-----------------------------------------------------------------------------GEOVISUALIZATON---------------------------------------------------------------------------------#

#geomap overall transaction
def plt_overall_map_trans():
    at=agg_trans[["state","transaction_count"]]
    at1=at.groupby("state")["transaction_count"].sum()
    at2=pd.DataFrame(at1).reset_index()
    at2=at2[["state","transaction_count"]].sort_values("state")
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(geojson)
    data = response.json()
    sta=sorted([feature['properties']['ST_NM'] for feature in data["features"]])
    df_st=pd.DataFrame({"state":sta})

    mergedf=df_st.merge(at2,on='state')

    fig=px.choropleth(mergedf,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM',locations='state',color='transaction_count',color_continuous_scale="matter",title='OVERALL USER TRANSACTIONS')
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(title_font=dict(size=30),title_font_color="#6739b7",title_x=0.25,height=700,
                       geo=dict(bgcolor='rgba(0,0,0,0)'),  # Transparent background color
                      paper_bgcolor='rgba(0,0,0,0)'  # Transparent paper background color)
                        )           
    return st.plotly_chart(fig,use_container_width=True)


#geomap overall user
def plt_overall_map_user():
    at=agg_user[["state","count"]]   
    at1=at.groupby("state")["count"].sum() 
    at2=pd.DataFrame(at1).reset_index()  
    at2=at2[["state","count"]].sort_values(["state","count"])
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(geojson)
    data = response.json()
    sta=sorted([feature['properties']['ST_NM'] for feature in data["features"]])
    df_st=pd.DataFrame({"state":sta})

    mergedf=df_st.merge(at2,on='state')

    fig=px.choropleth(mergedf,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM',locations='state',color='count',color_continuous_scale="oryel",title='OVERALL REGISTERED USERS')
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(title_font=dict(size=30),title_font_color="#E83A52",title_x=0.25,height=700,
                       geo=dict(bgcolor='rgba(0,0,0,0)'),  # Transparent background color
                      paper_bgcolor='rgba(0,0,0,0)'  # Transparent paper background color)
                        )
    return st.plotly_chart(fig,use_container_width=True)



# geomap transaction
def plt_map_trans(year,quarter,transaction_type):
    year=int(year)
    quarter=int(quarter)
    at=agg_trans[["state","year","quarter","transaction_type","transaction_count"]]   
    at1=at.loc[(at['year']== year)& (at['quarter']== quarter)& (at['transaction_type']==transaction_type)]     
    at2=at1[["state","transaction_count"]].sort_values("state")
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(geojson)
    data = response.json()
    sta=sorted([feature['properties']['ST_NM'] for feature in data["features"]])
    df_st=pd.DataFrame({"state":sta})

    mergedf=df_st.merge(at2,on='state')

    fig=px.choropleth(mergedf,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM',locations='state',color='transaction_count',color_continuous_scale="matter",title=f'{transaction_type.upper()} TYPE TRANSACTIONS')
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(title_font=dict(size=30),title_font_color="#6739b7",title_x=0.25,height=700,
                       geo=dict(bgcolor='rgba(0,0,0,0)'),  # Transparent background color
                      paper_bgcolor='rgba(0,0,0,0)'  # Transparent paper background color)
                        )           
    return st.plotly_chart(fig,use_container_width=True)

   
# geomap user

def plt_map_user(year,quarter):
    year=int(year)
    quarter=int(quarter)
    at=agg_user[["state","year","quarter","count","percentage"]]   
    at1=at.loc[(at['year']== year)& (at['quarter']== quarter)]     
    at2=at1[["state","count"]].sort_values(["state","count"])
    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson"
    response=requests.get(geojson)
    data = response.json()
    sta=sorted([feature['properties']['ST_NM'] for feature in data["features"]])
    df_st=pd.DataFrame({"state":sta})

    mergedf=df_st.merge(at2,on='state')

    fig=px.choropleth(mergedf,
                    geojson="https://gist.githubusercontent.com/jbrobst/56c13bbbf9d97d187fea01ca62ea5112/raw/e388c4cae20aa53cb5090210a42ebb9b765c0a36/india_states.geojson",
                    featureidkey='properties.ST_NM',locations='state',color='count',color_continuous_scale="oryel",title='REGISTERD USERS')
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(title_font=dict(size=30),title_font_color="#E83A52",title_x=0.3,height=700,
                       geo=dict(bgcolor='rgba(0,0,0,0)'),  # Transparent background color
                      paper_bgcolor='rgba(0,0,0,0)'  # Transparent paper background color)
                        )
    return st.plotly_chart(fig,use_container_width=True)
   

# query

#------------------------------------------------- Total Transaction Amount by State for different types of transaction"-------------------------------------------------------------------------#
def one(type):
    at=agg_trans[["state","year","transaction_type","transaction_amount"]]
    at1=at.loc[at['transaction_type']==type]
    at2=at1.groupby(["state","year"])['transaction_amount'].sum()
    at2=pd.DataFrame(at2).reset_index()
    at3=at2.sort_values(by=["state","year"])
    fig=px.bar(at3,x='state',y='transaction_amount',animation_frame='year',
               title=f"Total Transaction Amount by State for {type} type transaction")
    fig.update_layout(height=400,width=1300)
    return st.plotly_chart(fig)


# -------------------------------------------------------------total transaction count vs transaction amount-------------------------------------------------------------------------#
def two():
    at=agg_trans[["state","transaction_count","transaction_amount"]]
    at=at.groupby("state")[["transaction_count","transaction_amount"]].sum()

    fig=px.bar(data_frame=at.reset_index(),x="state",y="transaction_count",color="transaction_amount",
               title="statewise total transaction count and coresponding amount ")   #color_continuous_scale=px.colors.qualitative.Light24
    fig.update_layout(height=600,width=1300)
    fig.update_xaxes(tickangle=45)
    return st.plotly_chart(fig)

#------------------------------------------------------------------------- brands market presence----------------------------------------------------------------------------------#
def three():
    at=agg_user[["brands","count"]]
    at=at.groupby("brands")["count"].sum()

    fig=px.pie(data_frame=at.reset_index(),names="brands",values="count",
               title="brands market presence")
    fig.update_layout(height=400,width=1300)   
    return st.plotly_chart(fig)

#------------------------------------------------------------------ top 10 districts with highest transactions--------------------------------------------------------------------------#
def four():
    at=map_trans[["state","district","transaction_count","transaction_amount"]]
    at=at.groupby(["district","state"])[["transaction_count","transaction_amount"]].sum()
    at=at.sort_values(["transaction_count","transaction_amount"],ascending=False)
    at1=at.head(10)
    fig=px.bar(data_frame=at1.reset_index(),x="district",y="transaction_count",color="transaction_amount",hover_data="state",
               title="top 10 districts with highest transactions")
    fig.update_layout(height=400,width=1300)  
    return st.plotly_chart(fig)

#----------------------------------------------------------------top 10 districts with highest registeredUsers----------------------------------------------------------------#
def five():
    at=Map_user[["state","district","registeredUsers"]]
    at=at.groupby(["district","state"])[["registeredUsers"]].sum()
    at=at.sort_values(["registeredUsers"])  
    at1=at.tail(10)
    fig=px.bar(data_frame=at1.reset_index(),x="district",y="registeredUsers",hover_data=["state"],
               title="top 10 districts with highest registeredUsers")
    fig.update_layout(height=400,width=1300)  
    return st.plotly_chart(fig)

#---------------------------------------------------------------- top 10 pincode with highest transaction amount--------------------------------------------------------------#
def six():
    at=Top_trans[["state","pincode","count","amount"]]
    at=at.groupby(["pincode","state"])[["count","amount"]].sum()
    at=at.sort_values(["amount"],ascending=False) 
    at1=at.head(10)
    fig=px.bar(data_frame=at1.reset_index(),x="pincode",y="amount",hover_data=["count","state"],
               title="top 10 pincode with highest transaction amount")
    fig.update_layout(xaxis_type="category",height=400,width=1300)  
    return st.plotly_chart(fig)


#--------------------------------------------------------------------top 10 pincode with highest registerusers--------------------------------------------------------------------#
def seven():
    at=Top_user[["state","pincode","registeredUser"]]
    at=at.groupby(["pincode","state"])[["registeredUser"]].sum()
    at=at.sort_values(["registeredUser"],ascending=False) 
    at1=at.head(10)
    fig=px.bar(data_frame=at1.reset_index(),x="pincode",y="registeredUser",hover_data=["state"],
               title="top 10 pincode with highest registeruser")
    fig.update_layout(xaxis_type="category",height=400,width=1300)  
    return st.plotly_chart(fig)

#------------------------------------------------------------------ top 10 districts with lowest transactions-------------------------------------------------------------------------#
def eight():
    at=map_trans[["state","district","transaction_count","transaction_amount"]]
    at=at.groupby(["district","state"])[["transaction_count","transaction_amount"]].sum()
    at=at.sort_values(["transaction_count","transaction_amount"])
    at1=at.head(10)
    fig=px.bar(data_frame=at1.reset_index(),x="district",y="transaction_count",color="transaction_amount",hover_data="state",
               title="top 10 districts with lowest transactions")
    fig.update_layout(height=400,width=1300)  
    return st.plotly_chart(fig)

#----------------------------------------------------------------top 10 districts with lowest registeredUsers----------------------------------------------------------------#
def nine():
    at=Map_user[["state","district","registeredUsers"]]
    at=at.groupby(["district","state"])[["registeredUsers"]].sum()
    at=at.sort_values(["registeredUsers"],ascending=False)  
    at1=at.tail(10)
    fig=px.bar(data_frame=at1.reset_index(),x="district",y="registeredUsers",hover_data=["state"],
               title="top 10 districts with lowest registeredUsers") 
    fig.update_layout(height=400,width=1300) 
    return st.plotly_chart(fig)

#--------------------------------------------------------------------top 10 pincode with lowest registerusers--------------------------------------------------------------------#
def ten():
    at=Top_user[["state","pincode","registeredUser"]]
    at=at.groupby(["pincode","state"])[["registeredUser"]].sum()
    at=at.sort_values(["registeredUser"],ascending=False) 
    at1=at.tail(10)
    fig=px.bar(data_frame=at1.reset_index(),x="pincode",y="registeredUser",hover_data=["state"],
               title="top 10 pincode with lowest registeruser")
    fig.update_layout(xaxis_type="category",height=400,width=1300)  
    return st.plotly_chart(fig)



### ----------------------------------------------------------------------------streamlit-------------------------------------------------------------------------------------------------------------###

st.set_page_config(layout="wide")
st.markdown("<h1 style='text-align: center; color:#0EB5D3;'>PHONEPE PULSE DATA VISUALIZATION</h1>", unsafe_allow_html=True)
with st.expander(':blue[About Project]', expanded=True):
    st.markdown("""
    <p style='text-align: center; color:#0EB5D3;'>
    <h2 style='color:#0EB5D3'>About the PhonePe Pulse Data Visualization Project</h2>
    
    Welcome to the PhonePe Pulse Data Visualization project! This interactive web-based dashboard provides a comprehensive visual analysis of data related to transactions and user statistics within the PhonePe application. Developed using Python and the Streamlit library, this project aims to offer insights into various aspects of user behavior and transaction trends.

    <h3 style='color:#0EB5D3'>Project Goals</h3>

    The primary objective of this project is to present data-driven insights in an easily accessible and visually appealing format. By leveraging powerful data visualization techniques, we aim to provide a deeper understanding of the following key areas:

    - <b style='color:#0EB5D3'>Transaction Patterns</b>: Explore the distribution of transaction types and their frequency across different states and regions of India.
    - <b style='color:#0EB5D3'>User Engagement</b>: Analyze the growth of registered users and their engagement levels, shedding light on areas with high user activity.
    - <b style='color:#0EB5D3'>Top Performers</b>: Identify the districts and pin codes with the highest transaction amounts and registered users.
    - <b style='color:#0EB5D3'>Brands Presence</b>: Visualize the market presence of different brands within the PhonePe ecosystem.  
     </p>
    """, unsafe_allow_html=True)


selected = option_menu(None, ["transaction","user","query"],
                       icons=["currency-rupee","people-fill","search-heart"], 
                       default_index=0,
                       orientation="horizontal",
                       styles={"nav-link": {"font-size": "25px", "text-align": "centre", "margin": "0px", "--hover-color": "#0EB5D3",},
                               "icon": {"font-size": "25px"},
                               "container" : {"max-width": "6000px"},
                               "nav-link-selected": {"background-color": "#0EB5D3"}})

if selected== "transaction":
    mp_type=st.radio(''':blue[***Select an option to view geo visualization of data***]''',["overall","specific"],horizontal=True)
    if mp_type=="overall":
        plt_overall_map_trans()
    elif mp_type=="specific":
        col1,col2,col3=st.columns(3)
        with col1:
            y=st.selectbox('Select Year', ('2018','2019','2020','2021','2022'),key='Y1')
        with col2:
            qt=st.selectbox("select quarter",("1","2","3","4"),key='Q1')
        with col3:
            transaction=st.selectbox("select transaction type",("Recharge & bill payments","Peer-to-peer payments","Merchant payments","Financial Services","Others"))
        plt_map_trans(y,qt,transaction)


if selected=="user":
    mp_type=st.radio(''':blue[***Select an option to view geo visualization of data***]''',["overall","specific"],horizontal=True,key="u1")
    if mp_type=="overall":
        plt_overall_map_user()
    elif mp_type=="specific":
        col1,col2=st.columns(2)
        with col1:
            y1=st.selectbox('Select Year', ('2018','2019','2020','2021','2022'))
        with col2:
            qt1=st.selectbox("select quarter",("1","2","3","4"))
        plt_map_user(y1,qt1)



if selected=="query":
    q=st.selectbox(''':blue[***Select an option to view visualization of data***]''', 
                   ('Total Transaction Amount by State for different types of transaction','total transaction count vs transaction amount',
                                  'brands market presence','top 10 districts with highest transactions',
                                  'top 10 districts with highest registeredUsers','top 10 pincode with highest transaction amount','top 10 pincode with highest registerusers',
                                  'top 10 districts with lowest transactions','top 10 districts with lowest registeredUsers','top 10 pincode with lowest registerusers'
                                    ))

    if q=='Total Transaction Amount by State for different types of transaction':
        a= st.radio("select transaction type",("Recharge & bill payments","Peer-to-peer payments","Merchant payments","Financial Services","Others"),horizontal=True,key="trtype")
        one(a)
    elif q=='total transaction count vs transaction amount':
        two()
    elif q=='brands market presence':
        three()
    elif q=='top 10 districts with highest transactions':
        four()
    elif q=='top 10 districts with highest registeredUsers':
        five()
    elif q=='top 10 pincode with highest transaction amount':
        six()
    elif q=='top 10 pincode with highest registerusers':
        seven()
    elif q=='top 10 districts with lowest transactions':
        eight()
    elif q=='top 10 districts with lowest registeredUsers':
         nine()
    elif q=='top 10 pincode with lowest registerusers':
        ten()