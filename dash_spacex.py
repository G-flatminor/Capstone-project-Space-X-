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
    if selected_site == 'ALL':
        site_group = filtered_df.groupby('Launch Site')['class'].agg(['sum','count']).reset_index()
        site_group.columns = ['Launch Site', 'Success Count', 'Total Launches']
        site_group['Success Ratio'] = site_group['Success Count']/site_group['Total Launches']

    
        pie_fig = px.pie(site_group,
                        names='Launch Site',
                        values='Success Count',
                        title='Total Successful Launches by Site')

        # customdata = pie_data[['Count', 'Ratio']].to_numpy()
        pie_fig.update_traces(textinfo='none',
                            customdata=site_group[['Success Count', 'Success Ratio']],
                            texttemplate='%{customdata[0]}<br>%{customdata[1]:.2%}',
                            hovertemplate='Launch Site: %{label}<br>Success Count: %{customdata[0]}<br>Success Ratio: %{customdata[1]:.2%}')
        
        bar_fig = px.scatter(filtered_df,
                             x='Payload Mass (kg)', y='class',
                             color='Launch Site',
                             title='Payload vs Outcome for All Sites')
        return pie_fig, bar_fig



    else:
        filtered_df = filtered_df[filtered_df['Launch Site'] == selected_site]
        class_counts = filtered_df['class'].value_counts()
        total = class_counts.sum()
        ratio = class_counts / total

        pie_data = pd.DataFrame({
            'class': class_counts.index,
            'Count': class_counts.values,
            'Ratio': ratio.values
        })

        pie_fig = px.pie(pie_data,
                        names='class',
                        values='Count',
                        title=f'Success vs Failure for {selected_site}')

        customdata = pie_data[['Count', 'Ratio']].to_numpy()
        pie_fig.update_traces(textinfo='none',
                            customdata=customdata,
                            texttemplate='%{customdata[0]}<br>%{customdata[1]:.2%}',
                            hovertemplate='Outcome: %{label}<br>Count: %{customdata[0]}<br>Ratio: %{customdata[1]:.2%}')

        bar_fig = px.scatter(filtered_df,
                             x='Payload Mass (kg)', y='class',
                             title=f'Launch Outcome by Payload Mass for {selected_site}')
        return pie_fig, bar_fig




# Run the app
if __name__ == '__main__':
    app.run(debug = True)

