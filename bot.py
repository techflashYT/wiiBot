# This example requires the 'message_content' intent.

import discord
import subprocess
import cpuinfo
import neofetch

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

# Banned commands list
bannedCmds = [
    "xbps",
    "cat",
    "echo",
    "$(",
    "rm",
    "wget",
    "sh",
    "bash",
    "reboot",
    "power",
    "printf",
    "python",
    ">>",
    "<<",
    "||",
    "touch",
    "mk",
    "swapoff",
    "init",
    "write",
    "dd",
    "head"
]

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

            # Check if banned
            # for word in bannedCmds:
            #    if word in message.content:
            #        await message.channel.send("Command "+word+" is banned")
            #        return
            try:
                shRe = subprocess.run("su -c '"+shSc+"' discord", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                await message.channel.send("```\n"+shRe.stdout+"\n```\n")
            except Exception as e:
                await message.channel.send("```\n"+f"We fucked up: {e}"+"\n```")
# Get token
tok = ""
with open("token.txt", "r") as tf:
    tok = tf.read()
client.run(tok)
