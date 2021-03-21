import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import plotly.offline as pyo
import plotly.graph_objects as go #geographical heat maps
import dash
import dash_html_components as html 
import dash_core_components as dcc 
from dash.dependencies import Input, Output
from datetime import datetime

global source
source = "http://data.humdata.org/hxlproxy/data/download/time_series_covid19_deaths_global_iso3_regions.csv?dest=data_edit&filter01=merge&merge-url01=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid%3D1326629740%26single%3Dtrue%26output%3Dcsv&merge-keys01=%23country%2Bname&merge-tags01=%23country%2Bcode%2C%23region%2Bmain%2Bcode%2C%23region%2Bmain%2Bname%2C%23region%2Bsub%2Bcode%2C%23region%2Bsub%2Bname%2C%23region%2Bintermediate%2Bcode%2C%23region%2Bintermediate%2Bname&filter02=merge&merge-url02=https%3A%2F%2Fdocs.google.com%2Fspreadsheets%2Fd%2Fe%2F2PACX-1vTglKQRXpkKSErDiWG6ycqEth32MY0reMuVGhaslImLjfuLU0EUgyyu2e-3vKDArjqGX7dXEBV8FJ4f%2Fpub%3Fgid%3D398158223%26single%3Dtrue%26output%3Dcsv&merge-keys02=%23adm1%2Bname&merge-tags02=%23country%2Bcode%2C%23region%2Bmain%2Bcode%2C%23region%2Bmain%2Bname%2C%23region%2Bsub%2Bcode%2C%23region%2Bsub%2Bname%2C%23region%2Bintermediate%2Bcode%2C%23region%2Bintermediate%2Bname&merge-replace02=on&merge-overwrite02=on&tagger-match-all=on&tagger-01-header=province%2Fstate&tagger-01-tag=%23adm1%2Bname&tagger-02-header=country%2Fregion&tagger-02-tag=%23country%2Bname&tagger-03-header=lat&tagger-03-tag=%23geo%2Blat&tagger-04-header=long&tagger-04-tag=%23geo%2Blon&header-row=1&url=https%3A%2F%2Fraw.githubusercontent.com%2FCSSEGISandData%2FCOVID-19%2Fmaster%2Fcsse_covid_19_data%2Fcsse_covid_19_time_series%2Ftime_series_covid19_deaths_global.csv"

death = pd.read_csv(source)
death_1=death.drop(['Province/State','Lat','Long','Region Code','Region Name','Sub-region Code','Sub-region Name','Intermediate Region Code','Intermediate Region Name'],axis=1)
death_1=death_1.rename(columns={"ISO 3166-1 Alpha 3-Codes":"CODE"})
death_1=death_1.rename(columns={"Country/Region":"Country"})
sum_columns=list(death_1.select_dtypes(include=['float']).columns.values)
date=[str(datetime.strptime(i,'%m/%d/%y')) for i in sum_columns]
date1=[str(date[:10]) for date in date]
death_1=death_1.rename(columns=dict(zip(sum_columns,date1)))

death_1=death_1.iloc[1:,:]
death_1=death_1.groupby(['Country','CODE'])[date1].sum().reset_index()
#Creating a copy of dataframe for future usage
death_2=death_1.copy(deep=True)
shape=list(death_1.shape)
y=shape[1]
#print(death_1.iloc[:,:y-1])

#loop function to calculate the death cases individual day wise

for i in range(y-1,2,-1):
    a=i-1
    death_1.iloc[:,i] = death_1.iloc[:,i]-death_1.iloc[:,a]

death_1['Total']=death_2.iloc[:,-1]
y=list(death_1.shape)
shape1=y[1]

column_name = list(death_1.columns)
column_names = column_name[2:shape1]

y1=list(death_2.shape)

death_1_long = pd.DataFrame(columns=['Date','Country','Death'])

death_1_listdic=[]

for i in range(2,y[1]-1,1):
    for j in range(0,y[0],1):
        death_1_listdic.append({'Date':str(death_1.columns[i]),'Country':death_1.at[j,'Country'],'Death':death_1.iloc[j,i]})
        
death_1_long=death_1_long.append(death_1_listdic)
death_1_long['Date']=pd.to_datetime(death_1_long['Date']).dt.strftime("%Y-%m-%d")

death_2_long = pd.DataFrame(columns=['Date','Country','Death'])

death_2_listdic=[]

for i in range(2,y1[1],1):
    for j in range(0,y1[0],1):
        death_2_listdic.append({'Date':str(death_2.columns[i]),'Country':death_2.at[j,'Country'],'Death':death_2.iloc[j,i]})
        
death_2_long=death_2_long.append(death_2_listdic)
death_2_long['Date']=pd.to_datetime(death_2_long['Date']).dt.strftime("%Y-%m-%d")


