import AdvancedHTMLParser
import feedparser
import fetch
import pickle
import datetime

#import pprint
#pp = pprint.PrettyPrinter(indent=4)

import config
_config=config.Config().config

_cachedir = _config['cachedir']

class Feed(object):
    def __init__(self, feed, cachename='cache'):
        if type(feed) is list:
            self.rss_entries = list()
            for f in feed:
                self.rss_entries.extend(feedparser.parse(f)['entries'])
        else:
            self.rss_entries = feedparser.parse(feed)['entries']

        self.parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser(
            indexNames=False
        )
        #self.parser.addIndexOnAttribute('property')
        self.cache = dict()
        self.cachename = cachename
        self.fetch = fetch.Fetcher()
        try:
            with open(f"{_cachedir}/{cachename}.cache", 'rb') as f:
                self.cache = pickle.load(f)
                for x in self.cache.keys():
                    pubdate = self.cache[x]['published']
                    if (timedate.datetime.now() - pubdate
                        > datetime.timedelta(days=5)):
                        del self.cache[x]
        except:
            pass
        self.entries = list()

    def __del__(self):
        with open(f"{_cachedir}/{self.cachename}.cache", 'wb') as f:
            pickle.dump(self.cache, f)

    def good_url(self, link):
        if '/av/' in link:
            return False
        if '/news/in-pictures' in link:
            return False
        if '/news/blogs' in link:
            return False
        if '/news/newsbeat' in link:
            return False
        if '/news/stories' in link:
            return False
        if '/news/newsround' in link:
            return False
        return True


    def get_entries(self, sport=False, max=99):
        if self.entries:
            return self.entries

        entries = []
        for e in self.rss_entries:
            # pp.pprint(e)
            link = e['link']
            #print(link, flush=True)
            update = e['published_parsed']
            # Filter out stuff that doesn't work as teletext
            if not self.good_url(link):
                continue
            if '/sport/' in link and not sport:
                continue

            contents = self.extract(link, update)

            if contents is None:
                continue
            if '/sport/' in contents['link'] and not sport:
                 continue
            entries.append(contents)
            if len(entries) > max:
                break

        self.entries = entries
        return entries

    def get_metas(self):
        ret = dict()
        metas = self.parser.getElementsByTagName('meta')
        for m in metas:
            if 'property' in m.attributes:
                if 'content' in m.attributes:
                    ret[m.attributes['property']] = m.attributes['content']
        return ret

    def get_meta(self, metas, prop):
        if prop in metas:
            return metas[prop]
        return None

    def get_property(self, name, property):
        fields = self.parser.getElementsByAttr('property', property)
        for f in fields:
            if f.nodeName == name:
                if 'content' in f.attributes:
                    return f.attributes['content']
        return None


    def extract(self, url, pubdate):
        if url in self.cache:
            entry = self.cache[url]
            if entry is None:
                return None
            if pubdate == entry['published']:
                return entry

        print(f"Cache miss {url}", flush=True)
        paragraphs = []
        r = self.fetch.get(url)
        if r.status_code != 200:
            print(r.status_code)
            return None
        self.parser.parseStr(r.text)
        metas = self.get_metas()

        #link = self.get_property('meta', 'og:url')
        link = self.get_meta(metas, 'og:url')

        if not self.good_url(link):
            self.cache[url] = None
            return None

        title = self.parser.getElementsByClassName('story-body__h1')
        if title is not None:
            if len(title) <  1:
                title = None
        if title is None:
            title = self.parser.getElementsByTagName('title')
        if title is not None:
            title = title[0].textContent

        #description = self.get_property('meta', 'og:description')
        #stitle = self.get_property('meta', 'og:title')
        #section = self.get_property('meta', 'article:section')
        description = self.get_meta(metas, 'og:description')
        stitle = self.get_meta(metas, 'og:title')
        section = self.get_meta(metas, 'article:section')

        if 'In pictures:' in stitle:
            self.cache[url] = None
            return None

        storytag = self.parser.getElementById('story-body')
        if storytag is None:
            storytag = self.parser.getElementsByClassName('story-body__inner')[0]

        children = storytag.getAllChildNodes().getElementsByTagName('p')
        for p in children:
            if '-message' not in p.className:
                paragraphs.append(p.textContent.strip())


        self.cache[url] = dict(title=title,
                               short_title=stitle,
                               section=section,
                               link=link,
                               description=description,
                               text=paragraphs,
                               published=pubdate
        )
        return self.cache[url]
