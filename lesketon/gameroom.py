#!/
# I don't need all of these imports (or any of them), but I'm paranoid.
import discord  # discord api packages
from discord.ext import commands  # bot commands
import random  # simple random number generator
import datetime  # date and time module
from os.path import exists  # easy check if a file exists
import codecs  # for printing of utf-8 characters
import sys
import io
import json  # for save serialization
import traceback  # error handling
import asyncio  # asyncio.sleep() mostly
import re  # regex for command interpretation
import time  # simpler time module
from discord import opus  # for voice modules
import os  # os
import math  # gotta have sqrt()
import statistics  # and some other stuff
import logging
import shutil
import aiohttp
from copy import deepcopy


class GameRoom:
    """
    This is the GameRoom class.

    This Docstring should be fully detailed when this class is actually more than just a blank constructor.
    """

    def __init__(self):
        # I don't know what the constructor needs rn
