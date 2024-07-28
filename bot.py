import discord
import asyncio
import subprocess
import cpuinfo
import neofetch
import re

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

    if not message.content.startswith("$"):
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
        await handle_ps_command(message)

    elif message.content.startswith("$free"):
        await handle_free_command(message)

    elif message.content.startswith("$neofetch"):
        await handle_neofetch_command(message)

    else:
        await handle_custom_command(message)

async def handle_ps_command(message):
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, lambda: subprocess.run(["ps"], shell=True, capture_output=True, text=True))
    await message.reply("```ansi\n"+res.stdout+"\n```")

async def handle_free_command(message):
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, lambda: subprocess.run("free -h", shell=True, capture_output=True, text=True))
    await message.reply("```\n"+res.stdout+"\n```")

async def handle_neofetch_command(message):
    mymsg = await message.reply("Please wait, neofetch is running...")
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, neofetch.go)
    await mymsg.edit(content="```ansi\n"+res+"\n```")

async def handle_custom_command(message):
    shSc = ""
    shTo = 45
    if "<WIIBOTRUN>" in message.content:
        shSc = message.content.split("<WIIBOTRUN>")[1]
        shTo = re.sub(r'[^0-9]', '', message.content.split("<WIIBOTRUN>")[0])
        print(f"TO: {shTo}")
    else:
        shSc = message.content

    shSc = shSc[1:]
    try:
        myMsg = await message.reply("Please wait...")
        with open("/tmp/wiiBot_cmd", "w") as f:
            f.write(shSc)

        print(f"Running to: {shTo}")
        shCmd = f"su -c 'timeout {shTo} bash /tmp/wiiBot_cmd' discord"
        print(shCmd)

        loop = asyncio.get_event_loop()
        shRe = await loop.run_in_executor(None, lambda: subprocess.run(shCmd, shell=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.STDOUT))
        
        if len(shRe.stdout) > 3970:
            await myMsg.edit(content="**Warning**: Command output too much text, truncating\n```ansi\n"+shRe.stdout[0:1900]+"\n```\n")
            await myMsg.reply("```ansi\n"+shRe.stdout[1901:3800]+"\n```\n")
        elif len(shRe.stdout) > 1970:
            await myMsg.edit(content="```ansi\n"+shRe.stdout[0:1900]+"\n```\n")
            await myMsg.reply("```ansi\n"+shRe.stdout[1901:-1]+"\n```\n")
        elif len(shRe.stdout) == 0:
            await myMsg.edit(content="```ansi\n[command gave no output]\n```\n")
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
