# fantasy-cricket

This repository consists of code used to calculate Fantasy Cricket points and tabulate them in a Google Sheet. The code scrapes ESPNCricinfo scorecards and uses fixed point values from Dream11 to calculate scores for each participant's team.

### Installation and Usage
Open "Terminal" on your Mac. Then type the following commands (without the dollar sign):
```sh
# only have to do these commands once
$ git --version #this is to check if you have git installed
$ git clone https://github.com/akashpattnaik/fantasy-cricket
$ pip install gspread oauth2client
```
```sh
# commands to run each time
$ cd fantasy-cricket
$ python ipl_points.py # for IPL
$ python main.py # for international matches
```
Before a match, navigate to the folder called `fantasy-cricket`. Then open `match_info.json` or `ipl-match-info.json`. `match_info.json` should look like the following:

```json
{
    "series_id": 19496,
    "match_id": 1198240,
    "players_sheet": "Eng-Aus 2020 ODI Players",
    "teams_sheet": "Eng-Aus 3rd ODI",
    "match_type": "odi"
}
```

The `series_id` and `match_id` are from the url of the scorecard. For example, in [https://www.espncricinfo.com/series/**19496**/scorecard/**1198240**/england-vs-australia-3rd-odi-england-v-australia-2020](<https://www.espncricinfo.com/series/19496/scorecard/1198240/england-vs-australia-3rd-odi-england-v-australia-2020>), the `series_id` and `match_id` are bolded respectively. `players_sheet` and `teams_sheet` have to match the name of the sheets where the squads and our selected teams are exactly. And `match_type` should either be "test", "odi", or "t20". `ipl-match-info.json` only has a `match_id` field because everything else is fixed.
