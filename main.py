import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import Button, View, Select

import re
import difflib
from io import StringIO
import json
import copy
from datetime import datetime, timedelta

import math
import random
import numpy as np
import asyncio

from collections import defaultdict
from collections import Counter

import os
from pathlib import Path

import xml.etree.ElementTree as ET

from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("DISCORD_TOKEN")

ENVIRONMENT = os.getenv("ENVIRONMENT", "development").lower()

if ENVIRONMENT == "development":
    # Set your preferences
    dropbox_base = Path.home() / "Dropbox" / "SLA_Discord_bot"
    print(f"Running in development environment, Dropbox base path: {dropbox_base}")
    mainFolder = dropbox_base
    listFolder = dropbox_base / "SavedVariables"
    CardDatabaseLocation = dropbox_base / "SLA.customcards.xml"
else:
    mainFolder = Path(os.getcwd())
    print(f"Running in production environment, root directory: {mainFolder}")
    listFolder = mainFolder / "SavedVariables"
    CardDatabaseLocation = mainFolder / "SLA.customcards.xml"




# Get the current date and time
startTime = datetime.now()

# Format it as a human-readable string
readable_time = startTime.strftime("%H:%M:%S")
readable_date = startTime.strftime("%m-%d")


MD = {
    '0': '<:0:1301741602179383397>',
    '1': '<:1:1301741603106455633>',
    '2': '<:2:1301741604217819237>',
    '3': '<:3:1301741605652267078>',
    '4': '<:4:1301741606617088030>',
    '5': '<:5:1301741607548227647>',
    '6': '<:6:1301741608383021096>',
    '7': '<:7:1301741609393721457>',
    '8': '<:8:1301741703169839175>',
    '9': '<:9:1301741613210669107>',
    '10': '<:10:1301741704352632945>',
    'W': '<:W:1301755863119302656>',
    'U': '<:U:1301755855167033356>',
    'B': '<:B:1301742003310170162>',
    'R': '<:R:1301755858748833804>',
    'G': '<:G:1301742008356044920>',
    'RW': '<:RW_:1301756036419555361>',
    'WB': '<:WB:1301756059471446056>',
    'BR': '<:BR:1301742005411516416>',
    'BG': '<:BG:1301742004501479555>',
    'GU': '<:GU:1301755959101886484>',
    'WU': '<:WU:1301756061367144550>',
    'UB': '<:UB:1301756051871371274>',
    'UR': '<:UR:1301756058494308443>',
    'RG': '<:RG:1301756035333230622>',
    'GW': '<:GW:1301755960271966250>',
    'WR': '<:RW_:1301756036419555361>',
    'BW': '<:WB:1301756059471446056>',
    'RB': '<:BR:1301742005411516416>',
    'GB': '<:BG:1301742004501479555>',
    'UG': '<:GU:1301755959101886484>',
    'UW': '<:WU:1301756061367144550>',
    'BU': '<:UB:1301756051871371274>',
    'RU': '<:UR:1301756058494308443>',
    'GR': '<:RG:1301756035333230622>',
    'WG': '<:GW:1301755960271966250>',
    '2W': '<:2W:1301741934280179743>',
    '2U': '<:2U:1301741933227540520>',
    '2B': '<:2B:1301741929884815360>',
    '2R': '<:2R:1301741932153671741>',
    '2G': '<:2G:1301741930719215626>',
    'PW': '<:PW:1301755997731291169>',
    'PU': '<:PU:1301755996854550639>',
    'PB': '<:PB:1301755993688117278>',
    'PR': '<:PR:1301755995764293653>',
    'PG': '<:PG:1301755994409406525>',
    'T': '<:T:1301756037271126047>',
    'E': '<:E:1301918988875464807>',
    'X': '<:X:1301756062998855680>',
    'O': '<:O:1301755981839077406>'
}

def AND(items):
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    if len(items) == 2:
        return f"{items[0]} and {items[1]}"
    return ", ".join(items[:-1]) + f", and {items[-1]}"

frontSideCards_List = []
backSideCards_List = []
lower_commonsFromSheet_List = []
lower_uncommonsFromSheet_List = []
lower_raresFromSheet_List = []
lower_mythicsFromSheet_List = []
backSideRef_Dict = {}

def getSavedCardLists():

    global frontSideCards_List
    global backSideCards_List
    global lower_commonsFromSheet_List
    global lower_uncommonsFromSheet_List
    global lower_raresFromSheet_List
    global lower_mythicsFromSheet_List
    global backSideRef_Dict

    # Read in needed card lists
    with open(listFolder / "frontSideCards_List.json", "r") as file:
        frontSideCards_List = json.load(file)
    with open(listFolder / "backSideCards_List.json", "r") as file:
        backSideCards_List = json.load(file)
    with open(listFolder / "lower_commonsFromSheet_List.json", "r") as file:
        lower_commonsFromSheet_List = json.load(file)
    with open(listFolder / "lower_uncommonsFromSheet_List.json", "r") as file:
        lower_uncommonsFromSheet_List = json.load(file)
    with open(listFolder / "lower_raresFromSheet_List.json", "r") as file:
        lower_raresFromSheet_List = json.load(file)
    with open(listFolder / "lower_mythicsFromSheet_List.json", "r") as file:
        lower_mythicsFromSheet_List = json.load(file)

    for i in range(len(frontSideCards_List)):
        backSideRef_Dict[frontSideCards_List[i]] = backSideCards_List[i]

    for main in lower_commonsFromSheet_List,lower_uncommonsFromSheet_List,lower_raresFromSheet_List,lower_mythicsFromSheet_List:
        for cardkey in backSideCards_List:
            try:
                main.remove(cardkey)
            except: pass

ColorDict = {
    'W': discord.Color.from_rgb(252, 254, 255),
    'U': discord.Color.from_rgb(0, 117, 190),
    'B': discord.Color.from_rgb(47, 39, 36),
    'R': discord.Color.from_rgb(114, 39, 27),
    'G': discord.Color.from_rgb(0, 123, 67),
    'M': discord.Color.from_rgb(149, 129, 76),
    'C': discord.Color.from_rgb(197, 203, 217)
}

def CD(colorString):
    if len(colorString) == 0:
        colorCode = ColorDict['C']
    elif len(colorString) > 1:
        colorCode = ColorDict['M']
    else:
        colorCode = ColorDict[colorString]
    return colorCode

def manaswap(text):
    for symbol in MD:
        text = text.replace('{' + symbol.lower() + '}',MD[symbol])
        text = text.replace('{' + symbol.upper() + '}',MD[symbol])
    return text

nonAlph = re.compile('[^a-zA-Z]')
refTitlesDict = {}
FullCardsDict = {}

async def update_cards():
    getSavedCardLists()

    tree = ET.parse(CardDatabaseLocation)
    root = tree.getroot()

    cards_element = root.find('cards')
    if cards_element is None:
        raise ValueError("No <cards> section found in XML.")

    for card in cards_element.findall('card'):
        name = card.findtext('name', default='')
        indexName = nonAlph.sub('', name).lower()

        # Basic fields
        text = card.findtext('text', default='').replace('~', name)

        # Nested <prop> fields
        prop = card.find('prop')
        manacost = prop.findtext('manacost', default='') if prop is not None else ''
        cardtype = prop.findtext('type', default='') if prop is not None else ''
        pt = prop.findtext('pt', default='') if prop is not None else ''
        loyalty = prop.findtext('loyalty', default='') if prop is not None else ''
        colors = prop.findtext('colors', default='') if prop is not None else ''

        # <set> tag with attributes
        set_tag = card.find('set')
        URL = set_tag.get('picurl') if set_tag is not None else ''
        rarity = set_tag.get('rarity') if set_tag is not None else ''

        # Look for transform-related info
        transform = None
        for related in card.findall('related'):
            if related.get('attach') == 'transform':
                transform = related.text
                break

        FullCardsDict[indexName] = {
            'name': name,
            'manacost': manaswap(manacost),
            'text': manaswap(text),
            'type': cardtype,
            'URL': URL,
            'rarity': rarity,
            'pt': pt if pt else None,
            'loyalty': loyalty if loyalty else None,
            'colors': colors,
        }

        if transform:
            FullCardsDict[indexName]['transform'] = transform

    # Populate reference titles
    for indexName, data in FullCardsDict.items():
        clean_name = re.sub(r'[^A-Za-z0-9]+', '', data['name']).lower()
        refTitlesDict[clean_name] = data['name']

async def card_updater_loop():
    while True:
        await update_cards()
        await asyncio.sleep(8 * 60 * 60)  # 8 hours

def SearchCard(cardtitle):
    cardIndex = re.sub(r'[^A-Za-z0-9]+', '', cardtitle).lower()
    print(cardIndex)
    try: cardIndex = difflib.get_close_matches(cardIndex, FullCardsDict, cutoff=0.8)[0]
    except:
        potentialHits = []
        for title in refTitlesDict:
            if title[:len(cardIndex)].lower() == cardIndex or title[len(cardIndex)+1:].lower() == cardIndex:
                potentialHits.append(refTitlesDict[title])
            elif cardIndex in title.lower():
                potentialHits.append(refTitlesDict[title])

        if len(potentialHits) == 0:
            print(f"{cardIndex}: Failed to find similar card")
            response = f'Couldn\'t find "{cardtitle}"'
            success, name, manacost, bodyText, URL, color = False, cardtitle, 0, response, 'blank', 'blank'
        elif len(potentialHits) == 1:
            cardIndex = re.sub(r'[^A-Za-z0-9]+', '', potentialHits[0]).lower()
            success = True
        else:
            #print(f"{cardIndex}: Found a few similar cards: {potentialHits}")
            response = 'Found more than one "' + cardtitle + '". Did you want...\n- ' + "\n- ".join(potentialHits)
            success, name, manacost, bodyText, URL, color = False, cardtitle, 0, response, 'blank', 'blank'

    if cardIndex in FullCardsDict:
        success = True

        name = FullCardsDict[cardIndex]['name']
        manacost = FullCardsDict[cardIndex]['manacost']
        URL = FullCardsDict[cardIndex]['URL']
        color = CD(FullCardsDict[cardIndex]['colors'])

        bodyText = FullCardsDict[cardIndex]['type'] + " •  [" + FullCardsDict[cardIndex]['rarity'] + "]"
        bodyText += '\n' + FullCardsDict[cardIndex]['text']

        PT = FullCardsDict[cardIndex].get('pt')
        if PT: bodyText += '\n' + PT

        loyalty = FullCardsDict[cardIndex].get('loyalty')
        if loyalty: bodyText += '\n' + loyalty

        if 'transform' in FullCardsDict[cardIndex]:
            transformTitle = FullCardsDict[cardIndex]['transform']
            transformIndex = nonAlph.sub('', transformTitle).lower()
            bodyText += '\n---------'
            bodyText += '\n' + FullCardsDict[transformIndex]['name']
            bodyText += '\n' + FullCardsDict[transformIndex]['type']
            bodyText += '\n' + FullCardsDict[transformIndex]['text']


            PT = FullCardsDict[transformIndex].get('pt')
            if PT: bodyText += '\n' + PT

            loyalty = FullCardsDict[transformIndex].get('loyalty')
            if loyalty: bodyText += '\n' + loyalty

    return success, name, manacost, bodyText, URL, color

