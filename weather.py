import ttxcolour
import ttxutils
import ttxpage
import weathermap
from wx_ids import regions, city_ids, region_ids, observation_ids
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


def firstmap(locs):
    slocs = sorted(locs, key=lambda l: maporder[l])
    return slocs[0]


def weathermaps(W):
    cfg = _config["weather"]
    if datetime.datetime.now().hour > 16 or datetime.datetime.now().hour < 4:
        pages = (1, 2, 3)
    else:
        pages = (0, 1, 2)

    pagenum = cfg["maps"]
    subpage = 1

    page = ttxpage.TeletextPage("Weather Maps", pagenum, time=10)
    for index in pages:
        caption = None
        page.header(pagenum, subpage, status=0xC000)
        region_wx = dict()
        for reg_name, reg_id in region_ids.items():
            w = W.loc_forecast(reg_id, metoffer.DAILY)
            now = w.data[index]
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
            now = w.data[index]
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

    page.save()


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


def makeweather():
    W = WeatherCache()
    if not W.valid():
        print("Missing 'met_office_api' in configuration. Skipping weather.")
        return

    weathermaps(W)
    regionheadline = weatherregion(W)
    ukheadline = weatheroutlook(W)


def main():
    config.Config().add("defaults.yaml")
    config.Config().add("pm.yaml")
    config.Config().load()

    makeweather()


if __name__ == "__main__":
    main()
