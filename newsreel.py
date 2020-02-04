#!/usr/bin/python3

import re

import ttxpage
import config
_config=config.Config().config

class _Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class Newsreel(metaclass=_Singleton):
    def __init__(self):
        self.pages = []

    def clear(self):
        self.pages.clear()

    def add(self, lines):
        page = []
        pat = re.compile(r"OL,(\d+),(.*)")
        for l in lines:
            if l.startswith("PN"):
                if page:
                    self.pages.append(page)
                    page = []
            s = pat.match(l)
            if s:
                if int(s[1]) > 0 and int(s[1]) < 24:
                    line = s[2]
                    line = re.sub("( |\x1b[A-Z])\d{1,2}/\d{1,2}\s*$",
                                  "", line, count=1)
                    page.append((s[1],line))
        if page:
            self.pages.append(page)

    def save(self):
        pagenum = _config["newsreel"]["page"]
        duration = _config["newsreel"]["duration"]
        d = ttxutils.decode

        page = ttxpage.TeletextPage("Newsreel", pagenum, time=duration)
        subpage = 1
        for p in self.pages:
            page.header(pagenum, subpage, status=0xc000)
            for l in p:
                page.addline(l[0], l[1])
            page.addline(24,
                         d("€ANext News €BLocalNews €CSport  €FMain Menu"))
            page.addfasttext(0x154, 0x160, 0x300, 0x100, 0x8ff, 0x199)
            subpage += 1
        page.save()
