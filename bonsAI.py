# bonsAI Discord Moderation Bot using Artificial Intelligence
# Copyright (C) 2021 lmaobadatmath

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import discord, json, requests
from ratelimit import limits
import string
from settings import API_KEY, DISCORD_TOKEN
import re

client = discord.Client()

#this limit is because the Perspective API only allows one request per second
@limits(calls=1, period=1)
def toxic_check(message):
    api_key = API_KEY
    url = ('https://commentanalyzer.googleapis.com/v1alpha1/comments:analyze' + '?key=' + api_key)
    
#This part send a request to analyze the discord message based on whether it contains a threat, severe toxicity or an identity attack
    data_dict = {
        'comment': {'text': message},
        'languages': ['en'],
        'requestedAttributes': {'THREAT': {}, 'SEVERE_TOXICITY':{}, 'IDENTITY_ATTACK':{}},
        'doNotStore': 'true'
    }

    response = requests.post(url=url, data=json.dumps(data_dict)) 
    response_dict = json.loads(response.content)
    global thrattack
    global toxattack
    global toxattack
    global attack 
    thrattack = response_dict["attributeScores"]["THREAT"]["summaryScore"]["value"]
    toxattack = response_dict["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
    ideattack = response_dict["attributeScores"]["IDENTITY_ATTACK"]["summaryScore"]["value"]
    attack= max(thrattack,toxattack,ideattack)
    return attack

#sets the status of the of bot, in this case "Playing with AI"
@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))
    await client.change_presence(activity=discord.Game(name='with AI'))
    

@client.event
async def on_message(message): #creates the modqueue embed and sends reactions
    if message.author == client.user:
        return
    try:
        if toxic_check(message.clean_content) > 0.9:
            toxreason= await get_tox()
            jump_url = f"[Click to see context.]({message.jump_url})"
            mess=message.content
            chanl= client.get_channel(834778270968446976) #change channel id to match your modqueue channel id
            toxembed=discord.Embed(title='New potentially inappropriate message:',colour = discord.Colour.red())
            name= f"{message.author.name}#{message.author.discriminator}"
            toxembed.set_author(name=name , icon_url=message.author.avatar_url)
            toxembed.description = mess
            toxembed.add_field(name = "Flagged for: ", value =toxreason)
            toxembed.add_field(name = "Context:", value =jump_url)
            toxembed.add_field(name = "User ID:", value =message.author.id)
            sendembed = await chanl.send(embed=toxembed)
            banemoji = '<:BAN:835119271846871060>'
            await sendembed.add_reaction("✅")
            await sendembed.add_reaction("❌")
            await sendembed.add_reaction("🦵")
            await sendembed.add_reaction(banemoji) #this is a custom emoji, can be obtained here: https://bit.ly/3dQbi7g
    except:
        pass
async def get_tox():
    global typeattack
    if thrattack == attack:
        typeattack="Threat"
    elif toxattack == attack:
        typeattack="Severe Toxicity"
    else:
        typeattack="Identity Attack"
    return typeattack
@client.event
async def on_raw_reaction_add(payload): #analyzes reactions for the modqueue
    if payload.channel_id != 834778270968446976: #change channel id to match your modqueue channel id
        return 
    if payload.user_id == client.user.id: 
        return

    channel = client.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    guild=631730211880435752 #change guild id to match your modqueue guild id
    embed = msg.embeds[0]
    discorduser=await client.fetch_user(payload.user_id)

    if payload.emoji.name == '✅':
        embedcontents=embed.fields
        link=(embed.fields[1].value) 
        embed = discord.Embed(
			title=f"Approved by {discorduser}",
		    colour=discord.Color.green(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    elif payload.emoji.name == '❌':
        embedcontents=embed.fields
        link=(embed.fields[1].value) 
        linksplit=(embed.fields[1].value).split('/')
        orimsg_id = int(re.sub(r'[)]', '', linksplit[6])) #uses the stored embed link to get the message id and channel id of the message that was flagged
        orichannel= await client.fetch_channel(int(linksplit[5]))
        originalmessage = await orichannel.fetch_message(orimsg_id)
        await originalmessage.delete()
        embed = discord.Embed(
			title=f"Deleted by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    elif payload.emoji.name == '🦵':
        embedcontents=embed.fields
        link=(embed.fields[1].value)
        linksplit=(embed.fields[1].value).split('/')
        orimsg_id = int(re.sub(r'[)]', '', linksplit[6])) #uses the stored embed link to get the message id and channel id of the message that was flagged
        orichannel= await client.fetch_channel(int(linksplit[5]))
        originalmessage = await orichannel.fetch_message(orimsg_id)
        oriuser= await client.fetch_user(int(embed.fields[2].value)) #uses the stored embed user id to obtain the user id of the author of the flagged message
        await originalmessage.delete()
        kickguild = await client.fetch_guild(guild)
        await kickguild.kick(user=oriuser, reason=(embed.fields[0].value))
        embed = discord.Embed(
			title=f"Kicked by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    elif payload.emoji.name == 'BAN':
        embedcontents=embed.fields
        link=(embed.fields[1].value)
        linksplit=(embed.fields[1].value).split('/')
        orimsg_id = int(re.sub(r'[)]', '', linksplit[6])) #uses the stored embed link to get the message id and channel id of the message that was flagged
        orichannel= await client.fetch_channel(int(linksplit[5]))
        originalmessage = await orichannel.fetch_message(orimsg_id)
        oriuser= await client.fetch_user(int(embed.fields[2].value)) #uses the stored embed user id to obtain the user id of the author of the flagged message
        await originalmessage.delete()
        kickguild = await client.fetch_guild(guild)
        await kickguild.ban(user=oriuser, reason=(embed.fields[0].value))
        embed = discord.Embed(
			title=f"Banned by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await msg.edit(embed=embed)
        await msg.clear_reactions()
    else:
        pass

client.run(DISCORD_TOKEN)
