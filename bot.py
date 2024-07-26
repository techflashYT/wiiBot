# This example requires the 'message_content' intent.

import discord
import subprocess
import cpuinfo
import neofetch

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

    elif message.content.startswith("$specs"):
        finished = ""
        with open("/proc/cpuinfo", "r") as sp:
            for line in sp:
                finished += cpuinfo.process_line(line)

        await message.channel.send("```\n"+finished+"\n```")

    elif message.content.startswith("$ps"):
        res = subprocess.run(["ps"], shell=True, capture_output=True, text=True)
        await message.channel.send("```ansi\n"+res.stdout+"\n```")
    elif message.content.startswith("$free"):
        res = subprocess.run("free -h", shell=True, capture_output=True, text=True)
        await message.channel.send("```\n"+res.stdout+"\n```")
    elif message.content.startswith("$neofetch"):
        mymsg = await message.channel.send("Please wait, neofetch is running...");
        res = neofetch.go()
        await mymsg.edit(content="```ansi\n"+res+"\n```")
    else:
        if message.content.startswith("$"):
            shSc = message.content
            shSc = shSc.replace("$", " ")
            shRe = subprocess.run(shSc, shell=True, capture_output=True, text=True)
            await message.channel.send("```\n"+shRe.stdout+"\n```")
# Get token
tok = ""
with open("token.txt", "r") as tf:
    tok = tf.read()
client.run(tok)
