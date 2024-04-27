"""Model to handle data processing for Flight within USA displayer"""
import os
import pandas as pd

class Model:
    def __init__(self) -> None:
        self.gen_df()

    def gen_df(self):
        df1 = pd.read_csv(os.path.join(os.getcwd(), "datasets/Jan_2020_ontime.csv"))
        df2 = pd.read_csv(os.path.join(os.getcwd(), "datasets/Airline_dataset.csv"))
        df1.rename(columns={'"DAY_OF_MONTH"': "DAY_OF_MONTH",
                            '"DAY_OF_WEEK"': "DAY_OF_WEEK",
                            '"OP_CARRIER_AIRLINE_ID"': "OP_CARRIER_AIRLINE_ID",
                            '"ORIGIN"': "ORIGIN",
                            '"DEST"': "DEST",
                            '"DEP_TIME"': "DEP_TIME",
                            '"DEP_DEL15"': "DEP_DEL15",
                            '"ARR_TIME"': "ARR_TIME",
                            '"ARR_DEL15"': "ARR_DEL15",
                            '"CANCELLED"': "CANCELLED",
                            '"DIVERTED"': "DIVERTED",
                            '"DISTANCE"': "DISTANCE"})
        df1["ORIGIN"] = df1["ORIGIN"].str.replace('"','')
        df1["DEST"] = df1["DEST"].str.replace('"','')
        df2["FL_DATE"] = pd.to_datetime(df2["FL_DATE"], format="%m/%d/%y")
        df1["FL_DATE"] = "1/" + df1["DAY_OF_MONTH"].astype(str) + "/20"
        df1["FL_DATE"] = pd.to_datetime(df1["FL_DATE"], format="%m/%d/%y")
        joined_df = pd.merge(df1, df2, how="left",
                             left_on=["ORIGIN","DEST","DEP_TIME","ARR_TIME","FL_DATE"],
                             right_on=["ORIGIN_AIRPORT","DEST_AIRPORT","DEP_TIME","ARR_TIME","FL_DATE"])
        joined_df.drop(joined_df.columns[joined_df.columns.str.contains('unnamed',case = False)],
                       axis = 1, inplace = True)
        joined_df.dropna(subset=["ARR_DELAY"], inplace=True)
        print(joined_df.isnull().sum())


if __name__ == "__main__":
    data = Model()