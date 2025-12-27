import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score, roc_curve


class Utils:

    def calculate_distance(self, x1: int, y1: int, x2: int, y2: int):
        return np.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)

    def apply_coords_to_df(
        self, df: pd.DataFrame, width: int, height: int
    ) -> pd.DataFrame:
        df["x"] = df["x"] + (width / 2)
        df["y"] = df["y"] + (height / 2)

        df["x1"] = df["x"] * width / 100
        df["c1"] = abs(50 - df["y"]) * height / 100
        df["y1"] = (100 - df["y"]) * height / 100

        return df