plots=  ['equirectangular', 'mercator', 'orthographic', 'natural earth', 'kavrayskiy7', 'miller', 'robinson', 'eckert4',
            'azimuthal equal area', 'azimuthal equidistant', 'conic equal area', 'conic conformal', 'conic equidistant',
            'gnomonic', 'stereographic', 'mollweide', 'hammer',
            'transverse mercator', 'albers usa', 'winkel tripel',
            'aitoff', 'sinusoidal']

date_columns=list(death_1.select_dtypes(include=['float']).columns.values)

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']

app=dash.Dash(__name__,external_stylesheets=external_stylesheets)

fig1={}

colors = {
    'background': 'Black',
    'text': 'White'
}

def generate_table(dataframe):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(len(dataframe))
        ])
    ])

app.layout=html.Div([
    html.H1('Corona virus death cases dashboard',
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    html.H5("Data Source: https://data.humdata.org/dataset/novel-coronavirus-2019-ncov-cases",
        style={
            'textAlign': 'center',
            'color': colors['text']
        }),
    html.Div([
        html.H3('Total Death cases: '+"{:,}".format(int(death_2.iloc[:,-1].sum())),
        style={
        'textAlign': 'center',
        'color': colors['text']})
    ]),
    html.Div([
    html.Div([
         dcc.Dropdown(
        id='type-dropdown',
        options=[{'label':str(i),'value':i} for i in ['individual_date','continuous_growth']],
        value='individual_date'
                    )
    ],style={'width':'10%','display':'inline-block'}),
    html.Div([
    dcc.Dropdown(
    id='date-dropdown',
    options=[{'label':str(i),'value':i} for i in death_1_long['Date'].unique()],
    value=date1[0]
                )
    ],style={'width':'10%','display':'inline-block'}),
    html.Div([
         dcc.Dropdown(
        id='top-dropdown',
        options=[{'label':i,'value':int(i)} for i in range(5,51,5) ],
        value=int(5)
                    )
    ],style={'width':'10%','display':'inline-block'}),
    html.Div([
         dcc.Dropdown(
        id='graph-dropdown',
        options=[{'label':i,'value':i} for i in plots ],
        value=plots[0]
                    )
    ],style={'width':'10%','display':'inline-block'})],style={'width':'100%'}),
    html.Div([
    html.Div([
    dcc.Graph(
        id = 'date_wise')],style={'width':'50%','display':'inline-block'}),
    html.Div([
    dcc.Graph(
        id = 'top_countries')],style={'width':'50%','display':'inline-block'})],style={'width':'100%'}),
    html.Div([
    dcc.Dropdown(
    id='country-dropdown',
    options=[{'label':str(i),'value':i} for i in death_1_long['Country'].unique()],
    value='India'
                )
    ],style={'width':'20%','display':'inline-block'}),
    html.Div([
        dcc.Graph(
            id='line-trends')],style={'width':'100%'})
    ], style={'backgroundColor': colors['background']})

@app.callback(Output(component_id='date_wise',component_property='figure'),
            [Input(component_id='date-dropdown',component_property='value'),
            Input(component_id='graph-dropdown',component_property='value'),
            Input(component_id='type-dropdown',component_property='value')])
def set_plot(date,plotType,type):
    
    if type == 'individual_date':
        death_viz=death_1.copy(deep=True)

        death_viz['text'] = death_viz['Country'].astype(str) + '('  + 'code:' + death_viz['CODE'].astype(str)+ ')' + '<br>' \
                    'count: ' + death_viz[date].astype(str)

        trace = go.Choropleth(locations=death_viz['CODE'],z=death_viz[date],text=death_viz['Country'],autocolorscale=False,
                          colorscale="redor",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.7,"x": 1.3,"y": 0.4,
                                    'title': {"text":"Death cases", "side": "top"}})

        fig = {"data": [trace],
            "layout": go.Layout(title="Corona cases - "+str(date),plot_bgcolor=colors['background'],paper_bgcolor=colors['background'],font={'color':colors['text']},
             autosize=True,hovermode='closest',margin=dict(t=-0, b=0, l=0, r=0),geo={'bgcolor':'rgba(0,0,0,0)','showframe': True,'showcoastlines': True,'oceancolor':'aqua', 'showocean':True, 'projection':{'type': plotType}})}

    if type == 'continuous_growth':
        death_viz=death_2.copy(deep=True)

        death_viz['text'] = death_viz['Country'].astype(str) + '('  + 'code:' + death_viz['CODE'].astype(str)+ ')' + '<br>' \
                    'count: ' + death_viz[date].astype(str)

        trace = go.Choropleth(locations=death_viz['CODE'],z=death_viz[date],text=death_viz['Country'],autocolorscale=False,
                          colorscale="redor",marker={'line': {'color': 'rgb(180,180,180)','width': 0.5}},
                          colorbar={"thickness": 10,"len": 0.7,"x": 1.3,"y": 0.4,
                                    'title': {"text":"Death cases", "side": "top"}})

        fig = {"data": [trace],
            "layout": go.Layout(title="Corona cases - "+str(date),plot_bgcolor=colors['background'],paper_bgcolor=colors['background'],font={'color':colors['text']},
             autosize=True,hovermode='closest',margin=dict(t=-0, b=0, l=0, r=0),geo={'bgcolor':'rgba(0,0,0,0)','showframe': True,'showcoastlines': True,'oceancolor':'aqua', 'showocean':True, 'projection':{'type': plotType}})}

    return fig


