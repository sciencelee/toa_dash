from assets.fetch_data import *
import plotly.express as px

import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import numpy as np

import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State




zip_codes = pd.read_csv('assets/us-zip-code-latitude-and-longitude.csv', delimiter=';')
zip_codes.head()
zip_codes['Zip'] = zip_codes['Zip'].apply(lambda x: '{:05}'.format(x))
zip_codes.sort_values(by=['Zip'])
#active_teams['zip_code'] = active_teams['zip_code'].astype(int)
zip_codes.info()

zip_codes_crunch = zip_codes.groupby(['State', 'City']).mean()

#active_teams.merge(how='left', right=zip_codes, left_on='zip_code', right_on='Zip', validate='many_to_many').info()
# need something more like a lookup cest la vie
active_usa = active_teams[active_teams['country']=="USA"]
active_usa = active_usa.groupby(['state_prov', 'city'])['team_key'].apply(list).reset_index()

active_usa = active_teams[active_teams['country']=="USA"]
team_names = active_usa.groupby(['state_prov','city'])['team_name_short'].apply(list).reset_index()['team_name_short']
team_numbers = active_usa.groupby(['state_prov','city'])['team_key'].apply(list).reset_index()['team_key']

active_usa = active_usa.groupby(['state_prov','city']).mean().reset_index()

active_usa['team_names'] = team_names
active_usa['team_numbers'] = team_numbers

active_usa = active_usa.merge(how='left', right=zip_codes_crunch, left_on=['state_prov', 'city'], right_on=['State', 'City'])
active_usa['total_teams'] = active_usa['team_numbers'].apply(lambda x: len(x))
active_usa['header'] = active_usa.apply(lambda x: x.city + ',' + x.state_prov, axis=1)
active_usa['teams'] = active_usa.apply(lambda x: list(zip(x.team_numbers, x.team_names)), axis=1)
active_usa.head()
active_usa.info()


def ready_team_names(team_list):
    my_str = ''
    for team in team_list:
        my_str += ' '.join(team) + '<br>'
    return my_str


active_usa['teams'] = active_usa.teams.apply(ready_team_names)
active_usa.sort_values(by=['total_teams'], ascending=False)

#
# fig = px.scatter_geo(active_usa,
#                      lat="Latitude",
#                      lon='Longitude',
#                      color="total_teams",
#                      hover_name="header",
#                      hover_data={'teams':True,
#                                  'Latitude':False, 'Longitude': False},
#                      size='total_teams',
#                      #size_max=30,
#                      color_continuous_scale='Plotly3',
#                      opacity=0.7,
#                     )
#
# #fig.update_layout(mapbox_style="open-street-map",)
#
# fig.update_layout(
#         title_text = 'FTC Teams by City (USA only)',
#         showlegend = True,
#         geo = dict(
#             scope = 'usa',
#             landcolor = 'rgb(150, 150, 150)',
#         ),
#     )

print("HELLO")
plot_me = active_teams.groupby('country').count().reset_index()

high = plot_me['team_key'].max()
low = plot_me['team_key'].min()

plot_me['Total Teams (scaled)'] = plot_me['team_key'].apply(lambda x: (x - low) / high)
plot_me['Total Teams'] = plot_me['team_key']

fig = px.choropleth(data_frame=plot_me,
                    locations='country',
                    locationmode='country names',
                    color='Total Teams',
                    # hover_name='team_key',
                    # hover_data={'team_key':True,},
                    color_continuous_scale='Plasma',
                    # scope="world"
                    range_color=(0, 100),
                    )

fig.update_layout(
    coloraxis_colorbar=dict(
        title="Teams per Country",
    ),
    title_text='FIRST International Presence ({} countries)'.format(len(plot_me)),
)



# CREATE MY APP
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # default styling from tutorials
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


app.layout = html.Div([  # one big div for page
                        html.Div([
                            html.Button('Teams by Country', id='country', n_clicks=0),
                            html.Button('Teams by State', id='state', n_clicks=0),
                            html.Button('Teams by City', id='city', n_clicks=0),]
                            ),
                        html.Div(id='big', children='map goes here')# this is my div that contains my map.  look to css to change size etc.

                        ], style = {'height': '700'})

# dcc.Graph(id='map', figure=fig, style={"height": 700}),className='my-graph', id='big',),

# @app.callback(
#     Output('basic', 'children'),
#     Input('city', 'n_clicks'))
# def test(n_clicks):
#     return 'clicked {} times'.format(n_clicks)



#THIS IS A CALLBACK TO CHANGE MAP TO CITY
@app.callback(
    Output('big', 'children'),  # output goes to id:map and attribute:figure (which is my fig map)
    [Input('country', 'n_clicks'),
     Input('city', 'n_clicks'),
     Input('state', 'n_clicks')]
)
def change_map(bt1, bt2, bt3):
    '''
    My first callback with Dash.
    callback (INPUT) triggers this function
    function returns to the output location (in this case the Graph figure
    '''
    changed_id = [p['prop_id'] for p in dash.callback_context.triggered][0]
    if 'city' in changed_id:
        fig = px.scatter_geo(active_usa,
                             lat="Latitude",
                             lon='Longitude',
                             color="total_teams",
                             hover_name="header",
                             hover_data={'teams': True,
                                         'Latitude': False, 'Longitude': False},
                             size='total_teams',
                             # size_max=30,
                             color_continuous_scale='Plotly3',
                             opacity=0.7,
                             )

        # fig.update_layout(mapbox_style="open-street-map",)

        fig.update_layout(
            title_text='Active FTC Teams by City',
            showlegend=True,
            geo=dict(
                scope='usa',
                landcolor='rgb(150, 150, 150)',
            ),
        )

        return html.Div(dcc.Graph(figure=fig, style={"height": 700}))

    elif 'state' in changed_id:
        plot_active = active_teams.groupby(['state_prov']).count()[['team_key', 'zip_code', 'team_name_short']].reset_index()
        plot_active['State'] = plot_active['state_prov']
        plot_active['total_teams'] = plot_active['team_key']
        fig = px.choropleth(data_frame=plot_active,
                            locations='State',
                            locationmode="USA-states",
                            color='total_teams',
                            hover_name='State',
                            hover_data={'total_teams': True,
                                        'State': False, },
                            color_continuous_scale='Plotly3',
                            scope="usa")

        fig.update_layout(
            title_text='Active FTC Teams by State',
            coloraxis_colorbar=dict(
                title="Active Teams",
            )
        )
        return html.Div(dcc.Graph(figure=fig, style={"height": 700}))

    elif 'country' in changed_id:
        plot_me = active_teams.groupby('country').count().reset_index()

        high = plot_me['team_key'].max()
        low = plot_me['team_key'].min()

        plot_me['Total Teams (scaled)'] = plot_me['team_key'].apply(lambda x: (x - low) / high)
        plot_me['Total Teams'] = plot_me['team_key']

        fig = px.choropleth(data_frame=plot_me,
                            locations='country',
                            locationmode='country names',
                            color='Total Teams',
                            # hover_name='team_key',
                            # hover_data={'team_key':True,},
                            color_continuous_scale='Plasma',
                            # scope="world"
                            range_color=(0, 100),
                            )

        fig.update_layout(
            coloraxis_colorbar=dict(
                title="Teams per Country",
            ),
            title_text='Active FTC Teams Internationally ({} countries)'.format(len(plot_me)),
        )

        return html.Div(dcc.Graph(figure=fig, style={"height": 700}))


if __name__ == '__main__':
    app.run_server(debug=False)






