import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import re
import numpy as np
import json

from scraper import extract_batting_data, extract_bowling_data, find_xis

with open("match_info.json", "r") as read_file:
    match_info = json.load(read_file)

with open("points.json", "r") as read_file:
    points = json.load(read_file)

points = points[match_info["match_type"]]
    
scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('client-secret.json', scope)
client = gspread.authorize(creds)
sh = client.open('Fantasy Cricket')

batting_data = extract_batting_data(series_id = match_info["series_id"], match_id = match_info["match_id"])
bowling_data = extract_bowling_data(series_id = match_info["series_id"], match_id = match_info["match_id"])

players_sheet = sh.worksheet(match_info["players_sheet"])
selected_teams_sheet = sh.worksheet(match_info["teams_sheet"])

players_df = pd.DataFrame(players_sheet.get_all_records())
selected_teams_df = pd.DataFrame(selected_teams_sheet.get_all_records())

points_dict = dict(zip(players_df['Commentary Name'], [0]*len(players_df['Name'])))
names_dict = dict(zip(players_df['Name'], players_df['Commentary Name']))
roles_dict = dict(zip(players_df['Commentary Name'], players_df['Role']))

xis = find_xis(names_dict, series_id = match_info["series_id"], match_id = match_info["match_id"])

for index, row in batting_data.iterrows():
    name = row["Name"]
    dismissal = row["Desc"]
    runs = row["Runs"]
    balls = row['Balls']
    fours = row["4s"]
    sixes = row['6s']
    strike_rate = row['SR']
    
    if runs == 0:
        role = roles_dict[name]
        # no deduction for bowler ducks
        if role == "Bowler":
            point_change = 0
        else:
            point_change = points["duck"]
    else:
        point_change = runs
    
    # Strike Rate
    role = roles_dict[name]
    if role != "Bowler":
        if (match_info["match_type"] == "odi" and balls >= 20) or (match_info["match_type"] == "t20" and balls >= 10):
            sr_ind = np.searchsorted(points["sr_thresholds"], strike_rate, side='right')
            point_change += [-6, -4, -2, 0][sr_ind]

    if runs >= 100:
        point_change += points["century_bonus"]
    elif runs >= 50:
        point_change += points["fifty_bonus"]
    
    point_change += sixes*points["six_bonus"]
    point_change += fours*points["boundary_bonus"]
    
    points_dict[name] += point_change

    # Fielding
    if dismissal.find("sub (") == -1:
        # caught and bowled
        if dismissal.find("c & b") == 0:
            fielder = dismissal.split("c & b")[1].strip()
            fielder_com_name = [name for name in xis if fielder in name]
            points_dict[fielder_com_name[0]] += points["catch"]
        # catch
        elif dismissal.find("c") == 0:
            fielder = dismissal.split("c ")[1].split("b ")[0].strip()
            fielder = re.sub(r"[^\w-]+", ' ', fielder).strip()
            fielder_com_name = [name for name in xis if fielder in name]
            points_dict[fielder_com_name[0]] += points["catch"]
        # stumping
        if dismissal.find("st") == 0:
            fielder = dismissal.split("st ")[1].split("b ")[0].strip()
            fielder = re.sub(r"[^\w-]+", ' ', fielder).strip()
            fielder_com_name = [name for name in xis if fielder in name]
            points_dict[fielder_com_name[0]] += points["stumping"]
        # run out
        if dismissal.find("run out") == 0:
            fielders = [x.strip() for x in dismissal.split("run out")[1].replace('(', '').replace(')', '').split("/")]
            fielders = [re.sub(r"[^\w-]+", ' ', i).strip() for i in fielders]
            if len(fielders) >= 3:
                fielders = fielders[-2:]
            if len(fielders) == 1:
                thrower = fielders[0]
                catcher = fielders[0]
            else:
                thrower = fielders[0]
                catcher = fielders[1]
            thrower_com_name = [name for name in xis if thrower in name]
            catcher_com_name = [name for name in xis if catcher in name]
            points_dict[thrower_com_name[0]] += points["run_out_throw"]
            points_dict[catcher_com_name[0]] += points["run_out_catch"]

for index, row in bowling_data.iterrows():
    name = row["Name"]
    wickets = row["Wickets"]
    overs = row["Overs"]
    econ_rate = row["Econ"]

    point_change = points["wicket"]*wickets

    ## Economy rate
    if (match_info["match_type"] == "odi" and overs >= 5) or (match_info["match_type"] == "t20" and overs >= 2):
        econ_ind = np.searchsorted(points["econ_thresholds"], econ_rate, side='right')
        point_change += [6, 4, 2, 0, -2, -4, -6][econ_ind]

    # four and five wicket haul
    if wickets == 4:
        point_change += points["four_wkt"]
    if wickets >= 5:
        point_change += points["five_wkt"]
    points_dict[name] += point_change

for player in xis:
    points_dict[player] += points["in_xi"]

for index, row in selected_teams_df.iterrows():
    if not isinstance(row["Number"], int):
        continue

    full_name = row["Player"]
    capt = row["Captain/Vice Captain"]

    commentary_name = names_dict[full_name]
    fantasy_points = points_dict[commentary_name]

    if capt == "Captain":
        fantasy_points = fantasy_points * points["capt_factor"]
    if capt == "Vice Captain":
        fantasy_points = fantasy_points * points["vc_factor"]

    selected_teams_sheet.update('G' + str(index+2), fantasy_points)