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
        await message.reply('Hello!')

    elif message.content.startswith("$specs"):
        finished = ""
        with open("/proc/cpuinfo", "r") as sp:
            for line in sp:
                finished += cpuinfo.process_line(line)

        await message.reply("```\n"+finished+"\n```")

    elif message.content.startswith("$ps"):
        res = subprocess.run(["ps"], shell=True, capture_output=True, text=True)
        await message.reply("```ansi\n"+res.stdout+"\n```")
    elif message.content.startswith("$free"):
        res = subprocess.run("free -h", shell=True, capture_output=True, text=True)
        await message.reply("```\n"+res.stdout+"\n```")
    elif message.content.startswith("$neofetch"):
        mymsg = await message.reply("Please wait, neofetch is running...");
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
                myMsg = await message.reply("Please wait...")
                f = open("/tmp/wiiBot_cmd", "w")
                f.write(shSc)
                f.close()

                shRe = subprocess.run("su -c 'bash /tmp/wiiBot_cmd' discord", shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
                if len(shRe.stdout) > 3970:
                    await myMsg.edit(content="**Warning**: Command output too much text, truncating\n```ansi\n"+shRe.stdout[0:1900]+"\n```\n")
                    await myMsg.reply("```ansi\n"+shRe.stdout[1901:3800]+"\n```\n")
                elif len(shRe.stdout) > 1970:
                    await myMsg.edit(content="```ansi\n"+shRe.stdout[0:1900]+"\n```\n")
                    await myMsg.reply("```ansi\n"+shRe.stdout[1901:-1]+"\n```\n")
                else:
                    await myMsg.edit(content="```ansi\n"+shRe.stdout+"\n```\n")

            except Exception as e:
                content = "```\n"+f"We fucked up: {e}"+"\n```"
                if myMsg:
                    await myMsg.edit(content=content)
                else:
                    await message.channel.send(content)
# Get token
tok = ""
with open("token.txt", "r") as tf:
    tok = tf.read()
client.run(tok)
