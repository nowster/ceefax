import ttxpage
import ttxutils
import ttxcolour
import newsheaders
import bbcparse
import rss
import textwrap
import copy

regions = dict(
    ni     = ["Northern Ireland", "N IRELAND" "northern_ireland"],
    manc   = ["Manchester", "MANCHSTR", "england/manchester"],
    lancs  = ["Lancashire", "LANCS", "england/lancashire"],
    nwwal  = ["North West Wales", "NW WALES", "wales/north_west_wales"],
)

region = "lancs"

headlines_page = 0x101
index_page     = 0x102
summary_page   = 0x103
first_news     = 0x104
last_news      = 0x124

latest_page    = 0x150
ticker_page    = 0x151

regional_page  = 0x160
first_regional = 0x161
last_regional  = 0x169

sci_tech_page  = 0x154

def news_page(number, contents):
    url = contents['link']
    page = ttxpage.TeletextPage("News Page {:03x} {}".format(number, url),
                                number)
    page.header(number)
    category = newsheaders.newsheader(page, contents['section'])
    line = 4
    line += page.wrapline(line, 21, page.fixup(contents['title']),
                          ttxcolour.green())
    colour = ' '
    for para in contents['text']:
        if line <= 21:
            increment = page.wrapline(line, 22, page.fixup(para), colour)
            if increment:
                line += increment + 1
            colour = ttxcolour.cyan()

    newsheaders.newsfooter(page, category)
    page.save()

def news_headlines(entries, region=None):
    if region:
        page = ttxpage.TeletextPage(
            "Regional Headlines {:03x}".format(regional_page),
            regional_page)
        page.header(regional_page)
        category = newsheaders.newsheader(page, region)
        nextpage = first_regional
        maxlines = 9
    else:
        page = ttxpage.TeletextPage(
            "News Headlines {:03x}".format(headlines_page),
            headlines_page)
        page.header(headlines_page)
        category = newsheaders.newsheader(page, 'headlines')
        nextpage = first_news
        maxlines = 8

    line = 4
    count = 0

    for contents in entries:
        if line == 4:
            textattr = ttxcolour.colour(ttxcolour.DOUBLE_HEIGHT)
        else:
            textattr = ttxcolour.colour(ttxcolour.ALPHAWHITE)
        headline = page.truncate(page.fixup(contents['short_title']), 70, ' ')
        headlines = textwrap.wrap(headline, 35)
        page.addline(line, '{}{:<35}{}{:03x}'.format(textattr,
                                                     headlines[0],
                                                     ttxcolour.yellow(),
                                                     nextpage))
        nextpage = ttxutils.nextpage(nextpage)

        if line <= 4:
            line += 2
        else:
            line += 1
        if line >= 22:
            break

        if len(headlines) > 1:
            page.addline(line, '{}  {}'.format(
                ttxcolour.white(),
                headlines[1]))

        if line < 7 and region is None:
            line += 2
        else:
            line += 1
        count += 1
        if count >= maxlines:
            break

    newsheaders.newsheadlinesfooter(page, category)
    page.save()

def news_index(entries):
    page = ttxpage.TeletextPage(
        "News Index {:03x}".format(index_page),
            index_page, time=15)

    toptitles = []
    subtitles = []
    index = 0
    nextpage = first_news
    for contents in entries:
        if index < 3:
            textcolour = ttxcolour.cyan()
        else:
            textcolour = ttxcolour.white()
        headline = page.truncate(page.fixup(contents['short_title']), 35, ' ')
        if index <= 11:
            toptitles.append("{}{:<35}{}{:03x}".format(
                textcolour, headline,
                ttxcolour.yellow(), nextpage))
        else:
            subtitles.append("{}{:<35}{}{:03x}".format(
                textcolour, headline,
                ttxcolour.yellow(), nextpage))
        index += 1
        nextpage = ttxutils.nextpage(nextpage)

    maxsubpage = int((len(subtitles)+2) / 3)
    for subpage in range(maxsubpage):
        line = 4
        page.header(index_page, subpage + 1)
        category = newsheaders.newsheader(page, 'index')
        for t in toptitles:
            if line == 10:
                line += 1
            page.addline(line, t)
            line += 1
        page.addline(17, "{}Other News {}/{}".format(
                     ttxcolour.yellow(), subpage + 1, maxsubpage))
        line = 18

        offset = subpage * 3
        subset = subtitles[offset : offset + 3]
        for t in subset:
            page.addline(line, t)
            line += 1

        newsheaders.newsindexfooter(page)
        if offset + 3 > len(subtitles):
            break

    page.save()

