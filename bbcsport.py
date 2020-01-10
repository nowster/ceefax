import ttxpage
import ttxutils
import ttxcolour
import bbcparse
import fetch
import rss

import textwrap
import AdvancedHTMLParser
import dateutil.parser
import copy
import math
import pickle

import config
_config=config.Config().config


def leagues():
    league_tables = _config['football_league_tables']
    try:
        with open(f"{_config['cachedir']}/league.cache", 'rb') as f:
            cache = pickle.load(f)
    except:
        cache = dict()

    for num, url in league_tables:
        league(num, url, cache)

        with open(f"{_config['cachedir']}/league.cache", 'wb') as f:
            pickle.dump(cache, f)


def league(pagenum, url, cache):
    nextpage = ttxutils.nextpage(pagenum)
    page = ttxpage.TeletextPage("Football League Table",
                                pagenum)

    league, date, table = league_table(url, cache)

    league = league.upper().replace(" TABLE", "")
    datefmt = date.strftime("%b %d %H:%M")

    subpage = 1
    footers = [
        "€ANext page  €BFootball €CHeadlines €FSport"
    ]

    count = 0
    for r in table:
        count += 1
        if r[8]:
            count += 1

    pages = math.ceil(count / 14)

    newpage = True
    white = True
    row = 1
    pagecount = 0
    for r in table:
        if newpage:
            pagecount += 1
            page.header(pagenum, subpage)
            sport_header(page, 'Football')
            if pages > 1:
                index = f"{ttxcolour.white()}{pagecount}/{pages}"
            else:
                index = ''

            page.addline(4, f"{ttxcolour.green()}{league:<33} {index}")
            page.addline(6, f"{ttxcolour.white()}{datefmt}     P  W  D  L   F   A Pts")
            line = 8
            newpage = False

        if white:
            colour = ttxcolour.white()
        else:
            colour = ttxcolour.cyan()
        white = not white
        team = r[0]
        team = team.replace("Crystal Palace", "C Palace")
        team = team.replace("Huddersfield", "H'field")
        team = team[:12]

        p = f"{r[1]:>2}"
        w = f"{r[2]:>2}"
        d = f"{r[3]:>2}"
        l = f"{r[4]:>2}"
        f = f"{r[5]:>3}"
        a = f"{r[6]:>3}"
        pts = f"{r[7]:>3}"
        brk = r[8]

        page.addline(line, f"{row:>3} {team:<12} {p} {w} {d} {l} {f} {a} {pts}")
        row += 1
        line += 1
        if brk and line < 21:
            page.addline(line,
                         "{}---------------------------------------".format(
                             ttxcolour.red()))
            line += 1

        if line > 21:
            subpage += 1
            newpage = True
            line = 24
            for l in footers:
                page.addline(line, ttxutils.decode(l))
                line += 1
                page.addfasttext(nextpage, 0x302, 0x301, 0x300, 0x8ff, 0x320)

    if not newpage:
        line = 24
        for l in footers:
            page.addline(line, ttxutils.decode(l))
            line += 1
            page.addfasttext(nextpage, 0x302, 0x301, 0x300, 0x8ff, 0x320)
    page.save()


def league_table(url, cache):
    if url in cache:
        entry = cache[url]
        headers = { 'If-None-Match': f"{entry['etag']}" }
    else:
        entry = None
        headers = None

    f = fetch.Fetcher()
    resp = f.get(url, headers=headers)
    if resp.status_code == 304:
        return entry['value']
    if resp.status_code != 200:
        print(r.status_code)
        return None
    if entry and resp.headers.get('etag') == entry['etag']:
        return entry['value']

    parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
    parser.parseStr(resp.text)
    tables = parser.getElementsByTagName('table')
    rows = tables[0].getAllChildNodes().getElementsByTagName('tr')
    table = []
    for row in rows[1:-1]:
        data = row.getAllChildNodes().getElementsByTagName('td')
        r = []
        for d in [ 2,3,4,5,6,7,8,10 ]:
            r.append(data[d].textContent)
        r.append(row.attributes['class'] == "gs-o-table__row--break")
        table.append(r)
    time = parser.getElementsByTagName('time')
    time = dateutil.parser.isoparse(time[0].attributes['datetime'])
    league = parser.getElementsByTagName('h1')
    league = league[0].textContent


    value = (league, time, table)
    cache[url] = dict(
        value=value,
        etag=resp.headers.get('etag')
    )

    return value


