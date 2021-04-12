# helper functions for my app

def format_me(df, col):
    my_list = []
    for i in range(len(df)):
        row = df.iloc[i, :]
        my_list.append('{}pts - Team {} ({}, {}, {})'.format(row[col], row['team'], row['team_name'], row['city'], row['state_prov']))
    return my_list

def top_state_stat(df, state, col, top=1):
    #print('/{}/'.format(state))
    #print(df['state_prov'].unique())
    if state not in df['country'].unique():
        top_df = df[df['state_prov']==state].sort_values(col, ascending=False)[['team', 'team_name', 'city', 'state_prov', 'country', col]][:top]
    else:
        top_df = df[df['country']==state].sort_values(col, ascending=False)[['team', 'team_name', 'city', 'state_prov', 'country', col]][:top]

    text = format_me(top_df, col)

    if len(text)==0:
        text.append('No matches on record.')  # Ugh.  COVID
        for i in range(top):
            text.append('')

    if len(text)==1:
        ties = df[(df[col]==top_df[col].max()) & (df['state_prov']==state)]
        tie = len(ties.team.unique())
        teams = list(ties.team.astype(int).unique())
        if tie > 1:
            text = ['{}pts - {} way tie {}'.format(top_df[col].max(), tie, teams)]

    return text



def n_matches(df, state):
    # could be state or country passed depending on map
    if state in df['state_prov'].unique():
        n = len(df[df['state_prov']==state])
    else:
        n= len(df[df['country']==state])
    return n

