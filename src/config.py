# -*- encoding:utf-8 -*-
import os

global APP_PATH
# Take fixed file path, and not the relative file path
APP_PATH = os.path.dirname(os.path.realpath(__file__))
