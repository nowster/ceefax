import ttxpage
import ttxutils
import ttxcolour
import bbcparse
import fetch
import rss

import datetime
import textwrap
import AdvancedHTMLParser # type: ignore
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
    if len(table) == 12:
        pages = 1

    newpage = True
    white = True
    row = 1
    pagecount = 0
    status = 0x8000
    if pages > 1:
        status = 0xc000
    for r in table:
        if newpage:
            pagecount += 1
            page.header(pagenum, subpage, status=status)
            sport_header(page, 'Football')
            if pages > 1:
                index = f"{ttxcolour.white()}{pagecount}/{pages}"
            else:
                index = ''

            page.addline(4, f"{ttxcolour.green()} {league:<32} {index}")
            page.addline(6, f"{ttxcolour.white()} {datefmt}    P  W  D  L   F   A Pts")
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

        page.addline(line, f"{colour}{row:>2} {team:<12} {p} {w} {d} {l} {f} {a} {pts}")
        row += 1
        line += 1
        if brk and line < 21:
            page.addline(line,
                         "{}```````````````````````````````````````".format(
                             ttxcolour.red()))
            line += 1

        if (line > 21 and len(table)>12) or (line > 22):
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
        headers = { 'If-None-Match': entry['etag'] }
    else:
        entry = None
        headers = None

    f = fetch.Fetcher()
    resp = f.get(url, headers=headers)
    if resp.status_code == 304:
        return entry['value']
    if resp.status_code != 200:
        print(resp.status_code)
        return None
    if entry and resp.headers.get('etag') == entry['etag']:
        return entry['value']
    print(f"Cache miss {url}", flush=True)

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

def fixtures():
    try:
        with open(f"{_config['cachedir']}/fixtures.cache", 'rb') as f:
            cache = pickle.load(f)
    except:
        cache = dict()

    for page, offset, label in _config['football_fixtures']:
        day = datetime.date.today() + datetime.timedelta(days=offset)
        if not label:
            label = day.strftime("%A")
        fixture_page(page, day, f"{label.upper()}'S FIXTURES", cache)

    with open(f"{_config['cachedir']}/fixtures.cache", 'wb') as f:
        pickle.dump(cache, f)


def fixture_page(pagenum, date, dayname, cache):
    nextpage = ttxutils.nextpage(pagenum)
    page = ttxpage.TeletextPage("Football Fixtures",
                                pagenum)

    maxrows = 18
    isodate = date.isoformat()
    url = f"{_config['football_fixtures_url']}/{isodate}"
    fixes = fixtures_table(url, cache)
    pages = []
    header = f"{ttxcolour.green()}{dayname}"
    p = [header]
    for f in fixes:
        rows = []
        r = f"{ttxcolour.white()}{page.fixup(f['league']).upper()}"
        if f['round_']:
            r += f"{ttxcolour.magenta()}{page.fixup(f['round_'])}"
        rows.append(f"{r:<38}")
        for m in f['matches']:
            home_team = page.fixup(m['home_team'])[:13]
            away_team = page.fixup(m['away_team'])[:13]
            r = f"{ttxcolour.cyan()}{home_team:<13}"
            if m['kickoff']:
                r += f"{ttxcolour.white()}{'v':^5}"
            else:
                r += f"{ttxcolour.white()}{m['home_goals']:>2}"
                r += f"-{m['away_goals']:<2}"
            r += f"{ttxcolour.cyan()}{away_team:<13}"
            if m['kickoff']:
                r += f"{ttxcolour.green()}{page.fixup(m['kickoff']):>5}"
            elif m['status']:
                status = page.fixup(m['status'])[:5]
                r += f"{ttxcolour.yellow()}{status:>5}"
            rows.append(r)
        if ((len(p) + len(rows) <  maxrows)
            or (len(p) == 0 and len(rows) == maxrows)):
            if len(p)>1:
                p.append('')
            p.extend(rows)
        else:
            pages.append(p)
            p = [header]
            p.extend(rows)
    if len(fixes) == 0:
        p.append('')
        p.append(f'{ttxcolour.cyan()}No matches today.')
    pages.append(p)

    subpage = 0
    for p in pages:
        if len(pages) > 1:
            subpage += 1
            page.header(pagenum, subpage, status=0xc000)
        else:
            page.header(pagenum, subpage, status=0x8000)
        sport_header(page, 'Football')
        if len(pages) > 1:
            index = f"{subpage}/{len(pages)}"
            p[0] = f"{p[0]:<34}{ttxcolour.white()}{index:>5}"
        line = 4
        for r in p:
            if len(r):
                page.addline(line, r)
            line += 1
        sport_footer(page, 'Football')

    page.save()


