#!/usr/bin/python3

import ttxpage
import ttxcolour
import ttxutils
import bbcnews
import bbcsport
import fetch

import os
import time


import pprint
pp = pprint.PrettyPrinter(indent=4)


def makefrontpage(headlines):
    page = ttxpage.TeletextPage("Service Front Page", 0x100, time=8)

    subpage = 1
    for h in headlines:
        page.header(0x100, subpage)
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

        page.addfasttext(0x101, 0x300, 0x600, 0x199, 0x8ff, 0x199)
        page.save()

def main():

    for d in ['/ram/pages', '/ram/cache']:
        os.makedirs(d, mode=0o755, exist_ok=True)

    while True:
        start = time.time()
        headlines = []
        headlines.extend(bbcnews.makenews())
        headlines.extend(bbcsport.makesport())

        makefrontpage(headlines)
        end = time.time()
        print(f"Sleeping (run was {end - start:.2f}s)", flush=True)
        time.sleep(60)


if __name__ == "__main__":
    main()
