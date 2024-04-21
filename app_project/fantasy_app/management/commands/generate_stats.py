



#scrapes understat.com to gather team data for real world EPL teams
import requests
from bs4 import BeautifulSoup
import json
import pandas as pd
import os



season = ""
if season == "": 
    url = 'https://understat.com/league/EPL'
else: url = 'https://understat.com/league/EPL/{}'.format(season)

def season_scraper(season):
    #getting data/formatting it 
    res = requests.get(url)
    soup = BeautifulSoup(res.content, 'lxml')
    
        # data is under "scripts" tag. So, finding all the script tags
    script = soup.find_all('script')
    
    string_with_json_obj = ''

    for el in script:
        if 'teamsData' in el.text:
            string_with_json_obj = el.text.strip()
            
    #keeping only the part of string we need
    ind_start = string_with_json_obj.index("('") + 2
    ind_end = string_with_json_obj.index("')") 
    json_data = string_with_json_obj[ind_start: ind_end]

    json_data = json_data.encode('utf8').decode('unicode_escape')
    data = json.loads(json_data)#formatted json data
    
    #making a dictionary composed of team ID and team titles
    teams ={}
    for id in data.keys():
        teams[id] = data[id]['title']
        
    #getting column names 
    columns = []
    values = []
    for id in data.keys():
        columns = list(data[id]['history'][0].keys())
        break
    all_team_dicts = {}
    
    #getting all data for each team in the season and storing them in a dictionary with 'team' as key
    for id, team in teams.items():
        teams_data = []
        for i in data[id]['history']:
            teams_data.append(list(i.values()))

        df = pd.DataFrame(teams_data, columns = columns)
        all_team_dicts[team] = df
    #correcting the format of PPDA and OPDA(PPDA_allowed) to the ratio of PPDA and PPDA_allowed
    for team, df in all_team_dicts.items():
        all_team_dicts[team]['ppda_coef'] = all_team_dicts[team]['ppda'].apply(lambda x : x['att']/x['def'] if x['def'] != 0 else 0)
        all_team_dicts[team]['oppda_coef'] = all_team_dicts[team]['ppda_allowed'].apply(lambda x : x['att']/x['def'] if x['def'] != 0 else 0)
   
    #Getting columns to be averaged and summed

    cols_to_sum = ['xG', 'xGA', 'npxG', 'npxGA', 'deep', 'deep_allowed', 'scored', 'missed', 'xpts', 'wins', 'draws', 'loses', 'pts', 'npxGD']
    cols_to_mean = ['ppda_coef', 'oppda_coef']
    frames = []

    for team, df in all_team_dicts.items():
        sum_data = pd.DataFrame(df[cols_to_sum].sum()).transpose() # returns series data, so used transpose() 
        mean_data = pd.DataFrame(df[cols_to_mean].mean()).transpose() # returns series data, so used transpose() 
        sum_mean_data = sum_data.join(mean_data)
        sum_mean_data['team'] = team
        sum_mean_data['matches'] = len(df)
        frames.append(sum_mean_data)

    final_data = pd.concat(frames, sort = False, ignore_index =True)
    
    #ordering columns
    final_data = final_data[['team', 'matches', 'wins', 'draws', 'loses', 'scored', 'missed', 'pts','xG', 'npxG', 'xGA', 'npxGA', 'npxGD', 'ppda_coef', 'oppda_coef', 'deep', 'deep_allowed', 'xpts']]
    final_data.sort_values('pts', ascending= False, inplace = True)#sorting by points
    final_data.reset_index(inplace = True, drop = True)
    final_data['position'] = range(1, len(final_data) + 1)#adding positon coumn
    
    #IMPORTANT 
    #Finding the difference between "expected" and "real" values
    final_data.rename(columns ={'missed': 'conceded'}, inplace = True) # renamin 'missed' column to 'conceded'
    final_data['xG_diff'] = final_data['xG'] - final_data['scored']
    final_data['xGA_diff'] = final_data['xGA'] - final_data['conceded']
    final_data['xpts_diff'] = final_data['xpts'] - final_data['pts'] 
    
    #converting appropriate columns to integer values
    cols_to_int = ['wins', 'draws', 'loses', 'scored', 'conceded', 'pts', 'deep', 'deep_allowed']
    final_data[cols_to_int] = final_data[cols_to_int].astype(int)
    
    #Formatting and changing the order of the dataframe
    col_order = ['position','team', 'matches', 'wins', 'draws', 'loses', 'scored', 'conceded', 'pts', 'xG', 'xG_diff', 'npxG', 'xGA', 'xGA_diff', 'npxGA', 'npxGD', 'ppda_coef', 'oppda_coef', 'deep', 'deep_allowed', 'xpts', 'xpts_diff']
    final_data = final_data[col_order]
    pd.options.display.float_format = '{:,.2f}'.format
    
    
    #exporting data for each season to seperate folder
    if season == "": 
        outname_season = 'currentseasondata.csv'
    else: 
        outname_season = '{}_seasondata.csv'.format(season)
    # outdir_season = r'C:\Users\matth\soccer_ratings'.format(season)
    # if not os.path.exists(outdir_season):
    #     os.mkdir(outdir_season)
    # fullname_season = os.path.join(outdir_season, outname_season) 
    final_data.to_csv('{}'.format(outname_season),index = False)
    
    return final_data


statsdoc = season_scraper(season)
