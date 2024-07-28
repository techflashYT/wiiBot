import subprocess
import re

firstInfoLine = True
firstLogoLine = True

distro = "void"

def run_neofetch_logo():
    result = subprocess.run(['neofetch', '-L', "--ascii_distro", f"{distro}"], capture_output=True, text=True)
    return result.stdout


def run_neofetch_info():
    result = subprocess.run(['neofetch', '--backend', 'off', '--color_blocks', 'off'], capture_output=True, text=True)
    return result.stdout


def clean_logo_output(output):
    # Remove all non-color codes at the start and end
    output = re.sub(r'^\x1B\[\?\d+[hl]+', '', output)
    output = re.sub(r'\x1B\[19A\x1B\[9999999D.*$', '', output, flags=re.DOTALL)
    # Remove all non-color ANSI escape sequences except color codes
    output = re.sub(r'\x1B\[[0-9;]*[A-HJKST]', '', output)

    return output.rstrip()


def clean_info_output(output):
    # XXX: are we the first line, add 5 spaces
    global firstInfoLine
    if firstInfoLine:
        output = "     " + output
        firstInfoLine = False

    # Remove all non-color codes at the start
    output = re.sub(r'^\x1B\[\?\d+[hl]+', '', output)
    # Remove trailing non-color codes and blank lines
    output = re.sub(r'\x1B\[\?\d+[hl]+$', '', output, flags=re.DOTALL)
    output = output.rstrip()
    # Remove all non-color ANSI escape sequences except color codes
    output = re.sub(r'\x1B\[[0-9;]*[A-HJKST]', '', output)
    return output


def apply_last_color(line, last_color):
    # Check if the first non-whitespace character is an ANSI color code
    global firstLogoLine
    if re.match(r'^\s*\x1B\[[0-9;]*m', line):
        return line

    if firstLogoLine:
        firstLogoLine = False
        return line
    return last_color + line


def combine_logo_info(logo, info):
    logo_lines = logo.splitlines()
    info_lines = info.splitlines()

    # Determine the maximum width of the logo without ANSI codes
    max_logo_width = max(len(re.sub(r'\x1B\[[0-9;]*m', '', line)) for line in logo_lines)

    combined_lines = []
    last_color = ''
    ansi_color_re = re.compile(r'(\x1B\[[0-9;]*m)')

    for i in range(max(len(logo_lines), len(info_lines))):
        logo_part = logo_lines[i] if i < len(logo_lines) else ' ' * max_logo_width

        if logo_part.strip() == "":
            break
        # Extract the last color code in the line
        color_codes = ansi_color_re.findall(logo_part)
        if color_codes:
            # XXX: Don't apply if reset
            if color_codes[0] != "\x1b[0m" or len(color_codes) != 1:
                last_color = ''.join(color_codes)

        logo_part = apply_last_color(logo_part, last_color)

        info_part = info_lines[i] if i < len(info_lines) else ''
        # Ensure proper spacing between logo and system info
        combined_line = f"{logo_part}{' ' * (max_logo_width - len(re.sub(r'\x1B\[[0-9;]*m', '', logo_part)) + 4)}{info_part}"

        # XXX: last minute cleanup
        combined_line = combined_line.replace("\x1b[?25l", "")
        combined_line = combined_line.replace("\x1b[?25h", "")
        combined_line = combined_line.replace("\x1b[?7l", "")
        combined_line = combined_line.replace("\x1b[0m\x1b[0m", "\x1b[0m")

        # XXX: if we hit triple backticks we lose our codeblock
        combined_line = combined_line.replace("```", "``'")

        # XXX: combined_line.rstrip() doesn't work to remove whitespace :(
        while combined_line[-1] == ' ':
            combined_line = combined_line[:-1]

        if combined_line.endswith("\x1b[0m"):
            combined_line = combined_line[:-len("\x1b[0m")]

        combined_lines.append(combined_line)

    # Ensure the last line of the logo retains its color
    if combined_lines and last_color:
        combined_lines[-1] = apply_last_color(combined_lines[-1], last_color)

    combined_lines_str = '\n'.join(combined_lines)
    return combined_lines_str


def go():
    global firstInfoLine
    global firstLogoLine

    firstInfoLine = True
    firstLogoLine = True

    logo_output = run_neofetch_logo()
    info_output = run_neofetch_info()

    cleaned_logo = clean_logo_output(logo_output)
    cleaned_info = clean_info_output(info_output)

    return combine_logo_info(cleaned_logo, cleaned_info)
