import pandas as pd

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px #(need to pip install plotly==4.4.1)

df = pd.read_csv("mojobol_data.csv",index_col='call_id')
def generate_table(dataframe, max_rows=10):
    return html.Table([
        html.Thead(
            html.Tr([html.Th(col) for col in dataframe.columns])
        ),
        html.Tbody([
            html.Tr([
                html.Td(dataframe.iloc[i][col]) for col in dataframe.columns
            ]) for i in range(min(len(dataframe), max_rows))
        ])
    ])

external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']    
# you need to include __name__ in your Dash constructor if
# you plan to use a custom CSS or JavaScript in your Dash apps
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

#---------------------------------------------------------------
app.layout = html.Div([
    html.Div([
        html.H1(['Mojobol Data']),
        generate_table(df),
        dcc.Dropdown(
            id='my_dropdown',
            options=
                     [{'label': i, 'value': i} for i in df.columns]
            ,
            value='caller_id',
            multi=False,
            clearable=False,
            style={"width": "50%"}
        ),
    ]),

    html.Div([
        dcc.Graph(id='the_graph')
    ]), 
])

#---------------------------------------------------------------
@app.callback(
    Output(component_id='the_graph', component_property='figure'),
    [Input(component_id='my_dropdown', component_property='value')]
)

def update_graph(my_dropdown):
   
    
    if my_dropdown=="call_length":
        dff = df[[my_dropdown]]
        timedata=px.bar(data_frame=dff,x=df.index.values,y="call_length")
        return(timedata)



    else:
        dff = df[my_dropdown]    
        piechart=px.pie(
            data_frame=dff,
            names=my_dropdown,
            hole=.3,
            )

    return (piechart)


if __name__ == '__main__':
    app.run_server(debug=True)