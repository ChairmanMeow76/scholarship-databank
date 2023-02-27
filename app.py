import streamlit as st
import pandas as pd
from os import listdir
from os.path import join 
from json import load
import plotly.express as px

st.set_page_config(page_title='Scholarship Dumpster', layout= 'wide')

@st.cache_resource
def get_scholarship_data():
    return {
        'scholarships': pd.read_csv('data/scholarships.csv'),
        'deadlines': pd.read_csv('data/deadlines.csv'),
        'disciplines': pd.read_csv('data/disciplines.csv'),
        'levels': pd.read_csv('data/levels.csv'),
        'values': pd.read_csv('data/values.csv')
    }


@st.cache_resource
def get_geo_data():
    filenames = [country for country in listdir('countries') if 'geo.json' in country]
    countries = []
    for filename in filenames:
        with open(join('countries/',filename),'r') as f:
            countries.append(load(f)['features'][0])
    return countries


geo_data = get_geo_data()
df = get_scholarship_data()

st.header('Welcome to the scholarship hunter database')
st.markdown("""
    **Note**: some regions may not show on the map for different reasons(Europe: too big, Singapore: too small, Hong Kong: territory), but don't worry it will still show up on the table.
""")
st.markdown("""
    Multidisciplinary is set as default as it encompasses all other disciplines.
""")
st.markdown("""
    Unknown is set as default for country since it may overlap with your preference
""")
st.markdown("### Good luck")

country_preference = st.multiselect('country',df['scholarships'].host.unique(),default='Unknown')
deadline_preference = st.multiselect('deadline',df['deadlines'].deadline.unique())
discipline_preference = st.multiselect('discipline',df['disciplines'].discipline.unique(),default='Multidisciplinary')
level_preference = st.multiselect('level',df['levels'].study_level.unique())
value_preference = st.multiselect('value',df['values'].value.unique())

if len(country_preference) == 0 or country_preference == ['Unknown']:
    country_preference = df['scholarships'].host.unique()
if len(deadline_preference) == 0:
    deadline_preference = df['deadlines'].deadline.unique()
if len(discipline_preference) == 0 or discipline_preference == ['Multidisciplinary']:
    discipline_preference = df['disciplines'].discipline.unique()
if len(value_preference) == 0:
    value_preference = df['values'].value.unique()
if len(level_preference) == 0:
    level_preference = df['levels'].study_level.unique()





search_button = st.button('search')


if search_button:
    preferred_df = df['scholarships'][df['scholarships'].host.apply(lambda x: x in country_preference)]
    preferred_df.set_index(keys='scholarship_id',drop=True,inplace=True)
    
    deadline_match = df['deadlines'][df['deadlines'].deadline.apply(lambda x: x in deadline_preference)].groupby('scholarship_id')['deadline'].apply(
        lambda x: ', '.join(x)
    )
    discipline_match = df['disciplines'][df['disciplines'].discipline.apply(lambda x: x in discipline_preference)].groupby('scholarship_id')['discipline'].apply(
        lambda x: ', '.join(x)
    )
    level_match = df['levels'][df['levels'].study_level.apply(lambda x: x in level_preference)].groupby('scholarship_id')['study_level'].apply(
        lambda x: ', '.join(x)
    )
    value_match = df['values'][df['values'].value.apply(lambda x: x in value_preference)].groupby('scholarship_id')['value'].apply(
        lambda x: ', '.join(x)
    )

    preferred_df = preferred_df.join([deadline_match, discipline_match, level_match, value_match], how='inner', sort=True)
    
    choropleth_df = preferred_df.groupby(['country_id', 'host'])['country_id'].count()
    fig = px.choropleth(
        geojson=geo_data, 
        locations=[i[0] for i in choropleth_df.index], 
        color=choropleth_df.values,
        color_continuous_scale='Peach',
        hover_name=[i[1] for i in choropleth_df.index]
    )
    fig.update_geos(fitbounds="locations",visible=False)
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    
    st.plotly_chart(fig,use_container_width=True)
    st.write(preferred_df)