def reverseSearch(text):
    cardMatches = []
    for item in FullCardsDict:
        textString = manaSymbols((FullCardsDict[item]['text'])).lower()
        costString = manaSymbols((FullCardsDict[item]['manacost'])).lower()
        print(text.lower())
        print(textString)
        if text.lower() in textString or text.lower() in costString or text.lower() in FullCardsDict[item]['type'].lower():
            cardName = FullCardsDict[item]['name']
            cardMatches.append(cardName)
        elif 'pt' in FullCardsDict[item] and text.lower() in FullCardsDict[item]['pt'].lower():
            cardName = FullCardsDict[item]['name']
            cardMatches.append(cardName)
    return cardMatches

class Client(commands.Bot):
    async def on_ready(self):
        global persistent_draft_view
        print(f'Logged on as {self.user}')

        try:
            guild = discord.Object(id=1262157159530237963)
            synced = await self.tree.sync(guild=guild)
            print(f'Synced {len(synced)} commands to guild {guild.id}')

        except Exception as e:
            print(f'Error syncing commands: {e}')


        print("updating cards")
        await update_cards()
        print("Updated cards")

        client.add_view(DeckOptionsView())
        if persistent_draft_view is None:
            persistent_draft_view = DraftSetupView()
            self.add_view(persistent_draft_view)

        if not hasattr(self, 'card_updater_started'):
            self.loop.create_task(card_updater_loop())
            self.card_updater_started = True


    async def on_message(self, message):
        if message.author == self.user: return
        else: messageString = message.content

        #if message.author.id == 268547439714238465 and len(messageString) == 0:
        #    await message.delete()

        if messageString == '!':
            await message.reply(f"I've been awake since {readable_time} (on {readable_date})")

        if messageString.startswith('!echo'):
            await message.reply(f'Hi, your message was {messageString}')
        if messageString.startswith('!testmana'):
            await message.channel.send(f"<@{message.author.id}>, here's some mana: {MD['W']}, {MD['PB']}, {MD['O']}, {MD['RG']}")
        if "{{" and "}}" in messageString:

            if '}}}' in messageString:
                messageString = messageString.replace('}}}','_}}')
                tempResult = re.findall(r"\{\{(.*?)\}\}", messageString)
                result = []
                for item in tempResult:
                    result.append(item.replace('_',"}"))
            else:
                result = re.findall(r"\{\{(.*?)\}\}", messageString)

            print(f"{message.author.display_name}> is looking for '{' and '.join(result)}'")

            for cardtitle in result:
                cardtitle = manaSymbols(cardtitle)
                print(cardtitle)
                if 'search:' in cardtitle.lower():
                    cardMatches = []
                    searchText = cardtitle.lower().replace('search:','').strip()
                    cardTitles = reverseSearch(searchText)
                    if len(cardTitles) == 0:
                        await message.reply(f"No search results for: {searchText}")
                    else:
                        responseText = f'{len(cardTitles)} results in Cost, Type, Rules, and P/T for: "' + searchText + '".\n- ' + "\n- ".join(cardTitles)
                        if len(cardTitles) <= 10:
                            await message.reply(responseText)
                        else:
                            f = discord.File(StringIO(responseText), filename=f"search_result_{message.author.display_name}.txt")
                            await message.reply(f'Found {len(cardTitles)} results for {searchText}! Here they are as a file to save space.', file=f)

                else:
                    success, name, manacost, bodyText, URL, color = SearchCard(cardtitle)

                    if success:
                        embed = discord.Embed(title=(f"{name}  {manacost}") , description = bodyText, url=URL, color=color)
                        embed.set_thumbnail(url=URL)
                        await message.reply(embed=embed)
                    else:
                        await message.reply(bodyText)



        if messageString.startswith('!draft'):
            await message.reply("""Looks like you're looking for into on the in-discord draft I can do!
- Type **\draft-lobby** to get the start menu!
- Buttons and drop-down menus can control everything from there.
- You can start the draft with CPUs to fill out 8 total players. They do are about colors & archetypes and try to build reasonable decks.
- The draft will end automatically after 10 minutes of inactivity, but your deck is saved whenever it ends.
- Text commands can perform all buttonable actions, if you prefer them. Type **/draft-commands** *(a slash, not ! )* if you want a list.""")

intents = discord.Intents.default()
intents.message_content = True
client = Client(command_prefix="!", intents=intents)

GUILD_ID = discord.Object(id=1262157159530237963)

@client.tree.command(name="update-cards", description="Manually update the card database.", guild = GUILD_ID)
async def update_cards_command(interaction: discord.Interaction):
    await update_cards()
    await interaction.followup.send("Card update complete.", ephemeral=True)


@client.tree.command(name="draft-commands",description='Get a list of all draft slash commands', guild = GUILD_ID)
async def draftCommands(interaction: discord.Interaction, confirm: str):
    await interaction.response.send_message(f"""Here's a list of all the draft text commands! You can also start typing **/draft-** to see them listed out.
- /draft-lobby : Create the lobby with join, leave, and start buttons
- /draft-join : Join yourself to the draft
- /draft-leave : Remove yourself from the draft
- /draft-start N : Start the draft, with N total drafters (N = real people + CPUs, 8 by default)
- /draft-end confirm : End the draft without a vote (don't abuse, or this will require mod priveleges!)
- /draft-pack : View your draft pack
- /draft-select N : Select the Nth card from your draft pack
- /draft-deck : View your draft deck, card names only
- /draft-deck-full : View your draft deck with full card details in a file
- /draft-deck-export : Export your draft deck as a cockatrice deck list
- /set-cards : Get the most updated cockatrice set file to import
- /secret-search : Functionality of {{cardname}}, but without the rest of the server seeing the search or the results.
- /mod-view-deck : Requires mod role. View a deck by inputting the user ID (int for people, string for CPUs)
- /mod-view-pack : Requires mod role. View a deck by index.""", ephemeral=True)




















DraftIdentitiesList = ['RW', 'WB', 'BR' , 'BG', 'GU' , 'WU' , 'UB' , 'UR' , 'RG' , 'GW', 'BRG', 'UBG', 'URG', 'WUG', 'WUR', 'WBR', 'WRG', 'WBG', 'WUB', 'UBR']
ColorSymbolsList = ['W', 'U', 'B', 'R', 'G', 'RW', 'WR', 'WB', 'BR' , 'BG', 'GU' , 'UG', 'WU' , 'UB' , 'UR' , 'RG' , 'GW', 'WG', '2W', '2U', '2B', '2R', '2G']
AllColorsList = ['W', 'U', 'B', 'R', 'G']
DraftIDsWeightDictBASE = {'RW': 0, 'WB': 0, 'BR': 0, 'BG': 0, 'GU': 0, 'WU': 0, 'UB': 0, 'UR': 0, 'RG': 0, 'GW': 0, 'BRG': 0, 'UBG': 0, 'URG': 0, 'WUG': 0, 'WUR': 0, 'WBR': 0, 'WRG': 0, 'WBG': 0, 'WUB': 0, 'UBR': 0}

def GetCMC(cost):

    costValue = 0

    if "{" in cost:
        cost = cost.replace("}{"," ").replace("{","").replace("}","")

    splitCost = cost.split(' ')
    for bit in splitCost:
        if bit == '':
            costValue += 0
        elif bit.replace('}','').isdigit():
            costValue += int(bit.replace('}',''))
        else:
            costValue += 1

    return costValue


def logEpsilonChooser():

    """  With the values: mean = -1.9, std_dev = .2
            ~2% basically perfect (ε ~ .003)
            ~10% extremely good (ε ~ .005)
            ~20% very good (ε ~ .007)
            ~35% good (ε ~ .01)
            ~25% decent(ε ~ .02)
            ~10% (ε ~ .03)
            ~1% bad (ε ~ .04)
    """
    mean = -1.8
    std_dev = .2
    size = 1
    gaussian_choice = np.random.normal(loc=mean, scale=std_dev)

    epsilon = 10**gaussian_choice

    return epsilon


def extract_symbols(text):
    return re.findall(r"\{(.*?)\}", manaSymbols(text))


def findIdentityWeights(cardKey):

    manaCost = FullCardsDict[cardKey].get('manacost', '')
    rulesText = FullCardsDict[cardKey].get('text', '')

    manaSymbolsCost = extract_symbols(manaCost)
    manaSymbolsText = extract_symbols(rulesText)

    # Base dictionary of scores per identity
    scores = defaultdict(float)

    # Step 1: Determi3ne colors required to cast the spell
    requiredColors = set()
    twobridColors = set()

    for symbol in manaSymbolsCost:
        colors = [c for c in symbol if c in AllColorsList]
        if "2" in symbol and len(colors) == 1:
            twobridColors.add(colors[0])
        elif colors:
            requiredColors.update(colors)

    for identity in DraftIdentitiesList:
        if all(c in identity for c in requiredColors):
            scores[identity] = 1.0

    # Step 2: Add bonuses for twobrid cards
    for twobridColor in twobridColors:
        for identity in DraftIdentitiesList:
            if scores[identity] > 0 and twobridColor in identity:
                scores[identity] += 1.0  # Equivalent to saying "cheaper in this color"

    # Step 3: Analyze mana in text for bonus value
    textColorHits = defaultdict(int)

    for symbol in manaSymbolsText:
        for c in AllColorsList:
            if c in symbol:
                textColorHits[c] += 1

    for identity in DraftIdentitiesList:
        if scores[identity] > 0:
            count = sum(1 for c in identity if textColorHits[c] > 0)
            scores[identity] += count  # +1 for each color used in text

    # Step 4: Normalize to max of 1
    maxScore = max(scores.values(), default=0)
    if maxScore > 0:
        for identity in scores:
            scores[identity] = scores[identity] / maxScore

    return dict(scores)

def compute_deck_curve_and_types(deckKeys):
    curve = {}  # {CMC bucket (1-6): count}
    types = {'creature': 0, 'noncreature': 0}

    for key in deckKeys:
        card = FullCardsDict[key]
        cmc = GetCMC(manaSymbols(card['manacost']))
        bucket = min(cmc, 6)
        curve[bucket] = curve.get(bucket, 0) + 1

        if 'creature' in card.get('type', '').lower():
            types['creature'] += 1
        else:
            types['noncreature'] += 1

    return dict(sorted(curve.items())), types


