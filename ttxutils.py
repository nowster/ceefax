import ttxpage
import ttxcolour
from typing import List, Optional, Union

def nextpage(page):
    if type(page) is str:
        page = int(page, 16)
    while True:
        page += 1
        if (page & 0x0f) <= 9:
            return page

def decode(text):
    return text.replace("€", "\x1B").replace("¬", "\x7F")

def hexdiff(a, b):
    return ( 1 + int(f"{a:x}") - int(f"{b:x}") )

def index_page(category : str,
               pages : dict,
               header : List[str],
               footer : List[str],
               entries : list,
               fasttext : Optional[List[int]] = None,
               increment=1):
    index = pages['index']
    page = ttxpage.TeletextPage(
        f"{category} Index {index:03x}",
        index)
    page.header(index)
    line = 1
    for l in header:
        page.addline(line, decode(l))
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
        number = nextpage(number)
        if number > pages['last']:
            break
    line = 25 - len(footer)
    for l in footer:
        page.addline(line, decode(l))
        line += 1
    if fasttext and len(fasttext) in [3, 4, 6]:
        if len(fasttext) == 3:
            f = [pages['first'], *fasttext, 0x8ff, 0x199]
        if len(fasttext) == 4:
            f = [*fasttext, 0x8ff, 0x199]
        else:
            f = fasttext
        page.addfasttext(*f)
    else:
        page.addfasttext(pages['first'], 0x100, 0x101, 0x100, 0x8ff, 0x199)
    page.save()
