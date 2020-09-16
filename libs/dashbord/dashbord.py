import dash,os,pandas
import dash
import dash_core_components as dcc
import dash_html_components as html

df=pandas.read_csv("mojobol_data.csv")





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

app = dash.Dash(__name__, external_stylesheets=external_stylesheets)

app.layout = html.Div([
    html.H4(children='Mojobol data'),
    generate_table(df)
,dcc.Dropdown(
                id='crossfilter-xaxis-column',
                options=[{'label': i, 'value': i} for i in df.columns],
                value='time'
            )
  
            
            
 ] )

 @app.callback(
    dash.dependencies.Output('x-time-series', 'figure'),
    [dash.dependencies.Input('crossfilter-xaxis-column', 'hoverData')
    ])
if __name__ == '__main__':
    app.run_server(debug=True)

