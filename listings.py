import ttxcolour
import ttxutils
import ttxpage
import newsreel
import fetch

import datetime
from dateutil import tz
import pickle
import textwrap
import re
import json
import config

_config = config.Config().config

#
# Note: As of 2020-02-17, www.freesat.co.uk has bad DNS which can
# confuse dnsmasq's cache.
#

_freesat_guide = "https://www.freesat.co.uk/tv-guide"

_tv_mappings = [
    (["BBC One", "BBC 1"], 0x601),
    (["BBC Two", "BBC 2"], 0x602),
    (["ITV", "STV", "UTV"], 0x603),
    ("Channel 4", 0x604),
    ("Channel 5", 0x605),
    ("S4C", 0x606),
]

_radio_mappings = [
    ("BBC Radio 1", 0x641),
    ("BBC Radio 2", 0x642),
    ("BBC Radio 3", 0x643),
    ("BBC Radio 4 FM", 0x644),
    ("BBC R5L", 0x645),
    ("BBC Radio 4 Ex", 0x646),
    (["BBC WS", "BBC World Sv"], 0x648),
    ("Classic FM", 0x647),
    ("talkSport", 0x647),
    ("Absolute Radio", 0x647),
]


class ListingsCache(object):
    def __init__(self):
        self.fetch = fetch.Fetcher()
        self.csrf = None

        self.cache = dict(
            today=None,
            tomorrow=None,
            tv_channels=None,
            radio_channels=None,
            postcode=None,
            datestamp=None,
            bbc_region=None,
            itv_region=None,
        )
        cachedir = _config["cachedir"]
        try:
            with open(f"{cachedir}/listings.cache", "rb") as f:
                self.cache = pickle.load(f)
        except:
            pass
        self.get_channels()
        self.get_listings()

    def __del__(self):
        cachedir = _config["cachedir"]
        if self.cache:
            with open(f"{cachedir}/listings.cache", "wb") as f:
                pickle.dump(self.cache, f)

    def dummy_fetch(self):
        # want cookies
        url = f"{_freesat_guide}/"
        r = self.fetch.get(
            url, headers={"Referer": url}, cookies={"django_language": "en"},
        )
        if "csrftoken" in self.fetch.cookies:
            self.csrf = self.fetch.cookies["csrftoken"]
        else:
            # Sometimes requests doesn't parse cookies properly
            cookie = r.headers["Set-Cookie"]
            if "csrftoken" in cookie:
                m = re.search(r"csrftoken=([^;]+);", cookie)
                if m:
                    self.csrf = m.group(1)
                else:
                    print("ERROR: Can't find csrftoken")

    def get_channels(self):
        L = _config["listings"]
        postcode = L["postcode"]
        postcode = postcode.replace(" ", "")
        if self.cache["postcode"] == postcode:
            if (
                self.cache["tv_channels"] is not None
                and self.cache["radio_channels"] is not None
            ):
                return

        self.dummy_fetch()

        url = f"{_freesat_guide}/api/region/"
        r = self.fetch.post(
            url,
            data=f'"{postcode}"',
            headers={
                "Referer": f"{_freesat_guide}/",
                "X-CSRFToken": self.csrf,
            },
            cookies={"csrftoken": self.csrf},
        )
        if r.status_code != 200:
            print(repr(r.request.url))
            print(f"reg={r.status_code}")
            print(repr(r.request.headers))
            return None
        try:
            region = json.loads(r.text)["region"]["name"]
            if "/" in region:
                bbc, _, itv = region.partition("/")
            else:
                bbc = region
                itv = region
            self.cache["bbc_region"] = bbc
            self.cache["itv_region"] = itv
        except Exception as inst:
            print(type(inst), inst, flush=True)
            return None

        url = f"{_freesat_guide}/api/?post_code={postcode}"
        r = self.fetch.get(url)
        if r.status_code != 200:
            print(f"pc={r.status_code}")
            print(r.text)
            return None
        try:
            channels_data = json.loads(r.text)
        except Exception as inst:
            print(type(inst), inst, flush=True)
            return None

        chans = dict()
        wanted_channels = [
            101,
            102,
            103,
            104,
            105,
            111,
            120,
            700,
            702,
            703,
            704,
            705,
            708,
            711,
            721,
            724,
            731,
        ]
        for c in channels_data:
            if c["lcn"] in wanted_channels:
                if c["lcn"] == 120 and c["channelname"].startswith("S4C"):
                    pass
                else:
                    chans[c["channelname"]] = (
                        c["channelname"],
                        c["channelid"],
                        c["lcn"],
                    )

        tv_channels = []
        for m, p in _tv_mappings:
            hd = None
            sd = None
            for c in chans.keys():
                if type(m) is list:
                    for n in m:
                        if c.upper().startswith(n.upper()):
                            if c.endswith("HD"):
                                hd = chans[c]
                            else:
                                sd = chans[c]
                else:
                    if c.upper().startswith(m.upper()):
                        if c.endswith("HD"):
                            hd = chans[c]
                        else:
                            sd = chans[c]
            if sd:
                tv_channels.append((p, sd))
            elif hd:
                tv_channels.append((p, hd))
            # else:
            #    tv_channels.append(None)

        radio_channels = []
        for m, p in _radio_mappings:
            radio = None
            for c in chans.keys():
                if type(m) is list:
                    for n in m:
                        if c.upper().startswith(n.upper()):
                            radio = chans[c]
                else:
                    if c.upper().startswith(m.upper()):
                        radio = chans[c]

            if radio:
                radio_channels.append((p, radio))
            # else:
            #    radio_channels.append(None)

        self.cache["tv_channels"] = tv_channels
        self.cache["radio_channels"] = radio_channels
        self.cache["postcode"] = postcode

    def get_listings(self):
        last = self.cache["datestamp"]
        now = datetime.datetime.now()
        if last and now - last < datetime.timedelta(hours=4):
            return (self.cache["today"], self.cache["tomorrow"])

        numbers = []
        maps = dict()
        cmap = dict()
        pages = dict()
        for page, c in self.cache["tv_channels"]:
            if c is not None:
                name, chan_id, lcn = c
                maps[chan_id] = lcn
                cmap[lcn] = page
                pages[page] = 1
                numbers.append(chan_id)

        params = dict(channel=numbers)
        for day in [0, 1]:
            url = f"{_freesat_guide}/api/{day}/"
            r = self.fetch.get(url, params=params)
            if r.status_code != 200:
                print(f"day={r.status_code}")
                return None
            try:
                data = json.loads(r.text)
            except Exception as inst:
                print(type(inst), inst, flush=True)
                return None

            events = dict([(i, {}) for i in pages.keys()])
            for channel in data:
                for e in channel["event"]:
                    chan = maps[e["svcId"]]
                    dur = datetime.timedelta(seconds=e["duration"])
                    start = datetime.datetime.fromtimestamp(
                        e["startTime"], datetime.timezone.utc
                    ).astimezone(tz.tzlocal())
                    desc = e["description"]
                    flags = []

                    if "[HD]" in desc:
                        flags.append("HD")
                        desc = desc.replace("[HD]", "").strip()
                    if "Also in HD." in desc:
                        flags.append("HD")
                        desc = desc.replace("Also in HD.", "").strip()

                    while True:
                        m = re.search(r"\[(AD|S|SL|,)+\]\s*", desc)
                        if m:
                            desc = desc.replace(m.group(0), "").strip()
                            for g in m.group(0).split(","):
                                g = (
                                    g.replace("[", "")
                                    .replace("]", "")
                                    .replace(" ", "")
                                )
                                if g == "S":
                                    flags.append("S")
                                elif g == "AD":
                                    flags.append("AD")
                                elif g == "SL":
                                    flags.append("SL")
                        else:
                            break

                    name = e["name"]

                    if name.startswith("New: "):
                        name = name[5:]

                    page = cmap[chan]

                    if chan not in events[page]:
                        events[page][chan] = []

                    events[page][chan].append(
                        dict(
                            name=name,
                            desc=desc,
                            flags=flags,
                            start=start,
                            dur=dur,
                        )
                    )

            if day == 0:
                self.cache["today"] = events
            else:
                self.cache["tomorrow"] = events

        # Radio
        numbers = []
        maps = dict()
        cmap = dict()
        pages = dict()
        for page, c in self.cache["radio_channels"]:
            if c is not None:
                name, chan_id, lcn = c
                maps[chan_id] = lcn
                cmap[lcn] = page
                pages[page] = 1
                numbers.append(chan_id)

        params = dict(channel=numbers)
        url = f"{_freesat_guide}/api/0/"
        r = self.fetch.get(url, params=params)
        if r.status_code != 200:
            print(f"day={r.status_code}")
            return None
        try:
            data = json.loads(r.text)
        except Exception as inst:
            print(type(inst), inst, flush=True)
            return None

        events = dict([(i, {}) for i in pages.keys()])
        for channel in data:
            for e in channel["event"]:
                chan = maps[e["svcId"]]
                dur = datetime.timedelta(seconds=e["duration"])
                start = datetime.datetime.fromtimestamp(
                    e["startTime"], datetime.timezone.utc
                ).astimezone(tz.tzlocal())
                desc = e["description"]
                flags = []
                name = e["name"]
                if name.startswith("New: "):
                    name = name[5:]

                page = cmap[chan]

                if chan not in events[page]:
                    events[page][chan] = []

                events[page][chan].append(
                    dict(
                        name=name,
                        desc=desc,
                        flags=flags,
                        start=start,
                        dur=dur,
                    )
                )

        self.cache["radio"] = events

        self.cache["datestamp"] = now

    @property
    def radio_today(self):
        return self.cache["radio"]

    @property
    def tv_today(self):
        return self.cache["today"]

    @property
    def tv_tomorrow(self):
        return self.cache["tomorrow"]

    @property
    def tv_channels(self):
        r = []
        for page, c in self.cache["tv_channels"]:
            if c:
                r.append((page, c[0].replace("HD", "").strip()))
        return r

    def tv_lcn_to_name(self, lcn):
        name = None
        for page, c in self.cache["tv_channels"]:
            if c[2] == lcn:
                name = c[0].replace("HD", "").strip()
        return name

    def radio_lcn_to_name(self, lcn):
        name = None
        for page, c in self.cache["radio_channels"]:
            if c[2] == lcn:
                name = c[0].replace("FM", "").strip()
        return name

    @property
    def radio_channels(self):
        r = []
        for page, c in self.cache["radio_channels"]:
            if c:
                r.append((page, c[0].replace("FM", "").strip()))
        return r

    @property
    def region(self):
        self.get_channels()
        return (self.cache["bbc_region"], self.cache["itv_region"])


