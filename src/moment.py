# the order is important
token_map = {
    "%": "%%",
    "A": "%p",
    "ww": "%W",
    "dddd": "%A",
    "ddd": "%a",
    "d": "%w",
    "MMMM": "%B",
    "MMM": "%b",
    "MM": "%m",
    "YYYY": "%Y",
    "YY": "%y",
    "HH": "%H",
    "hh": "%I",
    "mm": "%M",
    "SSS": "%f",
    "ss": "%S",
    "ZZ": "%z",
    "z": "%Z",
    "DDDD": "%j",
    "DD": "%d",
}

def convert_moment_to_strptime_format(moment_date: str):
    """
    >>> convert_moment_to_strptime_format("YYYY-MM-DD")
    '%Y-%m-%d'
    """
    strptime_date = moment_date
    for [mt, st] in token_map.items():
        strptime_date = strptime_date.replace(mt, st)
    return strptime_date


if __name__ == "__main__":
    import doctest

    doctest.testmod()
