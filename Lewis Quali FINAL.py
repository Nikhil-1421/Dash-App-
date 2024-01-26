#!/usr/bin/env python
# coding: utf-8

# In[1]:


# Installing Dash

get_ipython().system('pip install dash')


# In[2]:


# Importing all the necessary libraries for this project 

from dash import Dash, html, dcc, callback, Output, Input
import plotly.express as px
import pandas as pd
import numpy as np
from dash import jupyter_dash
jupyter_dash.default_mode="external"


# In[3]:


# Creating a new dataframe from the the csv file stored in the GitHub repository

df = pd.read_csv('https://raw.githubusercontent.com/Nikhil-1421/Visualization-Interactive-Dashboard/main/output.csv?token=GHSAT0AAAAAACNIINFAZNULWRKMW4OAHZXEZNSXDDQ')


# In[4]:


# Getting a glimpse at the dataframe 

df.head()


# In[5]:


# Checking what kinds of data types are within each column 

df.dtypes


# In[6]:


# Replacing any missing values (stored as '\N') with 0:00.000 format

NTC = ['q1','q2','q3']
df[NTC] = df[NTC].replace(r'\N','0:00.000')
pd.set_option('display.max_columns', None)
pd.set_option('display.max_rows', None)
pd.set_option('display.width', None)
df[NTC]


# In[7]:


# Converting the 'year' column to numeric type and then sorting the dataframe to display by year

df['year'] = pd.to_numeric(df['year'])
df = df.sort_values(by='year')


# In[8]:


# Writing a function that will take our object type lap time values and store them as float values with 3 decimal places, this will help to plot the lap times per qualifying session

def convert_time_columns_to_float(df, time_columns):
    for col in time_columns:
        df[col] = df[col].apply(lambda x: float(x.split(':')[0])*60 + float(x.split(':')[1]) + float('0.' + x.split('.')[1]) if pd.notnull(x) else x)
    return df


# In[9]:


# Running the function and viewing the output  

convert_time_columns_to_float(df,NTC)


# In[10]:


# Creatinga function that will output the laptimes in the standard minutes:seconds.milliseconds format

def time2(time_in_seconds):
        time_in_seconds = float(time_in_seconds)
        minutes = int(time_in_seconds // 60)
        seconds = int(time_in_seconds % 60)
        milliseconds = int((time_in_seconds - int(time_in_seconds)) * 1000)
        formatted_time = f'{minutes:02d}:{seconds:02d}.{milliseconds:03d}'     
        return formatted_time


# In[11]:


# Creating the dashboard 
app = Dash(__name__)

#Using a function to serve_layout so that the dashboard will continuously update 
def serve_layout():
    return html.Div([
        html.H1(children='Lewis Hamilton Qualifying Performances',
               style={
                   'textAlign':'center'
               }),
        html.H3('Grand Prix',
               style={
                   'textAlign':'center'
               }),
        dcc.Dropdown(options=[
            {'label':gp, 'value': gp} for gp in df['Grand Prix'].unique()
        ],
                    value=df['Grand Prix'].unique()[0],
                    id='gpd'
                    ),
        html.H3('Year',
               style={
                   'textAlign':'center'
               }),
        dcc.Slider(
        min=df['year'].min(),
        max=df['year'].max(),
        step=1,
        value=df['year'].min(),
        id='year-slider',
        marks={int(year): {'label': str(year)} for year in df['year'].unique()}
        ),
        html.Div(id='scatter-plot'),
        html.H3(id='position-info',
                style={
                    'textAlign':'center'
                })
    ])

# Creating the callback that will update the scatter plot as different dropdown items and slider items are selected
@app.callback([
    Output('scatter-plot','children'),
    [Input('gpd','value'),
    Input('year-slider','value')]
])

# Writing a function to update the scatter plot based on the selected inputs 
def usp(selected_gp,selected_yr):
    fdf=df[(df['Grand Prix'] == selected_gp) & (df['year'] == selected_yr)]
    mfdf=pd.melt(fdf, id_vars=['Grand Prix','year'], value_vars=['q1','q2','q3'],
                var_name='Lap Type', value_name='Lap Time')

    fig=px.scatter(mfdf,
                  x='Lap Type',
                  y='Lap Time',
                  labels={
                      'Lap Type':'Qualifying Session',
                      'Lap Time':'Lap Time in Seconds'
                  },
                  hover_data={
                      'Lap Type': False,
                      'Lap Time': False
                  })
    
    fig.update_xaxes(tickvals=['q1', 'q2', 'q3'], ticktext=['Q1', 'Q2', 'Q3'])

    mfdf['Formatted Time'] = mfdf['Lap Time'].apply(time2)
    
    fig.update_traces(text=mfdf['Formatted Time'], mode='markers+text', textposition='top center')
    
    if mfdf.empty:
        return [html.H1('Looks like Lewis wasnt here!', style={'textAlign':'center'})]
    else:
        return [dcc.Graph(figure=fig)]
    
# Creating the callback that will output the result of the displayed scatter plot 
@app.callback([
    Output('position-info','children'),
    [Input('gpd','value'),
    Input('year-slider','value')]
])

# Writing a function that will update based on the finishing position, and will update based on whether or not a qualifying session was achieved by Lewis
def uppos(selected_gp,selected_yr):
    if df[(df['Grand Prix'] == selected_gp) & (df['year'] == selected_yr)].empty:
        return [f'Either the {selected_gp} did not take place in {selected_yr} or Lewis did not participate']
    
    else:
        position = df[(df['Grand Prix'] == selected_gp) & (df['year'] == selected_yr)]['position'].values[0]
        q1p = [16,17,18,19,20]
        q2p = [11,12,13,14,15]
        q3p = [1,2,3,4,5,6,7,8,9,10]
        if position in q1p:
            return [f'Lewis failed to reach Q2, Qualifying P{position} at the {selected_yr} {selected_gp}']
        else:
            if position in q2p:
                return [f'Lewis failed to reach Q3, Qualifying P{position} at the {selected_yr} {selected_gp}']
            else:
                if position in q3p:
                    return [f'Qualified P{position} at the {selected_yr} {selected_gp}']
                
# Using the serve_layout from before to initialize the app         
app.layout = serve_layout

if __name__ == '__main__':
    app.run(debug=True, port=8060)


# In[ ]:




