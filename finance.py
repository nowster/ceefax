import ttxcolour
import ttxutils
import ttxpage
import fetch

import AdvancedHTMLParser
import pickle
import dateutil.parser
import datetime
import config
import html

_config = config.Config().config

# URLs
_exchanges = "https://www.sharecast.com/indices/index.html"
_ftse = "https://www.sharecast.com/index/FTSE_100"
_currencies = "https://www.sharecast.com/currencies/index.html"


_indices = [
    [
        ("FTSE", "FTSE 100"),
        ("techMARK100", "techMARK 100"),
        ("Dow Jones", "Dow Jones I.A."),
        ("Hang Seng", "Hang Seng"),
        ("Nikkei 225", "Nikkei 225"),
        ("DJEurostoxx", "Euro Stoxx 50"),
    ],
    [
        ("FTSE", "FTSE 100"),
        ("techMARK100", "techMARK 100"),
        ("Dow Jones", "Dow Jones I.A."),
        ("Nasdaq", "Nasdaq 100"),
        ("£1=euro", "GBP/EUR"),
        ("£1=$", "GBP/USD"),
    ],
]


def stock_time(index, time):
    closed = True
    if datetime.datetime.now() - time > datetime.timedelta(minutes=30):
        closed = True
    elif index in ["FTSE 100", "techMARK 100"]:
        if datetime.time(7) < time.time() < datetime.time(16):
            closed = False
    elif index in ["Dow Jones I.A.", "Nasdaq 100"]:
        if datetime.time(14, 30) < time.time() < datetime.time(21):
            closed = False
    elif index in ["Hang Seng"]:
        if datetime.time(17, 30) < time.time():
            closed = False
    elif index in ["Nikkei 225"]:
        if datetime.time(18) < time.time():
            closed = False
    elif index in ["Euro Stoxx 50"]:
        if datetime.time(7) < time.time() < datetime.time(16):
            closed = False

    if closed:
        return "CLOSE"
    else:
        return time.strftime("%H:%M")


class FinanceCache(object):
    def __init__(self):
        self.cache = dict()
        self.maxage = datetime.timedelta(minutes=5)
        self.fetch = fetch.Fetcher()
        cachedir = _config["cachedir"]
        try:
            with open(f"{cachedir}/finance.cache", "rb") as f:
                self.cache = pickle.load(f)
        except:
            pass

    def __del__(self):
        cachedir = _config["cachedir"]
        if self.cache:
            with open(f"{cachedir}/finance.cache", "wb") as f:
                pickle.dump(self.cache, f)

    def get(self, url, maxage=None):
        if maxage is None:
            maxage = self.maxage
        elif type(maxage) is int:
            maxage = datetime.timedelta(minutes=maxage)
        if url in self.cache:
            entry = self.cache[url]
            if datetime.datetime.now() - entry["stamp"] < maxage:
                return entry["value"]
        else:
            entry = None

        resp = self.fetch.get(url)
        if resp.status_code == 304:
            return entry["value"]
        if resp.status_code != 200:
            print(resp.status_code)
            return None
        print(f"Cache miss {url}", flush=True)

        value = resp.text

        self.cache[url] = dict(value=value, stamp=datetime.datetime.now(),)

        return value


def get_indices(cache):
    text = cache.get(_exchanges)
    parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
    parser.parseStr(text)

    values = dict()
    article = parser.getElementsByTagName("article")
    bodies = article.getElementsByTagName("tbody")

    for row in bodies.getElementsByTagName("tr"):
        elements = row.getChildren().getElementsByTagName("td")
        name = elements[0].textContent.strip()
        name = html.unescape(name)
        price = elements[1].textContent.strip()
        change = elements[2].textContent.strip()
        percent = elements[3].textContent.strip()
        time = elements[4].textContent.strip()

        price = price.replace(",", "")
        change = change.replace(",", "")
        time = dateutil.parser.parse(time)
        values[name] = dict(
            price=price, change=change, percent=percent, time=time,
        )

    return values


def get_currencies(cache):
    text = cache.get(_currencies)
    parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
    parser.parseStr(text)

    values = dict()
    article = parser.getElementsByTagName("article")
    bodies = article.getElementsByTagName("tbody")[0].getChildren()

    for row in bodies.getElementsByTagName("tr"):
        elements = row.getChildren().getElementsByTagName("td")
        name = elements[0].textContent.strip()
        name = html.unescape(name)
        price = elements[1].textContent.strip()
        change = elements[2].textContent.strip()
        percent = elements[3].textContent.strip()
        time = elements[4].textContent.strip()

        price = price.replace(",", "")
        change = change.replace(",", "")
        time = dateutil.parser.parse(time)
        values[name] = dict(
            price=price, change=change, percent=percent, time=time,
        )

    return values


def get_ftse(cache):
    text = cache.get(_ftse)
    parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
    parser.parseStr(text)

    values = dict()
    table = parser.getElementsByTagName("table")
    bodies = table.getElementsByTagName("tbody")

    for row in bodies.getElementsByTagName("tr"):
        name = (
            row.getChildren().getElementsByTagName("th")[0].textContent.strip()
        )
        name = html.unescape(name)
        elements = row.getChildren().getElementsByTagName("td")
        price = elements[0].textContent.strip()
        percent = elements[1].textContent.strip()
        time = elements[5].textContent.strip()

        price = price.replace(",", "")
        time = dateutil.parser.parse(time)
        values[name] = dict(price=price, percent=percent, time=time,)

    return values


