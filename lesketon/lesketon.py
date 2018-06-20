#!/
# shebang goes here if you're gonna use a linux server^
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
from itemrole import ItemRole
from gameplayer import GamePlayer
from gamemaster import GameMaster

# ngl pretty much just copypasted harubot

def plurals(num):
    """
    returns s if plural or zero -- just a function I like to have around.
    Use case: f'{user.name} found {num} item{plurals(num)}!'
    """
    if num != 1:
        return ('s')
    return ('')


def yncheck(msg, *args):
    """
    yes/no prompt
    optional arg as True so as to avoid type confusion
    """
    if msg.content.lower() in 'y':
        return (True)
    elif msg.content.lower() in 'n':
        if args:
            return (False)
        return (True)


def numeralcheck(msg, *args):
    """
    numeral prompt
    optional arg as True so as to avoid type confusion with 0
    """
    try:
        num = int(msg.content)
        if num == 0 and not args:
            return ("done")
        return (num)
    except ValueError:
        if msg.content.lower() == "done":
            if args:
                return (0)
            return ("done")


class gamecommand:
    """
    Put into the function to create a session. You can use this to raise custom errors for things
    like 'you don't have the right item' or 'item is invalid'.
    """

    def __init__(self, name, interruptable, *, interruptmsg=False, requires=[]):
        self.name = name
        self.interruptable = interruptable
        if not interruptmsg:
            self.interruptmsg = (
                'You\'re currently resolving a {} command<channelline>. '
                'Please resolve that command first.'.format(self.name)
            )
        else:
            self.interruptmsg = interruptmsg
        self.requires = []

    @property
    def allowspm(self):
        return False

    @property
    def interrupts(self):
        return True


class nointerruptcommand(gamecommand):
    @property
    def interrupts(self):
        return False


gcTestCommand = gamecommand("Test Command", False)
gcGetItem = nointerruptcommand("Get Item", True)


