import json
import pandas as pd
import numpy as np

class SkillCornerData:
    
    # TRACKING DATA 
    def prepare_tracking_data_files(self, url: str, match_ids: list) -> list:
        td_data_matches_list = []
        
        for match_id in match_ids:
            td_data_match_url = url + f"{match_id}/{match_id}_tracking_extrapolated.jsonl"
            td_data_matches_list.append(td_data_match_url)
            
        return td_data_matches_list
    
    def load_tracking_data(self, url: str, match_ids: list) -> pd.DataFrame:
        # does not work, I need the match_id as well to the TD...
        # return pd.concat(
        #     map(lambda x: pd.read_json(x, lines=True), tracking_data_matches_list),
        #     ignore_index=True
        # )
        td_df = pd.DataFrame()
        
        for match_id in match_ids:
            td_match_data_url = url + f"{match_id}/{match_id}_tracking_extrapolated.jsonl"
            
            td_match_df = pd.read_json(td_match_data_url, lines=True)
    
            tracking_data_df = pd.json_normalize(
                td_match_df.to_dict("records"),
                "player_data",
                ["frame", "timestamp", "period", "possession", "ball_data"]
            )
            
            tracking_data_df["possession_player_id"] = tracking_data_df["possession"].apply(
                lambda x: x.get("player_id")
            )
            
            tracking_data_df["possession_group"] = tracking_data_df["possession"].apply(
                lambda x: x.get("group")
            )
            
            tracking_data_df = tracking_data_df.drop(columns=["possession", "ball_data"])
            tracking_data_df["match_id"] = match_id
    
            td_df = pd.concat([td_df, tracking_data_df], ignore_index=True)
            
        td_df = td_df.dropna(subset=['match_id'])
        
        return td_df 

    def process_tracking_data_dataframe(self, raw_tracking_data_df: pd.DataFrame) -> pd.DataFrame:
        tracking_data_df = pd.json_normalize(
            raw_tracking_data_df.to_dict("records"),
            "player_data",
            ["frame", "timestamp", "period", "possession", "ball_data"]
        )
        
        tracking_data_df["possession_player_id"] = tracking_data_df["possession"].apply(
            lambda x: x.get("player_id")
        )
        
        tracking_data_df["possession_group"] = tracking_data_df["possession"].apply(
            lambda x: x.get("group")
        )
        
        tracking_data_df = tracking_data_df.drop(columns=["possession", "ball_data"])
        
        return tracking_data_df
        
    # MATCHES METADATA    
    def prepare_metadata_files(self, url: str, match_ids: list) -> list:
        md_matches_list = []
        
        for match_id in match_ids:
            md_match_url = url + f"{match_id}/{match_id}_match.json"
            md_matches_list.append(md_match_url)
            
        return md_matches_list
    
    def load_metadata(self, metadata_matches_list: list) -> pd.DataFrame:
        return pd.concat(
            (pd.read_json(path, lines=True, encoding='utf-8') for path in metadata_matches_list),
            ignore_index=True
        )
        
    def process_players_metadata_dataframe(self, raw_players_metadata_df: pd.DataFrame) -> pd.DataFrame:
        players_metadata_df = pd.json_normalize(
            raw_players_metadata_df.to_dict("records"),
            max_level=2
        )
        
        players_metadata_df["home_team_side"] = players_metadata_df["home_team_side"].astype(str)
        
        players_df = pd.json_normalize(
            players_metadata_df.to_dict("records"),
            record_path="players",
            meta=[
                "home_team_score",
                "away_team_score",
                "date_time",
                "home_team_side",
                "home_team.name",
                "home_team.id",
                "away_team.name",
                "away_team.id",
            ]
        )
        
        players_df = players_df[
            ~((players_df.start_time.isna()) & (players_df.end_time.isna()))
        ]

        players_df = players_df.loc[players_df["player_role.acronym"] == "GK"]

        # Create flag from player
        players_df["team_name"] = np.where(
            players_df.team_id == players_df["home_team.id"],
            players_df["home_team.name"],
            players_df["away_team.name"],
        )

        players_df['total_minutes_played'] = (
            players_df.groupby('short_name')['playing_time.total.minutes_played']
            .transform('sum')
        )
        
        players_df['total_minutes_played_tip'] = (
            players_df.groupby('short_name')['playing_time.total.minutes_tip']
            .transform('sum')
        )
        
        players_df['total_minutes_played_otip'] = (
            players_df.groupby('short_name')['playing_time.total.minutes_otip']
            .transform('sum')
        )

        columns_to_keep = [
            "id",
            "short_name",
            "team_id",
            "team_name",
            "total_minutes_played",
            "total_minutes_played_tip",
            "total_minutes_played_otip",
            "player_role.acronym"
        ]
        
        players_df = players_df[columns_to_keep]
        
        players_df = players_df.sort_values('total_minutes_played', ascending=False).drop_duplicates(players_df.columns, ignore_index=True)

        return players_df

    # MATCHES DYNAMIC EVENTS
    def prepare_dynamic_events_files(self, url: str, match_ids: list) -> list:
        de_matches_list = []
        
        for match_id in match_ids:
            de_match_url = url + f"{match_id}/{match_id}_dynamic_events.csv"
            de_matches_list.append(de_match_url)
            
        return de_matches_list    

    def load_dynamic_events_data(self, dynamic_events_matches_list: list) -> pd.DataFrame:
        return pd.concat(
            map(pd.read_csv, dynamic_events_matches_list),
            ignore_index=True
        )
        
    def filter_player_possessions(self, dynamic_events_df: pd.DataFrame) -> pd.DataFrame:
        player_possessions = dynamic_events_df[dynamic_events_df['event_type'] == 'player_possession'].copy()

        # Group consecutive possessions by the same team
        player_possessions = player_possessions.sort_values(['match_id', 'index'])

        # Create team possession identifier
        player_possessions['team_possession_change'] = (
            player_possessions['team_id'] != player_possessions['team_id'].shift()
        ).astype(int)
        
        player_possessions['team_possession_id'] = player_possessions.groupby('match_id')['team_possession_change'].cumsum()
    
        player_possessions['team_changed'] = (
            (player_possessions['team_id'] != player_possessions['team_id'].shift()) |
            (player_possessions['match_id'] != player_possessions['match_id'].shift())
        ).astype(int)

        player_possessions['possession_chain_id'] = (
            player_possessions.groupby('match_id')['team_changed'].cumsum()
        )
        
        return player_possessions
