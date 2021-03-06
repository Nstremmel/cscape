import discord
import asyncio
import random
import time
import datetime
import os
import psycopg2
from discord.utils import get

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c = conn.cursor()
conn.set_session(autocommit=True)

# c.execute("DROP TABLE rsmoney")
# c.execute("""CREATE TABLE rsmoney (
#               id bigint,
#               osrs bigint,
#               rs3 bigint,
#               alora bigint,
#               ikov bigint,
#               spawnpk bigint,
#               runewild bigint,
#               zenyte bigint,
#               roatzpk bigint,
#               dreamscape bigint,
#               pkhonor bigint,
#               vitality bigint,
#               simplicity bigint,
#               privacy boolean,
#               channels text
#               )""")
# conn.commit()

c.execute("DROP TABLE meleduels")
c.execute("""CREATE TABLE meleduels (
              id bigint,
              currency text,
              bet integer,
              turn integer,
              Php integer,
              Ppoisoned boolean,
              Ppoisonturns integer,
              Pspecturns integer,
              Procktails integer,
              Pspecial integer,
              Bhp integer,
              Bpoisoned boolean,
              Bpoisonturns integer,
              Bspecturns integer,
              Brocktails integer,
              Bspecial integer,
              messageid bigint,
              channelid text
              )""")
conn.commit()

c.execute("DROP TABLE mageduels")
c.execute("""CREATE TABLE mageduels (
                id bigint,
                currency text,
                bet integer,
                turn integer,
                Php integer,
                Procktails integer,
                Pfrozen boolean,
                Bhp integer,
                Brocktails integer,
                Bfrozen boolean,
                messageid bigint,
                channelid text
                )""")
conn.commit()

c.execute("DROP TABLE rangeduels")
c.execute("""CREATE TABLE rangeduels (
                id bigint,
                currency text,
                bet integer,
                turn integer,
                Php integer,
                Procktails integer,
                Pknives integer,
                Bhp integer,
                Brocktails integer,
                Bknives integer,
                messageid bigint,
                channelid text
                )""")
conn.commit()

# c.execute("DROP TABLE bossduels")
# c.execute("""CREATE TABLE bossduels (
#                 id bigint,
#                 currency text,
#                 bet integer,
#                 boss text,
#                 level text,
#                 reflect boolean,
#                 Php integer,
#                 Procktails integer,
#                 Bhp integer,
#                 Brocktails integer,
#                 messageid bigint,
#                 channelid text
#                 )""")
# conn.commit()

client = discord.Client()

def add_member(userid):
    c.execute('INSERT INTO rsmoney VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (userid, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, False, ''))

def getvalue(userid, column, table):
    if isinstance(column, list):
        returned = []
        for i in column:
            returned.append(getvalue(userid, i, table))
        return returned
    else:
        strings = ['currency', 'channels', 'boss', 'level']
        booleans = ['Ppoisoned', 'Bpoisoned', 'Pfrozen', 'Bfrozen', 'reflect']

        if column == '07':
            column = 'osrs'
        try:
            c.execute("SELECT osrs FROM rsmoney WHERE id={}".format(userid))
            tester=int(c.fetchone()[0])
        except:
            print("New Member")
            add_member(int(userid))
            return 0

        c.execute("SELECT {} FROM {} WHERE id={}".format(column, table, userid))

        if column in booleans:
            return bool(c.fetchone()[0])
        elif column in strings:
            return str(c.fetchone()[0])
        else:
            return int(c.fetchone()[0])

def update_money(userid, currency, amount):
    if currency == '07':
        currency = 'osrs'
    total = getvalue(int(userid), currency, 'rsmoney')
    c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, total + amount, userid))

def isstaff(authorroles):
    for i in open('staff.txt'):
        guild = client.get_guild(550630947767320578)
        role = get(guild.roles, name=str(i.strip()))
        if role in authorroles:
            return 'verified'

def formatok(amount):
    if amount[-1:].lower() == 'm':
        return int(float(str(amount[:-1])) * 1000)
    elif amount[-1:].lower() == 'k':
        return int(float(str(amount[:-1])))
    elif amount[-1:].lower() == 'b':
        return int(float(str(amount[:-1])) * 1_000_000)
    else:
        return int(float(amount)*1000)

def formatfromk(amount):
    if amount>=1000000:
        if len(str(amount))==7:
            return '{0:.3g}'.format(amount*0.000001)+"B"
        elif len(str(amount))==8:
            return '{0:.4g}'.format(amount*0.000001)+"B"
        else:
            return '{0:.5g}'.format(amount*0.000001)+"B"
    elif amount>=1000:
        if len(str(amount))==4:
            return '{0:.3g}'.format(amount*0.001)+"M"
        elif len(str(amount))==5:
            return '{0:.4g}'.format(amount*0.001)+"M"
        elif len(str(amount))==6:
            return '{0:.5g}'.format(amount*0.001)+"M"
    else:
        return str(amount)+"k"


def hpupdate(user, opponent, duelType, words):
    if user[0] == 'CryptoScape Bot' or user[0] in ['Commander Zilyana', "K'ril Tsutsaroth", "Kree'arra", 'General Graardor', 'The King Black Dragon']:
        url = str(opponent[0].guild.icon_url)
        pair = [user, opponent]
    else:
        url = str(user[0].guild.icon_url)
        pair = [opponent, user]

    embed = discord.Embed(description = words, color = 16766463)
    embed.set_author(name='Fight to the Death!', icon_url=url)

    for counter, i in enumerate(pair):
        hp = int(i[1])
        if counter == 0:
            if duelType == 'boss':
                level = getvalue(pair[1][0].id, 'level', 'bossduels')
                if level == 'easy':
                    maxhp = 100
                elif level == 'normal':
                    maxhp = 250
                else:
                    maxhp = 500
            else:
                maxhp = 99
        else:
            maxhp = 99

        if hp in range(int(maxhp * 0.75), maxhp + 1):
            hp = get(client.emojis, name='hpbar100')
        elif hp in range(int(maxhp * 0.5), int(maxhp* 0.75)):
            hp = get(client.emojis, name='hpbar75')
        elif hp in range(int(maxhp * 0.25), int(maxhp * 0.5)):
            hp = get(client.emojis, name='hpbar50')
        elif hp in range(1, int(maxhp * 0.25)):
            hp = get(client.emojis, name='hpbar25')
        elif hp < 1:
            hp = get(client.emojis, name='hpbar0')
        rocktail = get(client.emojis, name='rocktail')
        if duelType == 'mele':
            embed.add_field(name=str(i[0]), value="Poisoned: "+str(i[4]) +
                                                        "\n"+str(rocktail)+": "+str(i[2]) +
                                                        "\nSpecial Attack: "+str(i[3])+"%" +
                                                        "\nHP Left: "+str(i[1])+'/99 '+str(hp), inline=True)
        elif duelType == 'mage':
            embed.add_field(name=str(i[0]), value= "\n"+str(rocktail)+": "+str(i[2]) +
                                                        "\nFrozen: "+str(i[3]) +
                                                        "\nHP Left: "+str(i[1])+'/99 '+str(hp), inline=True)
        elif duelType == 'range':
            embed.add_field(name=str(i[0]), value= "\n"+str(rocktail)+": "+str(i[2]) +
                                                        "\nKnives Left: "+str(i[3]) +
                                                        "\nHP Left: "+str(i[1])+'/99 '+str(hp), inline=True)
        elif duelType == 'boss':
            embed.add_field(name=str(i[0]), value= "\n"+str(rocktail)+": "+str(i[2]) +
                                                        "\nHP Left: "+str(i[1])+'/'+str(maxhp)+' '+str(hp), inline=True)
    return embed

