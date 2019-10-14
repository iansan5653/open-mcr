"""String-related utilities."""


def trim_middle_to_len(string: str, length: int, start: int = 15):
    difference = len(string) - length
    if difference > 0:
        return string[:start] + " ... " + string[start + difference + 5:]
    return string
