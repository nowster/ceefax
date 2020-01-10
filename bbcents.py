import ttxpage
import ttxutils
import ttxcolour
import bbcparse
import fetch
import rss

import config
_config=config.Config().config

def entertainment():
    pages = _config['pages']['entertainment']
    feed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'football')
    entries = feed.get_entries(
        max = ttxutils.hexdiff(pages['last'], pages['first']))

    header = [
        "€C€]€U|$xl0l<h<h<t(|$|l4|`<t`<<th<`<t(|$",
        "€C€]€U¬1¬j5j5jwj7} ¬ ¬k5¬j5¬j55¬jwj5¬ ¬",
        "€S#######################################"
    ]
    footer = [
        "€C€]€DTV    520  Lottery   555  Music 530",
        "€C€]€DFilms 540  Newsround 570  Games 550",
        "€ANext News€B FilmIndex€CTV Index€FEntsIndex",
    ]
    fastext = [ 0x540, 0x520, 0x500 ]
    pagenum = pages['first']

    for contents in entries:
        nextpage = ttxutils.nextpage(pagenum)
        if nextpage > pages['last']:
            nextpage = pages['index']
        ttxutils.news_page("Entertainment", pages,
                           pagenum, contents, header, footer,
                           fasttext=[nextpage, 0x540, 0x520, 0x500])
        pagenum = ttxutils.nextpage(pagenum)
        if pagenum > pages['last']:
            break

    entertainment_index(pages, entries)

    return (entries[0], pages['first'])


def entertainment_index(pages, entries):
    header = [
        "€C€]€U|$xl0l<h<h<t(|$|l4|`<t`<<th<`<t(|$",
        "€C€]€U¬1¬j5j5jwj7} ¬ ¬k5¬j5¬j55¬jwj5¬ ¬",
        "€S#######################################"
    ]
    footer = [
        "€C€]€DTV    520  Lottery   555  Music 530",
        "€C€]€DFilms 540  Newsround 570  Games 550",
        "€ANext News€BMusicInde€CNewsround€FEntsIndex"
    ]
    ttxutils.index_page("Entertainment", pages, header, footer, entries,
                        fasttext=[pages['first'], 0x502, 0x530, 0x500],
                        increment=1, rule=6,
                        number_colour=ttxcolour.yellow())

def makeentertainment():
    return [ entertainment() ]