def _get_span(nodes, class_name, tag_name=None, index=0,
              sub_class=None, as_list=False):
    values = nodes.getElementsByClassName(class_name)
    if tag_name:
        values = values.getElementsByTagName(tag_name)
    if sub_class:
        values = values.getElementsByClassName(sub_class)
    if not values:
        return None
    elif as_list:
        return [v.textContent for v in values]
    elif len(values) > index:
        return values[index].textContent
    else:
        return None

def fixtures_table(url, cache):
    if url in cache:
        entry = cache[url]
        headers = { 'If-None-Match': entry['etag'] }
    else:
        entry = None
        headers = None

    f = fetch.Fetcher()
    resp = f.get(url, headers=headers)
    if resp.status_code == 304:
        return entry['value']
    if resp.status_code != 200:
        print(f"{resp.status_code} on {url}")
        return None
    if entry and resp.headers.get('etag') == entry['etag']:
        return entry['value']
    print(f"Cache miss {url}", flush=True)

    parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
    parser.parseStr(resp.text)
    divs = parser.getElementsByClassName('qa-match-block')
    table = []
    for div_row in divs:
        children = div_row.getAllChildNodes()
        league = children.getElementsByTagName('h3')
        league = league[0].textContent.upper()
        if league not in _config['football_fixture_leagues']:
            continue
        round_ = children.getElementsByTagName('h4')
        if len(round_):
            round_ = round_[0].textContent
        else:
            round_ = None
        block = []
        matches = children.getElementsByTagName('ul')
        matches = matches[0].getAllChildNodes().getElementsByTagName('li')
        for match in matches:
            nodes = match.getAllChildNodes()
            home_team = _get_span(nodes, 'sp-c-fixture__team-name-trunc',
                                  'abbr',0)
            away_team = _get_span(nodes, 'sp-c-fixture__team-name-trunc',
                                  'abbr',1)
            home_goals = _get_span(nodes, 'sp-c-fixture__number--home')
            away_goals = _get_span(nodes, 'sp-c-fixture__number--away')
            status = _get_span(nodes, 'sp-c-fixture__aside')
            if not status:
                status = _get_span(nodes, 'sp-c-fixture__status')
            if status:
                status = status.replace("Match postponed -","")
                status = status.replace(" mins", "min")
                status = status.replace(' ','')
            kickoff = _get_span(nodes, 'sp-c-fixture__number--time')
            block.append(dict(
                home_team=home_team,
                away_team=away_team,
                home_goals=home_goals,
                away_goals=away_goals,
                status=status,
                kickoff=kickoff,
            ))

        table.append(dict(
            league=league,
            round_=round_,
            matches=block,
        ))

    cache[url] = dict(
        value=table,
        etag=resp.headers.get('etag')
    )

    return table


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
            '€W"###"###"###€T////,,-.,-.,,-.,-,/,///////'
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

def football_gossip_entries(url, cache):
    seen = []
    if url in cache:
        entry = cache[url]
        etag = entry['etag']
        if 'seen' in entry:
            seen = entry['seen']
        headers = { 'If-None-Match': entry['etag'] }
    else:
        etag = None
        entry = None
        headers = None

    f = fetch.Fetcher()

    # "seen" works around the CDN sending different etags occasionally
    resp = f.head(url, headers=headers)
    if resp.status_code == 304:
        return entry['value']
    if resp.status_code == 200:
        newetag = resp.headers.get('etag')
        if newetag in seen:
            cache[url]['etag'] = newetag
            return entry['value']

    resp = f.get(url, headers=headers)
    if resp.status_code == 304:
        return entry['value']
    if resp.status_code != 200:
        print(f"{resp.status_code} on {url}")
        return None
    if entry and (resp.headers.get('etag') == etag):
        return entry['value']
    print(f"Cache miss {url}", flush=True)
    seen.append(resp.headers.get('etag'))
    seen = seen[-10:]

    parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
    parser.parseStr(resp.content.decode("utf-8"))

    paragraphs = []
    div = parser.getElementById('story-body')
    children = div.getAllChildNodes().getElementsByTagName('p')
    for p in children:
        head = ""
        line = ""
        tail = ""
        first = True
        for c in p.childBlocks:
            if type(c) is str:
                if c:
                    if first:
                        head += c
                    else:
                        line += c
            else:
                if (c.nodeName == 'b' and first):
                    head += c.textContent
                    first = False
                elif c.nodeName == 'a':
                    tail = c.textContent
                else:
                    line += c.textContent

        line = line.replace('  ', ' ').strip()
        line = line.replace('()','').strip()
        while line.endswith('(') or line.endswith(')'):
            line = line[:-1]
        head = head.replace('  ', ' ').strip()
        tail = tail.replace('(','')
        tail = tail.replace(')','').strip()
        tail = f"({tail})"
        if head and line and tail:
            paragraphs.append((head, line, tail))

    cache[url] = dict(
        value=paragraphs,
        etag=resp.headers.get('etag'),
        seen=seen
    )
    return paragraphs