@app.callback(Output(component_id='top_countries',component_property='figure'),
            [Input(component_id='date-dropdown',component_property='value'),
            Input(component_id='type-dropdown',component_property='value'),
            Input(component_id='top-dropdown',component_property='value')])
def top_plot(Date,type,positions):
    global fig1

    if type == 'individual_date':
        country_wise_ind=death_1_long.groupby(['Date','Country'])['Death'].sum().reset_index().sort_values(by=['Death','Date'],ascending=False)
        country_wise_viz=country_wise_ind.loc[country_wise_ind['Date']==Date]
        country_wise_viz=country_wise_viz.head(positions)
        data = go.Bar(x=country_wise_viz['Country'],y=country_wise_viz['Death'])
        #fig.add_trace(go.Scatter(x=country_wise_viz["Date"],y=country_wise_viz["Death"],name="trend"))
        layout = go.Layout(title="top "+str(positions)+" countries affected on "+str(Date)+"("+type+")",hovermode='closest',plot_bgcolor=colors['background'],paper_bgcolor=colors['background'],font={'color':colors['text']},xaxis={'title':'Countries'},yaxis={'title':'Death_cases'})
        fig1 = go.Figure(data=data, layout=layout)

            
    if type == 'continuous_growth':
       # Date=datetime.strptime(Date[:10],'%Y-%m-%d')
        country_wise_cont=death_2_long.groupby(['Date','Country'])['Death'].sum().reset_index().sort_values(by=['Death','Date'],ascending=False)
        country_wise_viz=country_wise_cont.loc[country_wise_cont['Date']==Date]
        country_wise_viz=country_wise_viz.head(positions)
        data = go.Bar(x=country_wise_viz['Country'],y=country_wise_viz['Death'])
        #fig.add_trace(go.Scatter(x=country_wise_viz["Date"],y=country_wise_viz["Death"],name="trend"))
        layout = go.Layout(title="top "+str(positions)+" countries affected on "+str(Date)+"("+type+")",hovermode='closest',plot_bgcolor=colors['background'],paper_bgcolor=colors['background'],font={'color':colors['text']},xaxis={'title':'Countries'},yaxis={'title':'Death_cases'})
        fig1 = go.Figure(data=data, layout=layout)

    return fig1

@app.callback(Output(component_id='line-trends',component_property='figure'),
            [Input(component_id='type-dropdown',component_property='value'),
            Input(component_id='country-dropdown',component_property='value')])
def top_plot(type,country_list):

    if type == 'individual_date':
        country_wise_ind=death_1_long.groupby(['Date','Country'])['Death'].sum().reset_index()
        country_wise_viz=country_wise_ind.loc[country_wise_ind['Country']==country_list].sort_values(by=['Date'],ascending=True)
        data = go.Scatter(x=country_wise_viz["Date"], y=country_wise_viz["Death"],mode='lines+markers',marker={'size':8,'symbol':'pentagon'},line=dict(color='Red'))
        layout=go.Layout(title='Covid death cases date wise in '+country_list,hovermode='closest',plot_bgcolor=colors['background'],paper_bgcolor=colors['background'],font={'color':colors['text']},xaxis={'title':'Date','showgrid':False},yaxis={'title':'Death Cases','showgrid':False})
        fig2 = go.Figure(data=data,layout=layout)

            
    if type == 'continuous_growth':
       # Date=datetime.strptime(Date[:10],'%Y-%m-%d')
        country_wise_ind=death_2_long.groupby(['Date','Country'])['Death'].sum().reset_index()
        country_wise_viz=country_wise_ind.loc[country_wise_ind['Country']==country_list].sort_values(by=['Date'],ascending=True)
        data = go.Scatter(x=country_wise_viz["Date"], y=country_wise_viz["Death"],mode='lines+markers',marker={'size':8,'symbol':'pentagon'},line=dict(color='Red'))
        layout=go.Layout(title='Covid death cases date wise in '+country_list,hovermode='closest',plot_bgcolor=colors['background'],paper_bgcolor=colors['background'],font={'color':colors['text']},xaxis={'title':'Date','showgrid':False},yaxis={'title':'Death Cases','showgrid':False})
        fig2 = go.Figure(data=data,layout=layout)

    return fig2


if __name__ == '__main__':
    app.run_server()


