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
from itemrole import ItemRole
from gamerole import GameRole
from lesketon import bot


class GamePlayer:
    def __init__(self, player):
        self.id = player.id
        self.player = player
        self.set_defaults()

    def set_defaults(self):
        self.incommand = False
        self.commandtype = False
        self.lastmessage = None
        self.channel = None
        self.ready = False

    def update_message(self, fstr):
        self.lastmessage = fstr

    def in_command_msg(self, channel):
        """
        only called if character is in a command
        """
        a = self.commandtype.interruptmsg
        if "<channelline>" in a:
            if channel == self.channel:
                a = a.replace("<channelline>", "")
            elif channel.name and not self.channel.name:
                a = a.replace("<channelline>", " in PM")
            else:
                a = a.replace("<channelline>", " in {}".format(self.channel.name))
        return (a)

    @property
    def items(self):
        fl = []
        for role in self.player.roles:
            if role in botv.itemroles:
                fl.append(role)
        return fl

    def item_list(self, filter=None):
        if not self.items:
            return "You have no items."
        fstr = "```json\n"
        n = 0
        for item in self.items:
            n += 1
            fstr += str(n) + " - " + item.name + "\n"
        fstr += "```"
        return fstr

    def start_command(self, command):
        """
        assumes command is valid
        """
        if command.type.interrupts:
            self.incommand = command
            self.commandtype = self.incommand.type
            self.channel = command.channel

    def end_command(self, command):
        if self.incommand is command:
            self.incommand.end()
            self.set_defaults()

    async def give_item(self, item, recip):
        """ Assumes checks have been made! This can be altered to not do so. """
        await
        bot.remove_roles(self.player, item)
        await
        bot.add_roles(recip.player, item)

    async def get_role(self, role):
        if role not in self.player.roles:
            await
            bot.add_roles(self.player, role)

    async def remove_role(self, role):
        if role in self.player.roles:
            await
            bot.remove_roles(self.player, role)
