import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve


class Utils:

    def calculate_distance(self, x1: int, y1: int, x2: int, y2: int):
        """Calculates distance.

        Args:
            x1 (int): Start x.
            y1 (int): Start y.
            x2 (int): End x.
            y2 (int): End y.
        """        
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def apply_coords_to_df(
        self, df: pd.DataFrame, length: int, width: int
    ) -> pd.DataFrame:
        """Adds changes to the xy coordinates.

        Args:
            df (pd.DataFrame): DataFrame.
            width (int): Pitch length.
            height (int): Pitch width.

        Returns:
            pd.DataFrame: DataFrame.
        """        
        df["x"] = df["x"] + (length / 2)
        df["y"] = df["y"] + (width / 2)

        df["x1"] = df["x"] * width / 100
        df["c1"] = abs(50 - df["y"]) * width / 100
        df["y1"] = (100 - df["y"]) * width / 100

        return df
