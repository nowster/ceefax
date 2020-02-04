#!/usr/bin/python3

import ttxpage
import ttxcolour
import ttxutils
import bbcnews
import bbcsport
import bbcents
import weather
import fetch

import os
import time
import argparse

import config
_config=config.Config().config

def makefrontpage(headlines):
    page = ttxpage.TeletextPage("Service Front Page", 0x100, time=8)

    subpage = 1
    for h in headlines:
        if h is None:
            continue
        page.header(0x100, subpage, status=0xc000)
        # pp.pprint(h)
        entry, pagenum = h
        title = entry['short_title'].upper()
        title = page.truncate(title, 35, ' ')

        lines = [
            '€W`ppp`ppp`ppp€T||,,,<,,<,,<,,|,,,|,l<,|||',
            '€Wj $zj $zj tz€T€]€S¬7#j¬sj¬sj¬sh¬s¬4ouz?€T¬',
            "€Wj %jj %jj 'k€T€]€S¬upj¬pj¬pj¬ j¬ ¬5¬5j¬€T¬",
            '€W"###"###"###€T##########################',
            f"€C{entry['section']}",
            f"€M{title:<35}€C{pagenum:03x}",
            '',
            '€D```````````````````````````````````````',
            '€CA-Z INDEX     €G199€CNEWS HEADLINES  €G101',
            '€CBBC INFO      €G695€CNEWS FOR REGION €G160',
            "€CCHESS         €G568€CNEWSROUND       €G570",
            "€CCOMMUNITY€GBBC2€G650€CRADIO      €GBBC1€G640",
            "€CENTERTAINMENT €G500€CREAD HEAR  €GBBC2€G640",
            "€C                                       ",
            "€CFILM REVIEWS  €G526€CSPORT           €G300",
            "€CFINANCE€G  BBC2€G200€CSUBTITLING      €G888",
            "€CFLIGHTS       €G440€CTOP 40          €G528",
            "€CGAMES REVIEWS €G527€CTRAVEL          €G430",
            "€CHORSERACING   €G660€CTV LINKS        €G615",
            "€CLOTTERY       €G555€CTV LISTINGS     €G600",
            "€CSCI-TECH      €G154€CWEATHER         €G400",
            "€C                                       ",
            "€D€]€CCeefax: The world at your fingertips ",
            "€AHeadlines  €BSport €CLocal TV €FA-Z Index "
        ]
        line = 1
        for l in lines:
            page.addline(line, ttxutils.decode(l))
            line += 1
        subpage += 1

        page.addfasttext(0x101, 0x300, 0x600, 0x199, 0x8ff, 0x199)
        page.save()

def nms_extras(headlines):
    nms = _config['nms']
    if 'headlines_file' in nms:
        with open(nms['headlines_file'], 'w') as f:
            for h in headlines:
                story, pagenum = h
                print(story['section'], "\t",
                      story['short_title'],
                      f"\t{pagenum:03x}",
                      file=f)

def main():
    parser = argparse.ArgumentParser(description = "Make CEEFAX like pages")
    parser.add_argument('-e', '--every', metavar='N', type=int,
                        help = "Run every N seconds")
    parser.add_argument('-c', '--config', metavar='F', action='append',
                        help = "Config files")

    args = parser.parse_args()

    if args.config:
        for c in args.config:
            config.Config().add(c)
    else:
        config.Config().add() # default
    config.Config().load()

    for d in [_config['pagesdir'], _config['cachedir']]:
        os.makedirs(d, mode=0o755, exist_ok=True)

    while True:
        start = time.time()
        headlines = []
        headlines.extend(bbcnews.makenews())
        headlines.extend(bbcsport.makesport())
        headlines.extend(bbcents.makeentertainment())
        headlines.extend(weather.makeweather())

        makefrontpage(headlines)
        if 'nms' in _config:
            nms_extras(headlines)

        end = time.time()
        if args.every:
            print(f"Sleeping (run was {end - start:.2f}s)", flush=True)
            time.sleep(args.every)
        else:
            break

if __name__ == "__main__":
    main()
