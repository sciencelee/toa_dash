'''
This file builds my dataset for matches
Fetches all matches for season and looks up team names and info as well
'''

import time

import requests
import json
import pandas as pd
import os

# from dotenv import load_dotenv
#
# load_dotenv()  # take environment variables from .env.


# pull my key from environment vars
api_key = str(os.environ.get("SECRET"))
season = 2021



def get_active_teams(year):
    '''fetch a list of active teams for current year (or other)'''

    url = "https://theorangealliance.org/api/team"  # list of team dicts

    headers = {'Content-Type': 'application/json',
               'X-TOA-Key': api_key,
               'X-Application-Origin': 'toa_map',
               }

    params = {  # 'country':'Canada',
        # 'team_key': team_list,
        'last_active': year,
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print("Failed, status code:", r.status_code)
        return None

    my_json = r.json()

    active_teams = pd.DataFrame(my_json)
    return active_teams


def query_team(team):
    url = "https://theorangealliance.org/api/team/{}".format(team)  # list of team dicts

    headers = {'Content-Type': 'application/json',
               'X-TOA-Key': api_key,
               'X-Application-Origin': 'toa_map',
               }

    params = {  # 'country':'Canada',
        # 'team_key': team,
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print("Failed, status code:", r.status_code)
        return None

    my_json = r.json()

    df = pd.DataFrame(my_json)
    return df


def query_team_matches(team, season):
    url = "https://theorangealliance.org/api/team/{}/matches/{}".format(team, season)  # list of team dicts

    headers = {'Content-Type': 'application/json',
               'X-TOA-Key': api_key,
               'X-Application-Origin': 'toa_map',
               }

    params = {  # 'country':'Canada',
        # 'team_key': team,
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print("Failed, status code:", r.status_code)
        return None

    my_json = r.json()

    df = pd.DataFrame(my_json)
    return df


def crawl_matches(start, count, season):
    url = "https://theorangealliance.org/api/match/all/{}".format(season)  # list of team dicts

    headers = {'Content-Type': 'application/json',
               'X-TOA-Key': api_key,
               'X-Application-Origin': 'toa_map',
               }

    params = {
        'start': str(start),
        'count': str(count),
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print("Failed, status code:", r.status_code)
        return None

    my_json = r.json()

    df = pd.DataFrame(my_json)
    return df


def get_size(season):
    # grab total number of matches for season
    url = "https://theorangealliance.org/api/match/size".format(season)  # list of team dicts

    headers = {'Content-Type': 'application/json',
               'X-TOA-Key': api_key,
               'X-Application-Origin': 'toa_map',
               }

    params = {  # 'country':'Canada',
        # 'team_key': team,
    }
    r = requests.get(url, headers=headers, params=params)
    if r.status_code != 200:
        print("Failed, status code:", r.status_code)
        return None

    size = r.json()
    return size['result']



# build my dataset of matches
active_teams = get_active_teams(season)  # 2021 means 2020-2021


# get number of matches this season
n = get_size(season)

# make a df of all matches
for i in range(0, n, 500):
    if i == 0:
        matches = crawl_matches(0, 500, 2021)
    else:
        matches = matches.append(crawl_matches(i, 500, 2021))
    time.sleep(3)  # sleep to avoid imposed limit
    print(i)

matches = matches[~matches['event_key'].isin(['2021-NYEXC-NFERS', '2021-NJ-NFCWL2', '2021-AZ-AFCCS'])]
matches['team'] = matches['match_key'].apply(lambda x: x[x.rfind('-')+1:])

# this is a lookup, and will likely take a while
matches['team_info'] = matches['team'].apply(lambda x: active_teams[active_teams['team_number']==int(x)][['team_name_short', 'city', 'state_prov', 'country']].mode().values[0])

matches['team_name'] = matches['team_info'].apply(lambda x: x[0])
matches['city'] = matches['team_info'].apply(lambda x: x[1])
matches['state_prov'] = matches['team_info'].apply(lambda x: x[2])
matches['country'] = matches['team_info'].apply(lambda x: x[3])

# save it to file
matches.to_csv('matches.csv')