def adjustIDWeights(DraftIDsWeightDict_Temp, key, current_curve=None, current_type_counts=None):

    # Scale the importance of each factor in determining a card's weight
    # 1 = default, higher = more impact, lower = less impact
    # Impact is exponential: Care = 3  =>  result ^ 3
    rarity_Care = 1
    color_fit_Care = 4
    specialization_Care = .1
    ID_challenge_Care = .1
    curve_fit_Care = .1
    type_bias_Care = .1


    #print(key)
    identityScores = findIdentityWeights(key)

    rarityPowers = {'common': 1, 'uncommon': 2, 'rare': 4, 'mythic': 6}
    rarityPower = rarityPowers[FullCardsDict[key]['rarity'].lower()]

    #print(f"rarityPower: {rarityPower}")

    spreadScore = sum(identityScores.values())
    if spreadScore == 0:
        spreadScore = 1
    specialization = spreadScore ** (-.8)

    #print(f"specialization: {specialization}")

    # --- Extract card info ---
    CMC = GetCMC(manaSymbols(FullCardsDict[key]['manacost']))
    mv_bucket = min(CMC, 6)
    type_line = FullCardsDict[key].get('type', '').lower()
    is_creature = 'creature' in type_line

    # --- Mana Curve fitting: Set ideal targets ---
    ideal_curve = {0: 1, 1: 2, 2: 7, 3: 6, 4: 4, 5: 3, 6: 1}
    ideal_creature_ratio = 2.0  # You want 2x as many creatures as noncreatures

    if current_curve is None:
        current_curve = {}
    if current_type_counts is None:
        current_type_counts = {'creature': 0, 'noncreature': 0}

    # --- Curve fit: Find proportion of same-value cards (too many or two few?) ---
    ideal_total = sum(ideal_curve.values())
    total_cards_so_far = sum(current_curve.values()) + 1  # +1 to account for this candidate card

    ideal_proportion = ideal_curve.get(mv_bucket, 0) / ideal_total
    current_proportion = current_curve.get(mv_bucket, 0) / total_cards_so_far

    # Boost if underrepresented, scale down if overrepresented
    # Example: If ideal is 15% and current is 5%, multiplier ~3.0
    if ideal_proportion > 0:
        curve_fit = ideal_proportion / max(current_proportion, 0.001)  # avoid div by zero
    else:
        curve_fit = 1.0  # If the ideal has 0%, don’t penalize

    curve_fit = max(0.1, min(curve_fit, 10.0))

    #print(f"curve_fit: {curve_fit} - {ideal_proportion} / {max(current_proportion, 0.001)}")

    # --- Type bias dynamic multiplier ---
    creatures = current_type_counts.get('creature', 0)
    noncreatures = current_type_counts.get('noncreature', 0)
    if is_creature:
        ideal_ratio = ideal_creature_ratio
        current_ratio = (creatures + 1) / (noncreatures + 1)  # +1 to avoid div by zero
    else:
        ideal_ratio = 1 / ideal_creature_ratio
        current_ratio = (noncreatures + 1) / (creatures + 1)

    type_bias = ideal_ratio / current_ratio
    type_bias = max(0.1, min(type_bias, 10.0))

    #print(f"type_bias: {type_bias} - {ideal_ratio} / {current_ratio}")

    # --- Apply weight adjustment ---
    #print(identityScores)

    #print(CMC)

    baseAdjustment = (
    rarityPower**rarity_Care *
    specialization**specialization_Care *
    curve_fit**curve_fit_Care *
    type_bias**type_bias_Care *
    100)


    #print(f"{key}: {CMC} - {curve_fit} - {baseAdjustment}")


    for ID, score in identityScores.items():
        if score > 0:
            ID_challenge = len(ID) ** -1.5
            ID_adjustment = (baseAdjustment *
                score**color_fit_Care *
                ID_challenge**ID_challenge_Care)

            DraftIDsWeightDict_Temp[ID] += int(ID_adjustment)

    # --- Hybrid synergy bonus ---
    if len(identityScores) == 16:
        cardColors = FullCardsDict[key].get('colors', [])
        for ID in identityScores:
            if all(color in ID for color in cardColors):
                DraftIDsWeightDict_Temp[ID] += int(rarityPower * 10 * (len(ID) ** -2))

    return DraftIDsWeightDict_Temp


def get_deck_color_counts(deckCardKeys):
    """Counts how many cards in the deck contribute to each color."""
    colorCounts = Counter()

    for card in deckCardKeys:
        manaCost = FullCardsDict[card].get('manacost', '')
        text = FullCardsDict[card].get('text', '')
        symbols = extract_symbols(manaCost + text)

        for symbol in symbols:
            if len(symbol) == 2: Purity = 0.5 # Hybrid or Twobrid
            else: Purity = 1

            for color in AllColorsList:
                if color in symbol:
                    colorCounts[color] += Purity

    return colorCounts


def compute_color_balance(identity, colorCounts):
    """
    Returns a float from 0 to 1 measuring how evenly the deck supports the colors in `identity`.
    - 1 = perfectly balanced (equal counts)
    - 0 = totally unbalanced (any color missing)
    """
    colors = list(identity)
    counts = [colorCounts.get(c, 0) for c in colors]

    if any(c == 0 for c in counts):
        return 0.0  # One color totally unsupported

    mean = sum(counts) / len(counts)
    if mean == 0:
        return 0.0

    # Inverse of standard deviation normalized by mean
    variance = sum((c - mean) ** 2 for c in counts) / len(counts)
    std_dev = variance ** 0.5

    balance = max(0.0, 1 - (std_dev / mean))  # Normalize deviation
    return round(balance,1)


def ConsiderCardWeights(DraftIDsWeightDict_Temp, draftPackKeys, DeckKeys):
    #print(DraftIDsWeightDict_Temp)

    choiceWeightsDict = {}
    #print()
    deckPipsPrior = get_deck_color_counts(DeckKeys)
    #print()
    #print(f"Prior: {deckPipsPrior}")

    for key in draftPackKeys:
        CardPlayabilities = copy.deepcopy(DraftIDsWeightDictBASE)
        #print(f"{key} - {manaSymbols(FullCardsDict[key]['manacost'])}")
        curve, types = compute_deck_curve_and_types(DeckKeys)
        CardPlayabilities = adjustIDWeights(CardPlayabilities, key, curve, types)
        deckPips_IFADDED = deckPipsPrior + get_deck_color_counts([key])


        #print('---')
        #print(f"{key} - {manaSymbols(FullCardsDict[key]['manacost'])}")
        #print(f"Added: {deckPips_IFADDED}")

        colorFill = copy.deepcopy(DraftIDsWeightDictBASE)
        for ID in colorFill:
            colorFill[ID] = 1
            tempColorFill = {}
            for manaColor in ID:
                tempColorFill[manaColor] = deckPips_IFADDED[manaColor]

            try: normFactor = 1.0 / sum(tempColorFill.values())
            except: normFactor = 0
            normTempColorFill = {k: v*normFactor for k, v in tempColorFill.items()}

            colorFill[ID] = compute_color_balance(ID, normTempColorFill)

        #print(f"ColorFill: {brainPrint(colorFill)}")

        #print(f"-- playabilities, Weights, ColorFill -- {key}")
        #brainPrint(CardPlayabilities)
        #brainPrint(DraftIDsWeightDict_Temp)
        #brainPrint(colorFill)
        #print("------")

        cardWeight = sum(CardPlayabilities[ID]*DraftIDsWeightDict_Temp[ID]*colorFill[ID] for ID in CardPlayabilities.keys() & DraftIDsWeightDict_Temp.keys() & colorFill.keys())
        #print(f"{key}: {round(cardWeight)}")
        #brainPrint(CardPlayabilities)
        choiceWeightsDict[key] = cardWeight

    return choiceWeightsDict


def pick_card_weighted(scores: dict[str, float], epsilon: float) -> str:
    """
    Return a card name using a soft ε-greedy, score-differential-aware selection.

    Higher scores are favored, but lower scores can be picked occasionally depending on:
    - How close they are to the best score
    - The epsilon parameter (higher = more randomness)

    Epsilon values have approximately the following effect --
      ε = .001 -> Guaranteed to take the best card.
      ε = .005 -> Takes the best card ~99% of the time
       ε = .01 -> Always takes an extremely viable card. Usually takes the best (~80-90%)
       ε = .05 -> Takes a viable card ~50% of the time.
        ε = .1 -> Chance of a card's selection scales linearly with weight. More often makes bad choices.
        ε > .5 -> Nearly random selection. Only makes good choices by pure chance.

    Most CPUs should have ε between 0.005 (extremely wise) and 0.05 (rather unwise)
    """

    if epsilon == 0:
        epsilon = .0001

    if not scores:
        raise ValueError("Score dictionary must not be empty.")

    # Sort scores in descending order
    sorted_cards = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    best_score = sorted_cards[0][1]
    total_score = sum(s for _, s in sorted_cards)

    # Avoid divide-by-zero
    if total_score == 0:
        total_score = 1

    # Compute weights
    weights = []
    for _, score in sorted_cards:
        penalty = (best_score - score) / total_score
        weight = math.exp(-penalty / epsilon)
        weights.append(weight)

    # Normalize to probabilities
    weight_sum = sum(weights)
    probabilities = [w / weight_sum for w in weights]

    # Choose a card based on probabilities
    selected_card = random.choices(
        [name for name, _ in sorted_cards],
        weights=probabilities,
        k=1
    )[0]

    return selected_card


def filter_highest_rarity(draftPackKeys):
    # Group cards by rarity

    rarity_groups = {
        'Common': [],
        'Uncommon': [],
        'Rare': [],
        'Mythic': []
    }

    for key in draftPackKeys:
        rarity = FullCardsDict[key]['rarity']
        if rarity in rarity_groups:
            rarity_groups[rarity].append(key)

    # If any Mythics or Rares exist, return them together
    rare_and_mythics = rarity_groups['Rare'] + rarity_groups['Mythic']
    if rare_and_mythics:
        return rare_and_mythics

    RARITY_ORDER = ['Common', 'Uncommon', 'Rare', 'Mythic']

    # Otherwise return highest available rarity tier
    for rarity in reversed(RARITY_ORDER[:-2]):  # Skip Rare/Mythic
        if rarity_groups[rarity]:
            return rarity_groups[rarity]

    return []  # Should never happen unless pack is empty or malformed


