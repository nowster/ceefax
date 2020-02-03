import ttxcolour
import ttxutils
import ttxpage
import weathermap
from wx_ids import regions, city_ids, region_ids, observation_ids, fiveday_ids
import metoffer

import dateutil.parser
import dateutil.tz
import dateutil.utils
import datetime
import pickle
import textwrap
import re
import config

_config = config.Config().config

colours_a = [
    ttxcolour.ALPHACYAN,
    ttxcolour.ALPHAGREEN,
    ttxcolour.ALPHAMAGENTA,
    ttxcolour.ALPHAYELLOW,
    ttxcolour.ALPHARED,
    ttxcolour.ALPHAWHITE,
    ttxcolour.ALPHABLUE,
]
colours_m = [
    ttxcolour.MOSAICCYAN,
    ttxcolour.MOSAICGREEN,
    ttxcolour.MOSAICMAGENTA,
    ttxcolour.MOSAICYELLOW,
    ttxcolour.MOSAICRED,
    ttxcolour.MOSAICWHITE,
    ttxcolour.MOSAICBLUE,
]

weathers = {
    0: "Clear",
    1: "Sunny",
    2: "Partly cloudy",
    3: "Partly cloudy",
    4: "Not used",
    5: "Mist",
    6: "Fog",
    7: "Cloudy",
    8: "Overcast",
    9: "Lt.rain shower",
    10: "Lt.rain shower",
    11: "Drizzle",
    12: "Light rain",
    13: "Hvy.rain shower",
    14: "Hvy.rain shower",
    15: "Heavy rain",
    16: "Sleet shower",
    17: "Sleet shower",
    18: "Sleet",
    19: "Hail shower",
    20: "Hail shower",
    21: "Hail",
    22: "Lt.snow shower",
    23: "Lt.snow shower",
    24: "Light snow",
    25: "Hvy.snow shower",
    26: "Hvy.snow shower",
    27: "Heavy snow",
    28: "Thunder shower",
    29: "Thunder shower",
    30: "Thunder",
}
short_weathers = {
    0: "clear",
    1: "sunny",
    2: "pt cldy",
    3: "pt cldy",
    4: "notused",
    5: "mist",
    6: "fog",
    7: "cloudy",
    8: "ovrcast",
    9: "lt rain",
    10: "lt rain",
    11: "drizzle",
    12: "lt.rain",
    13: "hy shwr",
    14: "hy shwr",
    15: "hy rain",
    16: "sleet s",
    17: "sleet s",
    18: "sleet",
    19: "hail sh",
    20: "hail sh",
    21: "hail",
    22: "lt snow",
    23: "lt snow",
    24: "lt.snow",
    25: "hy snow",
    26: "hy snow",
    27: "hy.snow",
    28: "thnd sh",
    29: "thnd sh",
    30: "thunder",
}

maporder = {
    "highlands": 0,
    "grampian": 1,
    "tayside": 2,
    "central": 3,
    "northeast": 4,
    "nireland": 5,
    "yorks": 6,
    "northwest": 7,
    "wales": 8,
    "midlands": 9,
    "east": 10,
    "west": 11,
    "southwest": 12,
    "south": 13,
    "southeast": 14,
}


class WeatherCache(object):
    def __init__(self, cache_hours=6):
        if "met_office_api" in _config:
            self._M = metoffer.MetOffer(_config["met_office_api"])
        else:
            self._M = None

        self.cache_hours = cache_hours
        self.cache = dict()
        cachedir = _config["cachedir"]
        try:
            with open(f"{cachedir}/weather.cache", "rb") as f:
                self.cache = pickle.load(f)
        except:
            pass

    def __del__(self):
        cachedir = _config["cachedir"]
        if self.cache:
            with open(f"{cachedir}/weather.cache", "wb") as f:
                pickle.dump(self.cache, f)

    def valid(self):
        return self._M is not None

    @staticmethod
    def _cache_value_valid(isodate, offset):
        now = dateutil.utils.default_tzinfo(
            datetime.datetime.now(), dateutil.tz.gettz()
        )
        time = dateutil.utils.default_tzinfo(
            dateutil.parser.isoparse(isodate), dateutil.tz.gettz()
        )
        return time + datetime.timedelta(hours=offset) > now

    def loc_forecast(self, request, step, isotime=None, cache_hours=None):
        if cache_hours is None:
            cache_hours = self.cache_hours
        key = f"{request}%{step}%{isotime}"
        if key in self.cache:
            value = self.cache[key]
            if self._cache_value_valid(value.data_date, cache_hours):
                return value
        w = self._M.loc_forecast(request, step, isotime=isotime)
        value = metoffer.Weather(w)
        self.cache[key] = value
        return value

    def text_forecast(self, field, request, cache_hours=None):
        if cache_hours is None:
            cache_hours = self.cache_hours
        key = f"{field}!{request}"
        if key in self.cache:
            value = self.cache[key]
            if self._cache_value_valid(value.issued_at, cache_hours):
                return value
        w = self._M.text_forecast(field, request)
        value = metoffer.TextForecast(w)
        self.cache[key] = value
        return value

    def loc_observations(self, request, cache_hours=None):
        if cache_hours is None:
            cache_hours = self.cache_hours
        key = f"observations!{request}"
        if key in self.cache:
            value = self.cache[key]
            if self._cache_value_valid(value.data_date, cache_hours):
                return value
        w = self._M.loc_observations(request)
        try:
            value = metoffer.Weather(w)
        except:
            print(f"ERROR: {key}")
            print(repr(w))
            raise
        self.cache[key] = value
        return value


