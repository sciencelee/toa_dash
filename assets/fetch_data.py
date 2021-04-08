import requests
import json
import pandas as pd



def get_keys(path):
    #  retrieve your key/token from json file
    with open(path) as f:
        return json.load(f)


your_path = "/Users/aaronlee/Desktop/toa_login.json"  # Make a json file that stores your key
keys = get_keys(your_path)

api_key = keys['key']

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


active_teams = get_active_teams(2021)  # 2021 means 2020-2021

if __name__ == "__main__":
    active_teams = get_active_teams(2021)  # 2021 means 2020-2021
    print(query_team(3507))