def tv_header(name):
    name = name.upper()
    h = [
        "␖h<,,,,,,||␆````````````````````````````",
    ]
    if "BBC ONE" in name or "BBC 1" in name:
        h += [
            "␖j5k7j5␡ ␡n␓␡{%␡{%␡+%(␡ ␇     ␇",
            "␖j5j5\"m' ␡␡␓␡z5␡z5␡x4`␡0␇     ␇",
        ]
    elif "BBC TWO" in name or "BBC 2" in name:
        h += [
            "␖j5k7j5␡ ␡n␓␡{%␡{%␡+%bs␡␇     ␇",
            "␖j5j5\"m' ␡␡␓␡z5␡z5␡x4jup␇     ␇",
        ]
    elif "ITV" in name:
        h += [
            '␖j5k7j5␡ ␡n␓k7"␡!␡j5    ␇     ␇',
            "␖j5j5\"m' ␡␡␓zu ␡ +?!    ␇     ␇",
        ]
    elif "STV" in name:
        h += [
            '␖j5k7j5␡ ␡n␓~3"␡!␡j5    ␇     ␇',
            "␖j5j5\"m' ␡␡␓r? ␡ +?!    ␇     ␇",
        ]
    elif "UTV" in name:
        h += [
            "␖j5k7j5␡ ␡n␓␡j5k7j5␡    ␇     ␇",
            "␖j5j5\"m' ␡␡␓oz%j5\"o'    ␇     ␇",
        ]
    elif "CHANNEL 4" in name:
        h += [
            "␖j5k7j5␡ ␡n␓␡+%␡p0 ␡h4        ␇",
            "␖j5j5\"m' ␡␡␓␡x4␡j5 #k7        ␇",
        ]
    elif "CHANNEL 5" in name:
        h += [
            "␖j5k7j5␡ ␡n␓␡+%␡p0 ␡s!        ␇",
            "␖j5j5\"m' ␡␡␓␡x4␡j5 lz%        ␇",
        ]
    elif "S4C" in name:
        h += [
            "␖j5k7j5␡ ␡n␓ns!␡j5 ␡#         ␇",
            "␖j5j5\"m' ␡␡␓pz%#k7!␡p         ␇",
        ]

    h.append("␖*-,,,,,,/.␆````````````````````````````")

    return h


def main():
    config.Config().add("defaults.yaml")
    config.Config().add("pm.yaml")
    config.Config().load()

    L = ListingsCache()

    import pdb

    pdb.set_trace()
    print(repr(L.radio_channels))


if __name__ == "__main__":
    main()