def firstmap(locs):
    slocs = sorted(locs, key=lambda l: maporder[l])
    return slocs[0]


def weathermaps(W):
    cfg = _config["weather"]
    if datetime.datetime.now().hour > 16:
        advance = 1
    else:
        advance = 0

    pagenum = cfg["maps"]
    subpage = 1

    page = ttxpage.TeletextPage("Weather Maps", pagenum, time=10)
    for index in range(3):
        caption = None
        advanced = False
        page.header(pagenum, subpage, status=0xC000)
        region_wx = dict()
        for reg_name, reg_id in region_ids.items():
            w = W.loc_forecast(reg_id, metoffer.DAILY)
            now = w.data[index + advance]
            if (not advanced and
                now["timestamp"][0].date() < datetime.datetime.now().date()):
                # handle overnight transition
                advanced = True
                advance += 1
                now = w.data[index + advance]
            wx_type = now["Weather Type"][0]
            wx_type = weathers.get(wx_type, "N/A")
            if wx_type in region_wx:
                region_wx[wx_type].append(reg_name)
            else:
                region_wx[wx_type] = [reg_name]

        map = weathermap.WeatherMap()
        reg_mapping = dict()
        i = 0
        for wx, locs in region_wx.items():
            map.plot_text(firstmap(locs), colours_a[i], wx)
            for loc in locs:
                reg_mapping[loc] = colours_m[i]
            i += 1

        for city_name, city_id in city_ids.items():
            w = W.loc_forecast(city_id, metoffer.DAILY)
            now = w.data[index + advance]
            if not caption:
                caption = now["timestamp"][0].strftime("%A")
                if now["timestamp"][1] == "Night":
                    caption += " night"
            if now["timestamp"][1] == "Day":
                wx_temp = now["Day Maximum Temperature"][0]
            else:
                wx_temp = now["Night Minimum Temperature"][0]
            map.plot_temp(city_name, wx_temp)

        # This needs to go after temperatures, as it changes
        # the colours following the numbers
        map.plot_borders(reg_mapping)

        title = f"Weather for {caption}"
        title = f"{title:^39}"[2:]
        page.addline(
            1,
            ttxcolour.blue()
            + ttxcolour.colour(ttxcolour.NEW_BACK)
            + f"{ttxcolour.yellow()}{title}",
        )
        l = 2
        subpagenum = chr(ttxcolour.ALPHAWHITE) + f"{subpage}/3"
        map.put_text(2, 35, subpagenum)
        for ll in map.map_lines():
            page.addline(l, ll)
            l += 1
        title = "From the Met Office"
        title = f"{title:^39}"[2:]
        page.addline(
            23,
            ttxcolour.blue()
            + ttxcolour.colour(ttxcolour.NEW_BACK)
            + f"{ttxcolour.yellow()}{title}",
        )
        page.addline(
            24, ttxutils.decode("€ARegional  €BSport   €CWeather  €FMain Menu")
        )
        page.addfasttext(
            cfg["regional"], 0x300, cfg["index"], 0x100, 0x8FF, 0x199
        )
        subpage += 1

    page.save(add_to_newsreel=True)


