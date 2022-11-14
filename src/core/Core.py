import importlib
import os

from config import APP_PATH

"""
    Class responsible for opening controllers
"""


class Core:
    # -----------------------------------------------------------------------
    #        Methods
    # -----------------------------------------------------------------------
    """
        Given a controller name, return an instance of it
    
        @param controller:string Controller to be opened
    """

    @staticmethod
    def openController(controller):
        response = None

        # Set controller name
        controller = controller[0].upper() + controller[1:]
        controllerName = controller + "Controller"

        # Check if file exists
        if os.path.exists(APP_PATH + "/controllers/" + controllerName + ".py"):
            module = importlib.import_module("controllers." + controllerName)
            class_ = getattr(module, controllerName)
            response = class_()

        return response