def football_gossip_page(pagenum, entries):
    nextpage = ttxutils.nextpage(pagenum)
    page = ttxpage.TeletextPage("Football Gossip",
                                pagenum)

    maxrows = 18
    pages = []
    header = f"{ttxcolour.green()}Gossip column"
    p = [header]
    for f in entries:
        h, l, t = f
        h = page.fixup(h)
        l = page.fixup(l)
        t = page.fixup(t)
        lines = textwrap.wrap(f"{h}¬\t{l}",39,
                              expand_tabs=False, replace_whitespace=False)
        rows = []
        colour = ttxcolour.white()
        for ll in lines:
            if '\t' in ll or '¬' in ll:
                ll = ll.replace('¬', '\t')
                ll = ll.replace('\t\t', '\t')
                ll = ll.replace('\t', ttxcolour.cyan())
                rows.append(f"{colour}{ll}")
                colour = ttxcolour.cyan()
            else:
                rows.append(f"{colour}{ll}")
        if len(rows[-1]) + len(t) > 40:
            rows.append(f"{ttxcolour.green()}{t:>39}")
        else:
            rows[-1] += f"{ttxcolour.green()}{t}"
        if ((len(p) + len(rows) <  maxrows)
            or (len(p) == 0 and len(rows) == maxrows)):
            if len(p)>1:
                p.append('')
            p.extend(rows)
        else:
            pages.append(p)
            p = [header]
            p.extend(rows)
    pages.append(p)

    subpage = 0
    for p in pages:
        if len(pages) > 1:
            subpage += 1
            page.header(pagenum, subpage, status=0xc000)
        else:
            page.header(pagenum, subpage, status=0x8000)
        sport_header(page, 'Football')
        if len(pages) > 1:
            index = f"{subpage}/{len(pages)}"
            p[0] = f"{p[0]:<34}{ttxcolour.white()}{index:>5}"
        line = 4
        for r in p:
            if len(r):
                page.addline(line, r)
            line += 1
        sport_footer(page, 'Football')

    page.save()


def football_gossip():
    try:
        with open(f"{_config['cachedir']}/footballgoss.cache", 'rb') as f:
            cache = pickle.load(f)
    except:
        cache = dict()

    pages = _config['pages']['sport']['football']['gossip']
    pagenum = pages['page']
    url = pages['url']

    football_gossip_page(pagenum, football_gossip_entries(url, cache))

    with open(f"{_config['cachedir']}/footballgoss.cache", 'wb') as f:
        pickle.dump(cache, f)


def football():
    pages = _config['pages']['sport']['football']
    footballfeed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'football')
    entries = footballfeed.get_entries(sport=True,
                                       max = ttxutils.hexdiff(
                                           pages['last'], pages['first']))
    if not entries:
        return None

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
    fixtures()
    football_gossip()

    return [footentries[0], pages['first']]


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
    ttxutils.index_page("Football", pages, header, footer, entries,
                        fasttext=[0x300, 0x301, 0x300])

def formula1():
    pages = _config['pages']['sport']['formula1']
    f1feed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'formula1')
    entries = f1feed.get_entries(sport=True,
                                 max = ttxutils.hexdiff(
                                     pages['last'], pages['first']))

    if not entries:
        return None
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
    ttxutils.index_page("Formula 1", pages, header, footer, entries,
                        fasttext=[pages['first'], 0x300, 0x301, 0x300],
                        increment=2)

