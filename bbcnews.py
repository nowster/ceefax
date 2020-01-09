import ttxpage
import ttxutils
import ttxcolour
import newsheaders
import bbcparse
import rss
import textwrap
import copy

import config
config=config.Config().config

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

def news_headlines(entries, conf, region=None):
    pagenum = conf['headlines']
    if region:
        page = ttxpage.TeletextPage(
            f"Regional Headlines {pagenum:03x}",
            pagenum)
        page.header(pagenum)
        category = newsheaders.newsheader(page, region)
        nextpage = conf['first']
        maxlines = 9
    else:
        page = ttxpage.TeletextPage(
            f"News Headlines {pagenum:03x}",
            pagenum)
        page.header(pagenum)
        category = newsheaders.newsheader(page, 'headlines')
        nextpage = conf['first']
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

def news_index(entries, conf):
    pagenum = conf['index']
    page = ttxpage.TeletextPage(
        "News Index {:03x}".format(pagenum),
            pagenum, time=15)

    toptitles = []
    subtitles = []
    index = 0
    nextpage = conf['first']
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
        page.header(pagenum, subpage + 1)
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

def news_summary(entries, conf):
    summarynum = conf['summary']
    page = ttxpage.TeletextPage(f"News Summary {summarynum:03x}",
                                summarynum, time=15)
    offset = 0
    pagenum = conf['first']
    for subpage in range(2):
        page.header(summarynum, subpage + 1)
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

def news_scitech(entries, conf):
    pagenum = conf['carousel']
    page = ttxpage.TeletextPage(f"Sci-Tech {pagenum:03x}",
                                pagenum,
                                time = 15)

    subpage = 1
    length = len(entries)
    for contents in entries:
        page.header(pagenum, subpage)
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
    region = config['bbc_news_regions'][config['bbc_news_region']]
    news = config['pages']['news']['main']
    regional = config['pages']['news']['regional']

    newsfeed = bbcparse.Feed(rss.bbc_feed(news['feed']), 'newsmain')
    numstories = ttxutils.hexdiff(news['last'], news['first'])
    stories = newsfeed.get_entries(max=numstories)

    regionalfeed = bbcparse.Feed(rss.bbc_feed(region['feed']),
                                 "newsregional")
    numstories = ttxutils.hexdiff(regional['last'], regional['first'])
    regionalstories = regionalfeed.get_entries(max=numstories)

    page = news['first']
    for story in stories:
        news_page(page, story)
        page = ttxutils.nextpage(page)

    page = regional['first']
    for story in regionalstories:
        news_page(page, story)
        page = ttxutils.nextpage(page)

    news_index(stories, news)
    news_headlines(stories, news)
    news_summary(stories, news)

    news_headlines(regionalstories, regional, region['name'])

    scitech = config['pages']['news']['scitech']
    scitechfeed = bbcparse.Feed(rss.bbc_feed(scitech['feed']), "newssci")
    scitechstories = scitechfeed.get_entries()
    news_scitech(scitechstories, scitech)

    topstory = copy.deepcopy(stories[0])
    topstory['section'] = 'UK News'

    topregstory = copy.deepcopy(regionalstories[0])
    topregstory['section'] += ' News'

    return [
        (topstory, news['first']),
        (topregstory, regional['first']),
    ]