def isenough(amount, currency):
    if amount < 100:
        words = 'The minimum amount you can bet is **10k** gp ' + currency + '.'
        return (False, words)
    else:
        return (True, ' ')

def updateDuel(updater, userid, duelType):
    user = updater.pop(0)
    for counter, i in enumerate(updater):
        if duelType == 'mele':
            if user == 'CryptoScape Bot':
                columns = ['Bhp', 'Brocktails', 'Bspecial', 'Bpoisoned', 'Bpoisonturns', 'Bspecturns']
            else:
                columns = ['Php', 'Procktails', 'Pspecial', 'Ppoisoned', 'Ppoisonturns', 'Pspecturns']
        elif duelType == 'mage':
            if user == 'CryptoScape Bot':
                columns = ['Bhp', 'Brocktails', 'Bfrozen']
            else:
                columns = ['Php', 'Procktails', 'Pfrozen']
        elif duelType == 'range':
            if user == 'CryptoScape Bot':
                columns = ['Bhp', 'Brocktails', 'Bknives']
            else:
                columns = ['Php', 'Procktails', 'Pknives']
        elif duelType == 'boss':
            if user in ['Commander Zilyana', "K'ril Tsutsaroth", "Kree'arra", 'General Graardor', 'The King Black Dragon']:
                columns = ['Bhp', 'Brocktails']
            else:
                columns = ['Php', 'Procktails']
        else:
            columns=[]
        c.execute("UPDATE {} SET {}={} WHERE id={}".format(duelType + 'duels', columns[counter], i, userid))
    updater.insert(0, user)

async def rocktail(user, opponent, player, channel, duelType):
    sentid = getvalue(player[0].id, 'messageid', duelType + 'duels')
    sent = await channel.fetch_message(sentid)
    rocktail = get(client.emojis, name='rocktail')
    if user[2] < 1:
        await channel.send('You are out of ' + str(rocktail) + '. Please use a different move.', delete_after = 3.0)
    else:
        healing = random.randint(22, 29)
        user[2] -= 1
        user[1] += healing
        if user[1] > 99:
            user[1] = 99
        words = str(user[0]) + ' eats a ' + str(rocktail) + ' and heals **' + str(healing) + '** hp.'
        await sent.edit(embed=hpupdate(user, opponent, duelType, words))
        await asyncio.sleep(2.5)
    updateDuel(user, player[0].id, duelType)
    return None

async def dds(user, opponent, player, channel):
    sentid = getvalue(player[0].id, 'messageid', 'meleduels')
    sent = await channel.fetch_message(sentid)
    dds = get(client.emojis, name='dds')
    if user[3] < 25:
        await channel.send('You are out of ' + str(dds) + ' specs. Please use `!rocktail` or `!whip`.', delete_after = 3.0)
    else:
        user[3] -= 25
        hit1, hit2 = random.randint(0, 20), random.randint(0, 20)
        opponent[1] -= hit1 + hit2
        if opponent[1] < 0:
            opponent[1] = 0
        words = str(user[0]) + ' uses a ' + str(dds) + ' and deals **' + str(hit1) + ' + ' + str(hit2) +'** damage.'
        await channel.send(file=discord.File('dds.gif', filename='dds.gif'), delete_after = 2.5)
        await sent.edit(embed=hpupdate(user, opponent, 'mele', words))
        await asyncio.sleep(2.5)
        if opponent[1] < 1:
            updateDuel(user, player[0].id, 'mele')
            updateDuel(opponent, player[0].id, 'mele')
            return user[0]
        elif random.randint(1, 4) == 4:
            if opponent[4] == False:
                opponent[4] = True
                words = str(opponent[0]) + ' has been poisoned by the ' + str(dds) + '!'
                await sent.edit(embed=hpupdate(user, opponent, 'mele', words))
            await asyncio.sleep(2.5)
    updateDuel(user, player[0].id, 'mele')
    updateDuel(opponent, player[0].id, 'mele')
    return None

async def attack(boss, player, maxDamage, channel):
    sentid = getvalue(player[0].id, 'messageid', 'bossduels')
    sent = await channel.fetch_message(sentid)
    hit = random.randint(0, maxDamage)
    player[1] -= hit
    if player[1] < 0:
        player[1] = 0
    words = boss[0] + ' attacks you and deals **' + str(hit) + '** damage.'
    await sent.edit(embed=hpupdate(player, boss, 'boss', words))
    await asyncio.sleep(2.5)
    if player[1] < 1:
        return boss[0]
    else:
        return None

async def leach(boss, player, maxDamage, percentHeal, channel):
    sentid = getvalue(player[0].id, 'messageid', 'bossduels')
    sent = await channel.fetch_message(sentid)
    hit = random.randint(0, maxDamage)
    heal = int(hit * percentHeal)
    player[1] -= hit
    if player[1] < 0:
        player[1] = 0
    boss[1] += heal
    words = boss[0] + ' uses its leach ability, dealing **' + str(hit) + '** damage and healing **' + str(heal) + '** HP.'
    await sent.edit(embed=hpupdate(player, boss, 'boss', words))
    await asyncio.sleep(2.5)
    if player[1] < 1:
        return boss[0]
    else:
        return None

async def reflect(boss, player, channel):
    sentid = getvalue(player[0].id, 'messageid', 'bossduels')
    sent = await channel.fetch_message(sentid)
    c.execute('UPDATE bossduels SET reflect={} WHERE id={}'.format(True, player[0].id))
    words = boss[0] + ' uses its reflect ability. It will reflect **50%** of damage taken back at you for 1 turn.'
    await sent.edit(embed=hpupdate(player, boss, 'boss', words))
    await asyncio.sleep(2.5)

