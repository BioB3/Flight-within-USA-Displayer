"""Main part to start Flight within USA displayer app"""
from controller import Controller

if __name__ == "__main__":
    flight_displayer = Controller()
    flight_displayer.create_default_view()
    flight_displayer.run()