def news_summary(entries):
    page = ttxpage.TeletextPage(f"News Summary {summary_page:03x}",
                                summary_page, time=15)
    offset = 0
    pagenum = first_news
    for subpage in range(2):
        page.header(summary_page, subpage + 1)
        newsheaders.newsheader(page, 'summary')
        index = f"{subpage + 1}/2 "
        page.addline(4, f"{index:>40}")
        line = 5
        while offset < len(entries):
            contents = entries[offset]
            para = contents['text'][0]
            lines = page.wrapline(line, 21, page.fixup(para), ttxcolour.cyan())
            if lines:
                line += lines
                page.addline(line, f" See {pagenum:03x}")
                line += 2
                pagenum = ttxutils.nextpage(pagenum)
                offset += 1
            else:
                break
        newsheaders.newssummaryfooter(page)
    page.save()

def news_scitech(entries):
    page = ttxpage.TeletextPage(f"Sci-Tech {sci_tech_page:03x}", sci_tech_page,
                                time = 15)

    subpage = 1
    length = len(entries)
    for contents in entries:
        page.header(sci_tech_page, subpage)
        newsheaders.newsheader(page, 'scitechhead')
        line = 4
        line += page.wrapline(line, 21, contents['title'],
                              ttxcolour.yellow())
        colour = ' '
        for para in contents['text']:
            if line <= 21:
                line += page.wrapline(line, 22, page.fixup(para), colour) + 1
                colour = ttxcolour.cyan()
        index = f"{subpage}/{length} "
        footers = [
            f"{index:>40}"
            '€D€]€CHeadlines €G101€CIndex€G102€CSport  €G300',
            '€D€]€CFront Page€G100€CTV   €G600€CWeather€G400',
            '€ALocalNews€BHeadlines€CNews Indx€FMain Menu'
        ]
        line = 22
        for l in footers:
            page.addline(line, ttxutils.decode(l))
            line += 1
        page.addfasttext(0x160, 0x101, 0x102, 0x100, 0x8ff, 0x100)
        subpage += 1
    page.save()

def makenews():
    region_name, region_abbrev, region_rss = regions[region]
    ukfeed = bbcparse.Feed(rss.bbc_feed('uk_news'), 'newsuk')
    worldfeed = bbcparse.Feed(rss.bbc_feed('world_news'), 'newsworld')

    stories = ukfeed.get_entries() + worldfeed.get_entries()
    stories = stories[ : 1 + int(f"{last_news:x}") - int(f"{first_news:x}")]

    regionalfeed = bbcparse.Feed(rss.bbc_feed('regional', region_rss),
                                 "newsregional")
    regionalstories = regionalfeed.get_entries()
    regionalstories = regionalstories[ :
                                       1 +
                                       int(f"{last_regional:x}") -
                                       int(f"{first_regional:x}")]
    page = first_news
    for story in stories:
        news_page(page, story)
        page = ttxutils.nextpage(page)

    page = first_regional
    for story in regionalstories:
        news_page(page, story)
        page = ttxutils.nextpage(page)

    news_index(stories)
    news_headlines(stories)
    news_summary(stories)

    news_headlines(regionalstories, region_name)

    scitechfeed = bbcparse.Feed(rss.bbc_feed('scitech'), "newssci")
    scitechstories = scitechfeed.get_entries()
    news_scitech(scitechstories)

    topstory = copy.deepcopy(stories[0])
    topstory['section'] = 'UK News'

    topregstory = copy.deepcopy(regionalstories[0])
    topregstory['section'] += ' News'

    return [
        (topstory, first_news),
        (topregstory, first_regional),
    ]
