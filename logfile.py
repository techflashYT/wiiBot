import re 

__dump = None


def getValue(search_term):
    return _getValue(__dump, search_term)


def getBlock(search_term):
    return _getBlock(__dump, search_term)


def _getValue(dump, search_term):
    """
    Extract the value from a line that starts with a specific string and has a colon.

    Args:
        search_term (str): The string to search for at the beginning of the line.

    Returns:
        str: The value after the colon, or None if the search term is not found.
    """
    lines = dump.splitlines()
    search_term_with_colon = search_term + ":"
    for line in lines:
        if line.startswith(search_term_with_colon):
            # Extract the value after the colon
            return line.split(":", 1)[1].strip()
    return None


def _getBlock(dump, search_term):
    """
    Extract a block of information from the dump based on a search term, handling nested sub-blocks.

    Args:
        dump (str): The crash dump text.
        search_term (str): The term indicating the block to extract.

    Returns:
        list: A list of tuples where each tuple contains the sub-block name and its content as a string.
    """
    start_marker_re = re.compile(rf"=+\s*{re.escape(search_term)}\s*start\s*=+")
    end_marker_re = re.compile(rf"=+\s*{re.escape(search_term)}\s*end\s*=+")
    
    lines = dump.splitlines()
    in_block = False
    block_content = []
    sub_blocks = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        if start_marker_re.search(line):
            in_block = True
            block_content = []
            i += 1
            continue
        elif end_marker_re.search(line) and in_block:
            sub_blocks.append((search_term, block_content))
            return sub_blocks
        elif in_block:
            sub_block_match = re.search(r"=+\s*(.+?)\s*start\s*=+", line)
            if sub_block_match:
                sub_block_name = sub_block_match.group(1).strip()
                sub_block_content = _getBlock("\n".join(lines[i:]), sub_block_name)
                sub_blocks.append((sub_block_name, sub_block_content))
                # Move index to after the sub-block
                while i < len(lines) and not re.search(rf"=+\s*{re.escape(sub_block_name)}\s*end\s*=+", lines[i]):
                    i += 1
                in_block = True
            else:
                block_content.append(line)
        i += 1

    return sub_blocks

async def analyzeLogFile(crashText):
    global __dump
    __dump = crashText
    warn = []
    out = ""

    exitCode = int(getValue("Installer Error Code"))

    out += "Date of crash: **" + getValue("Date according to Linux") + "**\n"

    # Line 1 of the output
    if int(re.sub(' +', ' ', getBlock("Memory Info")[0][1][1]).split(' ')[-1]) < 6144:
        # less than 6MB free, probably OOM'd
        warn.append("Less than 6MB of RAM free at time of crash")

    kernelLogs = getBlock("Kernel Log messages")[0][1]
    badIO = []
    for line in kernelLogs:
        if "invoked oom-killer:" in line:
            warn.append("System ran out of memory and killed process")
        if "I/O error" in line:
            nextWord = False
            for word in line.split(' '):
                if nextWord and (word not in badIO):
                    # `word` contains a comma already
                    warn.append(f"Got I/O errors on /dev/{word} this is usually a sign of disk failure.")
                    nextWord = False
                    break

                if word == "dev":
                    nextWord = True

    if exitCode == 127:
        warn.append("Exit code was \"command not found\", your installer folder was probably corrupted!")
        exitCode = "127 (command not found)"


    out += "Exit Code: **" + str(exitCode) + "**\n"
    ret = "# Known Problems:\n"
    if len(warn) == 0:
        ret += "- **None**\n"
    for w in warn:
        ret += "- **" + w + "**\n"

    ret += "\n\n# Info:\n" + out

    return ret