def get_ftse100(cache):
    values = dict()
    url = _ftse_base + _ftse_url
    while url:
        text = cache.get(url, maxage=60)
        parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
        parser.parseStr(text)

        links = parser.find(tagname="a", title="Next")
        if links:
            url = _ftse_base + links[0].getAttribute("href")
        else:
            url = None

        tables = parser.getElementsByTagName("table")
        tbody = tables.getElementsByTagName("tbody")
        for row in tbody.getElementsByTagName("tr"):
            elements = row.getChildren().getElementsByTagName("td")
            code = elements[0].textContent.strip()
            if code in _codes:
                name = _codes[code]
            else:
                name = elements[1].textContent.strip()
                name = name.replace(";", "")  # bad encoding at LSEx
                name = name.title()
            currency = elements[2].textContent.strip()
            price = elements[3].textContent.strip()
            delta = elements[4].textContent.strip()
            percent = elements[5].textContent.strip()
            values[name] = dict(
                name=name,
                currency=currency,
                price=price,
                delta=delta,
                percent=percent,
            )

    return values


def finance_index(indices, ftse, currencies):
    header = [
        "␗j#3kj#3kj#3k␑␝␗  |,h4xl0xl0xl0|,h<     ",
        "␗j $kj $kj 'k␑␝␗  ␡#j5␡j5␡k5␡j5␡pjw     ",
        '␗"###"###"###␑////,/-.,-.,-.,-.,,-,/////',
        ttxcolour.yellow() + " SHARES PAGES:",
        "                        "
        + ttxcolour.cyan()
        + "FTSE100   "
        + ttxcolour.white()
        + "220",
        "",
        ttxcolour.cyan() + " Prices enjoy indicative status only.",
        ttxcolour.cyan() + " No responsibility for accuracy or use",
        ttxcolour.cyan() + " Share prices are updated every hour.",
        ttxcolour.cyan() + " Data is delayed by up to an hour.",
    ]
    separator = ttxcolour.red() + " ````````````````````````````````````` "

    footer = [
        separator,
        ttxcolour.red() + "   Market data from www.sharecast.com",
        separator,
        ttxcolour.red()
        + ttxcolour.colour(ttxcolour.NEW_BACK)
        + ttxcolour.white()
        + " Front page 100        Shares 220",
        ttxcolour.red()
        + "Shares   "
        + ttxcolour.green()
        + "Sport   "
        + ttxcolour.yellow()
        + "Weather  "
        + ttxcolour.cyan()
        + "Main Menu",
    ]

    ftse_time = stock_time("FTSE 100", indices["FTSE 100"]["time"])

    winners = 0
    losers = 0

    for k, v in ftse.items():
        if "-" in v["percent"]:
            losers += 1
        elif v["percent"] != "0.00%":
            winners += 1

    middle = []
    middle.append(separator)
    middle.append(
        ttxcolour.white()
        + " FTSE100"
        + ttxcolour.cyan()
        + "at "
        + ftse_time
        + ttxcolour.white()
        + "Winners"
        + ttxcolour.cyan()
        + f"{winners:<3}"
        + "Losers"
        + ttxcolour.red()
        + f"{losers:<2}"
    )
    middle.append(separator)

    pagenum = 0x200

    page = ttxpage.TeletextPage("Finance Index", pagenum, time=10)

    subpage = 1
    for i in _indices:
        bottom = []
        for name, index in i:
            if index in indices:
                data = indices[index]
            else:
                data = currencies[index]
            l = ttxcolour.yellow() + f" {page.fixup(name):<11.11}"
            l += ttxcolour.white() + f"{data['price']:<7.7} "
            change = data["change"]
            if "-" in change:
                a = ttxcolour.red() + f"{change:<7.7}"
            else:
                a = ttxcolour.cyan() + f"+{change:<6.6}"
            if a[-1] == ".":
                a = a[:-1] + " "
            l += a
            if "=" not in name:
                l += ttxcolour.cyan() + f"at {stock_time(index, data['time'])}"
            bottom.append(l)

        page.header(pagenum, subpage, status=0xC000)
        line = 1
        for l in header:
            page.addline(line, ttxutils.decode(l))
            line += 1
        for l in middle + bottom:
            page.addline(line, l)
            line += 1
        line = 25 - len(footer)
        for l in footer:
            page.addline(line, l)
            line += 1
        page.addfasttext(0x220, 0x300, 0x400, 0x100, 0x8FF, 0x199)
        subpage += 1

    page.save()


#    import pdb; pdb.set_trace()


def makefinance():
    import pprint

    F = FinanceCache()

    indices = get_indices(F)
    currencies = get_currencies(F)
    ftse = get_ftse(F)

    finance_index(indices, ftse, currencies)


def main():
    config.Config().add("defaults.yaml")
    config.Config().add("pm.yaml")
    config.Config().load()

    makefinance()


if __name__ == "__main__":
    main()