def is_football(section):
    return section in [
        "Football", "Bury", "Premier League", "African",
        "La Liga", "Rangers", "Tottenham", "League Cup",
        "Wales", "Republic of Ireland", "European Football",
        "England", "Celtic", "Man Utd", "Sunderland",
        "Barnsley", "Crystal Palace", "Scotland",
        "Women's Football", "Norwich", "Champions League",
        "Liverpool", "Arsenal", "Chelsea", "Southend",
        "Championship", "Man City", "Cardiff", "Scottish",
    ]


def sport_header(page, section):
    if is_football(section):
        header = [
            "€Wj#3kj#3kj#3k€T€]€R h<h<|h<|(|$|l4|l4| |",
            "€Wj $kj $kj 'k€T€]€R j7ju¬ju¬ ¬ ¬{4¬k5¬0¬0",
            '€W"###"###"###€T///-.-,,-,,/,/,,.,-.,.,.//',
        ]
    elif section in [ 'Formula 1', 'formula1' ]:
        header = [
            "€Wj#3kj#3kj#3k€T€]€Rh,hlhl <<4444hl hlhlh$  ",
            "€Wj $kj $kj 'k€T€]€Rj#jzj#5555u5ujk jzjjj1  ",
            '€W"###"###"###€T//-/-,-/....,.,--/-,---.//'
        ]
    elif section in [ 'Cricket' ]:
        header = [
            '€Wj#3kj#3kj#3k€T€]€R  |,h<|h4|,h4|h<(|$',
            "€Wj $kj $kj 'k€T€]€R  ¬pj7}j5¬pj7}jw ¬",
            '€W"###"###"###€T////,,-,,-.,,-.,-,/,///////'
        ]
    elif section in ['Rugby Union']:
        header = [
            '€Wj#3kj#3kj#3k€T€]€R    hl 44<,hl 44',
            "€Wj $kj $kj 'k€T€]€R    j#5u5u{js5s5",
            '€W"###"###"###€T//////-/.,.,,-,.,.////////'
        ]
    else:
        header = [
            "€Wj#3kj#3kj#3k€T€]€R   h<,h<|h<|h<|(|$      ",
            "€Wj $kj $kj 'k€T€]€R   bs¬j7#ju¬j7} ¬       ",
            '€W"###"###"###€T/////-,,-./-,,-.,/,///////'
        ]

    line = 1
    for l in header:
        page.addline(line, ttxutils.decode(l))
        line += 1

def sport_footer(page, section):
    nextpage = ttxutils.nextpage(page.page)
    if nextpage == 0x316:
        nextpage = 0x324
    if is_football(section):
        footer = [
            "€D€]€CCEEFAX FOOTBALL SECTION PAGE 302",
            "€D€]€CBBC WEBSITE: bbc.co.uk/football",
            "€ANext page  €BFootball €CHeadlines €FSport",
        ]
        pages = _config['pages']['sport']['football']
        index = pages['index']
    elif section in [ 'Formula 1', 'formula1' ]:
        footer = [
            "€D€]€CCEEFAX MOTORSPORT SECTION PAGE 360   ",
            "€D€]€CBBC WEBSITE: bbc.co.uk/motorsport    ",
            "€ANext page  €BM/sport  €CHeadlines €FSport ",
        ]
        pages = _config['pages']['sport']['formula1']
        index = pages['index']
    elif section in [ 'Cricket' ]:
        footer= [
            "€D€]€CCEEFAX CRICKET SECTION PAGE 340   ",
            "€D€]€CBBC WEBSITE: bbc.co.uk/cricket    ",
            "€ANext page  €BCricket €CHeadlines €FSport ",
        ]
        pages = _config['pages']['sport']['cricket']
        index = pages['index']
    elif section in [ 'Rugby Union' ]:
        footer= [
            "€D€]€CCEEFAX RUGBY SECTION PAGE 370   ",
            "€D€]€CBBC WEBSITE: bbc.co.uk/rugby    ",
            "€ANext page  €BRugby U €CHeadlines €FSport ",
        ]
        pages = _config['pages']['sport']['rugby_union']
        index = pages['index']
    else:
        footer = [
            "€D€]€CCEEFAX SPORT SECTION PAGE 300",
            "€D€]€CBBC WEBSITE: bbc.co.uk/sport",
            "€ANext page  €BFootball €CHeadlines €FSport",
        ]
        pages = _config['pages']['sport']['football']
        index = pages['index']

    line = 22
    for l in footer:
        page.addline(line, ttxutils.decode(l))
        line += 1
    page.addfasttext(nextpage, index, 0x301, 0x300, 0x8FF, 0x199)

