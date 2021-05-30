
import mysql.connector
from mysql.connector import Error
import pandas as pd

import plotly.express as px  # (version 4.7.0)
import plotly.graph_objects as go

from jupyter_dash import JupyterDash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output

import mysql.connector
from mysql.connector import Error


def create_db_connection(host_name, user_name, user_password, db_name):
    connection = None
    try:
        connection = mysql.connector.connect(
            host=host_name,
            user=user_name,
            passwd=user_password,
            database=db_name,
            port=3307
        )
        print("MySQL Database connection successful")
    except Error as err:
        print(f"Error: '{err}'")

    return connection

def read_query(connection, query):
    cursor = connection.cursor()
    result = None
    try:
        cursor.execute(query)
        result = cursor.fetchall()
        return result
    except Error as err:
        print(f"Error: '{err}'")

def get_estrato(estrato,promedio):
    if estrato=='Estrato 1':
        promedio[0]+=1
    elif estrato=='Estrato 2':
        promedio[1]+=1
    elif estrato=='Estrato 3':
        promedio[2]+=1
    else:
        promedio[3]+=1
        
    return promedio

def get_range(dfA):
    promedioA=[0,0,0,0]
    promedioB=[0,0,0,0]
    promedioC=[0,0,0,0]
    promedioD=[0,0,0,0]

    for i in range(len(dfA)):
        puntaje=dfA.loc[i,'puntaje']
        if puntaje>=100 and puntaje<=200:
            estrato=dfA.loc[i,'estrato']
            promedioA= get_estrato(estrato,promedioA)
        elif puntaje>=201 and puntaje<=300:
            estrato= dfA.loc[i,'estrato']
            promedioB= get_estrato(estrato,promedioB)
        elif puntaje>=301 and puntaje<=400:
            estrato=dfA.loc[i,'estrato']
            promedioC= get_estrato(estrato,promedioC)
        elif puntaje>=401 and puntaje<=500:
            estrato=dfA.loc[i,'estrato']
            promedioD= get_estrato(estrato,promedioD)
                
    
    return promedioA,promedioB,promedioC,promedioD

def get_pastel(rango):
    dicc={
        'estrato':estrato,
        'total':tot[rango]
    }
    
    df_pastel = pd.DataFrame(dicc, columns = ['estrato', 'total'])
    return df_pastel


connection = create_db_connection("testdb_mysql", "user", 'password','ICFES')



res=read_query(connection, "select * from Datos")
df= pd.DataFrame(res,columns=['id','departamento','estrato','internet','puntaje'])


df_median=df.groupby(['departamento','estrato'])[['puntaje']].mean()
df_median.reset_index(inplace=True)


df_internet=df.groupby(['internet','estrato'])[['puntaje']].mean()
df_internet.reset_index(inplace=True)
df_internet=df_internet.drop(df_internet.index[[6,13]])


connection.close()


tot = get_range(df)
estrato=['Estrato 1','Estrato 2','Estrato 3','Estrato 4']




import plotly.graph_objects as go

app = JupyterDash(__name__)

# ------------------------------------------------------------------------------
# App layout
app.layout = html.Div([

    html.H1("Web Application Dashboards with Dash", style={'text-align': 'center'}),

    dcc.Dropdown(id="slct_range",
                 options=[
                     {"label": "100-200", "value": 0},
                     {"label": "201-300", "value": 1},
                     {"label": "301-400", "value": 2},
                     {"label": "401-500", "value": 3}],
                 multi=False,
                 value=0,
                 style={'width': "40%"}
                 ),
    dcc.Graph(id='pie-chart', figure={}),
    dcc.Dropdown(id="slct_estrato",
                 options=[
                     {"label": "Estrato 1", "value": 'Estrato 1'},
                     {"label": "Estrato 2", "value": 'Estrato 2'},
                     {"label": "Estrato 3", "value": 'Estrato 3'},
                     {"label": "Estrato 4", "value": 'Estrato 4'},
                     {"label": "Estrato 5", "value": 'Estrato 5'}],
                 multi=False,
                 value='Estrato 1',
                 style={'width': "40%"}
                 ),
    dcc.Graph(id='scatter-plot', figure={}),
    dcc.Graph(id='horizontal-plot', figure={})
    

])

# ------------------------------------------------------------------------------
# Connect the Plotly graphs with Dash Components

@app.callback(
    Output("pie-chart", "figure"), 
    [Input("slct_range", "value")])
def generate_chart(option_value):
    fig = px.pie(get_pastel(option_value), values='total',names='estrato')
    return fig
    
    
@app.callback(
    Output("scatter-plot", "figure"), 
    [Input("slct_estrato", "value")])
def update_bar_chart(slct_estrato):  
    df_aux=df_median.loc[df_median['estrato'] == slct_estrato]
    fig = px.scatter(df_aux, x='departamento', y='puntaje', color='estrato')
    return fig

@app.callback(
    Output("horizontal-plot", "figure"), 
    [Input("slct_estrato", "value")])
def update_bar_chart(slct_estrato):  
#     fig = px.bar(df_internet, x="puntaje", y="internet", orientation='h',height=100)
    fig = px.line(df_internet, x='estrato', y='puntaje', color='internet')
    return fig


# ------------------------------------------------------------------------------
if __name__ == '__main__':
      app.run_server(host='localhost', port=8080, debug=True)
        