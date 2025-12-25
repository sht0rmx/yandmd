import importlib
import os
import pkgutil

from aiogram import Router

from utils.logging import logger

router = Router()

for _, name, _ in pkgutil.walk_packages([os.path.dirname(__file__)], prefix=__name__+ "."):
    logger.debug(f"Importing handler module: {name}")
    importlib.import_module(name)