def CPU_DraftPick(draftPackKeys, DraftIDsWeightDict_Temp, epsilon, deckKeys):
    # Step 1: Filter to only cards of the highest available rarity
    highestRarityCards = filter_highest_rarity(draftPackKeys)

    # Step 2: Score the filtered cards using ConsiderCardWeights
    choiceWeightsDict = ConsiderCardWeights(DraftIDsWeightDict_Temp, highestRarityCards, deckKeys)
    #print(choiceWeightsDict)
    # Step 3: Use soft ε-greedy selection to pick from scored cards
    chosenCardKey = max(choiceWeightsDict, key=choiceWeightsDict.get)
    #chosenCardKey = pick_card_weighted(choiceWeightsDict, epsilon)

    return chosenCardKey






def CreatePack():

    mythicChance = 1/7

    potCommons = copy.deepcopy(lower_commonsFromSheet_List)
    potUncommons = copy.deepcopy(lower_uncommonsFromSheet_List)
    potRares = copy.deepcopy(lower_raresFromSheet_List)
    potMythics = copy.deepcopy(lower_mythicsFromSheet_List)
    potAll = [potCommons,potUncommons,potRares,potMythics]

    if random.random() <= mythicChance: rareSlot = 3
    else: rareSlot = 2
    slotRarities = [0,0,0,0,0,0,0,0,0,0,1,1,1,rareSlot]

    rarityNames = ['Common', 'Uncommon', 'Rare', 'Mythic']

    draftPackKeys = []
    i = 1
    for rarityIndex in slotRarities:
        cardPool = potAll[rarityIndex]
        cardIndex = random.randint(0, len(cardPool)-1)

        cardKey = cardPool[cardIndex]
        draftPackKeys.append(cardKey)
        potAll[rarityIndex].remove(cardKey)

        del cardKey
        i += 1
    print(f"Pack generated: {', '.join(draftPackKeys)}")
    return draftPackKeys


def draftOutput(cardIndex, cardNumber):

    outputString = ''

    rulesLine = "  | "
    otherLine = "  - "

    name = FullCardsDict[cardIndex]['name']
    manacost = FullCardsDict[cardIndex]['manacost']
    URL = FullCardsDict[cardIndex]['URL']
    color = CD(FullCardsDict[cardIndex]['colors'])
    cardtype = FullCardsDict[cardIndex]['type']
    rarity = FullCardsDict[cardIndex]['rarity']
    rulesText = FullCardsDict[cardIndex]['text']

    outputString += '\n' + f"{cardNumber}: {rarity}"
    outputString += '\n' + f"{otherLine}{name}"
    outputString += '\n' + f"{otherLine}{manacost}"
    outputString += '\n' + otherLine + cardtype
    outputString += '\n' + rulesText

    if 'pt' in FullCardsDict[cardIndex]:
        outputString += '\n' + otherLine + FullCardsDict[cardIndex]['pt']
    if 'loyalty' in FullCardsDict[cardIndex]:
        outputString += '\n' + otherLine + 'Loyalty: ' + FullCardsDict[cardIndex]['loyalty']

    outputString += '\n' + otherLine + URL

    return outputString

def printCards(cardKeys, Player, OutputType):

    outputString = ''


    if str(OutputType).lower() == 'deck':
        PackNumber = OutputType

        outputString += f"Your deck"
        outputString += '\n'
        outputString += '\n' + f"({len(cardKeys)} cards)"
        outputString += '\n'
        outputString += '\n' + f"For {Player}"

    else:
        PackNumber = OutputType


        outputString += f"Pack #{PackNumber}"
        outputString += '\n'
        outputString += '\n' + f"Round #{15-len(cardKeys)}"
        outputString += '\n' + f"({len(cardKeys)} cards)"
        outputString += '\n' + f"For {Player}"

    cardIndex = 1

    for item in cardKeys:

        outputString += '\n' + ('--'*10)

        if item not in frontSideCards_List:
            outputString += draftOutput(item, cardIndex)
        else:
            outputString += '\n' + draftOutput(item, cardIndex)
            outputString += '\n' + '  !  Backside:'
            outputString += '\n' + draftOutput(backSideRef_Dict[item], cardIndex)

        cardIndex += 1

    return outputString

def manaSymbols(outputString):
    for symbol in MD:
        outputString = outputString.replace(MD[symbol], "{"+symbol+"}")
        outputString = outputString.replace(MD[symbol].lower(), "{"+symbol+"}")
    return outputString

















async def clean_up_draft():
    global DraftRunning
    global draftPackKeyList
    global DraftPlayerIDs
    global RoundNumber
    global DraftPlayerNames
    global DraftPlayerNumsDict
    global DraftPlayerDecksDict
    global ReadiedPlayersIDList
    global pinnedMessage
    global inactivity_task

    if inactivity_task:
        inactivity_task.cancel()
        try:
            await inactivity_task
        except asyncio.CancelledError:
            pass
        inactivity_task = None

    print("Clean up")
    await pinnedMessage.unpin()
    pinnedMessage = None

    guild = client.get_guild(1262157159530237963)
    role = guild.get_role(1375969105114431498)

    for playerID in DraftPlayerIDs:
        if type(playerID) == int:
            save_player_deck(playerID)
            member = guild.get_member(playerID)
            try:
                member = await guild.fetch_member(playerID)
            except discord.NotFound: return
            try:
                await member.remove_roles(role)
            except Exception as e:
                print(f"Failed to remove role from {member}: {e}")


    with open( mainFolder / "userList.json", 'w') as f: json.dump(DraftPlayerIDs, f)
    with open(mainFolder / "userNames.json", 'w') as f: json.dump(DraftPlayerNames, f)

    draftPackKeyList = []
    RoundNumber = 1
    DraftRunning = False
    DraftPlayerIDs = []
    DraftPlayerNames = []
    DraftPlayerNumsDict = {}
    DraftPlayerDecksDict = {}
    ReadiedPlayersIDList = []


def save_player_deck(user_id):
    deck_keys = DraftPlayerDecksDict.get(user_id, [])
    filepath = mainFolder / "savedDecks" / f"{user_id}.json"

    # Ensure the directory exists
    os.makedirs(os.path.dirname(filepath), exist_ok=True)

    with open(filepath, 'w') as f:
        json.dump(deck_keys, f, indent=2)

def load_player_deck(user_id):
    filepath = mainFolder / 'savedDecks' / f"{user_id}.json"

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"No saved deck for user {user_id}")
        return []

saved_decks_path = os.path.join(mainFolder, "savedDecks")
os.makedirs(saved_decks_path, exist_ok=True)

# Ensure files exist
if not os.path.isfile(mainFolder / "userList.json"):
    with open(mainFolder / "userList.json", 'w') as f:
        json.dump([], f)
if not os.path.isfile(mainFolder / "userNames.json"):
    with open(mainFolder / "userNames.json", 'w') as f:
        json.dump([], f)

##  Pull players from files in case bot was reset during draft lobby phase
with open(mainFolder / "userList.json", 'r') as f: DraftPlayerIDs = json.load(f)
with open(mainFolder / "userNames.json", 'r') as f: DraftPlayerNames = json.load(f)

##  Set default global variables
draftPackKeyList = []
RoundNumber = 1
DraftRunning = False
DraftPlayerNumsDict = {}
DraftPlayerDecksDict = {}
ReadiedPlayersIDList = []

NumOpenPacks = 1
PickNumber = 1
CPUsPickedYet = False
CPUPlayers = []
CPU_Epsilon_Assignments = {}
CPU_Weights_Dict = {}
realString = "real "

DraftPlayersListMessage = None

##  Silly list of possible CPU names (uses pronouns if only 1 CPU)
popular_mtg_characters = {"Jace": "his", "Chandra": "her", "Liliana": "her", "Gideon": "his", "Ajani": "his", "Bolas": "his", "Elspeth": "her", "Garruk": "his", "Nissa": "her", "Karn": "his", "Ugin": "his", "Tamiyo": "her", "Vraska": "her", "Ob Nixilis": "his", "Urza": "his", "Mishra": "his", "Sheoldred": "her", "Jin-Gitaxias": "his", "Elesh Norn": "her", "Tibalt": "his", "Oko": "his", "Tezzeret": "his", "Squee": "his", "Serra": "her", "Fblthp": "his", "Yawgmoth": "his"}


inactivity_task = None
last_interaction_time = datetime.now()


# === Check to end draft for inactivity ===
async def inactivity_monitor():
    global DraftRunning
    updateChannel = client.get_channel(1372451902461317172)
    while DraftRunning:
        await asyncio.sleep(15)  # Check every 15 seconds
        print("time check")
        if datetime.now() - last_interaction_time > timedelta(seconds=600):  # End draft if >10 passed since last interaction
            print(f"Ending draft for inactivity... Last interaction = {last_interaction_time}, Current = {datetime.now()}")
            endString = ""
            endString += "\n\n"
            print("Sending message")
            await updateChannel.send("<@&1375969105114431498>, The draft has been ended after 10 minutes of inactivity.\n\nYour decks has been saved, and can still be accessed with \"**/draft-deck**\" commands.\nYou can also recieve your deck as a DM, to save it for posterity.", view=DeckOptionsView(DmButton=True))
            await clean_up_draft()


# === Buttons in draft lobby ===

