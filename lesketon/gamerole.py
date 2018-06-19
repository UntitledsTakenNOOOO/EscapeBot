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


class GameRole:
    """
    This is the base class for role types; will carry info on whether the role counts as an item,
    the item's use function, etc. Attributes can be passed down using object inheritance.

    botv must be loaded for this to work! Never invoke this before botv is created in on_ready!
    Ideally, the gamemaster object below will be the one to invoke this, because the gamemaster isn't
    created until botv is done.
    """

    def __init__(self, role):
        self.role = role
        self.name = role.name

    @property
    def isItem(self):
        return False