class botcommand:
    def __init__(self, ctx, ctype):
        """
        data class for session object, carrying the ability to send messages and PMs and
        wait for messages.
        """
        self.setdefaults(ctx, ctype)
        self.player = botv.gm.get_player(ctx.message.author.id)
        if self.player.incommand:
            raise InCommandError
        if ctype.interrupts:
            self.player.startCommand(self)
        alist = ctx.message.content.split(' ')[1:]
        for obj in alist:
            a = botv.gm.get_player(re.sub(r'[<@!>]', '', obj), mentioncheck=True)
            if a:
                self.mentions.append(a)
            else:
                self.other.append(obj)

    def setdefaults(self, ctx, ctype):
        self.type = ctype
        self.ctx = ctx
        self.author = ctx.message.author
        self.id = ctx.message.author.id
        self.channel = ctx.message.channel
        self.ispm = False
        if self.channel.is_private:
            self.ispm = True
        self.player = None
        self.char = None
        self.invalidmention = False
        self.mentions = []
        self.other = []
        self.active = True
        self.ended = False
        self.waiting = False

    def changetype(self, type):
        self.type = type
        self.player.commandtype = type

    def changechannel(self, channel):
        self.channel = channel
        if isinstance(self.channel, discord.Member):
            self.ispm = True

    def cfunc(self, func):
        def rfunc(msg):
            if not self.ccheck(msg):
                return False
            else:
                return func(msg)

        return rfunc

    async def menu(self, func, *args):
        """
        Has the session wait for a response. Responses are sent through func() twice -- once during
        the built in command-check function for bot.wait_for_message, and one with any *args sent
        through.
        """
        self.waiting = True
        func2 = self.cfunc(func)
        while self.waiting:
            try:
                msg = await bot.wait_for_message(author=self.author, check=func2)
                if self.active and not self.ended:
                    self.waiting = False
                    return (func(msg, *args))
                elif self.ended:
                    self.waiting = False
                    raise CommandEndedError
                else:
                    pass
            except discord.HTTPException:
                pass

    def ccheck(self, msg):
        """
        Checks to see whether the message's channel, whatever it is,
        is correct
        """
        if msg.channel == self.channel or (msg.channel.is_private and self.ispm):
            return True
        return False

    async def fresp(self):
        """
        Has the session wait for a free response in the same channel with no qualifiers.
        This is to get things such as names.
        """
        self.waiting = True
        while self.waiting:
            try:
                msg = await bot.wait_for_message(author=self.author, check=self.ccheck)
                if self.active and not self.ended:
                    self.waiting = False
                    return (msg.content)
                elif self.ended:
                    self.waiting = False
                    raise CommandEndedError
                else:
                    pass
            except discord.HTTPException:
                pass

    async def pm(self, string, *, update=False):
        """
        Sends a PM to the session owner. If update=True, updates session.lastmessage.
        """
        said = False
        while not said:
            if not self.ended:
                for x in range(4):
                    try:
                        try:
                            await bot.send_message(self.author, string)
                        except discord.Forbidden:
                            await bot.send_message(self.channel, string)
                        said = True
                        if update and self.player:
                            self.player.updateMessage(string)
                        return
                    except (discord.HTTPException, OSError, aiohttp.ClientResponseError) as e:
                        print("Suffered", type(e), "error in botcommand.pm().")
                        print("info: ", string, self.player.id)
                        await asyncio.sleep(x ** x)
                self.end()
                raise CommandEndedError
            else:
                raise CommandEndedError

    async def say(self, string, *, update=True):
        """
        Sends a message in session.channel.
        """
        said = False
        while not said:
            if not self.ended:
                for x in range(4):
                    try:
                        msg = await bot.send_message(self.channel, string)
                        said = True
                        if update and self.player:
                            self.player.updateMessage(string)
                        return
                    except (discord.HTTPException, OSError, aiohttp.ClientResponseError) as e:
                        print("Suffered", type(e), "error in botcommand.say().")
                        print("info: ", string, self.channel.name, self.player.id)
                        await asyncio.sleep(x ** x)
                self.end()
                raise CommandEndedError
            else:
                raise CommandEndedError

    async def esay(self, string):
        """ as say, but end()s command afterwards. """
        said = False
        while not said:
            if not self.ended:
                for x in range(5):
                    try:
                        msg = await bot.send_message(self.channel, string)
                        self.end()
                        return
                    except (discord.HTTPException, OSError, aiohttp.ClientResponseError) as e:
                        print("Suffered", type(e), "error in botcommand.esay().")
                        print("info: ", string, self.channel.name, self.player.id)
                        await asyncio.sleep(x ** x)
                self.end()
            else:
                raise CommandEndedError

    async def dsay(self):
        """
        as esay, but always 'Done.'
        """
        await self.esay("Done.")

    def end(self):
        self.waiting = False
        self.ended = True
        if self.player.incommand == self:
            self.player.setdefaults()

    def pause(self):
        self.active = False

    def resume(self):
        self.active = True

    async def timeOut(self, dur):
        self.pause()
        await asyncio.sleep(dur)
        self.resume()