def weatherregion(W):
    cfg = _config["weather"]
    region = _config["bbc_news_regions"][_config["bbc_news_region"]]

    wx_text = W.text_forecast(
        metoffer.REGIONAL_FORECAST, regions[region["weather"]]
    )
    headline = wx_text.data[0][1]

    head1 = wx_text.data[1][0].replace(":", "")
    head2 = wx_text.data[2][0].replace(":", "")
    body1 = wx_text.data[1][1]
    body2 = wx_text.data[2][1]
    min = None
    max = None

    if "Minimum Temperature" in body1:
        s = re.search(r"Minimum Temperature (-?\d+)C", body1)
        min = s[1]
        s = re.search(r"Maximum Temperature (-?\d+)C", body2)
        max = s[1]
    else:
        s = re.search(r"Minimum Temperature (-?\d+)C", body2)
        min = s[1]
        s = re.search(r"Maximum Temperature (-?\d+)C", body1)
        max = s[1]

    body1 = re.sub(r" M(ax|in)imum Temperature -?\d+C.*", r"", body1)
    body2 = re.sub(r" M(ax|in)imum Temperature -?\d+C.*", r"", body2)

    header = [
        "€Wh,,lh,,lh,,l€T||,<<|,,|,,|,,|l<l,,<,,l||",
        "€Wj 1nj 1nj =n€T€]€S¬jj5¬shw{4k7juz5¬sjw{%",
        "€W*,,.*,,.*,,.€T€]€Sozz%¬pj5j5j5j5j5¬pj5j5",
        "1234567890123€T//-,,/,,-.-.-.-.-.,,-.-.//",
    ]
    footer = [
        "€T€]€G     REGIONAL€CNews€G160€CWeather€G302",
        "€T€]€GNATIONAL€CMain menu€G100€CWeather€G400",
        "€AOutlook  €BSport    €CWeather  €FMain Menu",
    ]
    short_name = f"{region['medium']:^13.13}"
    header[3] = short_name + header[3][13:]

    page = ttxpage.TeletextPage("Weather Page", cfg["regional"])

    subpage = 1
    for h, b in [(head1, body1), (head2, body2)]:
        lines = textwrap.wrap(page.fixup(b), 19)
        rows = ["", f"{ttxcolour.yellow()}{h.upper()}", ""]
        for l in range(13):
            try:
                t = lines[l]
            except:
                t = ""
            t = (
                f"{ttxcolour.green()}{t:<19.19}"
                f"{ttxcolour.colour(ttxcolour.MOSAICYELLOW)}5"
            )
            if l == 0:
                t += f"    {ttxcolour.yellow()}STATISTICS"
            elif l == 2:
                t += f"    {ttxcolour.white()}Maximum"
            elif l == 3:
                t += f"{ttxcolour.white()}Temperature{ttxcolour.yellow()}{max}C"
            elif l == 5:
                t += f"    {ttxcolour.white()}Minimum"
            elif l == 6:
                t += f"{ttxcolour.white()}Temperature{ttxcolour.yellow()}{min}C"
            rows.append(t)
        bot = f"{subpage}/2"
        rows.append(f"{bot:>39.39}")

        page.header(cfg["regional"], subpage, status=0xC000)
        line = 1
        for l in header:
            page.addline(line, ttxutils.decode(l))
            line += 1
        for ll in rows:
            page.addline(line, ll)
            line += 1
        line = 25 - len(footer)
        for l in footer:
            page.addline(line, ttxutils.decode(l))
            line += 1
        page.addfasttext(
            cfg["national"], 0x300, cfg["index"], 0x100, 0x8FF, 0x199
        )
        subpage += 1
    page.save()
    return headline