def sport_page(number, contents):
    url = contents['link']
    page = ttxpage.TeletextPage("Sport Page {:03x} {}".format(number, url),
                                number)
    page.header(number)
    sport_header(page, contents['section'])
    line = 4
    title = contents['title'].replace(" - BBC Sport", "")

    line += page.wrapline(line, 21,
                          page.fixup(title),
                          ttxcolour.green())
    colour = ' '
    for para in contents['text']:
        if line <= 21:
            line += page.wrapline(line, 22, page.fixup(para), colour) + 1
            colour = ttxcolour.cyan()
    sport_footer(page, contents['section'])
    page.save()

def football():
    pages = _config['pages']['sport']['football']
    footballfeed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'football')
    entries = footballfeed.get_entries(sport=True,
                                       max = ttxutils.hexdiff(
                                           pages['last'], pages['first']))

    pagenum = pages['first']
    footentries = list()
    for contents in entries:
        if '/football/' in contents['link']:
            contents['section'] = 'Football'
            footentries.append(contents)

    for contents in footentries:
        sport_page(pagenum, contents)
        pagenum = ttxutils.nextpage(pagenum)
        if pagenum > pages['last']:
            break

    football_index(footentries)

    # league tables go here
    leagues()

    return [footentries[0], pages['first']]


def sport_index(sport, pages, header, footer, entries, increment=1):
    index = pages['index']
    page = ttxpage.TeletextPage(
        f"{sport} Index {index:03x}",
        index)
    page.header(index)
    line = 1
    for l in header:
        page.addline(line, ttxutils.decode(l))
        line += 1

    colour = ttxcolour.colour(ttxcolour.DOUBLE_HEIGHT)
    number = pages['first']
    index = 0
    for contents in entries:
        if increment == 1:
            if index in [ 1, 6, 10 ]:
                line += 1
        elif index == 1:
            line += 1
        title = contents['short_title']
        l, _, r = title.partition(': ')
        if r:
            title = r
        title = page.truncate(title, 35, ' ')
        page.addline(line,
                     f"{colour}{title:<35}{ttxcolour.white()}{number:03x}")
        colour = ttxcolour.cyan()
        line += increment
        index += 1
        number = ttxutils.nextpage(number)
        if number > pages['last']:
            break
    line = 22
    for l in footer:
        page.addline(line, ttxutils.decode(l))
        line += 1
    page.addfasttext(pages['first'], 0x300, 0x301, 0x300, 0x8ff, 0x199)
    page.save()


def football_index(entries):
    pages = _config['pages']['sport']['football']
    header = [
        "€Wj#3kj#3kj#3k€T€]€R h<h<|h<|(|$|l4|l4| |",
        "€Wj $kj $kj 'k€T€]€R j7ju¬ju¬ ¬ ¬{4¬k5¬0¬0",
        '€W"###"###"###€T///-.-,,-,,/,/,,.,-.,.,.//'
    ]
    footer = [
        "€D€]€CRESULTS AND FIXTURES SECTION€G339 ",
        "€D€]€CBBC WEBSITE: bbc.co.uk/football",
        "€ATop story  €BRegional €CHeadlines €FSport",
    ]
    sport_index("Football", pages, header, footer, entries)

