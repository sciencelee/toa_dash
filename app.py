from assets.fetch_data import *
from assets.helper import *

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


# get state abbreviations
abbr = pd.read_csv('assets/abbr.csv')
#print(abbr[abbr['Abbreviation']=='IL']['State'].values[0])

# get zip code info
zip_codes = pd.read_csv('assets/us-zip-code-latitude-and-longitude.csv', delimiter=';')
zip_codes['Zip'] = zip_codes['Zip'].apply(lambda x: '{:05}'.format(x)) # make them uniform 5 digit strings
zip_codes_crunch = zip_codes.groupby(['State', 'City']).mean() # no need for zips, just need lat/lon of cities

# get all active usa teams - origniates from fetch_data import
active_usa = active_teams[active_teams['country']=="USA"]

# make a list of all team in each city and store in col
#team_list = active_usa.groupby(['state_prov', 'city'])['team_key'].apply(list).reset_index()
#print(active_usa)

# get team names and numbers from groupby
team_names = active_usa.groupby(['state_prov','city'])['team_name_short'].apply(list).reset_index()['team_name_short']
team_numbers = active_usa.groupby(['state_prov','city'])['team_key'].apply(list).reset_index()['team_key']

active_usa = active_usa.groupby(['state_prov','city']).mean().reset_index()
active_usa['team_names'] = team_names
active_usa['team_numbers'] = team_numbers

# now add the zipcode info for my teams
active_usa = active_usa.merge(how='left', right=zip_codes_crunch, left_on=['state_prov', 'city'], right_on=['State', 'City'])

# get the total_teams in each state by summing the list of team numbers
active_usa['total_teams'] = active_usa['team_numbers'].apply(lambda x: len(x))

# make a convenient tag for eah team to use for display
active_usa['header'] = active_usa.apply(lambda x: x.city + ',' + x.state_prov, axis=1)
active_usa['teams'] = active_usa.apply(lambda x: list(zip(x.team_numbers, x.team_names)), axis=1)


def ready_team_names(team_list):
    my_str = ''
    for team in team_list:
        my_str += ' '.join(team) + '<br>'
    return my_str

# further ready the display tag
active_usa['teams'] = active_usa.teams.apply(ready_team_names)
active_usa.sort_values(by=['total_teams'], ascending=False)


## make a figure to start page
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
# fig.update_layout(
#         title_text = 'FTC Teams by City (USA only)',
#         showlegend = True,
#         geo = dict(
#             scope = 'usa',
#             landcolor = 'rgb(150, 150, 150)',
#         ),
#     )


# ready data for country plot also
plot_me = active_teams.groupby('country').count().reset_index()
high = plot_me['team_key'].max()  # what is most teams in any country (usa)
low = plot_me['team_key'].min() # waht is low (just using this for potential scaling)

# now scale the total teams per country so we can visualize it
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
    margin={"r":0,"t":0,"l":0,"b":0},
    coloraxis_colorbar=dict(
        title="Teams per Country",
    ),
    title_text='FIRST International Presence ({} countries)'.format(len(plot_me)),
)



# THE STATE MAP WITH DATA
# let's ready our data for the state map with stats to the left side (should be cool when it works)
# ??? MAYBE NOT HERE???



# CREATE MY APP
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']  # default styling from tutorials
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server


# HTML Layout for my app in Dash format
app.layout = html.Div(
    [  # one big div for page
        html.Div(id='state-value', style={'display': 'none'}, children='NA'), # place to store my state value
        html.Div([
            html.Button('International', id='country', n_clicks=0),
            html.Button('Teams by State', id='state', n_clicks=0),
            html.Button('Teams by City', id='city', n_clicks=0)]
            ),
        html.Div([   # Big middle block split in two
            html.Div([  # This is my left half div
                    html.Div(id='stats', children="select a state from map"),
                    ], className="flex-child left flex1",),
            html.Div([
                        html.Div(id='map', # this is my div that contains my map.  look to css to change size etc.
                            className='my-graph',
                            children=html.Div(dcc.Graph(figure=fig)),
                            ),
                    ], className="flex-child right flex2",   # flex changes width of map
                    ),
                ], className='flex-container'),
        ], style = {'height': '700'})





#THIS IS A CALLBACK TO CHANGE MAP TYPE USING BUTTONS
@app.callback(
    Output('map', 'children'),  # output goes to id:map and attribute:figure (which is my fig map)
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
            showlegend=False,
            coloraxis_showscale=False,
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
                            custom_data=['State'],
                            hover_data={'total_teams': True,
                                        'State': False, },
                            color_continuous_scale='Plotly3',
                            scope="usa")

        fig.update_layout(
            margin={"r": 0, "t": 0, "l": 0, "b": 0},
            showlegend=False,
            coloraxis_showscale=False,
            title_text='Active FTC Teams by State',
            coloraxis_colorbar=dict(
                title="Active Teams",
            )
        )
        return html.Div(dcc.Graph(figure=fig, id='mappy', style={"height": 700}))

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
            coloraxis_showscale=False,
            coloraxis_colorbar=dict(
                title="Teams per Country",
            ),
            showlegend=False,
            title_text='Active FTC Teams Internationally ({} countries)'.format(len(plot_me)),
        )

        return html.Div(dcc.Graph(figure=fig, style={"height": 700}))




# THIS CALLBACK UPDATES THE STATE VALUE WHEN YOU CLICK A STATE ON THE MAP
@app.callback(Output('state-value', 'children'),  # output goes to hidden div to store val
              Input('mappy', 'clickData')) # Clickable map to grab state info (hopefully)
def write_state(clickData):
    if not clickData:
        return dash.no_update
    state = clickData['points'][0]['customdata'][0]  # grab state abbreviation from map click
    #print(state)
    return state


# CALLBACK DISPLAYS STATS FOR CHOSEN STATE
@app.callback(Output('stats', 'children'),  # output goes to stats display
                Input('state-value', 'children'))  # need the state in order to do calculations
def display_stats(state):
    top10 = top_state_stat(matches, state, 'red_score', top=5)
    auto = top_state_stat(matches, state, 'red_auto_score',)
    tele = top_state_stat(matches, state, 'red_tele_score')
    end = top_state_stat(matches, state, 'red_end_score')
    state_long = abbr[abbr['Abbreviation']==state]['State'].values[0].upper()
    match_total = n_matches(matches, state)

    # Is there a Jinja way to do this return in Dash????
    return html.Div([(html.H3(state_long)),
                    html.P([html.B('{} matches played this season'.format(match_total)),
                            html.Br(),
                            html.Br(),
                            html.B('TOP 5 SCORES'),
                           html.Br(),
                           top10[0],
                           html.Br(),
                           top10[1],
                           html.Br(),
                           top10[2],
                           html.Br(),
                           top10[3],
                           html.Br(),
                           top10[4],
                           html.Br(),
                           html.Br(),
                           html.B('TOP AUTONOMOUS SCORE'),
                           html.Br(),
                           auto[0],
                           html.Br(),
                           html.Br(),
                           html.B('TOP DRIVER CONTROLLED SCORE'),
                           html.Br(),
                           tele[0],
                           html.Br(),
                           html.Br(),
                           html.B('TOP ENDGAME SCORE'),
                           html.Br(),
                           end[0],
                           ]),
                    ])


if __name__ == '__main__':
    app.run_server(debug=False)






