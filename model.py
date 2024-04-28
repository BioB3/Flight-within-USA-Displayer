"""Model to handle data processing for Flight within USA displayer"""
import os
import pandas as pd

class Model:
    def __init__(self) -> None:
        self.__df = self.gen_df()

    def gen_df(self):
        """
        Read csv files as dataframe, join them and clean the data.
        Return: a dataframe consists of data from 2 datasets
        """
        df1 = pd.read_csv(os.path.join(os.getcwd(), "datasets/Jan_2020_ontime.csv"))
        df2 = pd.read_csv(os.path.join(os.getcwd(), "datasets/Airline_dataset.csv"))
        df1["ORIGIN"] = df1["ORIGIN"].str.replace('"','')
        df1["DEST"] = df1["DEST"].str.replace('"','')
        df2["FL_DATE"] = pd.to_datetime(df2["FL_DATE"], format="%m/%d/%y")
        df1["FL_DATE"] = "1/" + df1["DAY_OF_MONTH"].astype(str) + "/20"
        df1["FL_DATE"] = pd.to_datetime(df1["FL_DATE"], format="%m/%d/%y")
        df3 = pd.merge(df1, df2, how="left",
                             left_on=["ORIGIN","DEST","DEP_TIME","ARR_TIME","FL_DATE"],
                             right_on=["ORIGIN_AIRPORT","DEST_AIRPORT","DEP_TIME","ARR_TIME","FL_DATE"])
        df3["DEP_TIME_BLK"] = ["Early Morning" if 400 <= x < 800 else
                               ("Morning" if 800 <= x < 1200 else
                                ("Afternoon" if 1200 <= x < 1600 else
                                 ("Evening" if 1600 <= x < 1900 else
                                  ("Night" if x >= 1900 or x < 400 else None))))
                               for x in df3["DEP_TIME"]]
        df3["STATUS"] = ["Delayed" if x1 else
                         ("Diverted" if x2 else
                          ("Canceled" if x3 else "On-time"))
                         for x1, x2, x3 in zip(df3["DEP_DEL15"],
                                               df3["DIVERTED"],
                                               df3["CANCELLED"])]
        df3.drop(df3.columns[df3.columns.str.contains('unnamed',case = False)],
                       axis=1, inplace=True)
        df3.drop(["AIRLINE_ID","ORIGIN_AIRPORT","DEST_AIRPORT"], axis=1, inplace=True)


if __name__ == "__main__":
    data = Model()
