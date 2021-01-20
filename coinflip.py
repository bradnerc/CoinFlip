from discord.ext import commands
from dotenv import load_dotenv
from PIL import Image
from io import BytesIO
import discord
import random
import re
import requests
import json
import os
import urllib.request

#TODO: Change messages to embed box

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.messages = True
bot = commands.Bot(command_prefix = '$', intents = intents)
user_list = []
revealvalues = []
channel_ID = ""
message_dict = {}

@bot.command(name = 'flip',
             brief = 'Flip a coin',
             help = "Flips a single coin")
async def coinflip(ctx):
    
    toEmbed=discord.Embed(color=0x1ae671)
    var = random.randint(0,1)

    if var == 0:
        toEmbed.add_field(name = "Results", value = "The coin landed on HEADS!", inline = True)
    else :
        toEmbed.add_field(name="Results", value= "The coin laned on TAILS!", inline=True)

    sent = await ctx.send(embed = toEmbed)

@bot.command(name = 'flips',
             brief = "Flip n number of coins",
             help = '''Given n number of coins, determines how many of those
             coins will land on HEADS''')
async def multicoinflip(ctx, num:int):
    
    res = 0
    rec = num

    while num > 0:
        var = random.randint(0,1)
        num-= 1
        if var == 0:
            res+=1

    toEmbed=discord.Embed(color=0x1ae671)
    toEmbed.add_field(name = "Results", value = str(res) + ' coins landed HEADS out of ' + str(rec))

    await ctx.send(embed = toEmbed)

@bot.command(name = 'until',
             brief = 'Flips coins until a TAILS appears',
             help = '''Flips a coin and if HEADS, repeat until a coin lands on TAILS''')
async def flipuntil(ctx):
    toEmbed=discord.Embed(color=0x1ae671)
    res = 0
    var = random.randint(0,1)

    if var == 0:
        toEmbed.add_field(name = "Results", value = 'You got zero HEADS in a row!')
        await ctx.send(embed = toEmbed)

    while var == 1:
        res+=1
        var = random.randint(0,1)

    if res != 0:
        toEmbed.add_field(name = "Results", value = str(res) + ' coins landed HEADS in a row')
        await ctx.send(embed = toEmbed)

@bot.command(name = 'random',
             brief = 'Randomly picks a number between two given numbers',
             help = '''Randomly picks a number between two given numbers, where
             num1 < num2''')
async def pickrand(ctx, args1:int, args2:int):
    if args1 < args2:
        var = random.randint(int(args1), int(args2))
        toEmbed=discord.Embed(color=0x1ae671)
        toEmbed.add_field(name = "Results", value = 'The randomly picked number is: ' + str(var))
        await ctx.send(embed = toEmbed)

@bot.command(name = 'roll',
             brief = 'Rolls a number between 1 and the given number',
             help = 'Rolls a number between 1 and the given number')
async def roll(ctx, args:int):
    var = random.randint(1, int(args))
    toEmbed=discord.Embed(color=0x1ae671)
    toEmbed.add_field(name = "Results", value = str(var) + ' was the result of your roll.')
    await ctx.send(embed = toEmbed)
    
@bot.command(name = 'test',
             brief = 'A method for people to choose a number in secret',
             help = '''The bot will DM the listed users for their answers, and once
                    all users have replied, will send a message on the channel with
                    the answers''')
async def reveal(ctx, *args):
    global channel_ID
    await bot.wait_until_ready()
    for var in args:
        userRegex = re.compile(r'^[^#]+')
        username = userRegex.search(var)
        discrimRegex = re.compile(r'[#\d]+')
        discrim = discrimRegex.search(var)
        testdiscrim = discrim.group()[slice(1,len(discrim.group()),1)]
        temp = discord.utils.get(bot.get_all_members(),
                                 name=str(username.group()),
                                 discriminator=str(testdiscrim)).id
        user =  bot.get_user(temp)
        user_list.append(user)
        await user.send("What number will you pick?")
    channel_ID = ctx.channel.id

@bot.event
async def on_message(message):
        if isinstance(message.channel, discord.channel.DMChannel) and message.author != bot.user:
            if len(user_list) != 0:
                await message.channel.send('Duly Noted')
                revealvalues.append(message.author.name + ' chose ' + message.content + '!')
                user_list.remove(message.author)
                if(len(user_list) == 0):
                    await bot.wait_until_ready()
                    channel = bot.get_channel(int(channel_ID))
                    await channel.send(revealvalues)
        await bot.process_commands(message)

