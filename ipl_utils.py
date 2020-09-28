import gspread
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd 
import numpy as np
import json

def update_ipl_sheet(squad_sheet_name):
    scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
    creds = ServiceAccountCredentials.from_json_keyfile_name('client-secret.json', scope)
    client = gspread.authorize(creds)
    sh = client.open('Fantasy Cricket')
    squad_sheet = sh.worksheet(squad_sheet_name)

    # squad_sheet_df = pd.DataFrame(squad_sheet.get_all_records())
    points_mat = np.load("ipl_points_matrix.npy")

    with open("ipl_players.json") as f:
        data = json.load(f)

    all_players = list(data.keys())

    player_cols = ['A', 'G', 'M']
    for col in player_cols:
        next_col = chr(ord(col) + 4)
        squad = squad_sheet.get('{}2:{}26'.format(col, col))
        squad_points = []
        for player in squad:
            player_ind = all_players.index(player[0])
            squad_points.append(int(np.sum(points_mat[:, player_ind])))
        squad_points = [[i] for i in squad_points]
        squad_sheet.update('{}2:{}26'.format(next_col, next_col), squad_points)