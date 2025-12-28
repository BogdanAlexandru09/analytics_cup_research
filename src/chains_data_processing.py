import pandas as pd


class GKChains:

    def analyze_gk_chain(self, chain_df: pd.DataFrame, i: int) -> dict | None:
        """
        Analyze a possession chain to see if it starts with GK and reaches final third
        """

        if len(chain_df) == 0:
            return None

        #
        first_possession = chain_df.iloc[0]
        if first_possession["player_position"] != "GK":
            return None

        result = {
            # General Data
            "match_id": first_possession["match_id"],
            "frame_start": first_possession["frame_start"],
            "frame_end": first_possession["frame_end"],
            "possession_chain_id": first_possession["possession_chain_id"],
            "team_id": first_possession["team_id"],
            "team_name": first_possession["team_shortname"],
            "chain_length": len(chain_df),
            # Pitch Coordinates
            "x_start": first_possession["x_start"],
            "x_end": first_possession["x_end"],
            "y_start": first_possession["y_start"],
            "y_end": first_possession["y_end"],
            # Starting info
            "start_frame": first_possession["frame_start"],
            "start_third": first_possession["third_start"],
            "start_channel": first_possession["channel_start"],
            # Check if reaches attacking third
            "reached_attacking_third": False,
            "first_attacking_third_frame": None,
            "ended_in_attacking_third": False,
            # End info
            "end_type": chain_df.iloc[-1]["end_type"],
            "end_frame": chain_df.iloc[-1]["frame_end"],
            # Outcome
            "led_to_shot": False,
            "led_to_goal": False,
            # Phase info
            "start_phase": first_possession["team_in_possession_phase_type"],
            "end_phase": chain_df.iloc[-1]["team_in_possession_phase_type"],
            # Adding this index to make tracking easier for further processing
            "possession_index": i,
        }

        # Check if any possesison in the chain reaches attacking third
        attacking_third_rows = chain_df[(chain_df["third_end"] == "attacking_third")]

        if len(attacking_third_rows) > 0:
            result["reached_attacking_third"] = True
            result["first_attacking_third_frame"] = attacking_third_rows.iloc[0][
                "frame_start"
            ]

            # Check if chain ENDS in attacking third
            last_possession = chain_df.iloc[-1]
            if last_possession["third_end"] == "attacking_third":
                result["ended_in_attacking_third"] = True

        # Check outcomes
        # For shots/goals, check the last possession in the chain
        last_possession = chain_df.iloc[-1]

        if last_possession["end_type"] == "shot":
            result["led_to_shot"] = True

        # lead_to_goal is defined for each possession event
        # If ANY possession in the chain leads to a goal within 10 seconds, mark it
        if chain_df["lead_to_goal"].any():
            result["led_to_goal"] = True

        return result

    def get_gk_chains_info(self, gk_chains_df: pd.DataFrame):
        """GK Chains Analysis.

        Args:
            gk_chains_df (pd.DataFrame): DataFrame.
        """
        print("\n=== GK-Started Possession Chain Analysis ===")
        print(f"Total GK-started chains: {len(gk_chains_df)}")
        print(
            f"\nChains reaching attacking third: {gk_chains_df['reached_attacking_third'].sum()} "
            f"({gk_chains_df['reached_attacking_third'].mean()*100:.1f}%)"
        )
        print(
            f"Chains ending in attacking third: {gk_chains_df['ended_in_attacking_third'].sum()} "
            f"({gk_chains_df['ended_in_attacking_third'].mean()*100:.1f}%)"
        )

        print("\n=== Chain Outcomes ===")
        print(gk_chains_df["end_type"].value_counts())

        print("\n=== For chains reaching attacking third ===")
        attacking_chains = gk_chains_df[gk_chains_df["reached_attacking_third"] == True]
        if len(attacking_chains) > 0:
            print(f"Total: {len(attacking_chains)}")
            print("\nHow they ended:")
            print(attacking_chains["end_type"].value_counts())
            print(f"\nLed to shot: {attacking_chains['led_to_shot'].sum()}")
            print(f"Led to goal: {attacking_chains['led_to_goal'].sum()}")
            print(
                f"\nAverage chain length: {attacking_chains['chain_length'].mean():.1f} possessions"
            )

        print("\n=== Starting Phase Distribution ===")
        print(gk_chains_df["start_phase"].value_counts())

        print("\n=== Average Chain Length by Outcome ===")
        print(
            gk_chains_df.groupby("reached_attacking_third")["chain_length"].agg(
                ["mean", "median", "min", "max"]
            )
        )
            