class DraftSetupView(discord.ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Join Draft", style=discord.ButtonStyle.success, custom_id="lobby_draft_join")
    async def join_draft(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"{interaction.user.display_name} joining via Button.")
        await handle_draft_join(interaction)

    @discord.ui.button(label="Leave Draft", style=discord.ButtonStyle.danger, custom_id="lobby_draft_leave")
    async def leave_draft(self, interaction: discord.Interaction, button: discord.ui.Button):
        print(f"{interaction.user.display_name} leaving via Button.")
        await handle_draft_leave(interaction)

    @discord.ui.button(label="Start Draft with CPUs", style=discord.ButtonStyle.primary, custom_id="lobby_draft_start_cpu")
    async def start_with_cpus(self, interaction: discord.Interaction, button: discord.ui.Button):
        desired_drafters = 8
        await handle_draft_start(interaction, desired_drafters, setupButtonView=self)

    @discord.ui.button(label="Start Draft (no CPUs)", style=discord.ButtonStyle.secondary, custom_id="lobby_draft_start_no_cpu")
    async def start_no_cpus(self, interaction: discord.Interaction, button: discord.ui.Button):
        desired_drafters = 0
        await handle_draft_start(interaction, desired_drafters, setupButtonView=self)

persistent_draft_view = None


@client.tree.command(name="draft-lobby", description="Create a message with join, leave, and start buttons.", guild = GUILD_ID)
async def draft_setup(interaction: discord.Interaction):
    await interaction.response.send_message("Welcome to the draft!", view=persistent_draft_view)


# === Function to start the draft (called by /draft-start and pressing lobby start button) ===
async def handle_draft_start(interaction, desiried_drafters, setupButtonView):
    global last_interaction_time
    last_interaction_time = datetime.now()
    global DraftRunning
    global draftPackKeyList
    global NumOpenPacks
    global CPUsPickedYet
    global PickNumber
    global CPUPlayers
    global CPU_Epsilon_Assignments
    global CPU_Weights_Dict
    global inactivity_task
    global realString
    global pinnedMessage

    await update_cards()

    ## Handle "CPU" and "No CPU" buttons differently
    if desiried_drafters == 0: drafters = len(DraftPlayerIDs)
    else: drafters = desiried_drafters

    CPUsPickedYet = False
    PickNumber = 1
    NumOpenPacks = 1
    CPU_Epsilon_Assignments = {}
    CPU_Weights_Dict = {}
    if DraftRunning: # Error if running
        await interaction.response.send_message(f"The draft is already running", ephemeral=True)
        print(f"{interaction.user.display_name}: draft-start (Fail: already running)")
    elif type(drafters) != int: # Error if /draft-start command has invalid input
        await interaction.response.send_message('Draft NOT started. \n- Make sure to include the number of drafters (real + desired CPUs)', ephemeral=True)
        print(f"{interaction.user.display_name}: draft-start (Fail: no Confirm)")
    elif drafters > 16: # Error if too many drafters given by /draft-start
        await interaction.response.send_message('Woah there, killer! That\'s too many drafters! Try starting it again, with a reasonable number? (I\'ll accept less than 17, though even that\'s not exactly *reasonable*...)', ephemeral=True)
    elif len(DraftPlayerIDs) == 0: # Error if no players
        if drafters > 0:
            await interaction.response.send_message("Hold up! There's no real people in the draft! As cool as my CPUs are, they can't draft on their own! Try joining first.", ephemeral=True)
        else:
            await interaction.response.send_message("Hang on just a second... There's no one in the draft! And you don't even want CPUs?... Let's wait for someone to join first, yeah?", ephemeral=True)
    else:  # Start the draft!
        for item in setupButtonView.children:
            if isinstance(item, discord.ui.Button):
                item.disabled = True

        await interaction.message.edit(content="The draft has started. Enjoy!", view=setupButtonView)

        DraftRunning = True
        print(f"{interaction.user.display_name}: draft-start")

        CPUPlayers = []

        # Fill ranks with CPUs
        while len(DraftPlayerIDs) < drafters:
            newName = random.choice([name for name in popular_mtg_characters if name not in DraftPlayerIDs])
            DraftPlayerIDs.append(newName)
            CPUPlayers.append(newName)
            CPU_Epsilon_Assignments[newName] = logEpsilonChooser()  # Determine CPU randomness
            CPU_Weights_Dict[newName] = copy.deepcopy(DraftIDsWeightDictBASE)  # Set blank deck preferences

        ##  Write blank to saved user lists - If bot resets during draft, do a full reset.
        with open(mainFolder / "userList.json", 'w') as f: json.dump([], f)
        with open(mainFolder / "userNames.json", 'w') as f: json.dump([], f)

        if len(CPUPlayers) > 1:
            await interaction.response.send_message(f":robot:  {len(CPUPlayers)} CPUs have joined the draft. Say hi to {AND(CPUPlayers)}!")
        elif len(CPUPlayers) == 1:
            await interaction.response.send_message(f":robot:  {len(CPUPlayers)} CPUs have joined the draft. Say hi to {AND(CPUPlayers)}!")
        elif len(CPUPlayers) == 0:
            realString = ""
            await interaction.response.send_message(f"No CPUs have joined the draft. Enjoy playing with real people!")


        playerNumber = 0
        for playerID in DraftPlayerIDs:
            DraftPlayerNumsDict[playerID] = playerNumber
            DraftPlayerDecksDict[playerID] = []
            draftPackKeyList.append(CreatePack())
            playerNumber += 1

        inactivity_task = asyncio.create_task(inactivity_monitor())
        pinnedMessage = await interaction.channel.send('<@&1375969105114431498>, The draft is now starting!\n- **Click the button**, or type "**/draft-pack**" to crack open your first pack!', view=DraftPackView(True))
        await pinnedMessage.pin()

pinnedMessage = None

@client.tree.command(name="draft-start",description='Start the draft, with N total drafters (N = real people + CPUs, reccomended 8)', guild = GUILD_ID)
async def startDraft(interaction: discord.Interaction, desiried_drafters: int):
    print("Draft starting via Command.")
    await handle_draft_start(interaction, desiried_drafters)


async def handle_draft_join(interaction):
    global last_interaction_time
    global DraftPlayersListMessage
    last_interaction_time = datetime.now()
    if interaction.user.id in DraftPlayerIDs:
        await interaction.response.send_message(f"You're already in the draft!", ephemeral=True)
        print(f"{interaction.user.display_name}: draft-join (Fail: already in draft)")
    elif DraftRunning:
        await interaction.response.send_message(f"Sorry, the draft is already started. You'll have to join the next one.", ephemeral=True)
        print(f"{interaction.user.display_name}: draft-join (Fail: started)")
    else:
        print(f"{interaction.user.display_name}: draft-join")
        DraftPlayerIDs.append(interaction.user.id)
        DraftPlayerNames.append(interaction.user.display_name)
        role = discord.utils.get(interaction.guild.roles, id=1375969105114431498)
        await interaction.user.add_roles(role)
        #await interaction.response.send_message(f"{interaction.user.display_name} has joined the draft!" + "\n" + f" Current drafters ({len(DraftPlayerNames)}):" + "\n- " + '\n- '.join(DraftPlayerNames) + "\n" + 'When everyone is here, someone can hit the start button in the pinned message!')
        display_name = interaction.user.display_name
        if display_name not in DraftPlayerNames:
            DraftPlayerNames.append(display_name)
        with open( mainFolder / "userList.json", 'w') as f: json.dump(DraftPlayerIDs, f)
        with open( mainFolder / "userNames.json", 'w') as f: json.dump(DraftPlayerNames, f)

        # 1. Respond to the user with the short confirmation
        await interaction.response.send_message(f"{display_name} has joined the draft!", ephemeral=False)

        # 2. Build the updated list string
        drafter_list_text = (
            f"**Current drafters ({len(DraftPlayerNames)}):**\n"
            + '\n'.join(f"- {name}" for name in DraftPlayerNames)
            + "\nWhen everyone is here, someone can hit the start button in the pinned message!"
        )

        # 3. Delete the old list message, if it exists
        if DraftPlayersListMessage:
            try:
                await DraftPlayersListMessage.delete()
            except discord.NotFound:
                pass  # Message already deleted
            except discord.Forbidden:
                pass  # Bot lacks permissions

        # 4. Send new message and save the reference
        DraftPlayersListMessage = await interaction.channel.send(drafter_list_text)

@client.tree.command(name="draft-join",description="Join the draft", guild = GUILD_ID)
async def joinDraft(interaction: discord.Interaction):
    print(f"{interaction.user.display_name} joining via Command.")
    await handle_draft_join(interaction)


async def handle_draft_leave(interaction):
    if DraftRunning:
        await interaction.response.send_message(f"Sorry, the draft is already started. You're trapped here now! (It will break if you leave, so you'll have to end it first)", ephemeral=True)
        print(f"{interaction.user.display_name}: draft-leave (Fail: started)")
    elif interaction.user.id not in DraftPlayerIDs:
        await interaction.response.send_message(f"Good news, you're already not in the draft!", ephemeral=True)
        print(f"{interaction.user.display_name}: draft-leave (Fail: not in draft)")
    else:
        print(f"{interaction.user.display_name}: draft-leave")
        DraftPlayerIDs.remove(interaction.user.id)
        DraftPlayerNames.remove(interaction.user.display_name)
        with open( mainFolder / "userList.json", 'w') as f: json.dump(DraftPlayerIDs, f)
        with open(mainFolder / "userNames.json", 'w') as f: json.dump(DraftPlayerNames, f)
        role = discord.utils.get(interaction.guild.roles, id=1375969105114431498)
        await interaction.user.remove_roles(role)
        await interaction.response.send_message(f"{interaction.user.display_name} just left the draft :(")


@client.tree.command(name="draft-leave",description="Leave the draft", guild = GUILD_ID)
async def leaveDraft(interaction: discord.Interaction):
    print(f"{interaction.user.display_name} leaving via Command.")
    await handle_draft_leave(interaction)


@client.tree.command(name="draft-end",description="End the draft without a vote (don't abuse, or this will require mod priveleges!)", guild = GUILD_ID)
async def endDraft(interaction: discord.Interaction, confirm: str):
    global DraftRunning
    global draftPackKeyList
    global DraftPlayerIDs
    global RoundNumber
    global DraftPlayerNames
    global DraftPlayerNumsDict
    global DraftPlayerDecksDict
    global ReadiedPlayersIDList
    global inactivity_task

    if DraftRunning == False:
        await interaction.response.send_message(f"The draft isn't running yet", ephemeral=True)
        print(f"{interaction.user.display_name}: draft-end (Fail: not running)")
    elif confirm != 'confirm':
        await interaction.response.send_message('Draft NOT stopped. \n- If you meant to end the draft, include "confirm" in the draft-start command.\n- If you didn\'t mean to end it, no worries!', ephemeral=True)
        print(f"{interaction.user.display_name}: draft-end (Fail: no Confirm)")
    else:
        print(f"{interaction.user.display_name}: draft-end")
        endString = f""
        await interaction.response.send_message("Stopping draft...")
        await interaction.channel.send(f"<@&1375969105114431498>, The draft has been ended by {interaction.user.display_name}." + "\n\nYour decks has been saved, and can still be accessed with \"**/draft-deck**\" commands.\nYou can also recieve your deck as a DM, to save it for posterity.", view=DeckOptionsView(DmButton=True))
        await clean_up_draft()





class CardPickSelect(discord.ui.Select):
    def __init__(self, user_id: int, draft_keys: list[int]):
        self.user_id = user_id
        self.draft_keys = draft_keys
        options = [
            discord.SelectOption(label=f"{i+1}. {FullCardsDict[card]['name']} - {manaSymbols(FullCardsDict[card]['manacost'])}".replace(' - {}','').replace('{',' ').replace('}',' '), value=str(i))
            for i, card in enumerate(draft_keys)
        ]
        super().__init__(placeholder="Select a card", min_values=1, max_values=1, options=options)


    async def callback(self, interaction: discord.Interaction):
        global last_interaction_time
        last_interaction_time = datetime.now()
        if DraftRunning:
            if interaction.user.id != self.user_id:
                await interaction.response.send_message("This isn't your pack.", ephemeral=True)
                return

            # Disable the select dropdown to prevent repeat selections
            await interaction.response.edit_message(content="Card picked!", view=None)

            # Continue with your selection handling
            await handle_draft_select(interaction, int(self.values[0])+1, interaction.user.id)
        else:
            await interaction.response.edit_message(content="Tricky tricky hobitses, trying to break my code. There's no draft running right now. But you could go start one!", view=None)

class CardPickView(View):
    def __init__(self, user_id: int, draft_keys: list[int]):
        super().__init__()
        self.add_item(CardPickSelect(user_id, draft_keys))

class DraftPackView(discord.ui.View):
    def __init__(self, displayEnd: bool = False):
        super().__init__(timeout=None)
        self.add_item(ViewPackButton())
        if displayEnd:
            self.add_item(ViewEndButton())


class VoteButtonsView(discord.ui.View):
    def __init__(self, message: discord.Message):
        super().__init__(timeout=60)  # Auto-disable after 60 seconds
        self.message = message
        self.voters = set()

        self.real_players = [pid for pid in DraftPlayerIDs if pid not in CPUPlayers]
        self.total_required = (len(self.real_players) + 1) // 2  # majority

    async def check_vote(self, interaction: discord.Interaction):
        user_id = interaction.user.id

        if user_id not in self.real_players:
            await interaction.response.send_message("Only players in the draft can vote.", ephemeral=True)
            return False

        if user_id in self.voters:
            await interaction.response.send_message("You've already voted.", ephemeral=True)
            return False

        self.voters.add(user_id)
        return True

    def get_vote_status_text(self):
        return f"🗳️ Vote to end the draft. ({len(self.voters)}/{self.total_required} votes required)"

    async def end_draft(self, interaction: discord.Interaction):
        for child in self.children:
            child.disabled = True
        await self.message.edit(content="🛑 The draft has ended by majority vote.", view=self)
        await self.message.channel.send(content="<@&1375969105114431498>, the draft has been ended by a vote! \n\nYour decks has been saved, and can still be accessed with \"**/draft-deck**\" commands.\nYou can also recieve your deck as a DM, to save it for posterity.", view=DeckOptionsView(DmButton=True))
        await clean_up_draft()

    async def update_vote_message(self):
        await self.message.edit(content=self.get_vote_status_text(), view=self)

    @discord.ui.button(label="Vote to End", style=discord.ButtonStyle.danger)
    async def vote_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if not await self.check_vote(interaction):
            return
        await interaction.response.send_message("You voted to end the draft.", ephemeral=True)

        if len(self.voters) >= self.total_required:
            await self.end_draft(interaction)
        else:
            await self.update_vote_message()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.secondary)
    async def cancel_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message("Vote canceled. Nothing happens.", ephemeral=True)

    async def on_timeout(self):
        if DraftRunning:
            for child in self.children:
                child.disabled = True
            await self.message.edit(content=self.get_vote_status_text() + " (⏳ Timed out after 60 seconds - We draft on!)", view=self)


class ViewEndButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="End Draft", style=discord.ButtonStyle.danger)

    async def callback(self, interaction: discord.Interaction):
        if not DraftRunning:
            await interaction.response.send_message("No draft is currently running.", ephemeral=True)
            return

        msg = await interaction.response.send_message(
            f"🗳️ Vote to end the draft. (0/{(len(DraftPlayerIDs) - len(CPUPlayers) + 1) // 2} votes required)",
            view=VoteButtonsView(message=None)
        )
        sent_msg = await interaction.original_response()
        sent_view = VoteButtonsView(message=sent_msg)
        await sent_msg.edit(view=sent_view)
        #await interaction.response.send_message(f"<@&1375969105114431498>, {interaction.user.display_name} wants to end the draft. Vote here to end! (Majority wins)", view=VoteButtonsView(message=interaction.message))


class ViewPackButton(discord.ui.Button):
    def __init__(self):
        super().__init__(label="View Pack", style=discord.ButtonStyle.success)

    async def callback(self, interaction: discord.Interaction):
        global last_interaction_time
        global CPUsPickedYet
        last_interaction_time = datetime.now()

        if not DraftRunning:
            await interaction.response.send_message("There isn't a draft currently running. Why not start one?", ephemeral=True)
            return

        if not CPUsPickedYet:
            CPUsPickedYet = True
            asyncio.create_task(run_cpu_picks(interaction.channel))

        user_id = interaction.user.id

        if user_id not in DraftPlayerNumsDict:
            await interaction.response.send_message("You aren't in the draft, sorry. You'll have to wait for this one to finish, then you can start a new one!", ephemeral=True)
            return

        PackNumber = DraftPlayerNumsDict[user_id]
        cardKeys = draftPackKeyList[PackNumber]
        outputString = printCards(cardKeys, interaction.user.display_name, PackNumber)
        outputString = manaSymbols(outputString)
        f = discord.File(StringIO(outputString), filename=f"draftPack{PackNumber}Round{RoundNumber}.txt")

        view = CardPickView(user_id, cardKeys)

        await interaction.response.send_message(
            'Here\'s your pack.\nTo put a card into your deck, select it from the drop down or type "**/draft-select [number]**".\n\n(Tip: Click on <:expand:1376368607252189274> to view the whole file, NOT "expand").',
            view=view,
            file=f,
            ephemeral=True
        )


@client.tree.command(name="draft-pack",description="Recieve your draft pack", guild = GUILD_ID)
async def draftPack(interaction: discord.Interaction):
    global last_interaction_time
    global CPUsPickedYet
    last_interaction_time = datetime.now()
    if DraftRunning:
        userID = interaction.user.id
        if not CPUsPickedYet:
            CPUsPickedYet = True
            asyncio.create_task(run_cpu_picks(interaction.channel))
        if interaction.user.id in DraftPlayerNumsDict:
            print(f"{interaction.user.display_name}: draft-pack")
            PackNumber = DraftPlayerNumsDict[interaction.user.id]
            cardKeys = draftPackKeyList[PackNumber]
            outputString = printCards(cardKeys, interaction.user.display_name, PackNumber)
            outputString = manaSymbols(outputString)
            f = discord.File(StringIO(outputString), filename=f"draftPack{PackNumber}Round{RoundNumber}.txt")
            #await interaction.response.send_message('Here\'s your a pack.\nTo put a card into your deck, type "**\draft-select [number]**", where [number] corresponds to the card you want.\nA warning: Your first pick is final, so be sure, and be careful!', file=f, ephemeral=True)

            view = CardPickView(userID, cardKeys)
            #await interaction.followup.send_message(view=view, ephemeral=True)
            await interaction.response.send_message('Here\'s your a pack.\nTo put a card into your deck, type "**\draft-select [number]**", where [number] corresponds to the card you want.\nA warning: Your first pick is final, so be sure, and be careful!', view=view, file=f, ephemeral=True)
        else:
            await interaction.response.send_message("You aren't in the draft, sorry. You'll have to wait for this one to finish, then you can start a new one!", file=f, ephemeral=True)
    else:
        print(f"draft-pack attempt, too late")
        await interaction.response.send_message(f"There isn't a draft currently running. Why not start one?", ephemeral=True)

async def run_cpu_picks(interaction_channel):
    print("CPUs are picking cards...")
    for CPUName in CPUPlayers:
        epsilon = CPU_Epsilon_Assignments[CPUName]
        CPU_PackNumber = DraftPlayerNumsDict[CPUName]
        CPU_draftPackKeys = draftPackKeyList[CPU_PackNumber]
        CPU_deckKeys = DraftPlayerDecksDict[CPUName]

        DraftIDsWeightDict_Temp = CPU_Weights_Dict[CPUName]

        CPU_ChosenCardIndex = CPU_DraftPick(CPU_draftPackKeys, DraftIDsWeightDict_Temp, epsilon, CPU_deckKeys)
        CPU_draftPackKeys.remove(CPU_ChosenCardIndex)
        CPU_deckKeys.append(CPU_ChosenCardIndex)
        print(f"...{CPUName} chose {CPU_ChosenCardIndex}")

        curve, types = compute_deck_curve_and_types(CPU_deckKeys)
        DraftIDsWeightDict_Temp = adjustIDWeights(DraftIDsWeightDict_Temp, CPU_ChosenCardIndex, curve, types)

        Dedication = 1 + (PickNumber**2) / (2250 + 100000*epsilon)
        DraftIDsWeightDict_Temp = {
            k: ((v ** Dedication) / (sum(x ** Dedication for x in DraftIDsWeightDict_Temp.values()) or 1)) * 100
            for k, v in DraftIDsWeightDict_Temp.items()}

    if len(CPUPlayers) == 1:
        await interaction_channel.send(f":robot:  {CPUPlayers[0]} has selected {popular_mtg_characters[CPUPlayers[0]]} card.")
    elif len(CPUPlayers) != 0:
        await interaction_channel.send(f":robot:  The {len(CPUPlayers)} CPUs have selected their cards.")



