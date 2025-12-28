import numpy as np
from src.utils import Utils
import pandas as pd

class FeatureCreation:
    
    def create_features_dataframe(self, chains_list: np.ndarray, chains_df: pd.DataFrame) -> pd.DataFrame:
        """Creates the features DataFrame.

        Args:
            chains_list (np.ndarray): Possession chains list.
            chains_df (pd.DataFrame): Possession chains DataFrame.

        Returns:
            pd.DataFrame: DataFrame.
        """        
    # define and create the features DataFrame for each possession chain given as input
        utils = Utils()                                
        list_features = []
        for i in chains_list:
            dfs_possession_chain = chains_df.loc[chains_df["possession_index"] == i]
            if len(dfs_possession_chain) > 0:
                df_row_save = dfs_possession_chain.iloc[0]
                df_row_last = dfs_possession_chain.loc[dfs_possession_chain['team_id'] == df_row_save.team_id].iloc[-1]
                dict_possession_chain_features = {}
                
                dict_possession_chain_features["gkId"] = df_row_save["player_id"]
                dict_possession_chain_features["gk_end_x"] = df_row_save["x1"]
                dict_possession_chain_features["gk_end_x2"] = df_row_save["x1"]**2
                dict_possession_chain_features["gk_end_y"] = df_row_save["y1"]
                dict_possession_chain_features["gk_end_y2"] = df_row_save["y1"]**2
                dict_possession_chain_features["gk_end_c"] = df_row_save["c1"]
                dict_possession_chain_features["distance"] = np.sqrt(df_row_last["x1"]**2 + df_row_last["c1"]**2)
                dict_possession_chain_features["d2"] = df_row_last["x1"]**2 + df_row_last["c1"]**2
                dict_possession_chain_features["angle"] = np.where(np.arctan(7.32 * dict_possession_chain_features["gk_end_x"] / (dict_possession_chain_features["gk_end_x"]**2 + dict_possession_chain_features["gk_end_c"]**2 - (7.32/2)**2)) > 0, np.arctan(7.32 * dict_possession_chain_features["gk_end_x"] /(dict_possession_chain_features["gk_end_x"]**2 + dict_possession_chain_features["gk_end_c"]**2 - (7.32/2)**2)), np.arctan(7.32 * dict_possession_chain_features["gk_end_x"] /(dict_possession_chain_features["gk_end_x"]**2 + dict_possession_chain_features["gk_end_c"]**2 - (7.32/2)**2)) + np.pi).item()
                dict_possession_chain_features["match_period"] = 1 if df_row_last["period"] == "1.0" else 2
                dict_possession_chain_features["max_x_reached"] = df_row_last["x1"]

                start_to_end_distance = utils.calculate_distance(df_row_save["x1"], df_row_save["y1"], df_row_last["x1"], df_row_last["y1"])

                # add the label
                dict_possession_chain_features["gk_led_to_final_third"] = 1 if df_row_save["reached_attacking_third"] == True else 0
                
                # add the features to the main list
                list_features.append(dict_possession_chain_features)    
            
        return pd.DataFrame(list_features)
    
    def add_normalized_metrics_to_dataframe(self, df: pd.DataFrame):
        """Normalizes the metrics.

        Args:
            df (pd.DataFrame): DataFrame
        """        
        df["GKLaunchPer90"] = round(df["GKLaunch"]*90/df["total_minutes_played"], 2)
        # P30 TIP
        df["GKLaunchPer30TIP"] = round(df["GKLaunch"]*30/df["total_minutes_played_tip"], 2)
        # P30 OTIP
        df["GKLaunchPer30OTIP"] = round(df["GKLaunch"]*30/df["total_minutes_played_otip"], 2)
