"""Main part to start Flight within USA displayer app"""
from model import FlightDataModel
from view import UI
from controller import Controller

if __name__ == "__main__":
    flight_model = FlightDataModel()
    flight_controller = Controller(flight_model)
    flight_ui = UI(flight_controller)
    flight_controller.view = flight_ui
    flight_controller.run()
