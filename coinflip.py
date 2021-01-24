from discord.ext import commands
from discord import Game
from dotenv import load_dotenv
from PIL import Image
import discord
import random
import re
import requests
import json
import os
import urllib.request
import planechase_images

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
WOLFRAM = os.getenv('WOLFRAM')
intents = discord.Intents.default()
intents.members = True
intents.reactions = True
intents.messages = True
bot = commands.Bot(command_prefix = '$', intents = intents)
user_list = []
channel_ID = ""
wra = {}
price_dict = {}
planechase_list = []
card_set = {}
secret_message = discord.Embed(title= "The hidden values", color=0x1ae671)

@bot.command(name = 'flip',
             brief = 'Flip a coin',
             help = "Flips a single coin")
async def coinflip(ctx):
    
    toEmbed=discord.Embed(color=0x1ae671)
    var = random.randint(0,1)

    if var == 0:
        toEmbed.add_field(name = "Results", value = "The coin landed on HEADS!", inline = True)
    else :
        toEmbed.add_field(name="Results", value= "The coin landed on TAILS!", inline=True)

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

@bot.command(name = 'pRoll',
             brief = 'Rolls the planar die',
             help = '''4 sides of the die are blank, 1 side has the planeswalker symbol,
             and the last side has the chaos symbol''')
async def rollPlanar(ctx):
    toEmbed = discord.Embed(color=0x1ae671)
    res = random.randint(1,6)
    if res == 1:
        toEmbed.add_field(name="Rolling the Planar Die", value = 'You rolled the Chaos symbol!')
        toEmbed.set_thumbnail(url ='https://i.ibb.co/xjPdVbc/output-onlinepngtools.png')
    elif res == 6:
        toEmbed.add_field(name="Rolling the Planar Die", value = 'You rolled the Planeswalker symbol!')
        toEmbed.set_thumbnail(url = 'https://i.ibb.co/MG1Kx6n/output-onlinepngtools-1.png')
    else:
        toEmbed.add_field(name='Rolling the Planar Die', value = 'Nothing happened.')
    await ctx.send(embed = toEmbed)
    
@bot.command(name = 'secret',
             brief = 'A method for people to choose a number in secret',
             help = '''The bot will DM the listed users for their answers, and once
                    all users have replied, will send a message on the channel with
                    the answers''')
async def reveal(ctx, *args):
    global channel_ID
    global revealvalues
    secret_message.clear_fields()
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
    global secret_message
    if isinstance(message.channel, discord.channel.DMChannel) and message.author != bot.user:
        if len(user_list) != 0:
            temp = message.author
            secret_message.add_field(name= "...", value = temp.mention + "\n" + message.content, inline= True)
            await message.channel.send('Duly Noted')
            user_list.remove(message.author)
            if(len(user_list) == 0):
                await bot.wait_until_ready()
                channel = bot.get_channel(int(channel_ID))
                await channel.send(embed = secret_message)
    await bot.process_commands(message)

@bot.event
async def on_raw_reaction_add(payload):
    await react(payload)

@bot.event
async def on_raw_reaction_remove(payload):
    await react(payload)
                    
async def react(payload):
    if payload.user_id != bot.user.id:
        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        this_ID = payload.message_id
        if message.author == bot.user:
            if message.embeds[0].title == "WolframAlpha Search":
                if str(payload.emoji) == '⬅':
                    await nextHowl(message, "-")
                if str(payload.emoji) == '\N{BLACK RIGHTWARDS ARROW}':
                    await nextHowl(message, "+")
            elif message.embeds[0].title == "Card Price Results":
                if str(payload.emoji) == '⬅':
                    await nextPrice(message, "-")
                if str(payload.emoji) == '\N{BLACK RIGHTWARDS ARROW}':
                    await nextPrice(message, "+")
                if str(payload.emoji) == '\N{WHITE HEAVY CHECK MARK}':
                    await fetchPrices(message)
            elif message.embeds[0].title == "Planechase":
                if str(payload.emoji) == '⬅':
                    await nextPlane(message, "-")
                if str(payload.emoji) == '\N{BLACK RIGHTWARDS ARROW}':
                    await nextPlane(message, "+")
            else:
                if str(payload.emoji) == '⬅':
                    await nextCardPrice(message, "-")
                if str(payload.emoji) == '\N{BLACK RIGHTWARDS ARROW}':
                    await nextCardPrice(message, "+")

