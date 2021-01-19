from discord.ext import commands
from dotenv import load_dotenv
import discord
import random
import re
import requests
import json
import os

load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
print(TOKEN)

intents = discord.Intents.default()
intents.members = True
intents.reactions = True
bot = commands.Bot(command_prefix = '$', intents = intents)
user_list = []
revealvalues = []
channel_ID = ""
message_dict = {}

@bot.command(name = 'flip')
async def coinflip(ctx):
    print('Testing bot')

    var = random.randint(0,1)

    if var == 0:
        await ctx.send('The coin landed on HEADS!')

    if var == 1:
        await ctx.send('The coin landed on TAILS!')

@bot.command(name = 'flips')
async def multicoinflip(ctx, num:int):
    
    res = 0
    rec = num

    while num > 0:
        var = random.randint(0,1)
        num-= 1
        if var == 0:
            res+=1
            print(str(res))

    await ctx.send(str(res) + ' coins landed HEADS out of ' + str(rec))

@bot.command(name = 'until')
async def flipuntil(ctx):
    res = 0

    var = random.randint(0,1)

    if var == 0:
        await ctx.send('0 HEADS in a row')

    while var == 1:
        res+=1
        var = random.randint(0,1)

    if res != 0:
        await ctx.send(str(res) + ' coins landed HEADS in a row')

@bot.command(name = 'random')
async def pickrand(ctx, args1:int, args2:int):
    if args1 < args2:
        var = random.randint(int(args1), int(args2))
        await ctx.send('The randomly picked number is: ' + str(var))

@bot.command(name = 'roll')
async def roll(ctx, args:int):
    var = random.randint(1, int(args))

    await ctx.send(str(var) + ' was the result of your roll.')
    

@bot.command(name = 'test')
async def reveal(ctx, *args):
    global channel_ID
    await bot.wait_until_ready()
    for var in args:
        userRegex = re.compile(r'^[^#]+')
        username = userRegex.search(var)
        print(str(username.group()))
        discrimRegex = re.compile(r'[#\d]+')
        discrim = discrimRegex.search(var)
        testdiscrim = discrim.group()[slice(1,len(discrim.group()),1)]
        print(testdiscrim)
        print(str(discrim.group()))
        temp = discord.utils.get(bot.get_all_members(),
                                 name=str(username.group()),
                                 discriminator=str(testdiscrim)).id
        print(temp)
        user =  bot.get_user(temp)
        user_list.append(user)
        #me = await bot.fetch_user(str(temp))
        #await ctx.send(me, "Hello!")
        #await author.send("TEST!")
        #await me.send("Content")
        await user.send("What number will you pick?")
    channel_ID = ctx.channel.id
    print(str(channel_ID) + "This is the channel")

@bot.event
async def on_message(message):
        if isinstance(message.channel, discord.channel.DMChannel) and message.author != bot.user:
            print(user_list)
            print("These are the messaged members")
            if len(user_list) != 0:
                print(message.content)
                await message.channel.send('Duly Noted')
                print (user_list)
                print(str(channel_ID) + "Duly note")
                print(type(revealvalues))
                revealvalues.append(message.author.name + ' chose ' + message.content + '!')
                user_list.remove(message.author)
                if(len(user_list) == 0):
                    print(revealvalues)
                    print(str(channel_ID) + "TESTR!")
                    await bot.wait_until_ready()
                    channel = bot.get_channel(int(channel_ID))
                    print(channel)
                    await channel.send(revealvalues)
        await bot.process_commands(message)

#TODO Link to Scryfall API to allow for card lookup through $lookup "Force of Will" etc.
#TODO add arrows to allow to scroll through results

@bot.command(name = 'find')
async def findCard(ctx, *args):
    global message_dict
    search = ""
    for name in args:
        search += str(name) + " "
    print(search)
    print(type(search))
    response = requests.get("https://api.scryfall.com/cards/search?q=" + search)
    data = response.json()
    print(type(data))
    data2 = data['data']
    res = data2[0]
    print(res)
    print(type(res))
    res2 = res['image_uris']
    print(res2)
    getimage = res2['normal']
    print(getimage)
    message = await ctx.send(str(getimage))
    await message.add_reaction('⬅️')
    await message.add_reaction('➡️')
    message_dict[message.id] = [search, 0]
    print(message_dict)
    print(message_dict.get(message.id))

##    json1_data = data['data']
##    print(type(json1_data))
##    json_string = json.dumps(json1_data, indent = 4)
##    #print(json_string)
##    print(type(json_string))
##    message_id corresponding to (search arguments and num of times)

@bot.event
async def on_raw_reaction_add(payload):
    global message_dict
    if payload.user_id != bot.user.id:
        print("TEST")
        this_ID = payload.message_id
        print(this_ID)
        ID_res = message_dict.get(this_ID)
        val = ID_res[1] + 1
        args = ID_res[0]
        print(type(args))
        print(val)
        message_dict.update({int(this_ID) : [args, val]})
        print(message_dict)

        response = requests.get("https://api.scryfall.com/cards/search?q=" + args)
        data = response.json()
        data2 = data['data']
        res = data2[val]
        res2 = res['image_uris']
        getimage = res2['normal']
        print(getimage)

        channel = await bot.fetch_channel(payload.channel_id)
        message = await channel.fetch_message(payload.message_id)
        await message.edit(content=str(getimage))
        
    # edit message to show new link, then remove reaction

bot.run(TOKEN)
