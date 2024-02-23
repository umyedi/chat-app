"""

Ce fichier gère les paramètres de logging.

"""
import sys
import logging


logger = logging.getLogger()
logger.setLevel(logging.INFO)

formatter = logging.Formatter("[%(asctime)s] %(levelname)s:%(filename)s:%(lineno)d:%(message)s", "%Y-%m-%d %H:%M:%S")
level = logging.DEBUG

stdout_handler = logging.StreamHandler(sys.stdout)
stdout_handler.setLevel(level)
stdout_handler.setFormatter(formatter)

file_handler = logging.FileHandler("server.log")
file_handler.setLevel(level)
file_handler.setFormatter(formatter)

logger.addHandler(file_handler)
logger.addHandler(stdout_handler)
