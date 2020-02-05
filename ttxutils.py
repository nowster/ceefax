import ttxpage
import ttxcolour
from typing import List, Optional, Union

def nextpage(page : Union[int, str]) -> int:
    if type(page) is str:
        p = int(str(page), 16)
    else:
        p = int(page)
    while True:
        p += 1
        if (p & 0x0f) <= 9:
            return p

_trans_stored = None
def _make_viewdata(s):
    global _trans_stored
    if not _trans_stored:
        _translations = {}
        for i in range(32):
            _translations[chr(i + 0x2400)] = f"\x1B{chr(i+64)}"
        _translations[chr(0x2421)] = "\x7f"
        _trans_stored = s.maketrans(_translations)
    return s.translate(_trans_stored)

_trans_stored_low = None
def _make_viewdata_low(s):
    global _trans_stored_low
    if not _trans_stored_low:
        _translations = {}
        for i in range(32):
            _translations[chr(i)] = f"\x1B{chr(i+64)}"
            _translations[chr(i + 0x2400)] = f"\x1B{chr(i+64)}"
        _translations[chr(0x2421)] = "\x7f"
        _trans_stored_low = s.maketrans(_translations)
    return s.translate(_trans_stored_low)

def decode(text: str, low: bool=False) -> str:
    if low:
        text = _make_viewdata_low(text)
    else:
        text = _make_viewdata(text)
    return text.replace("€", "\x1B").replace("¬", "\x7F")

def hexdiff(a: str, b: str) -> int:
    return ( 1 + int(f"{a:x}") - int(f"{b:x}") )

def index_page(category : str,
               pages : dict,
               header : List[str],
               footer : List[str],
               entries : list,
               fasttext : Optional[List[int]] = None,
               increment : int =1,
               rule: Optional[str] = None,
               number_colour: str = ttxcolour.white()):
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
        if line == rule:
            page.addline(line,
                         f"{ttxcolour.magenta()}"
                         "```````````````````````````````````````")
            line += 1
        title = contents['short_title']
        l, _, r = title.partition(': ')
        if r:
            title = r
        title = page.truncate(title, 35, ' ')
        page.addline(line,
                     f"{colour}{title:<35.35}{number_colour}{number:03x}")
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
        elif len(fasttext) == 4:
            f = [*fasttext, 0x8ff, 0x199]
        else:
            f = fasttext
        page.addfasttext(*f)
    else:
        page.addfasttext(pages['first'], 0x100, 0x101, 0x100, 0x8ff, 0x199)
    page.save()

def generic_page(category : str,
                 pagenum : int,
                 pages : dict,
                 header : List[str],
                 footer : List[str],
                 lines : List[str],
                 fasttext : Optional[List[int]] = None):
    page = ttxpage.TeletextPage(
        f"{category} Page {pagenum:03x}",
        pagenum)
    page.header(pagenum)
    line = 1
    for l in header:
        page.addline(line, decode(l))
        line += 1

    for l in lines:
        page.addline(line, l)
        line += 1

    line = 25 - len(footer)
    for l in footer:
        page.addline(line, decode(l))
        line += 1
    if fasttext and len(fasttext) in [3, 4, 6]:
        if len(fasttext) == 3:
            f = [pages['index'], *fasttext, 0x8ff, 0x199]
        elif len(fasttext) == 4:
            f = [*fasttext, 0x8ff, 0x199]
        else:
            f = fasttext
        page.addfasttext(*f)
    else:
        page.addfasttext(pages['index'], 0x100, 0x101, 0x100, 0x8ff, 0x199)
    page.save()

def news_page(category : str,
              pages : dict,
              number : int,
              contents : dict,
              header : List[str],
              footer : List[str],
              fasttext : Optional[List[int]] = None):
    url = contents['link']
    page = ttxpage.TeletextPage(
        f"{category} Page {number:03x} {url}", number)
    page.header(number)
    line = 1
    for l in header:
        page.addline(line, decode(l))
        line += 1

    title = contents['title']
    line += page.wrapline(line, 21,
                          page.fixup(title),
                          ttxcolour.green())
    colour = ' '
    for para in contents['text']:
        if line <= 21:
            added = page.wrapline(line, 22, page.fixup(para), colour)
            if added:
                line += added + 1
            colour = ttxcolour.cyan()

    line = 25 - len(footer)
    for l in footer:
        page.addline(line, decode(l))
        line += 1
    if fasttext and len(fasttext) in [3, 4, 6]:
        if len(fasttext) == 3:
            f = [nextpage(number), *fasttext, 0x8ff, 0x199]
        if len(fasttext) == 4:
            f = [*fasttext, 0x8ff, 0x199]
        else:
            f = fasttext
        page.addfasttext(*f)
    else:
        page.addfasttext(pages['first'], 0x100, 0x101, 0x100, 0x8ff, 0x199)
    page.save()
