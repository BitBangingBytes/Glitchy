# -*- encoding:utf-8 -*-
from core.Core import Core
import sys
import logging
"""
    Main class. Responsible for running the application.
"""


class Main:
    @staticmethod
    def run():
        try:
            app = Core.openController("Glitchy")
            app.main()
        except Exception as e:
            print(str(e))


if __name__ == '__main__':
    # For a LOT of debugging information, set the logging level to DEBUG
    # For Informational messages, set the logging level to INFO
    # For Warning messages, set the logging level to WARNING
    logging.basicConfig(stream=sys.stdout, level=logging.WARNING)
    Main.run()
