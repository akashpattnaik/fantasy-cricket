import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

def extract_batting_data(series_id, match_id):
    URL = 'https://www.espncricinfo.com/series/'+ str(series_id) + '/scorecard/' + str(match_id)
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, 'lxml')

    table_body=bs.find_all('tbody')
    batsmen_df = pd.DataFrame(columns=["Name","Desc","Runs", "Balls", "4s", "6s", "SR", "Team"])
    # for i, table in enumerate(table_body[0:4:2]):
    for i, table in enumerate(table_body[::2]):
        rows = table.find_all('tr')
        for row in rows[::2]:
            cols=row.find_all('td')
            cols=[x.text.strip() for x in cols]
            if cols[0] == 'Extras':
                continue
            if len(cols) == 1:
                continue
            if len(cols) >= 8:
                if (cols[7] == '-'):
                    cols[7] = 100 # this is when a batsman has not faced a ball, set to 100 so points aren't deducted for SR
                batsmen_df = batsmen_df.append(pd.Series(
                [re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip(), cols[1], 
                int(cols[2]), int(cols[3]), int(cols[5]), int(cols[6]), float(cols[7]), i % 2], 
                index=batsmen_df.columns ), ignore_index=True)
    return batsmen_df

def extract_bowling_data(series_id, match_id):
    URL = 'https://www.espncricinfo.com/series/'+ str(series_id) + '/scorecard/' + str(match_id)
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, 'lxml')

    table_body=bs.find_all('tbody')
    bowler_df = pd.DataFrame(columns=['Name', 'Overs', 'Maidens', 'Runs', 'Wickets',
                                      'Econ', 'Wd', 'Nb','Team'])
    for i, table in enumerate(table_body[1::2]):
        rows = table.find_all('tr')
        for row in rows:
            cols=row.find_all('td')
            cols=[x.text.strip() for x in cols]
            if len(cols) == 11:
                bowler_df = bowler_df.append(pd.Series([cols[0], float(cols[1]), int(cols[2]), int(cols[3]), int(cols[4]), float(cols[5]), 
                                                         float(cols[9]), int(cols[10]), (i + 1) % 2], 
                                                       index=bowler_df.columns ), ignore_index=True)
    return bowler_df

def find_xis(names_dict, series_id, match_id):
    URL = 'https://www.espncricinfo.com/series/'+ str(series_id) + '/scorecard/' + str(match_id)
    page = requests.get(URL)
    bs = BeautifulSoup(page.content, 'lxml')

    table_body=bs.find_all('tbody')
    xis = []
    table_foot = bs.find_all('tfoot')

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
                xis.append(re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip())
            if len(cols) == 2:
                if cols[1] == 'Batsman' or cols[1] == 'Allrounder' or cols[1] == 'Bowler' or cols[1] == 'Wicketkeeper':
                    name = re.sub(r"\W+", ' ', cols[0].split("(c)")[0]).strip()
                    xis.append(names_dict[name])
    return set(xis)
