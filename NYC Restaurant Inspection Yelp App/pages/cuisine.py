import streamlit as st 
import pandas as pd 
import numpy as np
from sqlalchemy import create_engine
from datetime import datetime, date
import matplotlib.pyplot as plt
import seaborn as sns
import folium 
from folium import IFrame
from streamlit_folium import folium_static

engine = create_engine('sqlite:////Users/hannahkim/project/project3/inspection.db')

st.set_page_config(page_title="Cuisine Info", page_icon="🗺️")
st.sidebar.header('Cuisines to look at')

#Load df for Barplot 
cuisine_df = pd.read_sql('''SELECT inspection_date, camis, cuisine_description, sum(score) as score
                            FROM inspection
                            GROUP BY inspection_date, cuisine_description
                            ORDER BY sum(score) DESC;''', engine)
cuisine_df['inspection_date'] = pd.to_datetime(cuisine_df['inspection_date'])
cuisine_df['inspection_date'] = cuisine_df['inspection_date'].dt.year
##st.write(cuisine_df.head())

#INCLUDE HEADER 
st.header(
    f"Which top 5 cuisines recieved the most cummulative scores from inspection?"
)

#Create Filter
date_list = cuisine_df['inspection_date'].unique().tolist()
date_list.sort(reverse = False)
date_range = st.selectbox('Inspection Year', date_list, index = 0, key = "cuisine")



## update cuisine_df 
cuisine_df = cuisine_df[cuisine_df['inspection_date']==date_range]
cuisine_df_new = (cuisine_df.groupby(['inspection_date','cuisine_description'])['score']
                    .sum().reset_index().sort_values('score', ascending = False))
cuisine_df_new = cuisine_df_new[['inspection_date', 'cuisine_description', 'score']]

##st.write(cuisine_df_new)

# Interactive Barplot for cuisine vs score
fig, ax = plt.subplots(figsize=(20,10))
fig1 = sns.barplot(data=cuisine_df_new[:5],  x='score', y = 'cuisine_description', ax= ax, edgecolor=".3",
        linewidth=0.5, color = 'dodgerblue', ci = None)
#plt.tight_layout()
ax.bar_label(fig1.containers[0],label_type = 'center')
ax.set_ylabel('Cuisine',ha='center', labelpad = 20, fontsize = 12)
ax.set_xlabel('Cummulative Score',ha='center', labelpad = 20, fontsize = 12)
ax.set_title(f'Top 5 Cuisines with the Highest Cummulative Score from {date_range}',pad = 12, fontsize = 20)
st.pyplot(fig, use_container_width = True)