def weatheroutlook(W):
    cfg = _config["weather"]

    wx_text = W.text_forecast(metoffer.REGIONAL_FORECAST, regions["uk"])

    headline = wx_text.data[0][1]

    page = ttxpage.TeletextPage("Weather Page", cfg["national"])

    pages = []
    for i in range(3):
        head = wx_text.data[i + 1][0].replace(":", "")
        head = textwrap.wrap(page.fixup(head), 39)
        body = wx_text.data[i + 1][1]
        body = re.sub(r" M(ax|in)imum Temperature \d+C.*", r"", body)
        body = textwrap.wrap(page.fixup(body), 39)
        block = []
        for h in head:
            block.append(f" {h:<.39}")
        for b in body:
            block.append(f"{ttxcolour.cyan()}{b:<.39}")
        if len(pages) and len(pages[-1]) + len(block) + 1 <= 15:
            pages[-1].append('')
            pages[-1].extend(block)
        else:
            pages.append(block)

    header = [
        "␗j#3kj#3kj#3k␔␝␑␓h44|h<h<|(|$|h4|$|l    ",
        "␗j $kj $kj 'k␔␝␑␓*uu?jwj7␡ ␡ ␡k5␡1␡k4   ",
        '␗"###"###"###␔////,,.-,-.,/,/,-.,.,-.///',
    ]

    title = "From the Met Office"
    title = f"{title:^39}"[2:]
    footer = [
        ttxcolour.blue()
        + ttxcolour.colour(ttxcolour.NEW_BACK)
        + f"{ttxcolour.yellow()}{title}",
        ttxutils.decode("€AUK cities €BSport  €CWeather  €FMain Menu"),
    ]

    for subpage in range(len(pages)):
        rows = []
        top = f"{subpage + 1}/{len(pages)}"
        rows.append(f"{top:>39.39}")
        rows.append(" UK WEATHER OUTLOOK")
        rows.append("")
        rows.extend(pages[subpage])

        page.header(cfg["national"], subpage + 1, status=0xC000)
        line = 1
        for l in header:
            page.addline(line, ttxutils.decode(l))
            line += 1
        for l in rows:
            page.addline(line, l)
            line += 1
        line = 25 - len(footer)
        for l in footer:
            page.addline(line, l)
            line += 1
        page.addfasttext(
            cfg["observations"], 0x300, cfg["index"], 0x100, 0x8FF, 0x199
        )

    page.save()
    return headline


def weatherobservations(W):
    cfg = _config["weather"]

    minimum = 9999
    maximum = -9999
    rows = []
    timestamp = None
    for city, num in observation_ids.items():
        obs = W.loc_observations(num, cache_hours=1).data
        time = None
        temp = '-'
        wind_speed = '-'
        wind_dir = '-'
        pressure = '-'
        trend = '-'
        weather_type = None
        for o in obs:
            if "timestamp" in o:
                time = o["timestamp"][0]
            if "Temperature" in o:
                temp = round(float(o["Temperature"][0]))
            if "Wind Speed" in o:
                wind_speed = o["Wind Speed"][0]
            if "Wind Direction" in o:
                wind_dir = o["Wind Direction"][0]
            if "Pressure" in o:
                pressure = o["Pressure"][0]
            if "Pressure Tendency" in o:
                trend = o["Pressure Tendency"][0]
            if "Weather Type" in o:
                weather_type = o["Weather Type"][0]
        if len(rows) % 2 == 1:
            row_colour = ttxcolour.white()
        else:
            row_colour = ttxcolour.cyan()
        if trend == "F":
            trend_colour = ttxcolour.green()
        elif trend == "S":
            trend_colour = ttxcolour.white()
        else:
            trend_colour = ttxcolour.cyan()
        row = f"{row_colour}{city:<12.12}{temp:>4}{wind_dir:>4}{wind_speed:>3}"
        row += f"{pressure:>6}{trend_colour}{trend}{row_colour}"
        if weather_type is not None:
            row += short_weathers[weather_type]
        else:
            row += "n/a"
        rows.append(row)
        if timestamp is None or time > timestamp:
            timestamp = time
        if temp:
            if temp < minimum:
                minimum = temp
            if temp > maximum:
                maximum = temp

    header = [
        "␗j#3kj#3kj#3k␔␝␑␓h44|h<h<|(|$|h4|$|l    ",
        "␗j $kj $kj 'k␔␝␑␓*uu?jwj7␡ ␡ ␡k5␡1␡k4   ",
        '␗"###"###"###␔////,,.-,-.,/,/,-.,.,-.///',
    ]

    temps_c = []
    temps_f = []
    steps = (maximum - minimum) / 10
    if steps < 1:
        steps = 1
        minimum = (minimum + maximum) // 2 - 5
    for i in range(11):
        temp_c = round(minimum + i * steps)
        temp_f = round((temp_c * 1.8) + 32)
        c = str(temp_c)
        f = str(temp_f)
        l = max(len(c), len(f))
        temps_c.append(f"{c:>{l}}")
        temps_f.append(f"{f:>{l}}")

    footer = []
    footer.append(ttxutils.decode("   ␃pressure␆R␃rising␇S␃steady␂F␃falling"))
    footer.append("")
    back = (
        ttxcolour.blue()
        + ttxcolour.colour(ttxcolour.NEW_BACK)
        + ttxcolour.yellow()
    )
    footer.append(f"{back}C= " + " ".join(temps_c))
    footer.append(f"{back}F= " + " ".join(temps_f))
    footer.append(
        ttxutils.decode("€AUK 5 day€B Sport  €CWeather   €FMain Menu")
    )

    page = ttxpage.TeletextPage("Weather Reports", cfg["observations"])

    for subpage in (1, 2, 3):
        body = []
        top = f"{subpage}/3"
        body.append(f"{top:>39.39}")
        time = timestamp.strftime("%H%M")
        body.append(f"{ttxcolour.yellow()}CURRENT UK WEATHER: Report at {time}")
        body.append("")
        body.append(ttxutils.decode("            ␃temp   wind  pres"))
        body.append(ttxutils.decode("               ␇C    mph    mB"))
        base = (subpage - 1) * 10
        for l in rows[base : base + 10]:
            body.append(l)

        page.header(cfg["observations"], subpage, status=0xC000)
        line = 1
        for l in header:
            page.addline(line, ttxutils.decode(l))
            line += 1
        for l in body:
            page.addline(line, l)
            line += 1
        line = 25 - len(footer)
        for l in footer:
            page.addline(line, l)
            line += 1
        page.addfasttext(
            cfg["fiveday"], 0x300, cfg["index"], 0x100, 0x8FF, 0x199
        )
        subpage += 1
    page.save()


