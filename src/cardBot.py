# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import json
import os
import re

import discord
from discord import app_commands, embeds
from discord.ext import commands
from typing import Dict, Any

#from dotenv import load_dotenv, dotenv_values

PATTERN = r'\[\[([^\]]+)\]\]'


#project_folder = os.path.expanduser('~/')
#load_dotenv(os.path.join(project_folder, '.env'))

#print(project_folder)
#print(os.getenv("TOKEN"))


intents = discord.Intents.all()
# intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
cardFile = open("data/carddata.json", "r")
cardData = json.load(cardFile)
cards = cardData['cards']


@bot.event
async def on_ready():
  print('We have logged in as {0.user}'.format(bot))
"""
  try:
    #synced = await bot.tree.sync()
    bot.tree.copy_global_to(guild=discord.Object(id=os.environ['GUILD_ID']))
    synced = await bot.tree.sync(guild=None)
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)
"""


"""
# Normal Bot command for testing
@bot.command()
async def test(ctx):
  print('test')
"""

# create 25 entries for auto completion of card names based on the user input
async def cardNameEntries(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
  #cards = ['Card1', 'Card2', 'Card3', 'Card4']
  cardNameList = []
  #print(f'Cards: {len(cards)}')
  if current == '':  # nothing typed in by the user yet => return all cards, but only first 25 options
    for card in cards[:24]:
      cardNameList.append(
          app_commands.Choice(name=card["Name"] + ' (' + card["Set"] + ')', value=card["ImageFile"]))
  else:
    for card in cards:
      if current.lower() in card["Name"].lower():
        #print(f'Current: {current.lower()} - card name: {card["Name"].lower()}')
        cardNameList.append(
            app_commands.Choice(name=card["Name"] + ' (' + card["Set"] + ')', value=card["ImageFile"]))
  #print(f'Cards filtered: {len(cardList)}')
  #print(cardList[:24])
  return cardNameList[:24]  # only 25 options supported
"""
  return [app_commands.Choice(name=card['Name'] + ' (' + card["Set"] + ')', value=card['ImageFile']) for card in cards if current.lower() in card['Name'].lower()]
"""

# bot command for listing card names and resolve chosen card name into card-image-url
@bot.tree.command(name="card", description="Show a card")
@app_commands.describe(cards="Cards to choose from")
@app_commands.autocomplete(cards=cardNameEntries)
async def card(interaction: discord.Interaction, cards: str):
  #print(f'http://www.redemptionquick.com/lackey/sets/setimages/general/{cards}.jpg')
  await interaction.response.send_message(
      f'http://www.redemptionquick.com/lackey/sets/setimages/general/{cards}.jpg'
  )

# extract all cards from carddata.json which matches the given card name pattern
# only first card found per match will be taken
async def extractCards(cardNames: list[str]) -> list[Dict[str, Any]]:
  cardList = []
  for cardName in cardNames:
    for card in cards:
      if cardName.lower() in card["Name"].lower(): # first card found
        cardList.append(card)
        break # only select first card
  return cardList

async def createEmbeds(cardList: list[Dict[str, Any]]) -> list[discord.Embed]:
  embedList = []
  for card in cardList:
    cardImageURL = "http://www.redemptionquick.com/lackey/sets/setimages/general/" + \
                    card["ImageFile"] + ".jpg"
    embed=discord.Embed(title = card["Name"], url = cardImageURL, description = card["Type"])
    embed.set_thumbnail(url = card_image_url)
    embed.add_field(name = "card_set", value = card["Set"], inline=True)
    embed.add_field(name = "card_identifiers", value = card["Identifier"], inline=True)
    embed.add_field(name = "card_ability", value = card["SpecialAbility"], inline=True)
    embed.add_field(name = "card_stats", value = card["Strength"] + "/" + card["Toughness"],
                    inline=True)
    embed.add_field(name = "card_alignment", value = card["Alignment"], inline=True)
    embed.add_field(name = "card_brigades", value = card["Brigade"], inline=True)
    embed.add_field(name = "card_class", value = card["Class"], inline=True)
    embed.add_field(name = "card_reference", value = card["Reference"], inline=True)
    embed.add_field(name = "card_testament", value = card["Testament"], inline=True)
    embed.add_field(name = "card_legality", value = card["Legality"], inline=True)
    embed.add_field(name = "card_rarity", value = card["Rarity"], inline=True)
    embed.set_footer(text = card["Rarity"])
    embedList.append(embed)
    
  return embedList
    

@bot.event
# Normal Bot message handling for testing
async def on_message(message):
  if message.author == bot.user:
    return
    
  # find all entered card name patterns
  # and for each pattern extract the first matching card
  pattern_results = re.findall(PATTERN, message.content)
  if pattern_results:
    firstCardsFound = await extractCards(pattern_results)
    if firstCardsFound:
      await message.channel.send(embeds = createEmbeds(firstCardsFound))
  #for result in pattern_results:  
  #print(pattern_results)
  #print(message.content)
  #if pattern_results:
    #print(f'Message contains card pattern')


try:
  token = os.getenv("TOKEN") or ""
  if token == "":
    raise Exception("Please add your token to the Secrets pane.")
  bot.run(token)
except discord.HTTPException as e:
  if e.status == 429:
    print(
        "The Discord servers denied the connection for making too many requests"
    )
    print(
        "Get help from https://stackoverflow.com/questions/66724687/in-discord-py-how-to-solve-the-error-for-toomanyrequests"
    )
  else:
    raise e
