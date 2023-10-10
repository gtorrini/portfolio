# Standard libraries
from typing import Optional

# 3rd party libraries
import pandas as pd
from pandas import DataFrame
import requests

class TeamStats:
    def __init__(self, stats: DataFrame) -> None:
        self.all = stats
        self.forwards = stats[stats['position_generic'] == 'Forward']
        self.midfielders = stats[stats['position_generic'] == 'Midfielder']
        self.defenders = stats[stats['position_generic'] == 'Defender']
        self.goalies = stats[stats['position_generic'] == 'Goalkeeper']

class Team:
    def __init__(self, short_name: str, full_name: str, club_id: int, primary: str, secondary: str, tertiary: str) -> None:
        self.short_name = short_name
        self.full_name = full_name
        self.club_id = club_id
        self.color_1 = primary
        self.color_2 = secondary
        self.color_3 = tertiary

    def get_stats(self):
        # Set up request
        endpoint = 'http://stats-api.mlssoccer.com/v1/players/seasons'
        query_params = {'season_opta_id': 2023, 'competition_opta_id': 98, 'club_opta_id': self.club_id, 'include': ['regular_season_statistics', 'club', 'player']}

        # Handle request
        try:
            r = requests.get(url=endpoint, params=query_params, timeout=10)
            r.raise_for_status()   # raise HTTP errors
        except requests.exceptions.HTTPError as err_h:
            print('HTTP Error:', err_h)
        except requests.exceptions.ConnectionError as err_c:
            print('Network Error:', err_c)
        except requests.exceptions.Timeout as err_t:
            print('Timeout Error:', err_t)
        except requests.exceptions.RequestException as err_r:
            raise SystemExit(err_r)
        else:
            # Build DataFrame from JSON 
            norm_df = pd.json_normalize(r.json(), max_level=2)
            current_df = norm_df[norm_df['leave_date'].isna()]    # only select players from current roster
            stats_df = TeamStats(current_df)
            return stats_df
        
def league_stats(year: int, search: str, position: Optional[str] = None):
    # Set up request
    endpoint = f'''http://stats-api.mlssoccer.com/v1/{search}/seasons'''
    if (search == 'clubs'):
        query_params = {'season_opta_id': year, 'competition_opta_id': 98, 'include': ['regular_season_statistics', 'club'],}
    elif (search == 'players'):
        query_params = {'season_opta_id': year, 'competition_opta_id': 98, 'include': ['regular_season_statistics', 'club', 'player'], 'ttl': 1800, 'page_size': 1000}
        if (position is not None):
            query_params['player_season_position_generic'] = position
            match position:
                case 'Goalkeeper':
                    query_params['order_by'] = '-regular_season_player_season_stat_saves'
                case 'Forward' | 'Midfielder' | 'Defender':
                    query_params['order_by'] = '-regular_season_player_season_stat_goals'
                case _:
                    print('league_stats only accepts \"Forward\", \"Midfielder\", \"Defender\", or \"Goalkeeper\" as optional position strings. Please try again.')
                    return
    else:
        print('league_stats only accepts \"clubs\" or \"players\" as valid search strings. Please try again.')
        return

    # Handle request
    try:
        r = requests.get(url=endpoint, params=query_params, timeout=10)
        r.raise_for_status()   # raise HTTP errors
    except requests.exceptions.HTTPError as err_h:
        print('HTTP Error:', err_h)
    except requests.exceptions.ConnectionError as err_c:
        print('Network Error:', err_c)
    except requests.exceptions.Timeout as err_t:
        print('Timeout Error:', err_t)
    except requests.exceptions.RequestException as err_r:
        raise SystemExit(err_r)
    else:
        # Build DataFrame from JSON 
        norm_df = pd.json_normalize(r.json(), max_level=2)
        stats_df = norm_df[~norm_df['club.abbreviation'].isna()]     # only select actual teams

        # Sort into conferences
        west = ['ATX', 'COL', 'DAL', 'HOU', 'LA', 'LAFC', 'MIN', 'POR', 'RSL', 'SEA', 'SJ', 'SKC', 'STL', 'VAN']
        east = ['ATL', 'CHI', 'CIN', 'CLB', 'CLT', 'DC', 'MIA', 'MTL', 'NE', 'NSH', 'NYC', 'ORL', 'PHI', 'RBNY', 'TOR']
        conf = []
        for i in range(len(stats_df)):
            if (stats_df['club.abbreviation'].loc[stats_df.index[i]] in west):
                conf.append('W')
            elif (stats_df['club.abbreviation'].loc[stats_df.index[i]] in east):
                conf.append('E')
        stats_df.assign(conference = conf)
        return stats_df

# Create objects for each team:
atl = Team('ATL', 'Atlanta United', 11091, '#a32135', '#2c2a25', '#a99767')
cin = Team('CIN', 'FC Cincinnati', 11504, '#003087', '#fe5000', '#0b1f41')
clb = Team('CLB', 'Columbus Crew', 454, '#fddd00', '#000000', '#ffffff')
ner = Team('NE', 'New England Revolution', 928, '#0a2240', '#ce0e2d', '#ffffff')
orl = Team('ORL', 'Orlando City SC', 6900, '#61259e', '#f1d281', '#ffffff')
phi = Team('PHI', 'Philadelphia Union', 5513, '#0e1c2c', '#318dde', '#e3doa5')
stl = Team('STL', 'St. Louis City SC', 17012, '#ec1458', '#001544', '#fed500')
skc = Team('SKC', 'Sporting Kansas City', 421, '#0c2340', '#a5bad6', '#878b8c')
nsh = Team('NSH', 'Nashville SC', 15154, '#ece83a', '#1d1645', '#17191d')