def weatherfiveday(W):
    cfg = _config["weather"]

    maximum = -9999
    minimum = 9999
    today = None
    entries = []
    for city, num in fiveday_ids.items():
        wx = W.loc_forecast(num, metoffer.DAILY).data
        if today is None:
            today = wx[0]["timestamp"][0]
        entry = [city]
        for i in range(5):
            wx_type = short_weathers.get(wx[i * 2]["Weather Type"][0], "N/A")
            max_temp = int(wx[i * 2]["Day Maximum Temperature"][0])
            min_temp = int(wx[i * 2 + 1]["Night Minimum Temperature"][0])
            date = wx[i * 2]["timestamp"][0]
            entry.append(
                f"{date.strftime('%a')}" f"{max_temp:>4}{min_temp:>4} {wx_type}"
            )
            if max_temp > maximum:
                maximum = max_temp
            if min_temp < minimum:
                minimum = min_temp

        entries.append(entry)

    header = [
        "␗j#3kj#3kj#3k␔␝␑␓h44|h<h<|(|$|h4|$|l    ",
        "␗j $kj $kj 'k␔␝␑␓*uu?jwj7␡ ␡ ␡k5␡1␡k4   ",
        '␗"###"###"###␔////,,.-,-.,/,/,-.,.,-.///',
    ]

    temps_c = []
    temps_f = []
    steps = (maximum - minimum) / 10
    if steps < 1:
        steps = 1
        minimum = (minimum + maximum) // 2 - 5
    for i in range(11):
        temp_c = round(minimum + i * steps)
        temp_f = round((temp_c * 1.8) + 32)
        c = str(temp_c)
        f = str(temp_f)
        l = max(len(c), len(f))
        temps_c.append(f"{c:>{l}}")
        temps_f.append(f"{f:>{l}}")

    footer = []
    back = (
        ttxcolour.blue()
        + ttxcolour.colour(ttxcolour.NEW_BACK)
        + ttxcolour.yellow()
    )
    footer.append(f"{back}C= " + " ".join(temps_c))
    footer.append(f"{back}F= " + " ".join(temps_f))
    footer.append(
        ttxutils.decode("€AUK map  €B Sport  €CWeather   €FMain Menu")
    )

    page = ttxpage.TeletextPage("Weather Five Day", cfg["fiveday"])

    numpages = (len(entries) + 3) // 4
    for sub in range(numpages):
        body = []
        top = f"{sub+1}/{numpages}"
        body.append(f"{top:>39.39}")
        body.append(
            ttxcolour.yellow()
            + "UK FIVE DAY FORECAST FROM "
            + today.strftime("%e %b").strip()
        )
        body.append(ttxcolour.green() + "max for 0600-1800   min for 1800-0600")
        body.append(
            ttxcolour.yellow()
            + "    max min"
            + ttxcolour.white()
            + "C      "
            + ttxcolour.yellow()
            + "    max min"
            + ttxcolour.white()
            + "C"
        )
        for i in range(2):
            count = 0
            c1 = []
            c2 = []
            offset = (sub * 4) + i
            if offset < len(entries):
                c1 = entries[offset]
            offset = (sub * 4) + i + 2
            if offset < len(entries):
                c2 = entries[offset]
            while len(c1) and len(c2):
                row = ""
                if count % 2:
                    row += ttxcolour.cyan()
                else:
                    row += ttxcolour.white()
                if len(c1):
                    row += f"{c1[0]:<19.19} "
                    c1 = c1[1:]
                if len(c2):
                    row += c2[0]
                    c2 = c2[1:]
                body.append(row)
                count += 1
            body.append("")

        page.header(cfg["fiveday"], sub + 1, status=0xC000)
        line = 1
        for l in header:
            page.addline(line, ttxutils.decode(l))
            line += 1
        for l in body:
            page.addline(line, l)
            line += 1
        line = 25 - len(footer)
        for l in footer:
            page.addline(line, l)
            line += 1
        page.addfasttext(cfg["maps"], 0x300, cfg["index"], 0x100, 0x8FF, 0x199)
    page.save()