class botvars:
    """ 
    this class could hold all persistent bot variables. By default, it just holds an admin list and the
    default server; the deserialization process can be built to lock in all important roles and items.
    
    botv.admins is just a list of ids, only referenced by the isAdmin command. This is, of course.
    so you can manually override and test things.
    
    The information found by botvars will be fed into the GameMaster object, so that changing a role
    or an ID won't ruin a saved state.
    """

    """ metafunctions """

    def __init__(self, *, test=False):
        self.load()
        self.testver = test
        self.gm = GameMaster(self)

    def load(self):
        if exists("server\\botv.haru"):
            self.__dict__ = json.load(codecs.open("server\\botv.haru", "r", "utf-8"))
        else:
            self.server = "450764095260590080"
            self.ver = "0.0.0.1"
            self.admins = ['135561916566208512', '135574344712716288', '110204920719785984']
            self.accessroles = ['452924247254499348', '452924249796247552', '452924250802749440', '452924251691941888',
                                '452924252178350084']
            self.itemroles = ['456681710646460431']
            self.rooms = ['456673884222259212']
        self.deserialize()

    def save(self):
        codecs.open("server\\botv.haru", "w", "utf-8").write(json.dumps(self.serialized))

    def deserialize(self):
        self.server = discord.utils.get(bot.servers, id=self.server)
        for x in range(len(self.accessroles)):
            self.accessroles[x] = discord.utils.get(self.server.roles, id=self.accessroles[x])
        for x in range(len(self.itemroles)):
            self.itemroles[x] = discord.utils.get(self.server.roles, id=self.itemroles[x])

    @property
    def serialized(self):
        sav = deepcopy(self.__dict__)
        sav["server"] = sav["server"].id
        return sav

    """ standard checks """

    def isAdmin(self, user):
        """
        input a user object to find out if they're an admin -- returns True if so, False if not
        """
        if user.id in self.admins:
            return True
        return False

    """ standard functions """

    def purgeAll(self):
        pass


class RoomEscapeError(commands.CheckFailure):
    """
    Base class for exceptions, in case you want to make special exceptions in the commands
    exception handler. For more information on how to use this with the on_command_error handler,
    ask me. You shouldn't need this, but it's here if you do.
    """

    def __init__(self, *, msg=None):
        self.msg = msg

    @property
    def silent(self):
        return True


class CommandEndedError(RoomEscapeError):
    """ Raised by a session when someone starts a new command to end that session. """

    def __init__(self):
        self.msg = None


class NonPlayerError(RoomEscapeError):
    """ Raised if someone runs a command before being initialized as a player. """

    def __init__(self):
        self.msg = "You aren't a player."

    @property
    def silent(self):
        return False


class InCommandError(RoomEscapeError):
    """ Raised if someone runs a command while another command is unended. """

    def __init__(self):
        self.msg = "Please finish what you're doing before doing something new."

    @property
    def silent(self):
        return False


sys.stdout = io.TextIOWrapper(  # this is a workaround so I can run it in powershell because I'm lazy
    sys.stdout.detach(),
    encoding=sys.stdout.encoding,
    errors="backslashreplace",
    line_buffering=True
)

if "-test" in sys.argv:  # if in test version, use / instead of ~ as delimiter
    bot = commands.Bot(command_prefix='/')
    print('Alert: Running in Test Mode')
else:
    bot = commands.Bot(command_prefix='~')


@bot.event
async def on_command_error(error, ctx):  # ask me if you need this explained
    if isinstance(error, commands.NoPrivateMessage):
        await bot.send_message(ctx.message.author,
                         'This command cannot be used in private messages.')
    elif isinstance(error, commands.DisabledCommand):
        await bot.send_message(ctx.message.author,
                         'Sorry. This command is disabled and cannot be used.')
    elif isinstance(error, commands.CheckFailure):
        if error.silent:
            return
        if error.msg:
            await bot.send_message(ctx.message.channel, error.msg)
        else:
            player = botv.gm.players[ctx.message.author.id]
            msg = player.in_command_msg(ctx.message.channel)
            await bot.send_message(ctx.message.channel, msg)
    elif isinstance(error, commands.CommandInvokeError):
        print('In {0.command.qualified_name}:'.format(ctx), file=sys.stderr)
        traceback.print_tb(error.original.__traceback__)
        print(
            '{0.__class__.__name__}: {0}'.format(error.original),
            file=sys.stderr
        )


@bot.event
async def on_ready():
    """
    This runs once you've successfully logged in, so this is where we'll put all processes that
    identify and set specific rooms, roles, etc.
    """
    global botv
    print('------')
    print('Logged in as')
    print(bot.user.name)
    print(bot.user.id)
    print('------')
    print('Loading static/persistent variables.')
    botv = botvars(test="-test" in sys.argv)
    botv.gm.deserialize()
    print('Creating session.')
    print('------')
    # if you want to set a test version of the bot, this lets you
    # run the bot with the flag '-test' to instead run on the test version.


