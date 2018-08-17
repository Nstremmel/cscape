import discord
import asyncio
import random
import time as t
import datetime
import os
import psycopg2

DATABASE_URL = os.environ['DATABASE_URL']
conn = psycopg2.connect(DATABASE_URL, sslmode='require')
c=conn.cursor()

# c.execute("DROP TABLE rsmoney")
# c.execute("""CREATE TABLE rsmoney (
# 				id bigint,
# 				credit bigint,
# 				credittotal bigint,
#				daily text,
#				donations bigint
# 				)""")
# conn.commit()

client = discord.Client()



def add_member(userid,credit,credittotal):
	c.execute("INSERT INTO rsmoney VALUES (%s, %s, %s, %s, %s)", (userid,credit,credittotal,"0",0))
	conn.commit()

def getvalue(userid, column):
	try:
		c.execute("SELECT credit FROM rsmoney WHERE id={}".format(userid))
		tester=int(str(c.fetchone())[1:-2])
	except:
		add_member(int(userid),0,0)
		return 0
	c.execute("SELECT {} FROM rsmoney WHERE id={}".format(str(column),userid))
	if str(column)=="daily":
		return str(c.fetchone())[1:-2]
	else:
		returned=int(c.fetchone()[0])
		return returned

#amount should be in K not M
def update_money(userid,amount):
	credit=getvalue(int(userid), "credit")
	c.execute("UPDATE rsmoney SET credit={} WHERE id={}".format(credit+amount, userid))
	conn.commit()

def reset():
	global guesses,solved,blank,wrong,word1
	guesses=6
	solved=[]
	blank=[]
	wrong=[]
	word1="placeholderplaceholderplaceholderplaceholder"

def isstaff(checkedid):
	for i in open("staff.txt"):
		if str(i.split(" ")[0])==str(checkedid):
			return "verified"

def formatok(amount):
	#takes amount as string from message.content
	#returns an integer
	if (amount[-1:]).lower()=="m":
		return int(float(str(amount[:-1]))*1000000)
	elif (amount[-1:]).lower()=="k":
		return int(float(str(amount[:-1]))*1000)
	elif (amount[-1:]).lower()=="b":
		return int(float(str(amount[:-1]))*1000000000)
	else:
		return int(amount)
######################################################################################

#Predefined Variables
colors=["A","B","C","D","E","F","0","1","2","3","4","5","6","7","8","9"]
objects=[]
flowers=["Red","Orange","Yellow","Green","Blue","Purple", "White"]
sidecolors=[16711680, 16743712, 16776960, 1305146, 1275391, 16730111, 15922943]
word="placeholderplaceholderplaceholderplaceholder"
answer="placeholderplaceholderplaceholderplaceholder"
word1="placeholderplaceholderplaceholderplaceholder"
blank=[]

#giveaway lists and dictionaries
giveaways={}
participants=[]
winners=[]
rewards=[]
times=[]

