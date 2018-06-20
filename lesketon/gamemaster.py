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
from gameplayer import GamePlayer
from itemrole import ItemRole
from gamerole import GameRole


class GameMaster:
    """
    this class will hold all gamestate-related bot variables, and anything one might use to
    change them. GameMaster has a seperate save() function to botv below -- its saves will be
    used to restore the game state in case the need arises, such as if the internet flickers.
    """

    """ metafunctions """

    def __init__(self, botv):
        self.botv = botv
        if exists("save\\save.haru"):
            print("Gamemaster detected a saved session. Attempt to resume session? *(y/n)*")
            yn = input(">")
            if yn == 'y':
                self.load(botv, session = "save\\save.haru")
        else:
            self.load(botv)

    def load(self, botv, *, session=False):
        if session:
            # CODE TO RESUME SESSION WILL GO HERE -- I can help with this if necessary
            pass
        else:
            self.players = {}
        self.accessroles = list(self.botv.accessroles)
        self.itemroles = list(self.botv.itemroles)
        self.rooms = list(self.botv.rooms)
        self.server = botv.server

    def deserialize(self):
        for x in range(len(self.accessroles)):
            self.accessroles[x] = GameRole(self.accessroles[x])
        for x in range(len(self.itemroles)):
            self.itemroles[x] = ItemRole(self.itemroles[x])

    def save(self):
        pass
        # Save function goes here

    def get_player(self, id, *, mentioncheck=False):
        if id not in self.players:
            print(id, self.players)
            if mentioncheck:
                return None
            raise lesketon.NonPlayerError
        return self.players[id]

    def add_player(self, player):
        if player.id not in self.players:
            self.players[player.id] = GamePlayer(player)
            return "New player ({}) successfully added.".format(player.id)
        else:
            return "Player of id {} already registered.".format(player.id)

    async def mass_take_role(self, role):
        """
        Might want a try/catch
        """
        for player in self.players:
            if role.role in self.players[player].player.roles:
                await lesketon.bot.remove_roles(self.players[player].player, role.role)

    async def mass_give_role(self, role):
        for player in self.players:
            if role.role not in self.players[player].player.roles:
                await lesketon.bot.add_roles(self.players[player].player, role.role)


import lesketon
