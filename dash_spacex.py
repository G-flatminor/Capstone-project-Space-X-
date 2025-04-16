# Import required libraries
import pandas as pd
import plotly.graph_objects as go
import dash
from dash import dcc
from dash import html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df =  pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv')


# Create a dash application
app = dash.Dash(__name__)

# Get unique launch sites for dropdown options
site_options = [{'label': 'All Sites', 'value': 'ALL'}] + \
               [{'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()]

min_payload = spacex_df['Payload Mass (kg)'].min()
max_payload = spacex_df['Payload Mass (kg)'].max()


# Build dash app layout
app.layout = html.Div(children=[html.H1('Space X Launch Data',
                                         style={'textAlign':'center','color':'#503D36','font-size':30}),
                                
                                html.Div([dcc.Dropdown(id='site-dropdown',
                                                    options=site_options,
                                                    value='ALL',
                                                    placeholder="Select a Launch Site",
                                                    searchable=True
                                                    )], style={'width': '60%', 'padding': '20px'}),
                                
                                html.Br(),

                                dcc.RangeSlider(id='payload-slider',
                                                        min=min_payload, max=max_payload, step=1000,
                                                        marks={int(min_payload): str(int(min_payload)), int(max_payload): str(int(max_payload))},
                                                        value=[min_payload, max_payload]),

                                html.Br(),

                                dcc.Graph(id='success-pie'),

                                html.Br(),
                             
                                dcc.Graph(id='success-payload-scatter-chart')
                            ])

# Callback decorator
@app.callback([
               Output(component_id='success-pie', component_property='figure'),
               Output(component_id='success-payload-scatter-chart', component_property='figure'),
               ],
               [Input(component_id='site-dropdown', component_property='value'), 
                Input(component_id="payload-slider", component_property="value"),
                ]
            )

def update_charts(selected_site, payload_range):

    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & 
                            (spacex_df['Payload Mass (kg)'] <= high)]


    # Select data
    if selected_site == 'ALL':
        pie_df = filtered_df[filtered_df['class'] == 1]
        pie_fig = px.pie(pie_df,
                        names='Launch Site',
                        #value='class',
                        title='Total Successful Launches by Site')
        
        
        bar_fig = px.scatter(filtered_df,
                         x='Payload Mass (kg)', y='class',
                         color='Launch Site',
                         title='Payload vs Outcome for All Sites')
        
        return pie_fig, bar_fig
    
    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        pie_fig = px.pie(filtered_df,
                        names = 'class',
                        title=f'Success vs Failure for {selected_site}')
        
        bar_fig = px.scatter(filtered_df,
                        x='Payload Mass (kg)',
                        y='class',
                        title=f'Launch Outcome by Payload Mass for {selected_site}')

        return pie_fig, bar_fig


# Run the app
if __name__ == '__main__':
    app.run(debug = True)