def weatherindex(regionhead, ukhead):
    cfg = _config["weather"]

    page = ttxpage.TeletextPage("Weather Index", cfg["index"])
    regionheads = textwrap.wrap(page.fixup(regionhead), 35)
    regionhead = f"{regionheads[0]:<35.35}"
    regionheads = regionheads[1:]

    headline = "WEATHER NEWS:¬" + page.fixup(ukhead)
    headlines = textwrap.wrap(headline, 39)
    for i in range(len(headlines)):
        l = headlines[i]
        if i == 0:
            l = ttxcolour.yellow() + l.replace("¬", ttxcolour.green())
        elif i == len(headlines) - 1:
            l = (
                ttxcolour.green()
                + f"{l:<35.35}"
                + ttxcolour.yellow()
                + f"{cfg['maps']:03x}"
            )
        else:
            l = ttxcolour.green() + l
        headlines[i] = l

    header = [
        "␗j#3kj#3kj#3k␔␝␑␓h44|h<h<|(|$|h4|$|l    ",
        "␗j $kj $kj 'k␔␝␑␓*uu?jwj7␡ ␡ ␡k5␡1␡k4   ",
        '␗"###"###"###␔////,,.-,-.,/,/,-.,.,-.///',
    ]

    middle = [
        "␃UK␄````````````````````````````````````",
        "␆Forecast maps  ␃401␆UK Cities 5 Day␃406",
        "␆Regions        ␃402␆               ␃   ",
        "␆National       ␃403␆               ␃   ",
        "␆Current Weather␃404                    ",
        "                                        ",
    ]

    attrib = "From the Met Office"
    attrib = f"{attrib:^39}"[2:]
    footer = headlines + [
        "",
        ttxcolour.blue()
        + ttxcolour.colour(ttxcolour.NEW_BACK)
        + f"{ttxcolour.yellow()}{attrib}",
        ttxutils.decode("€AMaps  €BRegional  €COutlook  €FMain Menu"),
    ]

    page.header(cfg["index"])
    line = 1
    for l in header:
        page.addline(line, ttxutils.decode(l))
        line += 1
    page.addline(
        line,
        ttxcolour.colour(ttxcolour.DOUBLE_HEIGHT)
        + regionhead
        + ttxcolour.yellow()
        + f"{cfg['regional']:03x}",
    )
    line += 2
    for l in regionheads:
        page.addline(line, " " + l)
        line += 1
    line += 1
    for l in middle:
        page.addline(line, ttxutils.decode(l))
        line += 1
    line = 25 - len(footer)
    for l in footer:
        page.addline(line, l)
        line += 1
    page.addfasttext(
        cfg["maps"], cfg["regional"], cfg["national"], 0x100, 0x8FF, 0x199
    )
    page.save()


def makeweather():
    W = WeatherCache()
    if not W.valid():
        print("Missing 'met_office_api' in configuration. Skipping weather.")
        return []

    weathermaps(W)
    regionheadline = weatherregion(W)
    ukheadline = weatheroutlook(W)
    weatherobservations(W)
    weatherfiveday(W)
    weatherindex(regionheadline, ukheadline)

    return [
        [
            dict(section="Weather", short_title=ukheadline),
            _config["weather"]["maps"],
        ]
    ]


def main():
    config.Config().add("defaults.yaml")
    config.Config().add("pm.yaml")
    config.Config().load()

    makeweather()


if __name__ == "__main__":
    main()