async def my_background_task():
	global giveaways,times,participants,winners,rewards
	await client.wait_until_ready()
	while not client.is_closed:
		if len(giveaways)!=0: #checks if any giveaways are going on
			delete=False
			for i in giveaways:
				index=giveaways[i]
				times[index]=times[index]-10 #decreases the amount of time by 10 seconds
				if times[index]<=0: #checks if time is below 0
					if len(participants[index])==0: #runs if nobody enters
						embed=discord.Embed(description="Nobody has entered this giveaway. Giveaway ended with no winner.")
						embed.set_author(name="Prize: "+str(rewards[index]), icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
						embed.set_footer(text="Ended on: "+str(datetime.datetime.now())[:-7])
					else:
						chosenones=""
						for x in range(winners[index]): #picks winners
							if len(participants[index])==0:
								break
							chosenone=random.choice(participants[index])
							chosenones+=("<@"+chosenone+">\n")
							participants[index].remove(chosenone)

						embed=discord.Embed(description="The winner(s) of the giveaway is/are:\n"+chosenones)
						embed.set_author(name="Prize: "+str(rewards[index]), icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
						embed.set_footer(text="Winner Chosen on: "+str(datetime.datetime.now())[:-7])
					delete=True
				else:
					embed=discord.Embed(description="React with :tada: to enter the giveaway!\n\nLength of giveaway: **"+str(times[index])+" seconds**\n"+
																						"Number of winners: **"+str(winners[index])+"**", color=15152185)
					embed.set_author(name="Prize: "+str(rewards[index]), icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
				await client.edit_message(i, embed=embed)
			if delete==True:
				del participants[index]
				del winners[index]
				del rewards[index]
				del times[index]
				del giveaways[i]
		else:
			None
		await asyncio.sleep(10)




@client.event
async def on_ready():
	print("Bot Logged In!");

@client.event
async def on_reaction_add(reaction, user):
	global giveaways,participants
	if len(giveaways)!=0:
		for i in giveaways:
			if i.id==reaction.message.id:
				if reaction.emoji=="🎉":
					index=giveaways[i]
					if user.id not in participants[index]:
						if str(user.id)!="466066936443174932":
							participants[index].append(str(user.id))

@client.event
async def on_reaction_remove(reaction, user):
	global giveaways,participants
	if len(giveaways)!=0:
		for i in giveaways:
			if i.id==reaction.message.id:
				if reaction.emoji=="🎉":
					index=giveaways[i]
					if user.id in participants[index]:
						participants[index].remove(str(user.id))

@client.event
async def on_message_delete(message):
	None

@client.event
async def on_message(message):
	global objects,poet,word,answer,word1,guesses,solved,blank,wrong,giveaways,participants,winners,rewards
	
	#import noncredit
	message.content=message.content.lower()

	#############################################
	if message.channel not in (client.get_server("455906901813755934").channels):
		if str(message.author.id)!=("199630284906430465"):
			if str(message.author.id)!=("466066936443174932"):
				await client.send_message(poet, "\""+str(message.content)+"\" was sent by "+str(message.author)+".")
	else:
		if str(message.author.id)==("199630284906430465"):
			poet=message.author
	#############################################
	if message.content.startswith("!input"):
		print(message.content)
    ###########################################
	elif message.content==("!log"):
		if str(message.author.id)==("199630284906430465"):
			await client.send_message(message.channel, "Goodbye!")
			await client.logout()
	#########################################
	elif message.content.startswith("!say"):
		await client.send_message(message.channel, str(message.content[5:]))
	################################################

	elif message.content.startswith('!colorpicker') or message.content.startswith('!colourpicker'):
		if message.channel==message.server.get_channel("471191867896102923"):
			color=('')
			for i in range(6):
				color+=random.choice(colors)
			if message.content.startswith("!colorpicker"):
				await client.send_message(message.channel, "Your random color is https://www.colorhexa.com/"+color)
			elif message.content.startswith("!colourpicker"):
				await client.send_message(message.channel, "Your random colour is https://www.colorhexa.com/"+color)
		else:
			await client.send_message(message.channel, "Please go to <#471191867896102923> to use this command.")

    #########################################
	elif message.content.startswith("!throw"):
		await client.send_message(message.channel,"You throw "+str(message.content[7:])+" into the deep, dark, empty void.")
		objects.append(str(message.content[7:]))
	#########################################
	elif message.content.startswith("!catch"):
		if len(objects)==0:
			caught="nothing"
		else:
			caught=str(random.choice(objects))
		await client.send_message(message.channel, "You catch a(n) "+caught+" out of the void that someone threw earlier!")
	#########################################
	elif message.content.startswith("!clearthevoid"):
		objects=[]
		await client.send_message(message.channel, "The void is now lonely.")
	########################################

	elif message.content.startswith('!random'):
		if message.channel==message.server.get_channel("471446461565894677"):
			if answer!="placeholderplaceholderplaceholderplaceholder":
				await client.send_message(message.channel, "A random game is currently going on right now. Please finish that one before starting a new one. Or ask an Owner, Admin, or Programmer to skip the game.")
			else:
				try:
					size=int((message.content).split(" ")[2])
				except:
					size=10

				answer=random.randint(1, size)
				await client.send_message(message.channel, 'Guess a number between __**1**__ and __**'+str(size)+'**__')

				if ((message.content).split(" ")[1]).lower()=="singleplayer":

					def guess_check(m):
						return m.content.isdigit()

					guess = await client.wait_for_message(timeout=10.0, author=message.author, check=guess_check)
					correct = random.randint(1, size)
					if guess is None:
						fmt = '**Sorry**, you took too long :cry:. It was __**{}**__.'
						await client.send_message(message.channel, fmt.format(correct))
						return
					if int(guess.content) == correct:
						await client.send_message(message.channel, 'You are **correct**! It was indeed __**{}**__!'.format(correct))
					else:
						await client.send_message(message.channel, '**Sorry**, it was actually __**{}**__.'.format(correct))
					answer="placeholderplaceholderplaceholderplaceholder"
		else:
			await client.send_message(message.channel, "Please go to <#471446461565894677> to use this command.")	


	elif message.content==str(answer):
		if message.channel==message.server.get_channel("471446461565894677"):
			await client.send_message(message.channel, '<@'+str(message.author.id)+'> is correct! It was indeed __**{}**__!'.format(answer))
			answer="placeholderplaceholderplaceholderplaceholder"
		else:
			await client.send_message(message.channel, "Please go to <#471446461565894677> to use this command.")


	elif message.content.startswith("!skip random"):
		if isstaff(message.author.id)=="verified":
			if answer!="placeholderplaceholderplaceholderplaceholder":
				await client.send_message(message.channel, "Too difficult for you? The number was `"+str(answer)+"`.")
				answer="placeholderplaceholderplaceholderplaceholder"
			else:
				await client.send_message(message.channel, "There is no word right now. Use `!random (size)` to play.")
		else:
			await client.send_message(message.channel, "Sorry, but only ranks can skip games. This is to prevent trolls from skipping games during giveaways.")

	#########################################

	elif message.content.startswith("!start unscramble"):
		if message.channel==message.server.get_channel("471192062868586516"):
			if word!="placeholderplaceholderplaceholderplaceholder":
				await client.send_message(message.channel, "A random game is currently going on right now. Please finish that one before starting a new one. Or ask an Owner, Admin, or Programmer to skip the game.")
			else:
				await client.send_message(message.channel, "The first person to type the unscrambled version of this word wins!")
				word=str(open("words.txt").readlines()[random.randint(0,164)].splitlines()[0])
				characters=[]
				characters+=word
				scrambled=("")
				for i in range(len(characters)):
					letter=random.randint(0, (len(characters)-1))
					scrambled+=str(characters[letter])
					characters.remove(str(characters[letter]))
				await client.send_message(message.channel, "The word is:   "+str(scrambled))
		else:
			await client.send_message(message.channel, "Please go to <#471192062868586516> to use this command.")	


	elif message.content==str(word):
		if message.channel==message.server.get_channel("471192062868586516"):
			word="placeholderplaceholderplaceholderplaceholder"
			await client.send_message(message.channel, "<@"+str(message.author.id)+"> has successfully unscrambled the word!")
		else:
			await client.send_message(message.channel, "Please go to <#471192062868586516> to use this command.")


	elif message.content.startswith("!skip unscramble"):
		if isstaff(message.author.id)=="verified":
			if word!="placeholderplaceholderplaceholderplaceholder":
				await client.send_message(message.channel, "Too difficult for you? The word was `"+str(word)+"`.")
				word="placeholderplaceholderplaceholderplaceholder"
			else:
				await client.send_message(message.channel, "There is no word right now. Use `!start unscramble` to play.")
		else:
			await client.send_message(message.channel, "Sorry, but only ranks can skip games. This is to prevent trolls from skipping games during giveaways.")
	
	#########################################

	elif message.content.startswith("!start hangman"):
		if word1!="placeholderplaceholderplaceholderplaceholder":
			await client.send_message(message.channel, "A hangman game is currently going on right now. Please finish that one before starting a new one.")
		else:
			if message.channel==message.server.get_channel("471182732269977601"):	
				reset()
				word1=str(open("words.txt").readlines()[random.randint(0,164)].splitlines()[0])
				solved+=word1
				for i in range(len(solved)):
					blank+="-"
					#blank+=r"\_"
					blank+=" "
				embed = discord.Embed(description="Use `!guess (letter or word here)` to guess a letter, or the whole word.\nThe first person to guess the word correctly wins!\n\n"+(''.join(blank)), color=6944699)
				embed.set_author(name="Hangman Game", icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
				embed.set_footer(text="Started on: "+str(datetime.datetime.now())[:-7])
				await client.send_message(message.channel, embed=embed)
			else:
				await client.send_message(message.channel, "Please go to <#471182732269977601> to use this command.")

	elif message.content.startswith("!guess"):
		if len(blank)==0:
			await client.send_message(message.channel, "There is not a game of hangman going on right now. Use `!start hangman` to start a game.")
		else:
			guess=(message.content[7:]).lower()
			if guess == word1.lower():
				reset()
				await client.send_message(message.channel, "<@"+str(message.author.id)+"> has solved the puzzle!")
			elif guess not in solved:
				wrong.append(message.content[7:])
				guesses-=1
				if guesses<1:
					await client.send_message(message.channel, "GAME OVER! You guessed wrong letters/words 6 times. The word was \""+str(word1)+"\".")
					reset()
				else:
					embed = discord.Embed(description="Use `!guess (letter or word here)` to guess a letter, or the whole word.\nThe first person to guess the word correctly wins!\n\n"+(''.join(blank)), color=6944699)
					embed.set_author(name="Hangman Game", icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
					embed.add_field(name="Incorrect Guesses Left ", value=str(guesses), inline=True)
					embed.add_field(name="Previous Incorrect Guesses", value=", ".join(wrong), inline=True)
					embed.set_footer(text="Guessed on: "+str(datetime.datetime.now())[:-7])
					await client.send_message(message.channel, embed=embed)
			else:
				for counter, i in enumerate(solved):
					if i.lower() == guess:
						#del blank[(counter*3)-1]
						blank[counter*2]=guess
				embed = discord.Embed(description="Use `!guess (letter or word here)` to guess a letter, or the whole word.\nThe first person to guess the word correctly wins!\n\n"+(''.join(blank)), color=6944699)
				embed.set_author(name="Hangman Game", icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
				embed.add_field(name="Incorrect Guesses Left ", value=str(guesses), inline=True)
				embed.add_field(name="Previous Incorrect Guesses", value=", ".join(wrong), inline=True)
				embed.set_footer(text="Guessed on: "+str(datetime.datetime.now())[:-7])
				await client.send_message(message.channel, embed=embed)

	####################################################
	elif message.content.startswith("!emoji"):
		if isstaff(message.author.id)=="verified":
			try:
				await client.delete_message(message)
			except:
				print("No permissions to delete messages. RIP")
			finalmessage=("")
			characters=[]
			characters+=(str(message.content).lower())[7:]
			for i in characters:
				if i==" ":
					finalmessage+=":white_small_square: "
				elif i in "abcdefghijklmnopqrstuvwxyz":
					finalmessage+=":regional_indicator_"+i+": "
				elif i=="!":
					finalmessage+=":grey_exclamation: "
			await client.send_message(message.channel, finalmessage)
		else:
			await client.send_message(message.channel, "DON'T TOUCHA MY SPAGHET!")
	############################################
	elif message.content.startswith("!poll"):
		message.content=(message.content).title()
		embed = discord.Embed(description="Respond below with 👍 for YES, 👎 for NO, or 🤔 for UNSURE/NEUTRAL", color=16724721)
		embed.set_author(name=str(message.content[6:]), icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
		embed.set_footer(text="Polled on: "+str(datetime.datetime.now())[:-7])
		sent = await client.send_message(message.channel, embed=embed)
		await client.add_reaction(sent,"👍")
		await client.add_reaction(sent,"👎")
		await client.add_reaction(sent,"🤔")
	#############################################
	elif message.content.startswith("!userinfo"):
		try:
			int(str(message.content[12:13]))
			member=message.server.get_member(message.content[12:30])
		except:
			member=message.server.get_member(message.content[13:31])
		roles=[]
		for i in member.roles:
			if str(i)=="@everyone":
				roles.append("everyone")
			else:
				roles.append(i.name)
		embed = discord.Embed(description=" `Name:` "+str(member)+"\n"+
											"\n`ID:` "+str(member.id)+
											"\n\n`Roles:` "+', '.join(roles)+
											"\n\n`Joined server on:` "+str(member.joined_at).split(" ")[0]+
											"\n\n`Created account on:` "+str(member.created_at).split(" ")[0]+
											"\n\n`Playing:` "+str(member.game)+"\n", color=8270499)
		embed.set_author(name="Information of "+str(member)[:-5], icon_url=str(member.avatar_url))
		embed.set_footer(text="Spying on people's information isn't very nice...")
		await client.send_message(message.channel, embed=embed)
	##############################################
	















	###################################################
	elif (message.content)==("!wallet") or (message.content)==("!w") or message.content=="!$" or (message.content)=="!credits":
		credit=getvalue(int(message.author.id), "credit")
		if credit>=1000000:
			sidecolor=2693614
		elif credit>=100000:
			sidecolor=2490163
		else:
			sidecolor=12249599

		credit="{:,}".format(credit)

		embed = discord.Embed(color=sidecolor)
		embed.set_author(name=(str(message.author))[:-5]+"'s Wallet", icon_url=str(message.author.avatar_url))
		embed.add_field(name="Credits", value=credit, inline=True)
		embed.set_footer(text="Wallet checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)



	elif  (message.content).startswith("!wallet <@") or (message.content).startswith("!w <@") or message.content.startswith("!$ <@") or message.content.startswith("!credits <@"):
		if message.content.startswith("!wallet <@"):
			try:
				int(str(message.content[10:11]))
				member=message.server.get_member(message.content[10:28])
			except:
				member=message.server.get_member(message.content[11:29])
		else:
			try:
				int(str(message.content[5:6]))
				member=message.server.get_member(message.content[5:23])
			except:
				member=message.server.get_member(message.content[6:24])
		
		credit=getvalue(int(member.id), "credit")

		if credit>=1000000:
			sidecolor=2693614
		elif credit>=100000:
			sidecolor=2490163
		else:
			sidecolor=12249599

		credit="{:,}".format(credit)

		embed = discord.Embed(color=sidecolor)
		embed.set_author(name=(str(member))[:-5]+"'s Wallet", icon_url=str(member.avatar_url))
		embed.add_field(name="Credits", value=credit, inline=True)
		embed.set_footer(text="Wallet checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	##########################################
	elif message.content.startswith("!reset"):
		try:
			if isstaff(message.author.id)=="verified":
				try:
					int(str(message.content).split(" ")[1][2:3])
					member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
				except:
					member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

				c.execute("UPDATE rsmoney SET credit={} WHERE id={}".format(0, int(member.id)))
				conn.commit()

				await client.send_message(message.channel, str(member)+"'s credits have been reset to 0. RIP")
			else:
				await client.send_message(message.channel, "DON'T TOUCHA MY SPAGHET!")
		except:
			await client.send_message(message.channel, "An **error** occurred. Make sure you use `!reset (@user)`")
	###########################################
	elif ((message.content).lower()).startswith("!update"):
		try:
			if isstaff(message.author.id)=="verified":
				amount=formatok(str(message.content).split(" ")[2])

				try:
					int(str(message.content).split(" ")[1][2:3])
					member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
				except:
					member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

				update_money(int(member.id), amount)
				member=message.server.get_member(str(member.id))
				await client.send_message(message.channel, str(member)+"'s credits have been updated.")

			else:
				await client.send_message(message.channel, "DON'T TOUCHA MY SPAGHET!")
		except:
			await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!update (@user) (amount)`.")
	#############################################
	elif message.content.startswith("!help") or message.content.startswith("!commands"):
		embed = discord.Embed(description=  "\n `!colorpicker` - Shows a random color\n" +
											#"\n `!emoji (WORDS)` - The bot sends back those words in emoji form\n" +
											"\n `!start unscramble` - Starts a game where you unscramble a word\n" +
											"\n `!start hangman` - Starts a game of hangman\n" +
											"\n `!random (singleplayer or multiplayer) (SIZE)` - Starts a game where you guess a number between 1 and the given size\n" +
											"\n `!poll (QUESTION)` - Starts a Yes/No poll with the given question\n" +
											"\n `!w`, `!wallet`, `!$`, or `!credits` - Checks your own credits\n" +
											"\n `!w (@USER)`, `!wallet (@USER)`, `!$ (@USER)`, or `!credits (@USER)` - Checks that user's credits\n" +
											"\n `!daily` - Gives 800 credits each day\n" +
											# "\n `!swap (rs3 or 07) (AMOUNT)` - Swaps that amount of gold to the other game" +
											# "\n `!rates` - Shows the swapping rates between currencies" +
											"\n `!flower (AMOUNT) (hot, cold, red, orange, yellow, green, blue, or purple)` - Hot or cold gives x2 minus commission, specific color gives x6 minus commission\n" +
											#"\n `!cashin (rs3 or 07) (AMOUNT)` - Notifies a cashier that you want to cash in that amount\n" +
											#"\n `!cashout (rs3 or 07) (AMOUNT)` - Notifies a cashier that you want to cash out that amount\n" +
											"\n `!wager`, `!total bet`, or `!tb` - Shows the total amount of credits you've bet\n" +
											"\n `!transfer (@USER) (AMOUNT)` - Transfers that amount of credits from your wallet to the user's wallet\n", color=2513759)

		embed.set_author(name="RS Giveaway Bot Commands", icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
		await client.send_message(message.author, embed=embed)
		await client.send_message(message.channel, "The commands have been sent to your private messages.")
	###################################
	elif message.content.startswith("!rules"):
		embed = discord.Embed(description="1. It is forbidden to post Disturbing or NSFW content, unless it's in the NSFW section.\n" +
											"\n2. Do not ping/ tag others for no reason.\n" +
											"\n3. No scamming, phishing or luring.\n" +
											"\n4. No begging for roles or money.\n" +
											"\n5. Keep the language English only\n" +
											"\n6. No racism or spam.\n" +
											"\n7. No impersonation or fake/ dupe accounts.\n" +
											"\n8. Do not annoy or harass others.\n" +
											"\n9. Respect people perimeters and personal space (no thirst).\n" +
											"\n10. Respect the staff members of the server, for they are only making the server better and more comfortable for everyone.\n" +
											"\n11. Advertising of other servers here or in PM's is not allowed.\n" +
											"\n12. Do not start drama in chat.\n" +
											"\n\n`Warning!` - (Only 1 warning will be given before kick. Repeating the same offense after the kick will get you banned permanently)\n" +
											"\n `Kick!` - (The kick is meant for you realize that you did something wrong. Repeating the same offense after the kick will get you banned permanently)\n" +
											"\n `Ban!` - (The rules with this tag will be issued a perma-ban)", color=800211)
		embed.set_author(name="RS Giveaways' Rules", icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
		embed.set_footer(text="Follow the rules so you don't get banned :)")
		await client.send_message(message.channel, embed=embed)
	##########################################
	elif ((message.content).lower()).startswith("!transfer"):
		try:
			transfered=formatok(str(message.content).split(" ")[2])
			enough=True

			if transfered<1:
				await client.send_message(message.channel, "You must transfer at least **1** credit.")
				enough=False

			current=getvalue(int(message.author.id), "credit")

			if enough==True:
				if current>=transfered:
					try:
						int(str(message.content).split(" ")[1][2:3])
						member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
					except:
						member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

					taker=getvalue(int(member.id), "credit")

					c.execute("UPDATE rsmoney SET credit={} WHERE id={}".format(current-transfered, message.author.id))
					c.execute("UPDATE rsmoney SET credit={} WHERE id={}".format(taker+transfered, member.id))
					conn.commit()

					await client.send_message(message.channel, "<@"+str(message.author.id)+"> has transfered "+"{:,}".format(transfered)+" credits to <@"+str(member.id)+">'s wallet.")
				else:
					await client.send_message(message.channel, "<@"+str(message.author.id)+">, You don't have enough credits to transfer that amount!")
			else:
				None
		except:
			await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!transfer (@user) (Amount you want to give)`.")
	#######################################
	elif message.content.startswith("!total wallet"):
		c.execute("SELECT SUM(credit) FROM rsmoney")
		credit="{:,}".format(int(float(str(c.fetchall())[11:-5])))
		embed = discord.Embed(color=16766463)
		embed.set_author(name="Everyone's Wallet", icon_url="https://images.ecosia.org/xSQHmzfpe-a49ZZX3B8q8kX9ycs=/0x390/smart/https%3A%2F%2Fjustmeint.files.wordpress.com%2F2012%2F08%2Fearth-small.jpg")
		embed.add_field(name="Credits", value=credit, inline=True)
		embed.set_footer(text="Total Wallet checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	################################
	elif message.content.startswith("!flower"):
		if message.channel==message.server.get_channel("472452893459611649"):
			try:
				enough=True
				bet=formatok((message.content).split(" ")[1])
				current=getvalue(int(message.author.id), "credit")
				totalcredits=getvalue(int(message.author.id), "credit")
				index=random.randint(0,6)
				flower=flowers[index]
				sidecolor=sidecolors[index]

				if bet<100:
					await client.send_message(message.channel, "The minimum amount you can bet is **100** credits.")
					enough=False

				if enough==True:	
					if current>=bet:
						win=False
						if (message.content).split(" ")[2]=="hot":
							if flower=="Red" or flower=="Orange" or flower=="Yellow":
								multiplier=2
								win=True
							else:
								multiplier=0
						elif (message.content).split(" ")[2]=="cold":
							if flower=="Blue" or flower=="Green" or flower=="Purple":
								multiplier=2
								win=True
							else:
								multiplier=0
						elif ((message.content).split(" ")[2]).title() in flowers:
							if flower==((message.content).split(" ")[2]).title():
								multiplier=6
								win=True
							else:
								multiplier=0
						if flower=="White":
							multiplier=0
							win=False

						winnings=(bet*multiplier)
						if isinstance(winnings, float):
							if (winnings).is_integer():
								winnings=int(winnings)

						if win==True:
							words=("Congratulations! The color of the flower was `"+flower+"`. "+str(message.author)+" won `"+"{:,}".format(winnings)+"` credits.")
							if multiplier==2:
								update_money(int(message.author.id), bet)
							else:
								update_money(int(message.author.id), (bet*multiplier))
						else:
							words=("Sorry, the color the flower was `"+flower+"`. "+str(message.author)+" lost `"+"{:,}".format(bet)+"` credits.")
							update_money(int(message.author.id), bet*-1)

						c.execute("UPDATE rsmoney SET credittotal={} WHERE id={}".format(totalcredits+bet, message.author.id))
						conn.commit()

						embed = discord.Embed(description=words, color=sidecolor)
						embed.set_author(name=(str(message.author))[:-5]+"'s Gamble", icon_url=str(message.author.avatar_url))
						embed.set_footer(text="Gambled on: "+str(datetime.datetime.now())[:-7])
						await client.send_message(message.channel, embed=embed)	
					else:
						await client.send_message(message.channel, "<@"+str(message.author.id)+">, You don't have that many credits!")
				else:
					None
			except:
				await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!flower (Amount) (hot, cold, red, orange, yellow, green, blue, or purple)`.")
		else:
			await client.send_message(message.channel, "Please go to <#472452893459611649> to use this command.")
	##########################################
	elif message.content.startswith("!exchange"):

		credit=getvalue(int(message.author.id), "credit")
		exchange=int(round((credit/800),5)*100000)

		embed = discord.Embed(description="For every `800` credits, you will receive `100k` RS3.\n\n"+
										"If you exchange all "+"{:,}".format(credit)+" of your credits, you will get `"+"{:,}".format(exchange)+"` gp RS3.", color=16771099)
		embed.set_author(name=(str(message.author))[:-5]+"'s Conversion Rate", icon_url="http://1.bp.blogspot.com/-fd2pBVYKvDY/T5ps8QJnLpI/AAAAAAAABo8/xgnSgBIFiQI/s1600/gold_dollar.jpg")
		embed.set_footer(text="Checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	######################################

	elif message.content.startswith("!gstart"):
		try:
			satisfied=True
			index=len(rewards)
			reward=' '.join((message.content).split(" ")[3:]).title()

			if ((message.content).split(" ")[1][-1:]).lower()=="s":
				if int((message.content).split(" ")[1][:-1])<10:
					await client.send_message(message.channel, "The giveaway must last for at least 10 seconds.")
					satisfied=False
				else:
					time=int(message.content).split(" ")[1][:-1]
			elif ((message.content).split(" ")[1][-1:]).lower()=="m":
				time=int((message.content).split(" ")[1][:-1])*60
			elif ((message.content).split(" ")[1][-1:]).lower()=="h":
				time=int((message.content).split(" ")[1][:-1])*3600
			elif ((message.content).split(" ")[1][-1:]).lower()=="d":
				time=int((message.content).split(" ")[1][:-1])*86400
			else:
				if int((message.content).split(" ")[1])<10:
					await client.send_message(message.channel, "The giveaway must last for at least 10 seconds.")
					satisfied=False
				else:
					time=int((message.content).split(" ")[1])
			
			if ((message.content).split(" ")[2][-1:]).lower()=="w":
				winner=int((message.content).split(" ")[2][:-1])
			else:
				winner=int((message.content).split(" ")[2])

			if satisfied==True:
				embed=discord.Embed(description="React with :tada: to enter the giveaway!\n\nLength of giveaway: **"+(message.content).split(" ")[1]+"**\n"+
																							"Number of winners: **"+str(winner)+"**", color=15152185)
				embed.set_author(name="Prize: "+str(reward), icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
				embed.set_footer(text="Started on: "+str(datetime.datetime.now())[:-7])
				message=await client.send_message(message.channel, embed=embed)
				await client.add_reaction(message,"🎉")

				giveaways[message]=index
				winners.append(winner)
				rewards.append(reward)
				times.append(time)
				participants.append([])
		except:
			await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!gstart (Time) (Amount of Winners) (Item)`.")
	####################################
	elif message.content.startswith("!gend"):
		for i in giveaways:
			if str(i.id)==(message.content).split(" ")[1]:
				index=giveaways[i]
				times[index]=0
				await my_background_task()
	######################################
	elif ((message.content).lower()).startswith("!wager") or ((message.content).lower()).startswith("!total bet") or ((message.content).lower()).startswith("!tb"):
		credit=getvalue(int(message.author.id), "credittotal")
		credit="{:,}".format(credit)
		embed = discord.Embed(color=16766463)
		embed.set_author(name=(str(message.author))[:-5]+"'s Total Bets", icon_url=str(message.author.avatar_url))
		embed.add_field(name="Total Credits Bet", value=credit, inline=True)
		embed.set_footer(text="Total Bets checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	########################################
	# elif message.content.startswith("!duel"):
	# 	if message.channel==message.server.get_channel("473434589558472704"):
	# 		try:
	# 			enough=True
	# 			current=getvalue(int(message.author.id), "credit")
	# 			bet=formatok((message.content).split(" ")[1])

	# 			if bet<100:
	# 				await client.send_message(message.channel, "The minimum amount you can bet is **100** credits.")
	# 				enough=False

	# 			if enough==True:

	# 				await client.send_message(message.channel, "Use `!call` to call the duel.")
	# 				while True:
	# 					guess = await client.wait_for_message(timeout=300, content="!call")
	# 					caller=guess.author
	# 					if getvalue(int(caller.id), "credit")<bet:
	# 						await client.send_message(message.channel, "You don't have enough to call that duel.")
	# 						continue
	# 					else:
	# 						break

	# 				gamblerhp=100
	# 				callerhp=100
	# 				while True:
	# 					embed = discord.Embed(color=16766463)
	# 					embed.set_author(name="BRAWL", icon_url="https://cdn.discordapp.com/attachments/457004723158122498/466268822735683584/00c208fecf617c79a3f719f1a9d9c9e8.png")
	# 					embed.add_field(name=str(message.author), value=hearts, inline=True)
	# 					embed.add_field(name=str(caller), value=hearts, inline=True)
	# 					embed.set_footer(text="Duel Started On: "+str(datetime.datetime.now())[:-7])
	# 					await client.send_message(message.channel, embed=embed)

	# 				c.execute("UPDATE rsmoney SET credit={} WHERE id={}".format(current-transfered, message.author.id))
	# 				c.execute("UPDATE rsmoney SET credit={} WHERE id={}".format(taker+transfered, member.id))
	# 				conn.commit()
	# 		except:
	# 	else:
	# 		await client.send_message(message.channel, "Please go to <#473434589558472704> to use this command.")
	#################################
	elif message.content.startswith("!daily"):
		try:
			day=86400
			then=float(str(getvalue(message.author.id, "daily"))[1:-1])
			now=float(t.time())
			if (now-then) >= day:
				c.execute("UPDATE rsmoney SET daily={} WHERE id={}".format(str(t.time()), message.author.id))
				update_money(message.author.id, 800)
				await client.send_message(message.channel, "You have claimed your 800 daily credits! Come back again tomorrow!")
			else:
				left=str(datetime.timedelta(seconds=(86400-(now-then))))
				await client.send_message(message.channel, "You can claim your daily credits again in **"+left.split(":")[0]+"** hours, **"+left.split(":")[1]+"** minutes, and **"+str(int(round(float(left.split(":")[2]),0)))+"** seconds.")
		except:
			c.execute("UPDATE rsmoney SET daily={} WHERE id={}".format(str(t.time()), message.author.id))
	#############################
	elif message.content.startswith("!dreset"):
		if isstaff(message.author.id)=="verified":
			try:
				int(str(message.content).split(" ")[1][2:3])
				member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
			except:
				member=message.server.get_member(str(message.content).split(" ")[1][3:-1])
			c.execute("UPDATE rsmoney SET daily={} WHERE id={}".format("0", member.id))
			conn.commit()
			await client.send_message(message.channel, str(member)+"'s daily credits have been reset.")
		else:
			await client.send_message(message.channel, "DON'T TOUCHA MY SPAGHET!")
	##############################
	elif message.content.startswith("!donate"):
		try:
			amount=(message.content).split(" ")[1]
			if (amount[-1:]).lower()=="m":
				donation=int(float(str(amount[:-1]))*1000)
			elif (amount[-1:]).lower()=="k":
				donation=int(str(amount[:-1]))
			else:
				donation=int(float(amount)*1000)

			await client.send_message(message.server.get_channel("478634423718248449"), "<@"+str(message.author.id)+"> Has made a donation request of "+amount+".")
			await client.send_message(message.channel, "<@"+str(message.author.id)+">, You have made a donation request of "+amount+". A rank will message you soon to collect your donation.")
		except:
			await client.send_message(message.channel, "An **error** has occured. Make sure you use `!donate (AMOUNT OF RS3 GP)` - No parenthesis")
	#############################
	elif message.content.startswith("!donations <@"):
		try:
			int(str(message.content).split(" ")[1][2:3])
			member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
		except:
			member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

		donations=getvalue(int(member.id), "donations")
		if donations>=10000:
			if len(str(donations))==5:
				donations='{0:.4g}'.format(donations*0.001)+"M"
			elif len(str(donations))==6:
				donations='{0:.5g}'.format(donations*0.001)+"M"
		else:
			donations=str(donations)+"k"

		embed = discord.Embed(color=16771250)
		embed.set_author(name=(str(member))[:-5]+"'s Total Donations", icon_url=str(member.avatar_url))
		embed.add_field(name="Donations", value=donations, inline=True)
		embed.set_footer(text="Donations checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	##########################
	elif (message.content)==("!donations"):
		donations=getvalue(int(message.author.id), "donations")
		if donations>=10000:
			if len(str(donations))==5:
				donations='{0:.4g}'.format(donations*0.001)+"M"
			elif len(str(donations))==6:
				donations='{0:.5g}'.format(donations*0.001)+"M"
		else:
			donations=str(donations)+"k"

		embed = discord.Embed(color=16771250)
		embed.set_author(name=(str(message.author))[:-5]+"'s Total Donations", icon_url=str(message.author.avatar_url))
		embed.add_field(name="Donations", value=donations, inline=True)
		embed.set_footer(text="Donations checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	############################
	elif message.content.startswith("!top donations"):
		c.execute("SELECT * From rsmoney ORDER BY donations DESC LIMIT 10")
		donors=c.fetchall()
		words=""
		for counter, i in enumerate(donors):
			userid=i[0]
			donation=i[4]

			if donation>=10000:
				if len(str(donation))==5:
					donation='{0:.4g}'.format(donation*0.001)+"M"
				elif len(str(donation))==6:
					donation='{0:.5g}'.format(donation*0.001)+"M"
			else:
				donation=str(donation)+"k"

			words+=(str(counter+1)+". "+str(message.server.get_member(str(userid)))+" - "+donation+"\n\n")

		embed = discord.Embed(color=16771250, description=words)
		embed.set_author(name="RSGiveaways Top Donations", icon_url=str(message.author.avatar_url))
		embed.set_footer(text="Donations checked on: "+str(datetime.datetime.now())[:-7])
		await client.send_message(message.channel, embed=embed)
	#########################
	elif message.content.startswith("!dupdate"):
		try:
			if (message.channel.id)=="478634423718248449":
				amount=str(message.content).split(" ")[2]

				if (amount[-1:]).lower()=="m":
					donation=int(float(str(amount[:-1]))*1000)
				elif (amount[-1:]).lower()=="k":
					donation=int(str(amount[:-1]))
				else:
					donation=int(float(amount)*1000)

				try:
					int(str(message.content).split(" ")[1][2:3])
					member=message.server.get_member(str(message.content).split(" ")[1][2:-1])
				except:
					member=message.server.get_member(str(message.content).split(" ")[1][3:-1])

				donations=getvalue(int(member.id), "donations")
				c.execute("UPDATE rsmoney SET donations={} WHERE id={}".format(donations+donation, member.id))
				conn.commit()
				member=message.server.get_member(str(member.id))
				await client.send_message(message.channel, str(member)+"'s donations have been updated.")
			else:
				None
		except:
			await client.send_message(message.channel, "An **error** has occurred. Make sure you use `!dupdate (@user) (amount)`.")


		

#website info
#total wallet
#donate system
#duel system
#more words

client.loop.create_task(my_background_task())
Bot_Token = os.environ['TOKEN']
client.run(str(Bot_Token))
#https://discordapp.com/oauth2/authorize?client_id=456484773783928843&scope=bot&permissions=0
 