@bot.command(name = 'find',
             brief = 'Lookup a Magic the Gathering Card',
             help = '''Lookup a Magic the Gathering Card. If there are no results
                    this will return nothing''')
async def findCard(ctx, *args):
    global message_dict
    search = ""
    for name in args:
        search += str(name) + " "
    findImage = lookUpCard(search, 0)
    getImage = findImage[0]
    toEmbed=discord.Embed(title = "Card Search Results", color=0x1ae671)
    toEmbed.set_image(url=getImage)
    toEmbed.set_footer(text = "(1\\" + str(findImage[2]) + ")")
    test = await ctx.send(embed = toEmbed)
    await test.add_reaction('⬅')
    await test.add_reaction('➡️')
    message_dict[test.id] = [search, 0]

@bot.event
async def on_raw_reaction_add(payload):
    global message_dict
    if payload.user_id != bot.user.id:
        this_ID = payload.message_id
        ID_res = message_dict.get(this_ID)
        val = ID_res[1]
        if str(payload.emoji) == '⬅':
            val = ID_res[1] - 1
        if str(payload.emoji) == '➡️':
            val = ID_res[1] + 1
        args = ID_res[0]
        print(str(val) + "THIS IS VAL")
        message_dict.update({int(this_ID) : [args, val]})
        findImage = lookUpCard(args, val, int(this_ID))
        print(findImage)
        getimage = findImage[0]
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        thisEmbed = message.embeds[0]
        thisEmbed.set_image(url = getimage)
        thisEmbed.set_footer(text = "(" + str(findImage[1]+1) + "\\" + str(findImage[2]) + ")")
        await message.edit(embed = thisEmbed)

@bot.event
async def on_raw_reaction_remove(payload):
    global message_dict
    if payload.user_id != bot.user.id:
        this_ID = payload.message_id
        ID_res = message_dict.get(this_ID)
        val = ID_res[1]
        if str(payload.emoji) == '⬅':
            val = ID_res[1] - 1
        if str(payload.emoji) == '➡️':
            val = ID_res[1] + 1
        args = ID_res[0]
        message_dict.update({int(this_ID) : [args, val]})
        findImage = lookUpCard(args, val, int(this_ID))
        getimage = findImage[0]
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        thisEmbed = message.embeds[0]
        thisEmbed.set_image(url = getimage)
        thisEmbed.set_footer(text = "(" + str(findImage[1]+1) + "\\" + str(findImage[2]) + ")")
        await message.edit(embed = thisEmbed)

def lookUpCard(cardName, num, *args):
#args = optional parameter which tracks the message id
#num = index position
    global message_dict
    response = requests.get("https://api.scryfall.com/cards/search?q=" + cardName)
    data = response.json()
    data2 = data['data']
    if len(args) != 0:
        if num <  0:
            num = len(data2) - 1
            message_dict.update({int(args[0]) : [cardName, num]})
        if num > len(data2) - 1:
            num = 0
            message_dict.update({int(args[0]): [cardName, num]})
    res = data2[num]
    res2 = res['image_uris']
    getimage = res2['normal']
    return [getimage, num, len(data2)]

@bot.command(name = 'price')
# command to find price of given card
async def lookUpPrice():
    return

@bot.command(name = "planechase")
async def planeChase(ctx):
    response = requests.get("https://api.scryfall.com/cards/search?q=layout%3Aplanar")
    data = response.json()
    print(type(data))
    data2 = data['data']
    print(len(data2))
    print(type(data2))
    print(data2[0])
    res = data2[0]
    res2 = res['image_uris']
    getimage = res2['large']
    image = Image.open(urllib.request.urlopen(getimage))
    image = image.rotate(270, expand = True)
    print(type(image))
    with BytesIO() as image_binary:
        image.save(image_binary, 'PNG')
        image_binary.seek(0)
        sent = await ctx.send(file=discord.File(fp=image_binary, filename='image.png'))
    await sent.add_reaction('\N{LEFTWARDS BLACK ARROW}')
    await sent.add_reaction('\N{BLACK RIGHTWARDS ARROW}')

#TODO: shuffle the order of dict
    
bot.run(TOKEN)
