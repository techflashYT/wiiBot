import discord
import asyncio
import subprocess
import cpuinfo
import neofetch
import re
import string
import os
import io
import random
from time import time

intents = discord.Intents.default()
intents.message_content = True

client = discord.Client(intents=intents)

helpTxt = """# Wii Bot Help
This bot is ran off a real Nintendo Wii running void-linux.
To run a command, type '$' followed by the command.
If your app takes too long to execute, you can set a custom timeout by doing '$[t=30]<WIIBOTRUN>$' followed by the command and T is the timeout.

# DO NOT
 - Don't hammer the internet (i.e. transfer more than 1MB or so, the Wii's WiFi is incredibly poor)
 - Abuse the timeout.
 - Use too much disk space.
 - Do illegal things.
 - Exploit local servers.
 - Use a massive amount of CPU or RAM
"""

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

    elif message.content.startswith('$help'):
        await message.reply(helpTxt)

    elif message.content.startswith("$specs"):
        finished = ""
        with open("/proc/cpuinfo", "r") as sp:
            for line in sp:
                finished += cpuinfo.process_line(line)

        await message.reply("```\n"+finished+"\n```")

    elif message.content.startswith("$free"):
        await handle_free_command(message)

    elif message.content.startswith("$neofetch"):
        await handle_neofetch_command(message)

    else:
        await handle_custom_command(message)

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

    # warnings bitmask
    WARN_STILLRUNNING = 1
    WARN_TOOLONG = 2
    # WARN_SOMETHING = 4

    # warnings strings
    WARN_STR = [
        "Command is still running!  Reply to this message to provide input.",
        "Command output too much text, outputting to a file instead."
    ]

    warnings = 0
    warningsStr = ""

    def update_warnings(warning_bit, state):
        # update bitmask
        nonlocal warnings, warningsStr
        if state:
            warnings |= warning_bit
        else:
            warnings &= ~warning_bit

        warningsStr = ""
        # update warningsStr
        for i in range(2):
            if warnings & (1 << i):
                warningsStr += f"**Warning**: {WARN_STR[i]}\n"



    # Make random file name
    shFile = "/tmp/wiiBot_cmd_" + ''.join(random.choices(string.ascii_letters + string.digits, k=16))

    if "<WIIBOTRUN>" in message.content:
        shSc = message.content.split("<WIIBOTRUN>")[1]
        shTo = re.sub(r'[^0-9]', '', message.content.split("<WIIBOTRUN>")[0])
        print(f"TO: {shTo}")
    else:
        shSc = message.content

    shSc = shSc[1:]
    try:
        myMsg = await message.reply("Please wait...")
        with open(shFile, "w") as f:
            f.write(shSc)

        print(f"Running to: {shTo}")
        shCmd = f"su -c 'cd ~; timeout {shTo} bash {shFile}' discord"
        print(shCmd)
        update_warnings(WARN_STILLRUNNING, True)

        proc = await asyncio.create_subprocess_shell(
            shCmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.STDOUT,
            stdin=asyncio.subprocess.PIPE
        )

        output = []
        batch_lines = []
        last_send_time = time()
        no_file_yet = True

        async def update_message():
            nonlocal last_send_time, no_file_yet
            while proc.returncode is None:
                await asyncio.sleep(0.125)
                if batch_lines:
                    combined_output = "".join(output)
                    if len(combined_output) < 2000:
                        await myMsg.edit(content=warningsStr + "```ansi\n" + combined_output + "\n```")
                    elif no_file_yet or time() - last_send_time > 5:
                        file = discord.File(io.BytesIO(combined_output.encode()), filename="output.txt")

                        await myMsg.remove_attachments(myMsg.attachments)
                        await myMsg.add_files(file)

                        update_warnings(WARN_TOOLONG, True)
                        await myMsg.edit(content=warningsStr)
                        last_send_time = time()
                        no_file_yet = False
                    batch_lines.clear()

        asyncio.create_task(update_message())

        async for line in proc.stdout:
            line = line.decode()  # Decode bytes to string
            batch_lines.append(line)
            output.append(line)

        await proc.wait()
        update_warnings(WARN_STILLRUNNING, False)
        print("process finished")

        os.remove(shFile)

        # Finalize output and remove still running warning
        combined_output = "".join(output)
        if len(combined_output) + len(warningsStr) + len("```ansi\n\n```") < 2000:
            await myMsg.edit(content=warningsStr + "```ansi\n" + combined_output + "\n```")
        else:
            file = discord.File(io.BytesIO(combined_output.encode()), filename="output.txt")

            await myMsg.remove_attachments(myMsg.attachments)
            await myMsg.add_files(file)

            update_warnings(WARN_TOOLONG, True)
            await myMsg.edit(content=warningsStr)
            last_send_time = time()

    except Exception as e:
        content = "```\n" + f"We fucked up: {e}" + "\n```"
        if myMsg:
            await myMsg.edit(content=content)
        else:
            await message.channel.send(content)

# Get token
tok = ""
with open("token.txt", "r") as tf:
    tok = tf.read()

client.run(tok)
