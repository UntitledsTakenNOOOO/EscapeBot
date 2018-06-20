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
from gamerole import GameRole


class ItemRole(GameRole):
    """
    For the item roles, you'll pass an asynchronous function down through set_use, with no ().
    Then, when someone uses an item, you simply run it as

    await <itemrole>.use(ctx)

    and otherwise treat it like a normal session/command. If you want a more dedicated session
    system like HaruBot's, I can do that, but it's a lot more moving parts for little benefit
    so long as item uses aren't incredibly complex.

    You can also just add a task to the bot.loop() with this, so you can inject more stability into
    it where absolutely necessary if you go the lazy route.
    """

    def is_item(self):
        return True

    def set_use(func):
        self.use = func