async def whip(user, opponent, player, channel, duelType, reflect):
    sentid = getvalue(player[0].id, 'messageid', duelType + 'duels')
    sent = await channel.fetch_message(sentid)
    whip = get(client.emojis, name='whip')
    hit = random.randint(0, 27)
    opponent[1] -= hit
    if opponent[1] < 1:
        opponent[1] = 0
    words = str(user[0]) + ' has hit ' + str(opponent[0]) + ' with their ' + str(whip) + ' and dealt **' + str(hit) + '** damage.'
    await channel.send(file=discord.File('whip.gif', filename='whip.gif'), delete_after = 2.5)
    await sent.edit(embed=hpupdate(user, opponent, duelType, words))
    await asyncio.sleep(2.5)
    if reflect:
        user[1] -= int(hit/2)
        if user[1] < 0:
            user[1] = 0
        words = opponent[0] + ' has reflected **' + str(int(hit/2)) + '** damage back at you!'
        await sent.edit(embed=hpupdate(user, opponent, duelType, words))
        await asyncio.sleep(2.5)
    updateDuel(user, player[0].id, duelType)
    updateDuel(opponent, player[0].id, duelType)
    if opponent[1] < 1:
        return user[0]
    elif user[1] < 1:
        return opponent[0]
    else:
        return None

async def ice(user, opponent, player, channel):
    sentid = getvalue(player[0].id, 'messageid', 'mageduels')
    sent = await channel.fetch_message(sentid)
    ice = get(client.emojis, name='ice')
    hit = random.randint(0, 30)
    opponent[1] -= hit
    if opponent[1] < 0:
        opponent[1] = 0
    words = str(user[0]) + ' has hit ' + str(opponent[0]) + ' with ' + str(ice) + ' and dealt **' + str(hit) + '** damage.'
    await channel.send(file=discord.File('ice.gif', filename='ice.gif'), delete_after = 2.5)
    await sent.edit(embed=hpupdate(user, opponent, 'mage', words))
    await asyncio.sleep(2.5)
    if opponent[1] < 1:
        updateDuel(user, player[0].id, 'mage')
        updateDuel(opponent, player[0].id, 'mage')
        return user[0]
    elif random.randint(1, 5) == 5:
        opponent[3] = True
        words = str(opponent[0]) + ' has been frozen from ' + str(ice) + '.'
        await sent.edit(embed=hpupdate(user, opponent, 'mage', words))
        await asyncio.sleep(2.5)
    updateDuel(user, player[0].id, 'mage')
    updateDuel(opponent, player[0].id, 'mage')
    return None

async def blood(user, opponent, player, channel, duelType, reflect):
    sentid = getvalue(player[0].id, 'messageid', duelType + 'duels')
    sent = await channel.fetch_message(sentid)
    ice = get(client.emojis, name='blood')
    hit = random.randint(0, 24)
    opponent[1] -= hit
    if opponent[1] < 0:
        opponent[1] = 0
    healed = int(hit * 0.25)
    user[1] += healed
    if user[1] > 99:
        user[1] = 99
    words = (str(user[0]) + ' has hit ' + str(opponent[0]) + ' with ' + str(ice) + ", dealt **" + str(hit) + "** damage, and was healed for **" + str(healed) + "** HP.")
    await channel.send(file=discord.File('blood.gif', filename='blood.gif'), delete_after = 2.5)
    await sent.edit(embed=hpupdate(user, opponent, duelType, words))
    await asyncio.sleep(2.5)
    if reflect:
        user[1] -= int(hit/2)
        if user[1] < 0:
            user[1] = 0
        words = opponent[0] + ' has reflected **' + str(int(hit/2)) + '** damage back at you!'
        await sent.edit(embed=hpupdate(user, opponent, duelType, words))
        await asyncio.sleep(2.5)
    updateDuel(user, player[0].id, duelType)
    updateDuel(opponent, player[0].id, duelType)
    if opponent[1] < 1:
        return user[0]
    elif user[1] < 1:
        return opponent[0]
    else:
        return None

async def bow(user, opponent, player, channel):
    sentid = getvalue(player[0].id, 'messageid', 'rangeduels')
    sent = await channel.fetch_message(sentid)
    bow = get(client.emojis, name='bow')
    hit = random.randint(0, 20)
    opponent[1] -= hit
    if opponent[1] < 0:
        opponent[1] = 0
    words = str(user[0]) + ' has hit ' + str(opponent[0]) + ' with ' + str(bow) + ' and dealt **' + str(hit) + '** damage.'
    await channel.send(file=discord.File('bow.gif', filename='bow.gif'), delete_after = 2.5)
    await sent.edit(embed=hpupdate(user, opponent, 'range', words))
    await asyncio.sleep(2.5)
    updateDuel(opponent, player[0].id, 'range')
    if opponent[1] < 1:
        return user[0]
    else:
        return None

async def knife(user, opponent, player, channel):
    sentid = getvalue(player[0].id, 'messageid', 'rangeduels')
    sent = await channel.fetch_message(sentid)
    knife = get(client.emojis, name='knife')
    if user[2] < 1:
        await channel.send('You are out of ' + str(knife) + '. Please use a different move.', delete_after = 3.0)
    else:
        user[3] -= 1
        hit = random.randint(5, 25)
        opponent[1] -= hit
        if opponent[1] < 0:
            opponent[1] = 0
        words = str(user[0]) + ' has hit ' + str(opponent[0]) + ' with ' + str(knife) + ' and dealt **' + str(hit) + '** damage.'
        await channel.send(file=discord.File('knife.gif', filename='knife.gif'), delete_after = 2.5)
        await sent.edit(embed=hpupdate(user, opponent, 'range', words))
        await asyncio.sleep(2.5)
        updateDuel(user, player[0].id, 'range')
        updateDuel(opponent, player[0].id, 'range')
    if opponent[1] < 1:
        return user[0]
    else:
        return None
##############################################################################################################

