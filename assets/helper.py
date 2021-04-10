# helper functions for my app

def format_me(df, col):
    my_list = []
    for i in range(len(df)):
        row = df.iloc[i, :]
        my_list.append('{}pt - Team {} ({}, {})'.format(row[col], row['team'], row['team_name'], row['city']))
    return my_list

def top_state_stat(df, state, col, top=1):
    top = df[df['state_prov']==state].sort_values(col, ascending=False)[['team', 'team_name', 'city', 'state_prov', 'country', col]][:top]
    text = format_me(top, col)
    return text