@bot.command(name = 'card',
             brief = 'Look up a Magic the Gathering card',
             help = '''Looks up a Magic the Gathering card. If more than one match is returned, select your
                       card using the green checkmark. Each print variant will be given, along with the set name
                       and card price in USD.''')
async def findCard(ctx, *args):
    # if user reacts to current card with a checkmark, then
    # outputs all variants of card with corresponding set and price information
    # add response for when there is exactly only one card with that name
    # price_dict -> key = message.id, values = card name, image url, length of search index
    global price_dict
    image_urls = []
    card_name = []
    search = ""
    for name in args:
        search += str(name)
    response = requests.get("https://api.scryfall.com/cards/search?q=" + search)
    data = response.json()
    if len(data['data']) == 1:
        toEmbed=discord.Embed(title = "Processing", color=0x1ae671)
        message = await ctx.send(embed = toEmbed)
        image_urls.append(data['data'][0]['image_uris']['large'])
        cardname = data['data'][0]['name']
        cardname =cardname.replace(" ", "")
        card_name.append(cardname)
        price_dict[message.id] = (image_urls, card_name, 0)
        await fetchPrices(message)
        await message.add_reaction('\N{LEFTWARDS BLACK ARROW}')
        await message.add_reaction('\N{BLACK RIGHTWARDS ARROW}')
        await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')
        return
    for i in range(0, len(data['data'])):
        image_urls.append(data['data'][i]['image_uris']['large'])
        cardname = data['data'][i]['name']
        cardname = cardname.replace(" ", "")
        card_name.append(cardname)
    toEmbed = discord.Embed(title = "Card Price Results", color=0x1ae671)
    toEmbed.set_image(url = data['data'][0]['image_uris']['large'])
    toEmbed.set_footer(text = "(1\\" + str(len(data['data'])) + ")")
    message = await ctx.send(embed = toEmbed)
    price_dict[message.id] = [image_urls, card_name, 0]
    await message.add_reaction('\N{LEFTWARDS BLACK ARROW}')
    await message.add_reaction('\N{BLACK RIGHTWARDS ARROW}')
    await message.add_reaction('\N{WHITE HEAVY CHECK MARK}')

#cycle through cards to find the correct one to fetch prices for
async def nextPrice(message, value):
    global price_dict
    if value == "-":
        price_dict[message.id][2] -= 1
    else:
        price_dict[message.id][2] -= 1
    price_dict[message.id][2] = cycleIndex(price_dict[message.id][2], len(price_dict[message.id][1])-1)
    message.embeds[0].set_image(url = price_dict[message.id][0][price_dict[message.id][2]])
    message.embeds[0].set_footer(text = "(" + str((price_dict[message.id][2])+1) + "\\" +
                                 str(len(price_dict[message.id][1])) + ")")
    await message.edit(embed = message.embeds[0])

#card_set = list of set names, list of card images, list of prices, index location
async def nextCardPrice(message, val):
    global card_set
    if val == "-":
        card_set[message.id]['index'] -= 1
    else:
        card_set[message.id]['index'] += 1
    card_set[message.id]['index'] = cycleIndex(card_set[message.id]['index'],
                                               len(card_set[message.id]['image_uris'])-1)
    index = card_set[message.id]['index']
    message.embeds[0].set_image(url = card_set[message.id]['image_uris'][index])
    message.embeds[0].set_footer(text = card_set[message.id]['set_name'][index] + "\n" +
                                 "Non-foil: " + card_set[message.id]['prices'][index] + "\n"
                                 + "Foil: " + card_set[message.id]['foil'][index] + "\n"
                                 + "(" + str(card_set[message.id]['index']+1) + "\\" +
                                 str(len(card_set[message.id]['image_uris'])) + ")")
    await message.edit(embed = message.embeds[0])
    