#Predefined Variables
colors = ['A', 'B', 'C', 'D', 'E', 'F', '0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
flowers = ['Red', 'Orange', 'Yellow', 'Green', 'Blue', 'Purple']
sidecolors = [16711680, 16743712, 16776960, 1305146, 1275391, 16730111]
moves = ['!whip', '!dds', '!rocktail', '!ice', '!blood', '!bow', '!knife']

class currencies():
    osrs, ikov, spawnpk, runewild, zenyte, roatzpk, dreamscape, pkhonor, vitality, rs3, alora, simplicity = [0, 'osrs'], [0, 'ikov'], [0, 'spawnpk'], [0, 'runewild'], [0, 'zenyte'], [0, 'roatzpk'], [0, 'dreamscape'], [0, 'pkhonor'], [0, 'vitality'], [0, 'rs3'], [0, 'alora'], [0, 'simplicity']
    currencies = [osrs, ikov, spawnpk, runewild, zenyte, roatzpk, dreamscape, pkhonor, vitality, rs3, alora, simplicity]

async def my_background_task():
    await client.wait_until_ready()
    while (not client.is_closed):
        None
        await asyncio.sleep(600)

@client.event
async def on_ready():
    print('Bot Logged In!')

@client.event
async def on_raw_reaction_add(payload):
    user = client.get_user(payload.user_id)
    channel = client.get_channel(payload.channel_id)
    channelids = []
    for i in channel.guild.categories:
        if i.id in [727294344633254002, 550703277117931521, 727294625559216168, 676872820772569119, 701468989041279037]:
            for x in i.channels:
                channelids.append(x.id)
    if channel.id in channelids and payload.emoji.id == 676988116451590226 and user.id != 479862852895899649:
        channels = str(getvalue(user.id, 'channels', 'rsmoney'))
        if len(channels.split('|')) - 1 < 10:
            category = get(channel.guild.categories, name = 'Tickets')
            newChannel = await channel.guild.create_text_channel(channel.name + ' ' + str(user)[:-5], category=category)
            await newChannel.set_permissions(user, read_messages=True, send_messages=True, read_message_history=True)
            c.execute("UPDATE rsmoney SET channels='{}' WHERE id={}".format(channels + str(newChannel.id) + '|', user.id))
            embed = discord.Embed(description='<@' + str(user.id) + '>, this is your temporary private channel. You or a staff member can use `!close` when you are done to delete the channel.', color=11854069)
            embed.set_author(name='Private Channel Info', icon_url=channel.guild.icon_url)
            embed.set_footer(text='Channel Opened On: ' + str(datetime.datetime.now())[:-7])
            await newChannel.send(embed=embed)
        else:
            await channel.send('<@' + str(user.id) + '>, you can only have a maxiumum of *10* private channels open at a time!', delete_after = 3.0)

@client.event
async def on_reaction_remove(reaction, user):
    None

@client.event
async def on_message(message):
    global meleduel, magicduel
   
    message.content = message.content.lower()

    #######################################
    if message.content.startswith('!input'):
        print(message.content)
    #######################################
    elif message.content == '!log':
        if message.author.id == 199630284906430465:
            await message.channel.send('Goodbye!')
            await client.logout()
    #######################################
    elif message.content.startswith('!say'):
        await message.channel.send(str(message.content[5:]))
    #######################################
    elif message.content.startswith('!emoji'):
        if isstaff(message.author.roles) == 'verified':
            try:
                await message.delete()
            except:
                print('No permissions to delete messages. RIP')
            finalmessage = ''
            characters = []
            characters += str(message.content).lower()[7:]
            for i in characters:
                if i == ' ':
                    finalmessage += ':white_small_square: '
                elif i in 'abcdefghijklmnopqrstuvwxyz':
                    finalmessage += (':regional_indicator_' + i) + ': '
                elif i == '!':
                    finalmessage += ':grey_exclamation: '
            await message.channel.send(finalmessage)
        else:
            await message.channel.send("Admin Command Only")
    #######################################
    elif message.content.startswith('!poll'):
        message.content = message.content.title()
        embed = discord.Embed(description='Respond below with 👍 for YES, 👎 for NO, or 🤔 for UNSURE/NEUTRAL', color=16724721)
        embed.set_author(name=str(message.content[6:]), icon_url=message.guild.icon_url)
        embed.set_footer(text='Polled on: ' + str(datetime.datetime.now())[:(- 7)])
        sent = await message.channel.send(embed=embed)
        await sent.add_reaction('👍')
        await sent.add_reaction('👎')
        await sent.add_reaction('🤔')
    #######################################
    elif message.content.startswith('$userinfo'):
        try:
            int(str(message.content[12:13]))
            member = message.guild.get_member(int(message.content[12:30]))
        except:
            member = message.guild.get_member(int(message.content[13:31]))
        
        roles = []
        
        for i in member.roles:
            if str(i) == '@everyone':
                roles.append('Everyone')
            else:
                roles.append(i.name)
        
        embed = discord.Embed(description=" Name: "+str(member)+"\n"+
                                            "\nRoles: "+', '.join(roles)+"\n"+
                                            "\nJoined server on: "+str(member.joined_at).split(" ")[0]+"\n"+
                                            "\nCreated account on: "+str(member.created_at).split(" ")[0]+"\n"+
                                            "\nPlaying: "+str(member.activity)+"\n", color=8270499)
        embed.set_author(name='Information of ' + str(member)[:(- 5)], icon_url=str(member.avatar_url))
        embed.set_footer(text="Spying on people's information isn't very nice...")
        await message.channel.send(embed=embed)
    #######################################













    #######################################
    elif (message.content == '!wallet') or (message.content == '!w') or (message.content == '!$'):
        for i in currencies.currencies:
            i[0] = getvalue(message.author.id, i[1], 'rsmoney')

        if any(x[0] >= 1_000_000 for x in currencies.currencies):
            sidecolor = 2693614
        elif any(x[0] >= 10_000 for x in currencies.currencies):
            sidecolor = 2490163
        else:
            sidecolor = 12249599

        embed = discord.Embed(color=sidecolor)
        embed.set_author(name=str(message.author)[:-5] + "'s Wallet", icon_url=str(message.author.avatar_url))
        embed.set_footer(text='Wallet checked on: ' + str(datetime.datetime.now())[:-7])
        
        for i in currencies.currencies:
            i[0] = formatfromk(i[0])
            if i[0] == '0k':
                i[0] = '0 k'
            if i[1] == 'osrs':
                i[1] = '07'
            embed.add_field(name=i[1].title(), value=i[0], inline=True)
        
        await message.channel.send(embed=embed)

    elif message.content.startswith('!wallet <@') or message.content.startswith('!w <@') or message.content.startswith('!$ <@'):
        try:
            int(str(message.content).split(' ')[1][2:3])
            member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
        except:
            member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
        
        for i in currencies.currencies:
            i[0] = getvalue(member.id, i[1], 'rsmoney')

        if any(x[0] >= 1_000_000 for x in currencies.currencies):
            sidecolor = 2693614
        elif any(x[0] >= 10_000 for x in currencies.currencies):
            sidecolor = 2490163
        else:
            sidecolor = 12249599

        embed = discord.Embed(color=sidecolor)
        embed.set_author(name=str(member)[:-5] + "'s Wallet", icon_url=str(member.avatar_url))
        embed.set_footer(text='Wallet checked on: ' + str(datetime.datetime.now())[:-7])
        
        for i in currencies.currencies:
            i[0] = formatfromk(i[0])
            if i[0] == '0k':
                i[0] = '0 k'
            if i[1] == 'osrs':
                i[1] = '07'
            embed.add_field(name=i[1].title(), value=i[0], inline=True)
        
        await message.channel.send(embed=embed)    
    #######################################
    elif message.content == '!privacy on':
        c.execute('UPDATE rsmoney SET privacy=True WHERE id={}'.format(message.author.id))
        embed = discord.Embed(description=('<@' + str(message.author.id)) + ">'s wallet privacy is now enabled.", color=5174318)
        embed.set_author(name='Privacy Mode', icon_url=str(message.author.avatar_url))
        await message.channel.send(embed=embed)
    
    elif message.content == '!privacy off':
        c.execute('UPDATE rsmoney SET privacy=False WHERE id={}'.format(message.author.id))
        embed = discord.Embed(description=('<@' + str(message.author.id)) + ">'s wallet privacy is now disabled.", color=5174318)
        embed.set_author(name='Privacy Mode', icon_url=str(message.author.avatar_url))
        await message.channel.send(embed=embed)
    #######################################
    elif message.content.startswith('!reset'):
        try:
            if isstaff(message.author.roles) == 'verified':
                try:
                    int(str(message.content).split(' ')[1][2:3])
                    member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
                except:
                    member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
                currency = (message.content).split(' ')[2]
                c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, 0, member.id))
                await message.channel.send('<@' + str(member.id) + ">'s **" + currency.title() + "** balance has been reset to 0.")
            else:
                await message.channel.send('Admin Command Only!')
        except:
            await message.channel.send('An **error** occurred. Make sure you use `!reset (@USER) (CURRENCY)`')
    #######################################
    elif message.content.startswith('!update'):
        try:
            if isstaff(message.author.roles) == 'verified':
                try:
                    int(str(message.content).split(' ')[1][2:3])
                    member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
                except:
                    member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
                amount = formatok(str(message.content).split(' ')[2])
                currency = (message.content).split(' ')[3]
                update_money(member.id, currency, amount)
                embed = discord.Embed(description='<@' + str(member.id) + ">'s **" + currency.title() + "** balance has been updated.", color=5174318)
                embed.set_author(name='Update Request', icon_url=str(member.avatar_url))
                await message.channel.send(embed=embed)
            else:
                await message.channel.send('Admin Command Only!')
        except:
            await message.channel.send('An **error** has occurred. Make sure you use `!update (@USER) (AMOUNT) (CURRENCY)`.')
    #######################################
    elif message.content.startswith('!help') or message.content.startswith('!commands'):
        embed = discord.Embed(description=  #"\n `!colorpicker` - Shows a random color\n" +
                                            #"\n `!emoji (WORDS)` - The bot sends back those words in emoji form\n" +
                                            #"\n `!start unscramble` - Starts a game where you unscramble a word\n" +
                                            #"\n `!start hangman` - Starts a game of hangman\n" +
                                            #"\n `!random (singleplayer or multiplayer) (SIZE)` - Starts a game where you guess a number between 1 and the given size\n" +
                                            #"\n `!poll (QUESTION)` - Starts a Yes/No poll with the given question\n" +
                                            "\n `!w`, `!wallet`, `!$`, or `!tokens` - Checks your own tokens\n" +
                                            "\n `!w (@USER)`, `!wallet (@USER)`, `!$ (@USER)`, or `!tokens (@USER)` - Checks that user's tokens\n" +
                                            #"\n `!daily` - Gives 800 tokens each day\n" +
                                            # "\n `!swap (rs3 or 07) (AMOUNT)` - Swaps that amount of gold to the other game" +
                                            # "\n `!rates` - Shows the swapping rates between currencies" +
                                            "\n `!flower (AMOUNT) (hot, cold, red, orange, yellow, green, blue, or purple)` - Hot or cold gives x2 minus commission, specific color gives x6 minus commission\n" +
                                            #"\n `!cashin (rs3 or 07) (AMOUNT)` - Notifies a cashier that you want to cash in that amount\n" +
                                            #"\n `!cashout (rs3 or 07) (AMOUNT)` - Notifies a cashier that you want to cash out that amount\n" +
                                            #"\n `!wager`, `!total bet`, or `!tb` - Shows the total amount of tokens you've bet\n" +
                                            "\n `!ddsstake (AMOUNT)` - Hosts a mele duel betting that amount of tokens\n" +
                                            "\n `!magebox (AMOUNT)` - Hosts a magic duel betting that amount of tokens\n", color=2513759)
                                            #"\n `!transfer (@USER) (AMOUNT)` - Transfers that amount of tokens from your wallet to the user's wallet\n"
        embed.set_author(name='CryptoScape Bot Commands', icon_url=str(message.guild.icon_url))
        await message.channel.send(embed=embed)
    #######################################
    elif message.content.lower().startswith('!transfer'):
        try:
            transfered = formatok(str(message.content).split(' ')[2])
            currency = (message.content).split(' ')[3]
            current = getvalue(message.author.id, currency, 'rsmoney')
            if transfered >= 1:
                if current >= transfered:
                    try:
                        int(str(message.content).split(' ')[1][2:3])
                        member = message.guild.get_member(int((message.content).split(' ')[1][2:-1]))
                    except:
                        member = message.guild.get_member(int((message.content).split(' ')[1][3:-1]))
                    taker = getvalue(member.id, currency, 'rsmoney')
                    c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, current - transfered, message.author.id))
                    c.execute('UPDATE rsmoney SET {}={} WHERE id={}'.format(currency, taker + transfered, member.id))
                    await message.channel.send('<@' + str(message.author.id) + '> has transfered **' + formatfromk(transfered) + ' ' + currency.title() + '** to <@' + str(member.id) + ">'s wallet.")
                else:
                    await message.channel.send('<@' + str(message.author.id) + ">, You don't have enough money to transfer that amount!")
            else:
                await message.channel.send('You must transfer at least **1** unit of currency.')
        except:
            await message.channel.send('An **error** has occurred. Make sure you use `!transfer (@USER) (AMOUNT) (CURRENCY)`.')
    #######################################
    elif message.content == '!close':
        if message.channel.category.id == 705273543239401523:
            c.execute("SELECT id, channels FROM rsmoney")
            userid = None
            for i in c.fetchall():
                if str(message.channel.id) in str(i[1]):
                    userid = i[0]
            channels = getvalue(userid, 'channels', 'rsmoney')
            for i in channels.split('|'):
                if i == str(message.channel.id):
                    newChannels = (channels.split('|'))
                    newChannels.remove(str(i))
                    newChannels = '|'.join(newChannels)
                    c.execute("UPDATE rsmoney SET channels='{}' WHERE id={}".format(newChannels, userid))
                    await message.channel.delete()

    elif message.content.startswith('!message'):
        channelid = int(message.content.split(' ')[1])
        channel = client.get_channel(channelid)
        logo = get(client.emojis, name='crytoscapelogo')
        embed = discord.Embed(description='React to this message with ' + str(logo) + ' to create a **private room**.', color=1305146)
        embed.set_author(name=str(channel.name).title(), icon_url=str(message.guild.icon_url))
        await channel.send(embed=embed)
    #######################################
    elif message.content.startswith('!53') or message.content.startswith('!50') or message.content.startswith('!75') or message.content.startswith('!95'):
        if message.channel.id in [701470129942429697, 700186111422627870]:
            #try:
            currency = str(message.content).split(' ')[2]
            bet = formatok(str(message.content).split(' ')[1])
            current = getvalue(message.author.id, currency, 'rsmoney')
            
            if isenough(bet, currency)[0]:
                if message.content.startswith('!53x2') or message.content.startswith('!53'):
                    (title, odds, multiplier) = ('53x2', 54, 2)
                elif message.content.startswith('!50x1.8') or message.content.startswith('!50'):
                    (title, odds, multiplier) = ('50x1.8', 51, 1.8)
                elif message.content.startswith('!75x3') or message.content.startswith('!75'):
                    (title, odds, multiplier) = ('75x3', 76, 3)
                elif message.content.startswith('!95x7') or message.content.startswith('!95'):
                    (title, odds, multiplier) = ('95x7', 96, 7)
                
                if current >= bet:
                    #getrandint(id)
                    roll = random.randint(1, 100)
                    
                    if roll in range(1, odds):
                        winnings = bet
                        words = 'Rolled **' + str(roll) + '** out of **100**. You lost **' + formatfromk(bet) + '** ' + currency.title() + '.'
                        (sidecolor, gains, win) = (16718121, bet * -1, False)
                    else:
                        winnings = formatfromk(int(bet * multiplier))
                        words = 'Rolled **' + str(roll) + '** out of **100**. You won **' + str(winnings) + '** ' + currency.title() + '.'
                        winnings = formatok(winnings)
                        (sidecolor, gains, win) = (3997475, (bet * multiplier) - bet, True)
                    
                    update_money(message.author.id, currency, gains)
                    # c.execute('SELECT nonce FROM data')
                    # nonce = int(c.fetchone()[0])
                    # clientseed = getvalue(message.author.id, 'clientseed', 'rsmoney')
                    embed = discord.Embed(color=sidecolor)
                    embed.set_author(name=str(message.author), icon_url=str(message.author.avatar_url))
                    embed.add_field(name=title, value=words, inline=True)
                    # embed.set_footer(text=((('Nonce: ' + str(nonce - 1)) + ' | Client Seed: "') + str(clientseed)) + '"')
                    await message.channel.send(embed=embed)
                else:
                    await message.channel.send(('<@' + str(message.author.id)) + ">, you don't have that much gold!")
            else:
                await message.channel.send(isenough(bet, currency)[1])
            #except:
            #    await message.channel.send('An **error** has occurred. Make sure you use `!(50, 53, 75, or 95) (BET) (CURRENCY)`.')
        else:
            await message.channel.send('This command can only be used in one of the dicing channels.')
    ################################################
    # elif message.content.startswith('!flower'):
    #     try:
    #         enough = True
    #         bet = formatok(message.content.split(' ')[1])
    #         current = getvalue(int(message.author.id), 'tokens')
    #         totaltokens = getvalue(int(message.author.id), 'tokens')
    #         index = random.randint(0, 5)
    #         flower = flowers[index]
    #         sidecolor = sidecolors[index]
    #         commission = 0.05
    #         if bet < 100:
    #             await message.channel.send('The minimum amount you can bet is **100** tokens.')
    #             enough = False
    #         if enough == True:
    #             if current >= bet:
    #                 win = False
    #                 if message.content.split(' ')[2] == 'hot':
    #                     if (flower == 'Red') or (flower == 'Orange') or (flower == 'Yellow'):
    #                         multiplier = 2
    #                         win = True
    #                     else:
    #                         multiplier = 0
    #                 elif message.content.split(' ')[2] == 'cold':
    #                     if (flower == 'Blue') or (flower == 'Green') or (flower == 'Purple'):
    #                         multiplier = 2
    #                         win = True
    #                     else:
    #                         multiplier = 0
    #                 elif message.content.split(' ')[2].title() in flowers:
    #                     if flower == message.content.split(' ')[2].title():
    #                         multiplier = 6
    #                         win = True
    #                     else:
    #                         multiplier = 0
    #                 winnings = (bet * multiplier) - ((commission * bet) * multiplier)
    #                 if isinstance(winnings, float):
    #                     if winnings.is_integer():
    #                         winnings = int(winnings)
    #                 if win == True:
    #                     words = ((((('Congratulations! The color of the flower was `' + flower) + '`. ') + str(message.author)) + ' won `') + '{:,}'.format(winnings)) + '` tokens.'
    #                     if multiplier == 2:
    #                         update_money(int(message.author.id), bet - ((bet * commission) * multiplier))
    #                     else:
    #                         update_money(int(message.author.id), (bet * multiplier) - ((bet * commission) * multiplier))
    #                 else:
    #                     words = ((((('Sorry, the color the flower was `' + flower) + '`. ') + str(message.author)) + ' lost `') + '{:,}'.format(bet)) + '` tokens.'
    #                     update_money(int(message.author.id), bet * (- 1))
    #                 c.execute('UPDATE rsmoney SET tokenstotal={} WHERE id={}'.format(totaltokens + bet, message.author.id))
    #                 embed = discord.Embed(description=words, color=sidecolor)
    #                 embed.set_author(name=str(message.author)[:(- 5)] + "'s Gamble", icon_url=str(message.author.avatar_url))
    #                 embed.set_footer(text='Gambled on: ' + str(datetime.datetime.now())[:(- 7)])
    #                 await message.channel.send(embed=embed)
    #             else:
    #                 await message.channel.send(('<@' + str(message.author.id)) + ">, You don't have that many tokens!")
    #         else:
    #             None
    #     except:
    #         await message.channel.send('An **error** has occurred. Make sure you use `!flower (Amount) (hot, cold, red, orange, yellow, green, blue, or purple)`.')
    #######################################
    elif message.content.startswith('!meleduel') or message.content.startswith('!mageduel') or message.content.startswith('!rangeduel'):# or message.content.startswith('!boss'):
        #try:
        duelType = (message.content).split(' ')[0][1:-4]
        if duelType == '':
            duelType = 'boss'
        currency = (message.content).split(' ')[2]
        current = getvalue(message.author.id, currency, 'rsmoney')
        bet = formatok(message.content.split(' ')[1])
        bosses = ['Commander Zilyana', "K'ril Tsutsaroth", "Kree'arra", 'General Graardor', 'The King Black Dragon']
        if isenough(bet, currency):
            if current >= bet:
                try:
                    c.execute('SELECT Php FROM {} WHERE id={}'.format(duelType + 'duels', message.author.id))
                    tester = int(c.fetchone()[0])
                    await message.channel.send('You are already in a duel!')
                except:
                    update_money(message.author.id, currency, bet * -1)
                    #player=[0               1     2           3        4                 5                 6]
                    #player=[member object, hp, rocktails, special, poisoned, turns since poisoned, turns since speced]
                    if duelType == 'mele':
                        sent = await message.channel.send(embed=hpupdate(['CryptoScape Bot', 99, 4, 100, False, 0, 0], [message.author, 99, 4, 100, False, 0, 0], 'mele', 'New Game. Use `!rocktail`, `!dds`, or `!whip`.'))
                        c.execute('INSERT INTO meleduels VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (message.author.id, currency, bet, 1, 99, False, 0, 0, 4, 100, 99, False, 0, 0, 4, 100, sent.id, message.channel.id))
                    elif duelType == 'mage':
                        sent = await message.channel.send(embed=hpupdate(['CryptoScape Bot', 99, 2, False], [message.author, 99, 2, False], 'mage', 'New Game. Use `!rocktail`, `!ice`, or `!blood`.'))
                        c.execute('INSERT INTO mageduels VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (message.author.id, currency, bet, 1, 99, 2, False, 99, 2, False, sent.id, message.channel.id))
                    elif duelType == 'range':
                        sent = await message.channel.send(embed=hpupdate(['CryptoScape Bot', 99, 3, 4], [message.author, 99, 3, 4], 'range', 'New Game. Use `!rocktail`, `!bow`, or `!knife`.'))
                        c.execute('INSERT INTO rangeduels VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (message.author.id, currency, bet, 1, 99, 3, 4, 99, 3, 4, sent.id, message.channel.id))
                    elif duelType == 'boss':
                        level = message.content.split(' ')[3]
                        if level == 'easy':
                            bhp = 100
                        elif level == 'hard':
                            bhp = 500
                        else:
                            bhp = 250
                        boss = random.choice(bosses)
                        c.execute('INSERT INTO bossduels VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)', (message.author.id, currency, bet, boss, level, False, 99, 3, bhp, 0, 0, message.channel.id))
                        sent = await message.channel.send(embed=hpupdate([boss, bhp, 0], [message.author, 99, 3], 'boss', boss + ' awaits. Use `!rocktail`, `!whip`, or `!blood`.'))
                        c.execute('UPDATE bossduels SET messageid={} WHERE id={}'.format(sent.id, message.author.id))
            else:
                await message.channel.send("You don't have that much money!")
        else:
            await message.channel.send(isenough(bet, currency)[1])
        #except:
        #    await message.channel.send('An **error** has occured. Make sure you use `!(mageduel or meleduel) (AMOUNT) (CURRENCY)` or `!(boss) (AMOUNT) (CURRENCY) (easy, normal, hard)`')

    elif message.content in moves:
        inDuel = True
        try:
            c.execute('SELECT Php FROM meleduels WHERE id={}'.format(message.author.id))
            tester = int(c.fetchone()[0])
            duelType = 'mele'
        except:
            try:
                c.execute('SELECT Php FROM mageduels WHERE id={}'.format(message.author.id))
                tester = int(c.fetchone()[0])
                duelType = 'mage'
            except:
                try:
                    c.execute('SELECT Php FROM rangeduels WHERE id={}'.format(message.author.id))
                    tester = int(c.fetchone()[0])
                    duelType = 'range'
                except:
                    try:
                        c.execute('SELECT Php FROM bossduels WHERE id={}'.format(message.author.id))
                        tester = int(c.fetchone()[0])
                        duelType = 'boss'
                    except:
                        inDuel = False

        if inDuel:
            channelid = getvalue(message.author.id, 'channelid', duelType + 'duels')
            channel = client.get_channel(channelid)
            sentid = getvalue(message.author.id, 'messageid', duelType + 'duels')
            sent = await channel.fetch_message(sentid)
            winner = None
            if duelType != 'boss':
                turn = getvalue(message.author.id, 'turn', duelType + 'duels')

            def win(winner, duelType):
                if winner == 'CryptoScape Bot' or winner in ['Commander Zilyana', "K'ril Tsutsaroth", "Kree'arra", 'General Graardor', 'The King Black Dragon']:
                    words = winner + ' won the duel.'
                else:
                    if duelType == 'boss':
                        level = getvalue(winner.id, 'level', 'bossduels')
                        if level == 'easy':
                            multiplier = 1.3
                        elif level == 'hard':
                            multiplier = 3
                        else:
                            multiplier = 2
                    else:
                        multiplier = 1.8
                    currency = getvalue(winner.id, 'currency', duelType + 'duels')
                    bet = getvalue(winner.id, 'bet', duelType + 'duels')
                    update_money(winner.id, currency, bet * multiplier)
                    words = '<@' + str(winner.id) + '> won the duel and gained **' + formatfromk(bet * multiplier) + ' ' + currency + '**!'
                c.execute('DELETE FROM {} WHERE id={}'.format(duelType + 'duels', message.author.id))
                return words

            if duelType == 'mele':
                player = getvalue(message.author.id, ['Php', 'Procktails', 'Pspecial', 'Ppoisoned', 'Ppoisonturns', 'Pspecturns'], 'meleduels')
                player.insert(0, message.author)
                bot = getvalue(message.author.id, ['Bhp', 'Brocktails', 'Bspecial', 'Bpoisoned', 'Bpoisonturns', 'Bspecturns'], 'meleduels')
                bot.insert(0, 'CryptoScape Bot')

                if (turn == 1 and random.randint(0, 1) == 1) or turn > 1:
                    if player[3] < 100:
                        player[6] += 1
                        if (player[6] % 4) == 0:
                            player[3] += 25
                            await sent.edit(embed=hpupdate(bot, player, 'mele', 'You regain **25%** special attack.'))
                            await asyncio.sleep(2.5)
                    if player[4]:
                        player[5] += 1
                        if (player[5] % 4) == 0:
                            player[1] -= 6
                            if player[1] < 0:
                                player[1] == 0
                                winner = bot[0]
                            await sent.edit(embed=hpupdate(bot, player, 'mele', 'You take **6** damage from poison.'))
                            await asyncio.sleep(2.5)

                    if winner == None:
                        if message.content == '!rocktail':
                            winner = await rocktail(player, bot, player, channel, 'mele')
                        elif message.content == '!dds':
                            winner = await dds(player, bot, player, channel)
                        elif message.content == '!whip':
                            winner = await whip(player, bot, player, channel, 'mele', False)
                        else:
                            await channel.send('That is not a valid move!', delete_after = 4)
                else:
                    await channel.send('CryptoScape Bot will go first!', delete_after = 4)

                if winner == None:
                    if bot[3] < 100:
                        bot[6] += 1
                        if (bot[6] % 4) == 0:
                            bot[3] += 25
                            await sent.edit(embed=hpupdate(bot, player, 'mele', 'CryptoScape Bot regains **25%** special attack.'))
                            await asyncio.sleep(2.5)
                    if bot[4]:
                        bot[5] += 1
                        if (bot[5] % 4) == 0:
                            bot[1] -= 6
                            if bot[1] < 0:
                                bot[1] == 0
                                winner = player[0]
                            await sent.edit(embed=hpupdate(bot, player, 'mele', 'CryptoScape Bot takes **6** damage from poison.'))
                            await asyncio.sleep(2.5)

                    if winner == None:
                        if bot[1] < 40 and bot[2] > 0:
                            winner = await rocktail(bot, player, player, channel, 'mele')
                        elif bot[3] >= 25:
                            winner = await dds(bot, player, player, channel)
                        else:
                            winner = await whip(bot, player, player, channel, 'mele', False)

                        if winner != None:
                            await channel.send(win(winner, duelType))
                        await sent.edit(embed=hpupdate(bot, player, 'mele', 'It is your turn! Use `!rocktail`, `!dds`, or `!whip`.'))
                    else:
                        await channel.send(win(winner, duelType))
                else:
                    await channel.send(win(winner, duelType))

            elif duelType == 'mage':
                player = getvalue(message.author.id, ['Php', 'Procktails', 'Pfrozen'], 'mageduels')
                player.insert(0, message.author)
                bot = getvalue(message.author.id, ['Bhp', 'Brocktails', 'Bfrozen'], 'mageduels')
                bot.insert(0, 'CryptoScape Bot')

                if (turn == 1 and random.randint(0, 1) == 1) or turn > 1:
                    if player[3]:
                        await sent.edit(embed=hpupdate(bot, player, 'mage', 'You are frozen and cannot do anything this turn.'))
                        await asyncio.sleep(2.5)
                        player[3] = False
                    else:
                        if message.content == '!rocktail':
                            winner = await rocktail(player, bot, player, channel, 'mage')
                        elif message.content == '!ice':
                            winner = await ice(player, bot, player, channel)
                        elif message.content == '!blood':
                            winner = await blood(player, bot, player, channel, 'mage', False)
                        else:
                            await channel.send('That is not a valid move!', delete_after = 4)
                else:
                    await channel.send('CryptoScape Bot will go first!', delete_after = 4)

                if winner == None:
                    if bot[3]:
                        await sent.edit(embed=hpupdate(bot, player, 'mage', 'CryptoScape Bot is frozen and cannot do anything this turn.'))
                        await asyncio.sleep(2.5)
                        bot[3] = False
                    else:
                        if bot[1] < 30 and bot[2] > 0:
                            winner = await rocktail(bot, player, player, channel, 'mage')
                        elif bot[1] > 30 and bot[1] < 50:
                            winner = await blood(bot, player, player, channel, 'mage', False)
                        else:
                            winner = await ice(bot, player, player, channel)

                    if winner != None:
                        await channel.send(win(winner, duelType))
                    await sent.edit(embed=hpupdate(bot, player, 'mage', 'It is your turn! Use `!rocktail`, `!ice`, or `!blood`.'))
                else:
                    await channel.send(win(winner, duelType))

            elif duelType == 'range':
                player = getvalue(message.author.id, ['Php', 'Procktails', 'Pknives'], 'rangeduels')
                player.insert(0, message.author)
                bot = getvalue(message.author.id, ['Bhp', 'Brocktails', 'Bknives'], 'rangeduels')
                bot.insert(0, 'CryptoScape Bot')

                if (turn == 1 and random.randint(0, 1) == 1) or turn > 1:
                    if message.content == '!rocktail':
                        winner = await rocktail(player, bot, player, channel, 'range')
                    elif message.content == '!bow':
                        winner = await bow(player, bot, player, channel)
                    elif message.content == '!knife':
                        winner = await knife(player, bot, player, channel)
                    else:
                        await channel.send('That is not a valid move!', delete_after = 4)
                else:
                    await channel.send('CryptoScape Bot will go first!', delete_after = 4)

                if winner == None:
                    if bot[1] < 30 and bot[2] > 0:
                        winner = await rocktail(bot, player, player, channel, 'range')
                    elif bot[3] > 0:
                        winner = await knife(bot, player, player, channel)
                    else:
                        winner = await bow(bot, player, player, channel)

                    if winner != None:
                        await channel.send(win(winner, duelType))
                    await sent.edit(embed=hpupdate(bot, player, 'range', 'It is your turn! Use `!rocktail`, `!bow`, or `!knife`.'))
                else:
                    await channel.send(win(winner, duelType))

            elif duelType == 'boss':
                player = getvalue(message.author.id, ['Php', 'Procktails'], 'bossduels')
                player.insert(0, message.author)
                bot = getvalue(message.author.id, ['boss', 'Bhp', 'Brocktails'], 'bossduels')
                level = getvalue(message.author.id, 'level', 'bossduels')
                reflected = getvalue(message.author.id, 'reflect', 'bossduels')

                if message.content == '!rocktail':
                    winner = await rocktail(player, bot, player, channel, 'boss')
                elif message.content == '!whip':
                    winner = await whip(player, bot, player, channel, 'boss', reflected)
                elif message.content == '!blood':
                    winner = await blood(player, bot, player, channel, 'boss', reflected)
                else:
                    await channel.send('That is not a valid move!', delete_after = 4)

                if reflected:
                    c.execute('UPDATE bossduels SET reflect={} WHERE id={}'.format(False, message.author.id))
                    await message.channel.send(bot[0] + ' is no longer reflecting damage back at you', delete_after=2.5)
                    await asyncio.sleep(2.5)

                if winner == None:
                    if level == 'easy':
                        await attack(bot, player, 20, channel)
                    elif level == 'normal':
                        if bot[1] > 100:
                            if random.randint(1, 3) == 1:
                                winner = await leach(bot, player, 15, 0.3, channel)
                            else:
                                winner = await attack(bot, player, 25, channel)
                        else:
                            if random.randint(1, 3) == 1:
                                winner = await attack(bot, player, 20, channel)
                            else:
                                winner = await leach(bot, player, 20, 0.5, channel)
                    else:
                        if bot[1] > 300:
                            if random.randint(1, 2) == 1:
                                await reflect(bot, player, channel)
                            else:
                                winner = await attack(bot, player, 40, channel)
                        else:
                            if random.randint(1, 3) == 1:
                                winner = await attack(bot, player, 25, channel)
                            else:
                                winner = await leach(bot, player, 15, 2, channel)
    
                    if winner != None:
                        await channel.send(win(winner, duelType))
                    else:
                        await sent.edit(embed=hpupdate(bot, player, 'boss', 'It is your turn! Use `!rocktail`, `!whip`, or `!blood`.'))
                else:
                    await channel.send(win(winner, duelType))


            updateDuel(player, message.author.id, duelType)
            updateDuel(bot, message.author.id, duelType)
            if duelType != 'boss':
                c.execute('UPDATE {} SET turn={} WHERE id={}'.format(duelType + 'duels', turn + 1, message.author.id))
            await message.delete()
        else:
            await message.channel.send('You are not in a duel right now. Use `!(mageduel, meleduel, or boss) (AMOUNT) (CURRENCY)` to start one.')
    #######################################




#website info
#total wallet
#donate system
#duel system
#more words

client.loop.create_task(my_background_task())
Bot_Token = os.environ['TOKEN']
client.run(str(Bot_Token))
#heroku pg:psql postgresql-shallow-22073 --app cscape2
#https://discordapp.com/oauth2/authorize?client_id=479862852895899649&scope=bot&permissions=0