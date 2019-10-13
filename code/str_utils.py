def shorten_by_cutting_middle(string: str, length: int, startpoint: int = 15):
    difference = len(string) - length
    if difference > 0:
        return string[:startpoint] + " ... " + string[startpoint + difference + 5:]