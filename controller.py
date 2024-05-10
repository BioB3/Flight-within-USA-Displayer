"""Controller for Flight within USA displayer"""
from model import FlightDataModel
from view import UI

class Controller:
    def __init__(self) -> None:
        self.__model = FlightDataModel()
        self.__view = UI(self)
        self.__model.attach(self.__view)

    @property
    def model(self):
        return self.__model

    @property
    def view(self):
        return self.__view

    def set_search_type(self, index: int):
        self.model.set_state(index)

    def avg_delay_flight(self):
        filt, week, time_blk = self.view.get_cur_tab().get_selected_filter()
        self.model.get_avg_data(filt, week, time_blk)

    def percent_on_time(self):
        filt, week, time_blk = self.view.get_cur_tab().get_selected_filter()
        self.model.get_on_time_data(filt, week, time_blk)

    def percent_time_blk(self):
        filt, week, time_blk = self.view.get_cur_tab().get_selected_filter()
        self.model.get_time_blk_data(filt, week, time_blk)

    def update_graph_stats(self, tab=None):
        if not tab:
            tab = self.view.get_cur_tab()
        tab.cur_graph(self.model.series)
        tab.update_text(self.model.info)

    def get_airport(self):
        """
        Return available airport ID
        """
        return self.model.df.groupby("ORIGIN")["DEST"].apply(set)

    def get_airline(self):
        """
        Return available airline ID
        """
        return sorted(self.model.df["OP_CARRIER_AIRLINE_ID"].unique())

    def data_story_telling_data(self):
        return self.model.get_data_story_telling_data()

    def create_default_view(self):
        tab_list = list(self.view.tabs.values())
        for count in range(len(tab_list)):
            tab = tab_list[count]
            self.view.notebook.select(tab)
            self.set_search_type(count)
            filt, week, time_blk = tab.get_selected_filter()
            self.model.get_avg_data(filt, week, time_blk)
        self.view.notebook.select(tab_list[0])

    def run(self):
        self.__view.run()
