import discord
import hashlib
import csv
import re
import threading
import logging
import time
import os
from dotenv import load_dotenv
load_dotenv()

# Configure Logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger()

global shimmer_address_pattern
global hashed_string
global compare_hash_result
global shimmer_receiver_address
shimmer_address_pattern = os.getenv("SHIMMER_ADDRESS_PATTERN")
keywords = os.getenv("ADDRESS_KEYWORD_TO_SEARCH")

class ReplyClient(discord.Client):
    
    
    # define sleep_switch to zero
    sleep_switch = 0
    # define input/commands to trigger bot
    


    # define sleep period, during this time the embed will not be posted to Discord
    def thread_sleep(self):
        # sleep for N seconds
        time.sleep(10)
        self.sleep_switch = 0
        
    # print to console that we logged in
    async def on_ready(self):
        print('Logged on as', self.user)

    # the discord function
    async def on_message(self, message):

        # Read hashed file and compares input
        def compareHash(hashed_address):
            with open('encoded.csv', mode ='r', encoding='UTF8') as file:
                for line in file.readlines():
                    if line.startswith(hashed_address):
                        compare_hash_result = "✅ Address found"
                        return compare_hash_result

        # Get's address and hashes it
        def hashInput(input_address):
            a_string = str(input_address)
            hashed_string = hashlib.sha256(a_string.encode('utf-8')).hexdigest()
            return hashed_string

        # don't respond to ourselves
        if message.author == self.user:
            return
                              
        # let's read the message
        if any(keyword in message.content.casefold() for keyword in keywords):
            compare_hash_result = "ℹ️ Please insert a Shimmer address"
            address_status = compare_hash_result
            shimmer_reply_address = re.findall(shimmer_address_pattern, message.content, flags=re.IGNORECASE)
            for shimmer_receiver_address in shimmer_reply_address:
                compareHash(hashInput(shimmer_receiver_address))
                address_status = compareHash(hashInput(shimmer_receiver_address))
                if address_status == None:
                    address_status = "❌ Address NOT found!"
            
            # as long as the sleep_switch is off
            if self.sleep_switch == 0:
            # Set the sleep_switch to 1 so that the bot only adds reactions instead of posting the embed
                self.sleep_switch = 1                
                
                # build the embed message
                embedVar=discord.Embed(title = "Shimmer OG NFT giveaway address check")
                embedVar.add_field(name="Address Status", value=address_status, inline=True)

                # reply to the input/command with the embed
                await message.channel.send(embed=embedVar)
                            
                # define a thread for sleeping
                sleep_thread = threading.Thread(target=self.thread_sleep)
                # after posting the embed message go to sleep
                sleep_thread.start()
                
            # since the sleep_switch is at 1, the bot will only add the reaction to a message and ignore further input/commands    
            else:
                # react to the message
                await message.add_reaction("😠")
        else:
            print("TEST")   

# load discord intents
intents = discord.Intents.default()
intents.messages = True
client = ReplyClient(intents=intents)
discord_bot_token = os.getenv('DISCORD_DEV_TOKEN')
client.run(discord_bot_token)
