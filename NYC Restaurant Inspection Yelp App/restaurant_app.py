import streamlit as st 
import pandas as pd 
import numpy as np
from datetime import datetime, date
import matplotlib.pyplot as plt
import seaborn as sns
import folium 
from streamlit_folium import folium_static



#Page setting 
st.set_page_config(page_title = 'NYC Restaurant Inspection App', page_icon = '🍽️',layout = 'wide')

#title 
st.title("NYC Restaurant Inspection")



menu_options = ['Find Restaurants', 'Cuisine Detector']
options = st.sidebar.selectbox('Menu', menu_options)

if options == 'Find Restaurants':

# Introduction 

    st.header('Introduction')
    with st.expander('Click to expand'): 
        st.write(
    "An average of 56% Americans eat out about 2-3 times a week revealed in a [survey.](https://www.fourth.com/resource/truth-about-dining-out-infographic/)"   
    )
        st.markdown(
        'Statistics released by [CDC](https://www.cdc.gov/foodsafety/foodborne-germs.html) indicates roughly every year around "48 million individuals get sick" from foodborne illnesses. This dashboard aims to give awareness to the public on how restaurants in NYC are scored and graded in terms of food safety.'
    )



##Create map 
    st.header('Restaurant Viewer')
# Load Df for Map
# 
    @st.cache

    def read_file(csv_file): 
        return pd.read_csv(csv_file)

    map_df = read_file('map.csv')
    #map_df['inspection_date'] = pd.to_datetime(map_df['inspection_date'])
    #map_df['inspection_date'] = map_df['inspection_date'].dt.year
    #map_df.drop_duplicates(subset = ['inspection_date', 'camis', 'dba', 'Score'], inplace = True)

# load df to select longitude and latitude 
 

#create filters 

    with st.form(key = 'map'): 
        mask1, mask2, mask3, mask4 = st.columns(4)
        with mask1:
            year_list = map_df['inspection_date'].unique().tolist()
            year_list.sort(reverse = False)
            year_range = st.selectbox('Inspection Year', year_list, index = 0, key = "map")

        with mask2: 
    #which cuisines 
            cuisine_list = map_df['cuisine_description'].unique().tolist()
            cuisine_list.sort(reverse = False)
            cuisine_picker = st.multiselect('Cuisine', cuisine_list)
        with mask3:
     #which grade 
            grade_list = map_df['grade'].unique().tolist()
            grade_list.sort(reverse = False)
            grade_picker = st.multiselect('Grade', grade_list)  

        with mask4:
    #which score range
            score_list = map_df['score'].sort_values().unique()
            score_min = score_list.min()
            score_max= score_list.max()
            score_picker = st.select_slider('Score Range', value = (score_min, score_max), options = score_list) 
            score_right, score_left = score_picker[0], score_picker[1]
    
        submit_bt = st.form_submit_button()
    ## update map_df 
        map_df = (map_df[(map_df['inspection_date']== year_range)])
        map_df = (map_df[(map_df['cuisine_description'].isin(cuisine_picker))])
        map_df = (map_df[(map_df['grade'].isin(grade_picker))])
        map_df = (map_df[(map_df["score"] <= score_left) & (map_df['score'] >= score_right)]) 
        map_df.reset_index(drop=True, inplace=True)


        if len(map_df) == 0:
            st.error('Please try again. This combination yields no results.')
            error_map = folium.Map(location = [40.72949735852703, -73.94232410274962], 
                           zoom_start= 8, max_zoom =10, tiles = "OpenStreetMap")
            load_error_map = folium_static(error_map)
        else: 
        #st.write(map_df)
            latitude_center = map_df['latitude'].mean()
            longitude_center = map_df['longitude'].mean()
    #location_list = map_df[['latitude', 'longitude']].values.tolist()
            m= folium.Map(location = [latitude_center, longitude_center], 
                   zoom_start = 12, tiles = "OpenStreetMap")
    #create color coded markers based on grade level 

            for i in range (0,len(map_df)): 
                grade_level = map_df['grade'].iloc[i]
                if grade_level == 'A': 
                    color = 'blue'
                elif grade_level == 'B': 
                    color = 'orange'
                elif grade_level == 'C': 
                    color = 'red'
                elif grade_level == 'Grade Pending': 
                    color = 'lightblue'
                elif grade_level == 'Grade pending resulted in a closure ': 
                    color = 'pink'
                elif grade_level == 'Missing Grade': 
                    color = 'darkpurple'
                else: 
                    color = 'gray'

            #create popup text 
                cuisine_type = map_df['cuisine_description'].iloc[i]
                address_ = map_df['address'].iloc[i]
                name_dba = map_df['dba'].iloc[i]
                score_num = map_df['score'].iloc[i]

                html_text = f"""
            <!DOCTYPE html>
            <html>
            <head>
            <h4 style = "margin-bottom:10"; width = "200px">Name: {name_dba}</h4>
            <h4 style = "margin-bottom:10"; width = "200px">Cuisine: {cuisine_type}</h4>
            <h4 style = "margin-bottom:10"; width = "200px">Address: {address_}</h4>
            <h4 style = "margin-bottom:10"; width = "200px">Grade: {grade_level}</h4>
            <h4 style = "margin-bottom:10"; width = "200px">Score: {score_num}</h4>
            </html>
            """
                iframe = folium.IFrame(html = html_text,
                           width = 300,
                           height = 200)
 
                popup_create = folium.Popup(iframe, min_width = 300, max_width = 500)
            #create marker
                folium.Marker(
                location = [map_df['latitude'].iloc[i], map_df['longitude'].iloc[i]], 
                icon = folium.Icon(color = color, icon  = 'fa-cutlery', prefix = 'fa'),
                popup= popup_create).add_to(m)
            load_map = folium_static(m)
            st.text(f'Loaded {len(map_df)} results.')

else: 

#Load df for Barplot 
    @st.cache

    def read_file(csv_file): 
        return pd.read_csv(csv_file)

    cuisine_df = read_file('cuisine.csv')
    #cuisine_df['inspection_date'] = cuisine_df['inspection_date'].dt.year
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