def cricket_fixtures_table(url, cache):
    if url in cache:
        entry = cache[url]
        headers = { 'If-None-Match': entry['etag'] }
    else:
        entry = None
        headers = None

    f = fetch.Fetcher()
    resp = f.get(url, headers=headers)
    if resp.status_code == 304:
        return entry['value']
    if resp.status_code != 200:
        print(f"{resp.status_code} on {url}")
        return None
    if entry and resp.headers.get('etag') == entry['etag']:
        return entry['value']
    print(f"Cache miss {url}", flush=True)

    parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser()
    parser.parseStr(resp.text)
    spans = parser.getElementsByClassName('qa-fixture-block')
    table = []
    for span_row in spans:
        children = span_row.getAllChildNodes()
        series = children.getElementsByTagName('h3')
        series = series[1].textContent.upper()
        if series.upper() not in _config['cricket_series']:
            continue
        block = []
        matches = children.getElementsByTagName('ul')
        matches = matches[0].getAllChildNodes().getElementsByTagName('li')
        for match in matches:
            nodes = match.getAllChildNodes()
            link = nodes.getElementsByTagName('a')
            if link:
                link = link[0].getAttribute('href')

            home_team = _get_span(nodes, 'sp-c-head-to-head__team-name-trunc',
                                  'abbr',0)
            away_team = _get_span(nodes, 'sp-c-head-to-head__team-name-trunc',
                                  'abbr',1)
            home_score = _get_span(nodes, 'sp-c-head-to-head__home-team-scores',
                                   sub_class='sp-c-head-to-head__cricket-score',
                                   as_list=True)
            away_score = _get_span(nodes, 'sp-c-head-to-head__away-team-scores',
                                   sub_class='sp-c-head-to-head__cricket-score',
                                   as_list=True)
            status = _get_span(nodes, 'sp-c-head-to-head__status')
            title = _get_span(nodes, 'sp-c-head-to-head__title')
            venue = _get_span(nodes, 'sp-c-head-to-head__venue')
            time = _get_span(nodes, 'qa-score-time')
            home_batting = _get_span(nodes,
                                     'sp-c-head-to-head__team-indicator--home')
            away_batting = _get_span(nodes,
                                     'sp-c-head-to-head__team-indicator--away')
            block.append(dict(
                home_team=home_team,
                away_team=away_team,
                home_score=home_score,
                away_score=away_score,
                status=status,
                link=link,
                title=title,
                time=time,
                venue=venue,
                home_batting=bool(home_batting),
                away_batting=bool(away_batting),
            ))

        table.append(dict(
            series=series,
            matches=block,
        ))

    cache[url] = dict(
        value=table,
        etag=resp.headers.get('etag')
    )

    return table

