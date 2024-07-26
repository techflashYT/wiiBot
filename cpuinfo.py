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
