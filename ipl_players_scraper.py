import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
import numpy as np
import json

# scope = ['https://spreadsheets.google.com/feeds','https://www.googleapis.com/auth/drive']
# creds = ServiceAccountCredentials.from_json_keyfile_name('client-secret.json', scope)
# client = gspread.authorize(creds)
# sh = client.open('Fantasy Cricket')

# database_sheet = sh.worksheet("IPL Player Database Backup")

URL = "https://www.espncricinfo.com/ci/content/squad/index.html?object=1210595"
page = requests.get(URL)
bs = BeautifulSoup(page.content, 'lxml')

players = {}
ultag = bs.find('ul', {'class': 'squads_list'})
for litag in ultag.find_all('li'):
    a = litag.find('a', href=True)
    team = " ".join(a.text.split()[:-1])
    print(team)
    href = a['href']
    squad_URL = "https://www.espncricinfo.com/" + href
    squad_page = requests.get(squad_URL)
    squad_bs = BeautifulSoup(squad_page.content,'lxml')
    players_div  = squad_bs.find('div', {'role': 'main'})
    player_list = players_div.find_all("ul")[0]
    for player in player_list.find_all("li"):
        for atag in player.find_all('a', href=True):
            name = atag.text.strip()
            href = atag['href']
        print(name)
        players[name] = [team]
        player_attributes = player.find_all('span')
        
        # Overseas Player
        if len(player_attributes) == 5:
            players[name].append("Overseas")
        else:
            players[name].append("Domestic")

        # Role
        role_list = [span for span in player_attributes if span.find('b') and "Playing role:" in span.text]
        if (len(role_list) == 0):
            players[name].append("Unknown")
        else:
            role = role_list[0].text.split(':')[-1]
            if "allrounder" in role or "Allrounder" in role:
                players[name].append("All-Rounder")
            elif 'batsman' in role or 'Batsman' in role or "Wicketkeeper" in role:
                players[name].append("Batsman")
            elif 'Bowler' in role:
                players[name].append("Bowler")

        # Commentary Name
        
        player_URL = "https://www.espncricinfo.com/" + href

        player_page = requests.get(player_URL)
        player_bs = BeautifulSoup(player_page.content,'lxml')
        
        if not player_bs.find("div", {"class": "ciPlayertextbottomborder"}):
            players[name].append("Unknown")
            continue

        matches_table = player_bs.find("div", {"class": "ciPlayertextbottomborder"}).find_next_sibling('table')
        match_href = matches_table.find("a", href=True)['href']
        
        
        match_URL = "https://www.espncricinfo.com/" + match_href
        
        match_page = requests.get(match_URL)
        match_bs = BeautifulSoup(match_page.content,'lxml')
        
        table_body=match_bs.find_all('tbody')
        xis = []
        table_foot =match_bs.find_all('tfoot')

        for i, table in enumerate(table_foot):
            rows = table.find_all('tr')
            if len(rows) == 3:
                dnb_names = rows[1].find_all('span')
                dnb_names = [x.text.replace(u'\xa0', '').strip(' ,') for x in dnb_names]
                dnb_names = [re.sub(r"\W+", ' ', i.split("(c)")[0]).strip() for i in dnb_names]
                dnb_names = [i for i in dnb_names if i]
                xis.extend(dnb_names)

        for i, table in enumerate(table_body):
            rows = table.find_all('tr')
            for row in rows:
                cols=row.find_all('td')
                cols=[x.text.strip() for x in cols]
                if len(cols) >= 8:
                    player_entry = re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip()
                    if name.split()[-1] in player_entry and name[0] == player_entry[0] and len(players[name]) != 4:
                        players[name].append(player_entry)
                if len(cols) == 2:
                    if cols[1] == 'Batsman' or cols[1] == 'Allrounder' or cols[1] == 'Bowler' or cols[1] == 'Wicketkeeper':
                        player_entry = re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip()
                        if name.split()[-1] in player_entry and name[0] == player_entry[0] and len(players[name]) != 4:
                            players[name].append(player_entry)
                if (len(players[name]) == 4):
                    break
            if (len(players[name]) == 4):
                break


json = json.dumps(players)
f = open("ipl_players.json", "w")
f.write(json)
f.close()

# players_li = [[name] + players[name] for name in players.keys()]
# database_sheet.update([["Name", "Team", "Overseas/Domestic", "Role", "Commentary Name"]] + players_li)
