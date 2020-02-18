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


class ListingsCache(object):
    def __init__(self):
        self.fetch = fetch.Fetcher()
        self.csrf = None

        self.cache = dict(
            today=None,
            tomorrow=None,
            channels=None,
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
            channels = self.cache["channels"]
            if channels is not None:
                return channels

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
        wanted_channels = [101, 102, 103, 104, 105, 111, 120]
        for c in channels_data:
            if c["lcn"] in wanted_channels:
                if c["lcn"] == 120 and c["channelname"].startswith("S4C"):
                    pass
                else:
                    chans[c["channelname"]] = (
                        c["channelname"],
                        c["channelid"],
                    )

        mappings = [
            ["BBC One", "BBC 1"],
            ["BBC Two", "BBC 2"],
            "ITV",
            "Channel 4",
            "Channel 5",
            "S4C",
        ]

        channels = []
        for m in mappings:
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
                channels.append(sd)
            elif hd:
                channels.append(hd)
            else:
                channels.append(None)

        self.cache["channels"] = channels
        self.cache["postcode"] = postcode
        return channels

    def get_listings(self):
        last = self.cache["datestamp"]
        now = datetime.datetime.now()
        if last and now - last < datetime.timedelta(hours=4):
            return (self.cache["today"], self.cache["tomorrow"])

        numbers = []
        maps = dict()
        i = 0
        for c in self.cache["channels"]:
            if c is not None:
                name, chan_id = c
                maps[chan_id] = i
                numbers.append(chan_id)
                i += 1

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

            events = dict([(i, []) for i in range(len(numbers))])
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

                    events[chan].append(
                        dict(
                            name=name,
                            desc=desc,
                            flags=flags,
                            start=start,
                            dur=dur,
                        )
                    )

            import pprint

            pprint.pprint(events)
            return


def main():
    config.Config().add("defaults.yaml")
    config.Config().add("pm.yaml")
    config.Config().load()

    L = ListingsCache()

    c = L.get_channels()

    L.get_listings()


#    import pdb
#    pdb.set_trace()


if __name__ == "__main__":
    main()
