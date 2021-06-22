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
import discord, json, requests, discord_components
from discord_components import interaction
from discord.ext.commands import Bot
from discord_components import DiscordComponents, Button, ButtonStyle, InteractionType, component
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
    global ideattack
    global attack 
    thrattack = response_dict["attributeScores"]["THREAT"]["summaryScore"]["value"]
    toxattack = response_dict["attributeScores"]["SEVERE_TOXICITY"]["summaryScore"]["value"]
    ideattack = response_dict["attributeScores"]["IDENTITY_ATTACK"]["summaryScore"]["value"]
    attack= max(thrattack,toxattack,ideattack)
    return attack

#sets the status of the of bot, in this case "Playing with AI"
@client.event
async def on_ready():
    DiscordComponents(client)
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
            await chanl.send(embed=toxembed)
            await chanl.send(
                "Please act based on whether any rules were broken",
                components=[[
                    Button(style=ButtonStyle.green, label = "Approve message"),
                    Button(style=ButtonStyle.red, label = "Delete message"),
                    Button(style=ButtonStyle.red, label = "Kick user"),
                    Button(style=ButtonStyle.red, label = "Ban user")
                ]]
                )        
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
async def on_button_click(interaction):
    if interaction.responded:
        return
    await interaction.respond(content = "Not Implemented")

@client.event
async def on_button_click(interaction): #analyzes reactions for the modqueue
    guild= await client.fetch_guild(631730211880435752) #change guild id to match your modqueue guild id
    label = interaction.component.label
    interactionChannel = client.get_channel(834778270968446976) 
    interactionUser = interaction.user.id

    interactionMessage = await interactionChannel.fetch_message(interaction.message.id)
    async for message in interactionChannel.history(limit=1, before=interaction.message):
        lastMessage= message
    embedMessage= lastMessage.embeds[0]
    #print(embedMessage) Debug printout
    discorduser=await client.fetch_user(interactionUser)
    if label.startswith("Approve message"):
        link=embedMessage.fields[1].value 
        embed = discord.Embed(
			title=f"Approved by {discorduser}",
		    colour=discord.Color.green(),
            description=link)
        await lastMessage.edit(embed=embed)
        await interactionMessage.delete(delay=None)
    elif label.startswith("Delete"):
        link=(embedMessage.fields[1].value) 
        linkSplit=(embedMessage.fields[1].value).split('/')
        originalEmbedID = int(re.sub(r'[)]', '', linkSplit[6])) #uses the stored embed link to get the message id and channel id of the message that was flagged
        originalchannel= await client.fetch_channel(int(linkSplit[5]))
        originalmessage = await originalchannel.fetch_message(originalEmbedID)
        await originalmessage.delete()
        embed = discord.Embed(
			title=f"Deleted by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await lastMessage.edit(embed=embed)
        await interactionMessage.delete(delay=None)
    elif label.startswith("Kick"):
        link=(embedMessage.fields[1].value)
        linkSplit=(embedMessage.fields[1].value).split('/')
        originalEmbedID = int(re.sub(r'[)]', '', linkSplit[6])) #uses the stored embed link to get the message id and channel id of the message that was flagged
        originalchannel= await client.fetch_channel(int(linkSplit[5]))
        originalmessage = await originalchannel.fetch_message(originalEmbedID)
        originalUser= await client.fetch_user(int(embedMessage.fields[2].value)) #uses the stored embed user id to obtain the user id of the author of the flagged message
        await originalmessage.delete()
        await guild.kick(user=originalUser, reason=(embedMessage.fields[0].value))
        embed = discord.Embed(
			title=f"Kicked by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await lastMessage.edit(embed=embed)
        await interactionMessage.delete(delay=None)
    elif label.startswith("Ban"):
        link=(embedMessage.fields[1].value)
        linksplit=(embedMessage.fields[1].value).split('/')
        originalEmbedID = int(re.sub(r'[)]', '', linksplit[6])) #uses the stored embed link to get the message id and channel id of the message that was flagged
        originalchannel= await client.fetch_channel(int(linksplit[5]))
        originalmessage = await originalchannel.fetch_message(originalEmbedID)
        originalUser= await client.fetch_user(int(embedMessage.fields[2].value)) #uses the stored embed user id to obtain the user id of the author of the flagged message
        kickguild = await client.fetch_guild(guild)
        await kickguild.ban(user=originalUser, reason=(embedMessage.fields[0].value))
        embed = discord.Embed(
			title=f"Banned by {discorduser}",
		    colour=discord.Color.red(),
            description=link)
        await lastMessage.edit(embed=embed)
        await interactionMessage.delete(delay=None)
    else:
        pass

client.run(DISCORD_TOKEN)
