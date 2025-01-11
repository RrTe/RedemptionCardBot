# This code is based on the following example:
# https://discordpy.readthedocs.io/en/stable/quickstart.html#a-minimal-bot

import json
import os
import re
import discord
from keep_alive import keep_alive
from discord import app_commands, embeds
from discord.ext import commands
from typing import Dict, Any
#from dotenv import load_dotenv, dotenv_values

#*****************************************************************************************
# for daki.cc token needs to be provided within own config.py file and imported here with
# from config import TOKEN
#*****************************************************************************************

keep_alive()

PATTERN = r'\[\[([^\]]+)\]\]'
#text = "[[text1]] some other text [[text2]] more text [[text3]]"

#matches = re.findall(PATTERN, text)
#print(matches)

#project_folder = os.path.expanduser("~/")
#load_dotenv(os.path.join(project_folder, ".env"))

#print(project_folder)
#print(os.getenv("TOKEN"))


intents = discord.Intents.all()
# intents.message_content = True

bot = commands.Bot(command_prefix="/", intents=intents)
cardFile = open("data/carddata.json", "r")
cardData = json.load(cardFile)
cards = cardData["cards"]


@bot.event
async def on_ready():
  print("We have logged in as {0.user}".format(bot))
"""
  try:
    #synced = await bot.tree.sync()
    bot.tree.copy_global_to(guild=discord.Object(id=os.environ["GUILD_ID"]))
    synced = await bot.tree.sync(guild=None)
    print(f"Synced {len(synced)} command(s)")
  except Exception as e:
    print(e)
"""


"""
# Normal Bot command for testing
@bot.command()
async def test(ctx):
  print("test")
"""

# create 25 entries for auto completion of card names based on the user input
async def cardNameEntries(
    interaction: discord.Interaction,
    current: str,
) -> list[app_commands.Choice[str]]:
  #cards = ["Card1", "Card2", "Card3", "Card4"]
  cardNameList = []
  #print(f"Cards: {len(cards)}")
  if current == "":  # nothing typed in by the user yet => return all cards, but only first 25 options
    for card in cards[:24]:
      cardNameList.append(
          app_commands.Choice(name=card["Name"] + " (" + card["Set"] + ")", value=card["ImageFile"]))
  else:
    for card in cards:
      if current.lower() in card["Name"].lower():
        #print(f"Current: {current.lower()} - card name: {card["Name"].lower()}")
        cardNameList.append(
            app_commands.Choice(name=card["Name"] + " (" + card["Set"] + ")", value=card["ImageFile"]))
  #print(f"Cards filtered: {len(cardList)}")
  #print(cardList[:24])
  return cardNameList[:24]  # only 25 options supported
"""
  return [app_commands.Choice(name=card["Name"] + " (" + card["Set"] + ")", value=card["ImageFile"]) for card in cards if current.lower() in card["Name"].lower()]
"""

# bot command for listing card names and resolve chosen card name into card-image-url
@bot.tree.command(name="card", description="Show a card")
@app_commands.describe(cards="Cards to choose from")
@app_commands.autocomplete(cards=cardNameEntries)
async def card(interaction: discord.Interaction, cards: str):
  #print(f"http://www.redemptionquick.com/lackey/sets/setimages/general/{cards}.jpg")
  await interaction.response.send_message(
      #f"http://www.redemptionquick.com/lackey/sets/setimages/general/{cards}.jpg"
      f"https://raw.githubusercontent.com/jalstad/RedemptionLackeyCCG/refs/heads/master/RedemptionQuick/sets/setimages/general/{cards}.jpg"
  )

# bot command for listing card names and display the selected card name afterwards
@bot.tree.command(name="cardname", description="Show a card name")
@app_commands.describe(cards="Card names to choose from")
@app_commands.autocomplete(cards=cardNameEntries)
async def cardname(interaction: discord.Interaction, cards: str):
  await interaction.response.send_message(cards)
  
# extract all cards from carddata.json which matches the given card name pattern
# only first card found per match will be taken
async def extractCards(cardNames: list[str]) -> list[Dict[str, Any]]:
  cardList = []

  for cardName in cardNames:
    cardExactMatch = False
    firstCardFound = False
    cardFound = None
    for card in cards: # only max. one card per name must be added.
      if not cardExactMatch:
        if cardName.lower().strip() == card["Name"].lower().strip():
          cardFound = card
          cardExactMatch = True
          break # if there is a full match, then we're done
        if not firstCardFound and (cardName.lower() in card["Name"].lower()): # first card found
          cardFound = card
          firstCardFound = True
    cardList.append(cardFound) # only max. one card per name must be added.

  return cardList

async def createEmbeds(cardList: list[Dict[str, Any]]) -> list[discord.Embed]:
  embedList = []

  for card in cardList:
    #card_image_url = "http://www.redemptionquick.com/lackey/sets/setimages/general/" + \
    #                card["ImageFile"] + ".jpg"
    card_image_url = "https://raw.githubusercontent.com/jalstad/RedemptionLackeyCCG/refs/heads/master/RedemptionQuick/sets/setimages/general/" + \
                    card["ImageFile"] + ".jpg"

    embed=discord.Embed(colour = discord.Colour.dark_gold(), title = card["Name"],
                        url = card_image_url, description = card["Type"])
    embed.set_thumbnail(url = card_image_url)
    #embed.set_image(url = card_image_url)
    #embed.set_author(name = "author",
    #                 icon_url = "https://amiga.freecluster.eu/Redemption/RDE/assets/symbols/blue_small_compressed.png")
    embed.add_field(name = "Set", value = card["Set"], inline=True)
    
    card_identifier = card["Identifier"]
    if card_identifier:
      card_identifier = "*" + card_identifier + "*"
      embed.add_field(name = "Identifier", value = card_identifier, inline = False)

    card_ability = card["SpecialAbility"]
    if card_ability:
      embed.add_field(name = "Special Ability", value = card["SpecialAbility"], inline = False)

    if card["Strength"] or card["Toughness"]:
      embed.add_field(name = "Strength/Toughness", value = card["Strength"] + "/" + card["Toughness"],
                      inline=True)
      
    embed.add_field(name = "Alignment", value = card["Alignment"], inline = True)

    if card["Brigade"]:
      embed.add_field(name = "Brigades", value = card["Brigade"], inline = True)

    if card["Class"]:
      embed.add_field(name = "Class", value = card["Class"], inline = True)
 
    embed.add_field(name = "Reference", value = card["Reference"], inline = True)
    embed.add_field(name = "Testament", value = card["Testament"], inline = True)
    
    card_legality = card["Legality"]
    if not card_legality:
      card_legality = "Classic"
    embed.add_field(name = "Legality", value = card_legality, inline = True)
    
    embed.set_footer(text = card["Rarity"],
                     icon_url = "https://amiga.freecluster.eu/Redemption/RDE/assets/sets/0.png")
    # print(f"https://amiga.freecluster.eu/Redemption/RDE/assets/sets/" + card["Set"] + ".png")
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
  #print(pattern_results)
  #print(message.content)
  if pattern_results:
    firstCardsFound = await extractCards(pattern_results)
    if firstCardsFound:
      await message.channel.send(embeds = await createEmbeds(firstCardsFound))
    else:
      await message.channel.send(f"No card(s) found")


try:
  #*****************************************************************************************
  # for daki.cc token needs to assigned just by
  # token = TOKEN
  #*****************************************************************************************
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
