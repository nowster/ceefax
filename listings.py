import ttxcolour
import ttxutils
import ttxpage
import newsreel
import fetch

import datetime
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

_freesat_api = "https://www.freesat.co.uk/tv-guide/api/"

class ListingsCache(object):
    def __init__(self):
        self.fetch = fetch.Fetcher()

        self.cache = dict(
            today=None,
            tomorrow=None,
            channels=None,
            postcode=None,
            datestamp=None,
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

    def get_channels(self):
        L = _config["listings"]
        postcode = L["postcode"]
        postcode = postcode.replace(" ", "")
        if self.cache["postcode"] == postcode:
            channels = self.cache["channels"]
            if channels is not None:
                return channels


        url = f"{_freesat_api}?post_code={postcode}"
        r = self.fetch.get(url)
        if r.status_code != 200:
            print(r.status_code)
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
                    chans[c["channelname"]] = (c["channelname"],c["channelid"])

        mappings = [
            ["BBC One", "BBC 1"],
            ["BBC Two", "BBC 2"],
            "ITV", "Channel 4", "Channel 5", "S4C"
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


def main():
    config.Config().add("defaults.yaml")
    config.Config().add("pm.yaml")
    config.Config().load()

    L = ListingsCache()

    c = L.get_channels()
    import pdb; pdb.set_trace()



if __name__ == "__main__":
    main()