def formula1():
    pages = _config['pages']['sport']['formula1']
    f1feed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'formula1')
    entries = f1feed.get_entries(sport=True,
                                 max = ttxutils.hexdiff(
                                     pages['last'], pages['first']))

    pagenum = pages['first']
    f1entries = list()
    for contents in entries:
        if '/formula1/' in contents['link']:
            contents['section'] = 'Formula 1'
            f1entries.append(contents)

    for contents in f1entries:
        sport_page(pagenum, contents)
        pagenum = ttxutils.nextpage(pagenum)
        if pagenum > pages['last']:
            break

    f1_index(f1entries)

    return [f1entries[0], pages['first']]

def f1_index(entries):
    pages = _config['pages']['sport']['formula1']
    header = [
        "€Wj#3kj#3kj#3k€T€]€Rh,hlhl <<4444hl hlhlh$  ",
        "€Wj $kj $kj 'k€T€]€Rj#jzj#5555u5ujk jzjjj1  ",
        '€W"###"###"###€T//-/-,-/....,.,--/-,---.//'
    ]
    footer= [
        "€D€]€CCEEFAX MOTORSPORT SECTION PAGE 360   ",
        "€D€]€CBBC WEBSITE: bbc.co.uk/motorsport    ",
        "€ANext page  €BM/sport  €CHeadlines €FSport ",
    ]
    sport_index("Football", pages, header, footer, entries, increment=2)


def cricket():
    pages = _config['pages']['sport']['cricket']
    feed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'cricket')
    raw_entries = feed.get_entries(sport=True,
                                   max = ttxutils.hexdiff(
                                       pages['last'], pages['first']))

    pagenum = pages['first']
    entries = list()
    for contents in raw_entries:
        if '/cricket/' in contents['link']:
            contents['section'] = 'Cricket'
            entries.append(contents)

    for contents in entries:
        sport_page(pagenum, contents)
        pagenum = ttxutils.nextpage(pagenum)
        if pagenum > pages['last']:
            break

    cricket_index(entries)

    return [entries[0], pages['first']]

def cricket_index(entries):
    pages = _config['pages']['sport']['cricket']
    header = [
        '€Wj#3kj#3kj#3k€T€]€R  |,h<|h4|,h4|h<(|$',
        "€Wj $kj $kj 'k€T€]€R  ¬pj7}j5¬pj7}jw ¬",
        '€W"###"###"###€T////,,-,,-.,,-.,-,/,///////'
    ]
    footer= [
        "€D€]€CCEEFAX CRICKET SECTION PAGE 340   ",
        "€D€]€CBBC WEBSITE: bbc.co.uk/cricket    ",
        "€ANext page  €BCricket €CHeadlines €FSport ",
    ]
    sport_index("Cricket", pages, header, footer, entries, increment=2)


def rugby_union():
    pages = _config['pages']['sport']['rugby_union']
    feed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'rugby_union')
    raw_entries = feed.get_entries(sport=True,
                                   max = ttxutils.hexdiff(
                                       pages['last'], pages['first']))

    pagenum = pages['first']
    entries = list()
    for contents in raw_entries:
        if '/rugby-union/' in contents['link']:
            contents['section'] = 'Rugby Union'
            entries.append(contents)

    for contents in entries:
        sport_page(pagenum, contents)
        pagenum = ttxutils.nextpage(pagenum)
        if pagenum > pages['last']:
            break

    rugby_union_index(entries)

    return [entries[0], pages['first']]

def rugby_union_index(entries):
    pages = _config['pages']['sport']['rugby_union']
    header = [
        '€Wj#3kj#3kj#3k€T€]€R    hl 44<,hl 44',
        "€Wj $kj $kj 'k€T€]€R    j#5u5u{js5s5",
        '€W"###"###"###€T//////-/.,.,,-,.,.////////'
    ]
    footer= [
        "€D€]€CCEEFAX RUGBY SECTION PAGE 370   ",
        "€D€]€CBBC WEBSITE: bbc.co.uk/rugby    ",
        "€ANext page  €BRugby U €CHeadlines €FSport ",
    ]
    sport_index("Rugby", pages, header, footer, entries, increment=2)


def makesport():
    topfoot = copy.deepcopy(football())
    topfoot[0]['section'] = "Football"

    return [
        topfoot,
        formula1(),
        cricket(),
        rugby_union()
    ]