async def handle_draft_select(interaction: discord.Interaction, card_number: int, userID):
    global DraftPlayerNumsDict
    global ReadiedPlayersIDList
    global RoundNumber
    global NumOpenPacks
    global DraftRunning
    global CPUsPickedYet
    global PickNumber
    global draftPackKeyList

    PackNumber = DraftPlayerNumsDict[userID]
    draftPackKeys = draftPackKeyList[PackNumber]

    if userID in ReadiedPlayersIDList:
        print(f"{interaction.user.display_name}: draft-select (Fail: Already selected)")
        await interaction.followup.send(f"You've already added a card from this pack. Sit tight!" + "\n" + f"**{len(ReadiedPlayersIDList)} of {len(DraftPlayerIDs) - len(CPUPlayers)}** players are done selecting.", ephemeral=True)
    else:
        if card_number > len(draftPackKeys):
            print(f"{interaction.user.display_name}: draft-select (Fail: Value too high)")
            await interaction.followup.send(f"There's only {len(draftPackKeys)} cards in your pack, please pick again!", ephemeral=True)

        else: # Run the card selection process
            ChosenCardIndex = draftPackKeys[card_number-1]

            draftPackKeys.remove(ChosenCardIndex)
            DraftPlayerDecksDict[userID].append(ChosenCardIndex)

            ReadiedPlayersIDList.append(userID)

            await interaction.channel.send(f"{interaction.user.display_name} selected a card. ({len(ReadiedPlayersIDList)}/{len(DraftPlayerIDs) - len(CPUPlayers)} {realString}players have selected)")
            print(f"{interaction.user.display_name}: draft-select: {FullCardsDict[ChosenCardIndex]['name']}")

            await interaction.followup.send(
                f"You added {FullCardsDict[ChosenCardIndex]['name']} to your deck.\nYou can use these buttons to view your picks so far:",
                ephemeral=True,
                view=DeckOptionsView()
            )

    if len(ReadiedPlayersIDList) == (len(DraftPlayerIDs) - len(CPUPlayers)): # Start the next round
        CPUsPickedYet = False
        PickNumber += 1
        if RoundNumber == 15 and NumOpenPacks >= 3:
            DraftRunning = False

        ReadiedPlayersIDList = []
        RoundNumber += 1
        for playerID in DraftPlayerNumsDict:
            DraftPlayerNumsDict[playerID] += 1
            if DraftPlayerNumsDict[playerID] >= len(DraftPlayerNumsDict):
                DraftPlayerNumsDict[playerID] = 0
        await asyncio.sleep(1)
        if RoundNumber == 15:
            if NumOpenPacks < 3: # Reset packs to 'open new ones' in the next round
                RoundNumber = 1
                NumOpenPacks += 1
                playerNumber = 0
                draftPackKeyList = []
                for playerID in DraftPlayerIDs:
                    DraftPlayerNumsDict[playerID] = playerNumber
                    playerNumber += 1
                    draftPackKeyList.append(CreatePack())
                await interaction.channel.send(f"<@&1375969105114431498>, That's everyone! And **all packs are now empty**, so we're on to the next round." + "\n" + 'You\'ve been given a brand new pack. **Click the button**, or type "**/draft-pack**" to crack it open!', view=DraftPackView())
            else: # End the draft because out of cards
                print("Ending draft - 3rd pack empty")
                await clean_up_draft()
                await interaction.channel.send(f"<@&1375969105114431498>, That's everyone! All packs are empty, and **that was our third pack**, so the draft is **DONE!**" + "\n\nYour decks has been saved, and can still be accessed with the buttons below and \"**/draft-deck**\" commands.\n You can also have your deck list and info DM'ed to you, and download cockatrice data to play with them!", view=DeckOptionsView(DmButton=True))

        else:
            await interaction.channel.send(f"<@&1375969105114431498>, That's everyone! Round {RoundNumber} begins! All packs have been passed in a circle"  + "\n" + '**Click the button**, or type "**/draft-pack**" to see your new pack.', view=DraftPackView())




@client.tree.command(name="draft-select",description="Write in the number of the card you want", guild = GUILD_ID)
async def draftSelect(interaction: discord.Interaction, card_number: int):

    await interaction.response.defer(ephemeral=True)

    global last_interaction_time
    last_interaction_time = datetime.now()
    global DraftPlayerNumsDict
    global ReadiedPlayersIDList
    global RoundNumber
    global NumOpenPacks
    global DraftRunning
    global CPUsPickedYet
    global PickNumber

    if DraftRunning:
        userID = interaction.user.id
        if userID not in DraftPlayerNumsDict: await interaction.followup.send(f"You aren't in the draft, sorry. You'll have to wait for this one to finish, then you can start a new one!", ephemeral=True)
        else:
            if not CPUsPickedYet: # Handle CPU card selection
                CPUsPickedYet = True
                asyncio.create_task(run_cpu_picks(interaction.channel))

            await handle_draft_select(interaction, card_number, userID) # Handle current player's card selection
    else:
        await interaction.followup.send(f'There isn\'t a draft running currenty. Why not start a new one? Try **/draft-join** first.')


def get_user_id_by_pack(pack_number):
    global last_interaction_time
    last_interaction_time = datetime.now()
    for user_id, number in DraftPlayerNumsDict.items():
        if number == pack_number:
            return user_id
    return None  # if not found

@client.tree.command(name="mod-view-deck",description="View any deck", guild = GUILD_ID)
async def modviewdeck(interaction: discord.Interaction, deck_owner: str, level: int):
    global last_interaction_time
    last_interaction_time = datetime.now()
    deckList = DraftPlayerDecksDict[deck_owner]
    if deck_owner in DraftPlayerDecksDict:
        print(f"{interaction.user.display_name}: draft-deck: {', '.join(deckList)}")
        deckOutputString = f'The current deck ({len(deckList)} cards):'
        if level == 0:
            for cardIndex in deckList:
                deckOutputString += "\n- " + FullCardsDict[cardIndex]['name']
            await interaction.response.send_message(deckOutputString, ephemeral=True)
        elif level == 1:
            for cardIndex in deckList:
                deckOutputString += "\n- " + FullCardsDict[cardIndex]['name'] + "  -  " + FullCardsDict[cardIndex]['colors']
            await interaction.response.send_message(deckOutputString, ephemeral=True)
        elif level == 2:
            outputString = printCards(deckList, interaction.user.display_name, 'deck')
            outputString = manaSymbols(outputString)
            f = discord.File(StringIO(outputString), filename=f"draftDeck{interaction.user.display_name}.txt")


    else: await interaction.response.send_message("That player doesn't have a deck", ephemeral=True)

@client.tree.command(name="mod-view-pack",description="View any pack", guild = GUILD_ID)
async def modviewpack(interaction: discord.Interaction, packnumber: int):
    global last_interaction_time
    last_interaction_time = datetime.now()
    if packnumber > (len(draftPackKeyList)-1):
        await interaction.response.send_message('Value too large:', ephemeral=True)
    else:
        if DraftRunning:
            print(f"{interaction.user.display_name}: draft-pack")
            userID = get_user_id_by_pack(packnumber)
            cardKeys = draftPackKeyList[packnumber]
            outputString = printCards(cardKeys, userID, packnumber)
            outputString = manaSymbols(outputString)
            f = discord.File(StringIO(outputString), filename=f"draftPack{packnumber}Round{RoundNumber}.txt")
            await interaction.response.send_message('The pack:', file=f, ephemeral=True)
        else:
            print(f"admin-draft-pack attempt, too late")
            await interaction.response.send_message(f'The draft is already finished. Go check your deck with "**/draft-deck**" (names), "**/draft-deck-full**" (full text), or "**/draft-deck-export**" (Cockatrice deck file).')




class DeckOptionsView(View):
    def __init__(self, DmButton: bool = False):
        super().__init__(timeout=None)
        self.include_dm_button = DmButton
        if self.include_dm_button:
            self.add_item(self.DMButton())
            self.add_item(self.CockatriceButton())

    @discord.ui.button(label="Deck - Names only", style=discord.ButtonStyle.secondary, custom_id="deckList", row=0)
    async def decklist_button(self, interaction, button: Button):
        await handle_decklist(interaction)

    @discord.ui.button(label="Deck - Searchable Dropdown", style=discord.ButtonStyle.primary, row=0, custom_id="deckDropdown")
    async def dropdown_button(self, interaction: discord.Interaction, button: Button):
        player_id = interaction.user.id
        view = DeckDropdownView(player_id)
        await interaction.response.send_message(
            "Select a card to view its details (and the full pretty render!):",
            view=view,
            ephemeral=True
        )

    @discord.ui.button(label="Deck - Full card text", style=discord.ButtonStyle.secondary, custom_id="deckFull", row=0)
    async def deckfull_button(self, interaction, button: Button):
        await handle_deckfull(interaction)

    def DMButton(self):
        class DMDeckButton(discord.ui.Button):
            def __init__(self):
                super().__init__(
                    label="Deck - DM me everything",
                    style=discord.ButtonStyle.success,
                    row=1,
                    custom_id="deckDM"
                )

            async def callback(self, interaction: discord.Interaction):
                playerID = interaction.user.id
                username = interaction.user.display_name

                # Get deck
                if DraftRunning and playerID in DraftPlayerNumsDict:
                    deckList = DraftPlayerDecksDict[playerID]
                elif os.path.isfile(mainFolder / "savedDecks" / f"{playerID}.json"):
                    deckList = load_player_deck(playerID)
                else:
                    if DraftRunning:
                        await interaction.response.send_message("Sorry, you aren't in the draft and don't have a saved deck.", ephemeral=True)
                    else:
                        await interaction.response.send_message("There is no draft currently running.", ephemeral=True)
                    return

                # Name list string
                deckOutputString = f"Your decklist ({len(deckList)} cards):"
                for cardIndex in deckList:
                    deckOutputString += "\n- " + FullCardsDict[cardIndex]['name']
                deckOutputString += '\n\nUse {{cardname}} in the server to view cards.'

                # Full deck file
                outputString = printCards(deckList, username, 'deck')
                outputString = manaSymbols(outputString)
                f = discord.File(StringIO(outputString), filename=f"draftDeck_{username}_{datetime.now().strftime('%Y_%m_%d_%H:%M')}.txt")

                try:
                    await interaction.user.send(deckOutputString)
                    await interaction.user.send(file=f)
                    await interaction.response.send_message("✅ Check your DMs!", ephemeral=True)
                except discord.Forbidden:
                    await interaction.response.send_message("❌ Couldn't send you a DM. Please enable them and try again.", ephemeral=True)

        return DMDeckButton()

    def CockatriceButton(self):
        class CockatriceFileButton(discord.ui.Button):
            def __init__(self):
                super().__init__(
                    label="Updated cockatrice set (play with your cards!)",
                    style=discord.ButtonStyle.secondary,
                    emoji='📁',
                    row=1,
                    custom_id="deckCockatrice"
                    #url='https://drive.google.com/file/d/1EmfPWnFDjPV29U2INJ09tbGEQtwqCLII/view?usp=drive_link'
                )

            async def callback(self, interaction: discord.Interaction):
                if not os.path.exists(CardDatabaseLocation):
                    await interaction.response.send_message("❌ Couldn't find the Cockatrice file.", ephemeral=True)
                    return

                file = discord.File(CardDatabaseLocation, filename="SLA.customcards.xml")
                #await interaction.response.send_message("Here's the latest custom set file. You can upload it to cockatrice in your customsets folder", file=file, ephemeral=True)
                class CockatriceLinksView(discord.ui.View):
                    def __init__(self):
                        super().__init__()
                        self.add_item(discord.ui.Button(
                            label="Download Cockatrice",
                            url="https://cockatrice.github.io/",
                            style=discord.ButtonStyle.link
                        ))
                        self.add_item(discord.ui.Button(
                            label="How to upload a set file",
                            url="https://ponymtg.github.io/cockatrice3.html",
                            style=discord.ButtonStyle.link
                        ))

                await interaction.response.send_message(
                    content="Here's the latest custom set file. You can upload it to cockatrice in your customsets folder:",
                    file=file,
                    view=CockatriceLinksView(),
                    ephemeral=True
)

        return CockatriceFileButton()

