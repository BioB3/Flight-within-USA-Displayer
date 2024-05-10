"""Controller for Flight within USA displayer"""
from model import FlightDataModel
from view import UI

class Controller:
    """
    Controller that interact with model and view
    """
    def __init__(self) -> None:
        self.__model = FlightDataModel()
        self.__view = UI(self)
        self.__model.attach(self.__view)

    @property
    def model(self):
        """
        Getter for model attribute.
        """
        return self.__model

    @property
    def view(self):
        """
        Getter for view attribute.
        """
        return self.__view

    def set_search_type(self, index: int):
        """
        Set the search state of the model
        : param index : the index of the selected search state
        """
        self.model.set_state(index)

    def avg_delay_flight(self):
        """
        Call the model's get_avg_data method using selected filter as parameters
        """
        filt, week, time_blk = self.view.get_cur_tab().get_selected_filter()
        self.model.get_avg_data(filt, week, time_blk)

    def percent_on_time(self):
        """
        Call the model's get_on_time_data method using selected filter as parameters
        """
        filt, week, time_blk = self.view.get_cur_tab().get_selected_filter()
        self.model.get_on_time_data(filt, week, time_blk)

    def percent_time_blk(self):
        """
        Call the model's get_time_blk_data method using selected filter as parameters
        """
        filt, week, time_blk = self.view.get_cur_tab().get_selected_filter()
        self.model.get_time_blk_data(filt, week, time_blk)

    def update_graph_stats(self, tab=None):
        """
        Update the graph in the UI graph frame
        : param tab : the tab that contains graph to be updated
        """
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
        return sorted(self.model.df["OP_CARRIER_AIRLINE_ID"].apply(str).unique())

    def data_story_telling_data(self):
        """
        Return data needed for data storytelling page
        """
        return self.model.get_data_story_telling_data()

    def run(self):
        """
        Run the app
        """
        self.__view.run()