def cricket_fixture_page(pagenum, dates, cache):
    nextpage = ttxutils.nextpage(pagenum)
    page = ttxpage.TeletextPage("Cricket Fixtures",
                                pagenum)

    maxrows = 18
    pages = []
    for offset in dates:
        date = datetime.date.today() + datetime.timedelta(days=offset)
        if offset == 0:
            dayname = "Today"
        elif offset == -1:
            dayname = "Yesterday"
        else:
            dayname = date.strftime("%A")

        isodate = date.isoformat()
        url = f"{_config['cricket_fixtures_url']}/{isodate}"
        fixes = cricket_fixtures_table(url, cache)
        header = f"{ttxcolour.yellow()}{dayname}'s Matches"
        p = [header]
        for f in fixes:
            rows = []
            r = f"{ttxcolour.white()}{page.fixup(f['series']).upper()}"
            rows.append(f"{r:<38}")
            for m in f['matches']:
                if len(rows)>1:
                    rows.append('')
                home_team = page.fixup(m['home_team'])
                away_team = page.fixup(m['away_team'])
                if m['home_batting']:
                    home_team = f"{home_team:<.16}{ttxcolour.yellow()}*"
                    r = f"{ttxcolour.cyan()}{home_team:<18.18}"
                else:
                    r = f"{ttxcolour.cyan()}{home_team:<17.17}"
                r += f"{ttxcolour.white()}v"
                if m['away_batting']:
                    away_team = f"{away_team:<.16}{ttxcolour.yellow()}*"
                    r += f"{ttxcolour.cyan()}{away_team:<18.18}"
                else:
                    r += f"{ttxcolour.cyan()}{away_team:<17.17}"
                rows.append(r)
                if m['title']:
                    rows.append(f"{ttxcolour.green()}{page.fixup(m['title'])}")
                if m['home_score'] and m['away_score']:
                    for innings in range(2):
                        if innings < len(m['home_score']):
                            a = page.fixup(m['home_score'][innings])
                        else:
                            a = ''
                        if innings < len(m['away_score']):
                            b = page.fixup(m['away_score'][innings])
                        else:
                            b = ''
                        if a or b:
                            r = f"{ttxcolour.cyan()}{a:<17.17}   {b:<17.17}"
                            rows.append(r)

                r = ''
                if m['time']:
                    if m['time'] != 'LIVE':
                        if r:
                            r += ': '
                        r += page.fixup(m['time'])
                if m['status']:
                    status = page.fixup(m['status'])
                    r += f"¬\t{status}"
                if m['venue']:
                    venue = page.fixup(m['venue'])
                    r += f"¬\t{venue}"
                colour = ttxcolour.green()
                for ll in textwrap.wrap(r, 39, expand_tabs=False,
                                        replace_whitespace=False):
                    if '\t' in ll or '¬' in ll:
                        ll = ll.replace('¬', '\t')
                        ll = ll.replace('\t\t', '\t')
                        if ll.startswith('\t'):
                            ll = ll.replace('\t','')
                            colour = ttxcolour.magenta()
                        else:
                            ll = ll.replace('\t', ttxcolour.magenta())
                        rows.append(f"{colour}{ll}")
                        colour = ttxcolour.magenta()
                    else:
                        rows.append(f"{colour}{ll}")
            if ((len(p) + len(rows) <  maxrows)
                or (len(p) == 0 and len(rows) == maxrows)):
                if len(p)>1:
                    p.append('')
                p.extend(rows)
            else:
                pages.append(p)
                p = [header]
                p.extend(rows)
        if len(fixes) == 0:
            p.append('')
            p.append(f'{ttxcolour.cyan()}No matches today.')
        pages.append(p)

    subpage = 0
    for p in pages:
        if len(pages) > 1:
            subpage += 1
            page.header(pagenum, subpage, status=0xc000)
        else:
            page.header(pagenum, subpage, status=0x8000)
        sport_header(page, 'Cricket')
        if len(pages) > 1:
            index = f"{subpage}/{len(pages)}"
            p[0] = f"{p[0]:<34.34}{ttxcolour.white()}{index:>5}"
        line = 4
        for r in p:
            if len(r):
                page.addline(line, r)
            line += 1
        sport_footer(page, 'Cricket')

    page.save()

def cricket_fixtures():
    try:
        with open(f"{_config['cachedir']}/cricket_fixtures.cache", 'rb') as f:
            cache = pickle.load(f)
    except:
        cache = dict()

    for page, offsets in _config['cricket_fixtures']:
        cricket_fixture_page(page, offsets, cache)

    with open(f"{_config['cachedir']}/cricket_fixtures.cache", 'wb') as f:
        pickle.dump(cache, f)

def cricket():
    pages = _config['pages']['sport']['cricket']
    feed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'cricket')
    raw_entries = feed.get_entries(sport=True,
                                   max = ttxutils.hexdiff(
                                       pages['last'], pages['first']))

    if not raw_entries:
        return None

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
    cricket_fixtures()

    return [entries[0], pages['first']]

def cricket_index(entries):
    pages = _config['pages']['sport']['cricket']
    header = [
        '€Wj#3kj#3kj#3k€T€]€R  |,h<|h4|,h4|h<(|$',
        "€Wj $kj $kj 'k€T€]€R  ¬pj7}j5¬pj7}jw ¬",
        '€W"###"###"###€T////,,-,,-.,,-.,-,/,///////'
    ]
    footer= [
        "€D€]€CScorecards 350  Fixtures 357/358/359",
        "€D€]€CCRICKET 340    WEB bbc.co.uk/cricket",
        "€ANext page  €BCricket €CHeadlines €FSport ",
    ]
    ttxutils.index_page("Cricket", pages, header, footer, entries,
                        fasttext=[0x300, 0x301, 0x300], increment=2)


def rugby_union():
    pages = _config['pages']['sport']['rugby_union']
    feed = bbcparse.Feed(rss.bbc_feed(pages['feed']), 'rugby_union')
    raw_entries = feed.get_entries(sport=True,
                                   max = ttxutils.hexdiff(
                                       pages['last'], pages['first']))
    if not raw_entries:
        return None

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
    ttxutils.index_page("Rugby", pages, header, footer, entries,
                        fasttext=[0x300, 0x301, 0x300], increment=2)


def makesport():
    topfoot = copy.deepcopy(football())
    if topfoot:
        topfoot[0]['section'] = "Football"

    return [
        topfoot,
        formula1(),
        cricket(),
        rugby_union()
    ]