# once card is confirmed, gets all variants of that card with corresponding price information
# is called when reacting to appropriate message with a green checkmark
# index is index of price_dict for the correct card
# card_set = list of set names, list of card images, list of prices, index location
async def fetchPrices(message):
    global price_dict
    global card_set
    response = requests.get("https://api.scryfall.com/cards/search?q=" +
                            price_dict[message.id][1][price_dict[message.id][2]] + "+unique%3Aprints")
    data = response.json()
    data2 = data['data']
    cardsList = []
    set_names = []
    prices = []
    foil_prices = []
    card_info = {}
    for i in range(len(data2)):
        cardsList.append(data2[i]['image_uris']['large'])
        set_names.append(data2[i]['set_name'])
        prices.append(str(data2[i]['prices']['usd']))
        foil_prices.append(str(data2[i]['prices']['usd_foil']))
    card_info['index'] = 0
    card_info['image_uris'] = cardsList
    card_info['set_name'] = set_names
    card_info['prices'] = prices
    card_info['foil'] = foil_prices
    card_set[message.id] = card_info
    toEmbed = discord.Embed(title = data2[0]['name'])
    toEmbed.set_footer(text = card_set[message.id]['set_name'][0] + "\n" +
                       "Non-foil: " + card_set[message.id]['prices'][0] + "\n" +
                       "Foil: " + card_set[message.id]['foil'][0] + "\n" +
                       "(1\\" + str(len(card_set[message.id]['image_uris'])) + ")")
    toEmbed.set_image(url = card_set[message.id]['image_uris'][0])
    message.embeds[0] = toEmbed
    await message.edit(embed = message.embeds[0])
                          
@bot.command(name = "planechase",
             brief = "A deck containing Magic the Gathering Planechase cards",
             help = 'A randomized order of all 86 Planechase related cards')
async def planeChase(ctx):
    global planechase_list
    response = requests.get("https://api.scryfall.com/cards/search?q=layout%3Aplanar")
    data = response.json()
    data2 = data['data']
    cardsList = []
    for i in range(len(data2)):
        cardsList.append(data2[i]['image_uris']['large'])
    planechase_list.append(cardsList)
    planechase_list.append(0)
    random.shuffle(planechase_list[0])
    getimage = planechase_list[0][0]
    toEmbed=discord.Embed(title = "Planechase", color=0x1ae671)
    toEmbed.set_image(url=planechase_images.plc[getimage])   
    sent = await ctx.send(embed = toEmbed)
    await sent.add_reaction('\N{LEFTWARDS BLACK ARROW}')
    await sent.add_reaction('\N{BLACK RIGHTWARDS ARROW}')

async def nextPlane(message, val):
    global planechase_list
    if val == "-":
        planechase_list[1] -= 1
    else:
        planechase_list[1] += 1
    if planechase_list[1] > len(planechase_list[0])-1:
        planechase_list[1] = 0
    if planechase_list[1] < 0:
        planechase_list[1] = len(planechase_list[0])-1
    message.embeds[0].set_image(url = planechase_images.plc[planechase_list[0][planechase_list[1]]])
    await message.edit(embed = message.embeds[0])

@bot.command(name='howl',
             brief= 'Ask WolframAlpha a question',
             help = 'Returns query result in image forms')
async def wolframAlpha(ctx, *args):
    global WOLFRAM
    global wra
    image_list = []
    title_list = []
    search = ''
    for name in args:
        search += str(name) + " "
    response = requests.get("http://api.wolframalpha.com/v2/query?input=" + search + "&appid=" + str(WOLFRAM) + "&output=json")
    res = response.json()['queryresult']['pods']
    length = 0
    for i in range(0, response.json()['queryresult']['numpods']):
        for j in range(0, len(res[i]['subpods'])):
            image_list.append(res[i]['subpods'][j]['img']['src'])
            title_list.append(res[i]['title'])
    toEmbed = discord.Embed(color=0x1ae671, title= "WolframAlpha Search")
    toEmbed.set_image(url = res[0]['subpods'][0]['img']['src'])
    toEmbed.set_footer(text=title_list[0] + "\n" + "(1" + "\\" + str(len(image_list)) + ")")
    message = await ctx.send(embed = toEmbed)
    info_list = [title_list, image_list, length]
    wra[message.id] = info_list
    await message.add_reaction('\N{LEFTWARDS BLACK ARROW}')
    await message.add_reaction('\N{BLACK RIGHTWARDS ARROW}')

async def nextHowl(message, value):
    global wra
    if value == "-":
        wra[message.id][2] -= 1
    else:
        wra[message.id][2] += 1
    wra[message.id][2] = cycleIndex(wra[message.id][2], len(wra[message.id][0])-1)
    message.embeds[0].set_image(url = wra[message.id][1][wra[message.id][2]])
    message.embeds[0].set_footer(text = wra[message.id][0][wra[message.id][2]] + "\n" + "("
                                 + str(wra[message.id][2] +1) + "\\" + str(len(wra[message.id][1])) + ")")                               
    await message.edit(embed = message.embeds[0])
    
def cycleIndex(value, indexLength):
#Helper function to determine if the attempted index value is out of bounds
    if value > indexLength:
        return 0
    elif value < 0:
        return indexLength
    else:
        return value

bot.run(TOKEN)
