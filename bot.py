# This example requires the 'message_content' intent.

import discord
import subprocess

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Process a line of cpuinfo
def process_line(input_line):
    # Split the input line at the first colon
    parts = input_line.split(':', 1)

    # Get the part before the colon, removing tabs
    before_colon = parts[0].replace('\t', '')

    # Pad the string to 16 characters with spaces
    before_colon_padded = before_colon.ljust(16)

    # Get the remainder of the line (the colon and everything after it)
    remainder = parts[1] if len(parts) > 1 else ''

    # Combine the padded part and the remainder
    result = before_colon_padded + (':' + remainder if remainder else '')

    return result

@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')

@client.event
async def on_message(message):
    if message.author == client.user:
        return

    if message.content.startswith('$hello'):
        print("Ran Hello.")
        await message.channel.send('Hello!')
    if message.content.startswith("$specs"):
        finished = ""
        with open("cpuinfo", "r") as sp:
            for line in sp:
                finished += process_line(line)
        
        await message.channel.send("```\n"+finished+"\n```")
        
    if message.content.startswith("$neofetch"):
        res = subprocess.run(["neofetch"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        await message.channel.send("```ansi\n"+res+"\n```")

# Get token
tok = ""
with open("token.txt", "r") as tf:
    tok = tf.read()
client.run(tok)