@bot.event
async def on_member_remove(member):
    """
    This runs any time a player leaves the server. If that player has important roles, it keeps
    the member object around for you to mess with and check.
    """
    pass


@bot.event
async def on_member_join(member):
    """
    This runs any time a new player enters the server. You can use this to do a lot of things, such
    as grouping them up and applying the first role/preparing them for the tutorial.
    """
    pass


@bot.event
async def on_message(message):
    """
    Whenever someone invokes something with the @bot.commands() decorator, the bot.process_commands
    function here will run it. The hacky way to get this to work with no delimiter is just to
    have a list of command words in the botv or generated by the command creation process, and just
    check to see if the message starts with one of those command words. If so, just...
    ... add the delimiter to the message before sending it through bot.process commands.
    """
    if message.channel.is_private:  # < makes PMs show up on command line
        sendto = ""
        if message.author.name == bot.user.name:
            sendto = "(-> {}) ".format(message.channel.user.name)
        print("{} {}{}: {}".format(str(datetime.datetime.now())[5:19], sendto, message.author.name, message.content))
    if message.content.startswith('~'):  # < makes commands case-insensitive
        a = message.content
        b = message.content.find(' ')
        if b != -1:
            c = message.content.replace(a[:b], a[:b].lower(), 1)
        else:
            c = message.content.lower()
        message.content = c
    await bot.process_commands(message)


"""BASIC COMMANDS EXAMPLES"""


@bot.command(pass_context=True)
async def hello(ctx):
    """
    Await all async commands. These are the different ways to send messages. 
    bot.say() only works within the bot.command() wrapper, so under normal circumstances, you'll
    want to pass channel down into any other function and use bot.send_message().
    """
    await bot.say("Hello, {}.".format(ctx.message.author.name))  # These two are equivalent within a bot.command
    await bot.send_message(ctx.message.channel, "I heard you.")  # These two are equivalent within a bot.command
    await asyncio.sleep(1)  # This can be used to pause for X time, in this case 1 second
    msg = await bot.send_message(ctx.message.author, "You can also do this.")
    await asyncio.sleep(1)
    await bot.delete_message(msg)  # bot.say and bot.send_message create message objects which you can do things with
    msg = await bot.send_message(ctx.message.author, "Too slow, it's gone.")
    await asyncio.sleep(5)
    await bot.edit_message(msg, msg.content + " But here's a consolation prize.")
    await bot.add_reaction(ctx.message, '👍')  # you can do the same stuff to the ctx.message object


@bot.command(pass_context=True, aliases=["go away", "begone"])
async def leave(ctx, *, check=""):
    """
    if an admin says 'leave now, bot', 'go away now, bot', or 'begone now, bot', the bot will leave.
    """
    #    if botv.isAdmin(ctx.message.author) and check == "now, bot":
    # if necessary, save checks can go here; check presently commented out because botv can
    # fail to initialize in testing
    await bot.say("Allan, please add dialogue!")
    quit()


@bot.command()
async def listroles():
    roles = botv.server.roles
    fstr = "Roles I can see:\n```json\n"
    n = 0
    for role in roles:
        n += 1
        fstr += str(n) + " - " + role.name
        for accessrole in botv.accessroles:
            if role == accessrole.role:
                fstr += " (appears to be an access role)"
        for ItemRole in botv.itemroles:
            if role == ItemRole.role:
                fstr += " (appears to be an item role)"
        fstr += "\n"
    fstr += "```"
    await bot.say(fstr)


@bot.command(pass_context=True)
async def basicynprompt(ctx):
    await bot.say("Are you going to answer this question with 'n'? *(y/n)*")
    msg = await bot.wait_for_message(  # There's a much better way to handle this, with a wrapper
        author=ctx.message.author, channel=ctx.message.channel, check=yncheck
    )  # But this is the basic functionality
    if msg.content == 'y':
        await bot.say("**Liar.**")
        await bot.add_reaction(msg, '🇳')
    else:
        await bot.say("**You fool.**")
        await bot.add_reaction(msg, '🇾')


