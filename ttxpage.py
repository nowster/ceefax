#!/usr/bin/python3

import textwrap
import html

pagedir = '/ram/pages'

class TeletextPage(object):
    def __init__(self, description="News Page",
                 pagenum=0x800,
                 cycles=None, time=None):
        self.lines=[]
        if cycles is not None:
            self.ct="CT,{},C".format(cycles)
        elif time is not None:
            self.ct="CT,{},T".format(time)
        else:
            self.ct="CT,10,T"
        self.lines.append("DS,inserter")
        self.lines.append("DE,{}".format(description))
        self.lines.append(self.ct)
        self.page = "{:03x}".format(pagenum)

        self.translations = {
            'é': 'e', 'á': 'a', 'Ó': 'O', 'Ö': 'O', 'ö': 'o', '£': '#',
            '’': "'", 'ó': 'o', '‘': "'", 'ç': 'c',
            'í': 'i', '…': '.', 'É': 'E', 'ë':'e', '“': '"',
            '”': '"', "—": '-', '[': '(', ']': ')', 'ü': 'u',
            "€": "E", '#': '_',
        }

    def header(self, pagenum=0x800, subpage=0, status=0x8000):
        sp = subpage % 100
        self.lines.append("PN,{:03x}{:02}".format(pagenum,sp))
        self.lines.append("SC,{:04}".format(subpage))
        self.lines.append("PS,{:04x}".format(status))
        self.page = "{:03x}".format(pagenum)

    def wrapline(self, start_line, max_line, content, colour=" "):
        lines = textwrap.wrap(content, 39)
        if len(lines) + start_line > max_line:
            return 0

        count = 0
        for l in lines:
            if len(l) > 1:
                self.lines.append("OL,{},{}{}".format(count + start_line,
                                                      colour, l))
                count += 1

        return count

    def addline(self, line_num, text):
        self.lines.append("OL,{},{}".format(line_num, text))

    def addfasttext(self, red=0, green=0, yellow=0, cyan=0, link=0, index=0):
        self.lines.append(
            "FL,{:03x},{:03x},{:03x},{:03x},{:03x},{:03x}".format(
                red, green, yellow, cyan, link, index))

    def truncate(self, text, max_length, split=None):
        text = self.fixup(text)
        if len(text) <= max_length:
            return text
        if split:
            a,b,c = text[:max_length].rpartition(split)
            if a:
                return a
            else:
                return b
        else:
            return textwrap.shorten(text, width=max_length, placeholder="...")

    def fixup(self, text):
        trans = text.maketrans(self.translations)
        text = html.unescape(text)
        return text.translate(trans)

    def save(self, format_string="{}/page{}.tti"):
        with open(format_string.format(pagedir,self.page),
                  mode="w", newline="\r\n") as f:
            f.write("\n".join(self.lines))
