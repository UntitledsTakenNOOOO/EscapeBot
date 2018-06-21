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

    Contains an ID (its snowflake) for access purposes, a (potentially empty) list of items,
    and a function that could correspond to any number of puzzles relevant to the room.
    """

    def __init__(self, id, description, items, fixtures, func):
        #you can take items, fixtures are room objects you can examine or use.
        self.id = id
        self.description = description
        self.items = items
        self.fixtures = fixtures
        self.func = func

    def run(self, *args):
    	#takes whatever function we pass it, which will be one of many puzzles.
        self.func(args)