# Now, to test basic functionality...

@bot.command(pass_context=True)
async def addplayer(ctx):
    if not botv.isAdmin(ctx.message.author):
        await bot.say("You are not set as an admin.")
        return
    else:
        fstr = "Added {} players to current session:\n"
        fcount = 0
        for player in ctx.message.mentions:
            fcount += 1
            botv.gm.add_player(player)
            fstr += player.name + "(" + player.id + ")\n"
        await bot.say(fstr.format(fcount))


@bot.command(pass_context=True)
async def basicbotcommand(ctx):
    bc = botcommand(ctx, gcTestCommand)
    await bc.esay("Working as intended.")


@bot.command(pass_context=True)
async def nonbasicbotcommand(ctx):
    bc = botcommand(ctx, gcTestCommand)
    await bc.say("Can you target this command with Wasteland? *(y/n)*")
    score = 0
    yn = await bc.menu(yncheck, True)
    if yn:
        score += 1
        await bc.say("Correct. Does Early Harvest untap this command? *(y/n)*")
    else:
        await bc.say("Incorrect. Does Early Harvest untap this command? *(y/n)*")
    yn = await bc.menu(yncheck, True)
    if yn:
        await bc.say("Incorrect. Your score is {}.".format(score))
    else:
        score += 1
        await bc.say("Correct. Your score is {}.".format(score))
    if not score:
        await bc.say("As punishment, you will be stuck in this command forever...")
    else:
        await bc.pm("Thank you for playing.")
        bc.end()


@bot.command(pass_context=True)
async def getitem(ctx):
    bc = botcommand(ctx, gcGetItem)
    if bc.ctx.message.role_mentions:
        for role in bc.ctx.message.role_mentions:
            print(role, botv.itemroles)
            for item in botv.itemroles:
                print(item)
            if role in botv.itemroles:
                await bc.player.getRole(role)
                await bc.say('Got item: \"{}!"'.format(role.name))
            else:
                await bc.say('{} doesn\'t appear to be an item role.'.format(role.name))
        bc.end()
    else:
        await bc.esay("No role mentions found.")


@bot.command(pass_context=True)
async def loseitem(ctx):
    bc = botcommand(ctx, gcGetItem)
    if bc.ctx.message.role_mentions:
        for role in bc.ctx.message.role_mentions:
            print(role, botv.itemroles)
            for item in botv.itemroles:
                print(item)
            if role in botv.itemroles:
                await bc.player.removeRole(role)
                await bc.say('Removed item: \"{}!"'.format(role.name))
            else:
                await bc.say('{} doesn\'t appear to be an item role.'.format(role.name))
        bc.end()
    else:
        await bc.esay("No role mentions found.")


@bot.command(pass_context=True)
async def giveitem(ctx):
    bc = botcommand(ctx, gcGetItem)
    player = bc.player
    if bc.mentions:
        if not player.items:
            await bc.esay("You have nothing to give.")
            return
        recip = bc.mentions[0]
        await bc.say("What would you like to give them?" + player.itemlist())
        n = await bc.menu(numeralcheck, True)
        if n > len(player.items):
            await bc.esay("You don't have that many items.")
        elif n:
            item = player.items[n - 1]
            await player.giveItem(item, recip)
            await bc.esay("Given item {} to {}!".format(item.name, recip.player.name))
        else:
            bc.dsay()
    else:
        await bc.esay("You need to mention a player to give an item to.")


@bot.command(pass_context=True)
async def ready(ctx):
    bc = botcommand(ctx)
    player = bc.player
    player.ready = not player.ready


if '-test' in sys.argv:
    bot.run("TEST VERSION OF THE BOT'S TOKEN GOES HERE")
else:
    bot.run('NDU2NTMwOTY2MzM3NTUyNDE1.DgN4aQ.ZRF8_sWj2V6_S25aSMiSV7SeQ7E')

if __name__ == "__main__":
