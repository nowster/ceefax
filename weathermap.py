import ttxcolour
import ttxutils

_region_boundaries = {
    "highlands": [
        (2, 13),
        (3, 13),
        (3, 20),
        (4, 12),
        (5, 12),
        (6, 13),
        (7, 14),
        (8, 14),
    ],
    "grampian": [(4, 19), (5, 19), (6, 20)],
    "tayside": [(7, 18), (8, 17)],
    "central": [(9, 13), (10, 15), (11, 15)],
    "nireland": [(10, 9), (11, 8), (11, 13), (12, 8), (13, 9)],
    "northeast": [(9, 21), (10, 21), (11, 23)],
    "northwest": [(11, 18), (12, 15), (13, 19), (14, 19)],
    "yorks": [(12, 23), (13, 23), (14, 24)],
    "wales": [(14, 15), (15, 15), (16, 15), (17, 16), (18, 13), (19, 15)],
    "midlands": [(15, 20), (16, 23), (17, 20), (18, 23)],
    "west": [(18, 20), (19, 19), (20, 21)],
    "east": [(16, 26), (17, 29), (18, 27)],
    "south": [(20, 21), (21, 22), (22, 22)],
    "southeast": [(19, 28), (20, 25), (21, 26)],
    "southwest": [(20, 15), (21, 14), (21, 18), (22, 13)],
}

_text_locs = [
    (2, 1),  # 0
    (5, 0),  # 1
    (8, 0),  # 2
    (14, 0),  # 3
    (17, 0),  # 4
    (20, 0),  # 5
    (2, 25),  # 6
    (5, 26),  # 7
    (8, 25),  # 8
    (11, 28),  # 9
    (14, 30),  # 10
    (18, 31),  # 11
    (21, 31),  # 12
]

_text_placements = {
    "highlands": [1, 0, 6],
    "grampian": [7, 6, 1],
    "tayside": [8, 7, 1],
    "central": [2, 8, 7],
    "nireland": [3, 2, 4],
    "northeast": [8, 7, 9, 2],
    "northwest": [3, 4, 2],
    "yorks": [9, 8, 10],
    "wales": [4, 3, 5],
    "midlands": [3, 9, 4],
    "west": [4, 5, 3],
    "east": [11, 10, 12, 9],
    "south": [5, 12, 11, 10],
    "southeast": [11, 12, 10],
    "southwest": [5, 4, 12],
}

_city_temp_locations = {
    "inverness": (3, 20, "l"),
    "pitlochry": (6, 20, "l"),
    "edinburgh": (9, 21, "l"),
    "belfast": (11, 13, "l"),
    "newcastle": (11, 23, "l"),
    "manchester": (14, 22, "r"),
    "birmingham": (16, 23, "l"),
    "cardiff": (18, 20, "l"),
    "plymouth": (21, 19, "l"),
    "cambridge": (17, 29, "lm"),
    "london": (19, 28, "lm"),
}


class WeatherMap(object):
    def __init__(self):
        self.map = [
            "",
            "",
            "            ␚␒`4`~¬|¬}                  ",
            "            ␚␒?0~¬¬¬¬%                  ",
            "          ␞␚␒j*¬¬¬¬¬y||t                ",
            "          ␞␚␒ ({¬¬¬¬¬¬¬?                ",
            "            ␚␒!'¬¬¬¬¬¬¬!                ",
            "            ␞␚␒~¬¬¬¬¬w1                 ",
            "            ␞␚␒~¬¬¬¬¬w1                 ",
            "            ␚␒j)+¬¬¬¬¬¬}                ",
            "       ␞␚␕p|¬t  x¬¬¬¬¬¬¬0               ",
            '       ␚␕n¬¬¬¬u +" ¬¬¬¬¬¬               ',
            "       ␚␕+¬¬¬¬¬ > ␞+¬¬¬¬¬5              ",
            '       ␞␚␕"%*o!     *¬¬¬¬¬u             ',
            "              ␚␕`   *¬¬¬¬¬¬}            ",
            "             ␞␚␕k|¬¬¬¬¬¬¬¬¬¬            ",
            "              ␚␕'o¬¬¬¬¬¬¬␞¬}z¬t         ",
            "              ␞␚␕j¬¬¬¬¬¬¬¬¬¬¬¬¬         ",
            "            ␚␕`||¬¬¬¬¬␞¬¬¬¬¬¬␟7         ",
            '             ␞␚␕!"//#h¬¬¬¬¬¬¬¬pp        ',
            "             ␞␚␕ t¬¬¬¬¬¬¬¬¬¬¬¬¬!        ",
            "             ␚␕h¬¬¬¬¬␞¬?s///?#          ",
            "            ␚␕8?' \"'    \"               ",
        ]
        self.text_slots = dict()

    def map_lines(self):
        return [ttxutils.decode(l, low=True) for l in self.map[2:]]

    def plot_temp(self, city, temperature):
        temp = int(temperature)
        y, x, direction = _city_temp_locations[city]
        s = ""
        if "m" in direction:
            s += chr(ttxcolour.RELEASE)
        s += chr(ttxcolour.ALPHAWHITE)
        s += str(temp)
        s += chr(ttxcolour.MOSAICGREEN)  # this will get overwritten
        if "l" in direction:
            x = x - (len(s) - 1)
        for c in s:
            t = self.map[y]
            self.map[y] = f"{t[:x]}{c}{t[x+1:]}"
            x += 1

    def plot_borders(self, region_colours_dict):
        borders = list()
        for name, edges in _region_boundaries.items():
            for edge in edges:
                borders.append((*edge, name))

        # sort by row, then column
        borders.sort(key=lambda b: b[0] * 1000 + b[1])

        last_row = 0
        last_colour = None
        for b in borders:
            plot = False
            row, column, name = b
            new_colour = chr(region_colours_dict[name])
            current = self.map[row][column]
            while current.isdigit():
                column += 1
                current = self.map[row][column]
            if row != last_row:
                plot = True
                last_row = row
            elif new_colour != last_colour:
                plot = True
            elif new_colour != current:
                if current < " ":
                    plot = True
            if plot:
                last_colour = new_colour
                t = self.map[row]
                self.map[row] = f"{t[:column]}{new_colour}{t[column+1:]}"

    def plot_text(self, region, colour, text):
        indexes = _text_placements[region]
        while True:
            if indexes:
                index = indexes[0]
                indexes = indexes[1:]
                if index not in self.text_slots:
                    self.text_slots[index] = True
                    break
            else:
                index = 0
                while index in self.text_slots:
                    index += 1
                break
        row, column = _text_locs[index]
        for word in text.split():
            s = f"{chr(colour)}{word}"
            x = column
            for c in s:
                t = self.map[row]
                self.map[row] = f"{t[:x]}{c}{t[x+1:]}"
                x += 1
            row += 1

    def put_text(self, row, column, text):
        x = column
        for t in text:
            r = self.map[row]
            self.map[row] = f"{r[:x]}{t}{r[x+1:]}"
            x += 1