async def handle_decklist(interaction):
    playerID = interaction.user.id

    def get_type_priority(type_line):
        type_order = [
            "Creature", "Vehicle", "Equipment", "Artifact", "Aura", "Enchantment",
            "Instant", "Sorcery", "Planeswalker", "Battle", "Land"
        ]
        for i, t in enumerate(type_order):
            if t in type_line:
                return i
        return len(type_order)  # Put unknowns at the end

    def format_deck(deckList):
        card_counts = Counter(deckList)
        card_entries = []

        for cardIndex, count in card_counts.items():
            name = FullCardsDict[cardIndex]['name']
            type_line = FullCardsDict[cardIndex]['type']
            qty_name = f"{count}x {name}" if count > 1 else name
            card_entries.append((get_type_priority(type_line), type_line, name.lower(), qty_name))

        # Sort by type priority, then alphabetically by name
        card_entries.sort()

        return '\n- ' + '\n- '.join(entry[-1] for entry in card_entries)

    if DraftRunning and playerID in DraftPlayerNumsDict:
        deckList = DraftPlayerDecksDict[playerID]
        print(f"{interaction.user.display_name}: draft-deck: {', '.join(deckList)}")
        deckOutputString = f'Your current deck ({len(deckList)} cards):'
        deckOutputString += format_deck(deckList)
        deckOutputString += '\n\nType "**\\secret-search [cardname]**" or use the Searchable Dropdown for details on a card (no one will see your request or the response)'
        await interaction.response.send_message(deckOutputString, ephemeral=True)

    elif os.path.isfile(mainFolder / "savedDecks" / f"{playerID}.json"):
        deckList = load_player_deck(playerID)
        print(f"{interaction.user.display_name}: draft-deck: {', '.join(deckList)}")
        deckOutputString = f"There's no draft right now, but here's the saved deck from your last draft ({len(deckList)} cards):"
        deckOutputString += format_deck(deckList)
        deckOutputString += '\n\nType "**\\secret-search [cardname]**" or use the Searchable Dropdown for details on a card (no one will see your request or the response)'
        await interaction.response.send_message(deckOutputString, ephemeral=True)

    elif DraftRunning:
        await interaction.response.send_message("Sorry, you aren't in the draft, and don't have a draft deck saved.", ephemeral=True)

    else:
        await interaction.response.send_message("There is no draft currently running.", ephemeral=True)


async def handle_deckfull(interaction):
    playerID = interaction.user.id
    if DraftRunning and playerID in DraftPlayerNumsDict:
        cardKeys = DraftPlayerDecksDict[playerID]
        outputString = printCards(cardKeys, interaction.user.display_name, 'deck')
        outputString = manaSymbols(outputString)
        f = discord.File(StringIO(outputString), filename=f"draftDeck{interaction.user.display_name}.txt")
        await interaction.response.send_message('Here\'s your current deck!', file=f, ephemeral=True)
    elif os.path.isfile(mainFolder / "savedDecks" / f"{playerID}.json"):
        cardKeys = load_player_deck(playerID)
        outputString = printCards(cardKeys, interaction.user.display_name, 'deck')
        outputString = manaSymbols(outputString)
        f = discord.File(StringIO(outputString), filename=f"draftDeck{interaction.user.display_name}.txt")
        await interaction.response.send_message("Here's the saved deck from your last draft:", file=f, ephemeral=True)
    elif DraftRunning:
        await interaction.response.send_message("Sorry, you aren't in the draft, and don't have a saved deck.", ephemeral=True)
    else:
        await interaction.response.send_message("There is no draft currently running.", ephemeral=True)


@client.tree.command(name="set-cards", description="Play with the cards! Get the latest custom Cockatrice set file with helpful links.", guild = GUILD_ID)
async def setCards(interaction: discord.Interaction):
    if not os.path.exists(CardDatabaseLocation):
        await interaction.response.send_message("❌ Couldn't find the Cockatrice file. I'll let the boss know.", ephemeral=True)
        #await asyncio.sleep(1)
        await interaction.channel.send(f"<@409518287450406912>! Help! I couldn't find the Cockatrice file for {interaction.user.display_name}!")
        return

    file = discord.File(CardDatabaseLocation, filename="SLA.customcards.xml")

    class CockatriceLinksView(discord.ui.View):
        def __init__(self):
            super().__init__()
            self.add_item(discord.ui.Button(
                label="Download Cockatrice",
                url="https://cockatrice.github.io/",
                style=discord.ButtonStyle.link
            ))
            self.add_item(discord.ui.Button(
                label="Upload a Set File",
                url="https://ponymtg.github.io/cockatrice3.html",
                style=discord.ButtonStyle.link
            ))

    await interaction.response.send_message(
        content="Here's the latest custom set file. You can upload it to Cockatrice in your `customsets` folder:",
        file=file,
        view=CockatriceLinksView(),
        ephemeral=True
    )



@client.tree.command(name="draft-deck",description="Recieve a list of of your drafted cards", guild = GUILD_ID)
async def draftDeck(interaction: discord.Interaction):
    await handle_decklist(interaction)


@client.tree.command(name="draft-deck-full",description="Recieve the full text of all your drafted cards", guild = GUILD_ID)
async def draftDeckFull(interaction: discord.Interaction):
    await handle_deckfull(interaction)

@client.tree.command(name="draft-deck-export",description="Recieve a cockatrice deckfule for all your drafted cards", guild = GUILD_ID)
async def draftDeckExport(interaction: discord.Interaction):
    global last_interaction_time
    last_interaction_time = datetime.now()
    print(f"{interaction.user.display_name}: draft-deck-export")
    playerID = interaction.user.id
    if DraftRunning and playerID in DraftPlayerNumsDict:
        cardKeys = DraftPlayerDecksDict[playerID]
        outputString = """<?xml version="1.0" encoding="UTF-8"?>
<cockatrice_deck version="1">
    <deckname></deckname>
    <comments></comments>
    <zone name="main">"""
        for cardKey in cardKeys:
            outputString += "\n        " + f'<card number="1" name="{FullCardsDict[cardKey]["name"]}"/>'
        outputString += "\n" + """    </zone>
</cockatrice_deck>
"""
        f = discord.File(StringIO(outputString), filename=f"draftDeck_{interaction.user.display_name}.cod")
        await interaction.response.send_message('Here\'s your current deck.\nUpload it to your cockatrice deck folder to edit it and play!', file=f, ephemeral=True)

    elif os.path.isfile(mainFolder / "savedDecks" / f"{playerID}.json"):
        cardKeys = load_player_deck(playerID)
        outputString = """<?xml version="1.0" encoding="UTF-8"?>
<cockatrice_deck version="1">
    <deckname></deckname>
    <comments></comments>
    <zone name="main">"""
        for cardKey in cardKeys:
            outputString += "\n        " + f'<card number="1" name="{FullCardsDict[cardKey]["name"]}"/>'
        outputString += "\n" + """    </zone>
</cockatrice_deck>
"""
        f = discord.File(StringIO(outputString), filename=f"draftDeck_{interaction.user.display_name}.cod")
        await interaction.response.send_message('There\'s no draft right now, but here\'s the saved deck from your last draft.\nUpload it to your cockatrice deck folder to edit it and play!', file=f, ephemeral=True)

    elif DraftRunning:
        await interaction.response.send_message("Sorry, you aren't in the draft, and don't have a draft deck saved. \nIf you wait for this draft to finish, then you can start a new one and make a deck!", ephemeral=True)
    else:
        await interaction.response.send_message("There is no draft currently running. Try starting a new one!", ephemeral=True)

async def perform_secret_search(interaction: discord.Interaction, card_name: str):
    success, name, manacost, bodyText, URL, color = SearchCard(card_name)
    if success:
        print(f"{interaction.user.display_name}: secret-search for {name}")
        embed = discord.Embed(title=(f"{name}  {manacost}"), description=bodyText, url=URL, color=color)
        embed.set_thumbnail(url=URL)
        await interaction.response.send_message(embed=embed, ephemeral=True)
    else:
        print(f"{interaction.user.display_name}: secret-search FAILED for {card_name}")
        await interaction.response.send_message(bodyText, ephemeral=True)

@client.tree.command(name="secret-search", description="Input a card name, and its details are whispered to you (no one else will know what you searched)", guild=GUILD_ID)
async def secretSearch(interaction: discord.Interaction, card_name: str):
    await perform_secret_search(interaction, card_name)

class DeckDropdownView(View):
    def __init__(self, player_id: int, page: int = 0):
        super().__init__(timeout=None)
        self.player_id = player_id
        self.page = page  # 0-indexed: 0, 1, 2
        self.per_page = 14

        self.deck = self.get_deck()
        self.max_page = (len(self.deck) - 1) // self.per_page

        self.dropdown = DeckCardDropdown(self.deck, self.page, self.per_page)
        self.add_item(self.dropdown)

        if self.max_page > 0:
            self.add_item(PreviousPageButton())
            self.add_item(NextPageButton())

    def get_deck(self):
        if DraftRunning and self.player_id in DraftPlayerNumsDict:
            return DraftPlayerDecksDict[self.player_id]
        elif os.path.isfile( mainFolder / "savedDecks" / f"{self.player_id}.json"):
            return load_player_deck(self.player_id)
        else:
            return []

    async def flip_page(self, interaction: discord.Interaction, direction: int):
        new_page = self.page + direction
        if 0 <= new_page <= self.max_page:
            new_view = DeckDropdownView(self.player_id, page=new_page)
            await interaction.response.edit_message(view=new_view)
        else:
            await interaction.response.defer()

class DeckCardDropdown(Select):
    def __init__(self, deck_keys, page, per_page):
        start = page * per_page
        end = start + per_page
        self.options_data = deck_keys[start:end]

        options = [
            discord.SelectOption(
                label=f"{idx+1}: {FullCardsDict[card]['name']} - {manaSymbols(FullCardsDict[card]['manacost'])}".replace(" - {}","").replace('}',' ').replace('{',' '),
                value=f"{start + idx}:{FullCardsDict[card]['name']}"[:100]  # ensure uniqueness
            )
            for idx, card in enumerate(self.options_data)
        ]

        super().__init__(
            placeholder=f"Pick a card (Page {page + 1})...",
            min_values=1,
            max_values=1,
            options=options
        )

    async def callback(self, interaction: discord.Interaction):
        card_name = self.values[0].split(":", 1)[1]  # strip index prefix
        await perform_secret_search(interaction, card_name)


class PreviousPageButton(Button):
    def __init__(self):
        super().__init__(label="⬅️ Previous", style=discord.ButtonStyle.secondary, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: DeckDropdownView = self.view
        await view.flip_page(interaction, -1)


class NextPageButton(Button):
    def __init__(self):
        super().__init__(label="Next ➡️", style=discord.ButtonStyle.secondary, row=1)

    async def callback(self, interaction: discord.Interaction):
        view: DeckDropdownView = self.view
        await view.flip_page(interaction, 1)


client.run(TOKEN)