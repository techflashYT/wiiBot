# This example requires the 'message_content' intent.

import discord
import subprocess

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

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
        spec = ""
        with open("/proc/cpuinfo", "rb") as sp:
            spec = sp.read()
        await message.channel.send("```\n"+spec.decode()+"```")
    if message.content.startswith("$neofetch"):
        res = subprocess.run(["neofetch"], stdout=subprocess.PIPE).stdout.decode('utf-8')
        await message.channel.send("```ansi\n"+res+"\n```")

# Get token
tok = ""
with open("token.txt", "r") as tf:
    tok = tf.read()
client.run(tok)
