import AdvancedHTMLParser # type: ignore
import feedparser # type: ignore
import fetch
import pickle
import time
import datetime
import itertools
import re

#import pprint
#pp = pprint.PrettyPrinter(indent=4)

import config
_config=config.Config().config

def _interleave(iterables):
    zip = [ x for x in itertools.zip_longest(*iterables)]
    zip = [ x for x in itertools.chain(*zip)]
    seen = {}
    ret = []
    for z in zip:
        # Deduplicate and remove null entries
        if z is not None:
            l = z['link']
            if l not in seen:
                seen[l] = True
                ret.append(z)
    return ret

def _remove_scripts(t):
    # BBC sometimes have inline JavaScript scripts that are not
    # within comments, which greatly confuses the parser if they
    # have the text <html> inside them.
    # Football match report pages are the usual culprit.
    regex = re.compile(r'<script(| type="text/javascript")>.+?<\/script>',
                       re.DOTALL)
    return regex.sub('', t)

def _mkdatetime(t):
    return datetime.datetime.fromtimestamp(time.mktime(t))

class Feed(object):
    def __init__(self, feed, cachename='cache'):
        self.error = False
        if type(feed) is list:
            self.rss_entries = list()
            for f in feed:
                p = feedparser.parse(f)
                if p.bozo:
                    self.error = True
                else:
                    self.rss_entries.append(p['entries'])
            # Interleave the feeds
            self.rss_entries = _interleave(self.rss_entries)
        else:
            p = feedparser.parse(feed)
            if p.bozo:
                self.error = True
            else:
                self.rss_entries = feedparser.parse(feed)['entries']

        if self.error:
            self.parser = None
            self.cache = None
            self.fetch = None
            self.rss_entries = None
            self.entries = None
            return

        self.parser = AdvancedHTMLParser.IndexedAdvancedHTMLParser(
            indexNames=False
        )
        #self.parser.addIndexOnAttribute('property')
        self.cache = dict()
        self.cachename = cachename
        self.fetch = fetch.Fetcher()
        _cachedir = _config['cachedir']
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
        if len(self.rss_entries) == 0:
            print("ERROR: empty rss list")
        self.entries = list()

    def __del__(self):
        _cachedir = _config['cachedir']
        if self.cache:
            with open(f"{_cachedir}/{self.cachename}.cache", 'wb') as f:
                pickle.dump(self.cache, f)

    def good_url(self, link):
        if link is None:
            return False
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
        if '/newsround' in link:
            return False
        return True


    def get_entries(self, sport=False, max=99):
        if not self.rss_entries:
            return None
        if self.entries:
            return self.entries

        duplicates=dict()

        entries = []
        for e in self.rss_entries:
            # pp.pprint(e)
            link = e['link']
            if link in duplicates:
                continue
            duplicates[link]=True

            update = _mkdatetime(e['published_parsed'])
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
            if len(entries) >= max:
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
        try:
            text = _remove_scripts(r.content.decode("utf-8"))
            self.parser.parseStr(text)
        except Exception as inst:
            print(type(inst), inst, flush=True)
            # print(text, file=open('/tmp/parsefail.html', 'w'))
            return None

        try:
            metas = self.get_metas()

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

            description = self.get_meta(metas, 'og:description')
            stitle = self.get_meta(metas, 'og:title')
            section = self.get_meta(metas, 'article:section')

            if 'in pictures:' in stitle.lower():
                self.cache[url] = None
                return None
            if 'in pictures:' in title.lower():
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
        except:
            import traceback
            print("Parsing exception:")
            traceback.print_exc()
            print(f"in {url}", flush=True)
            self.cache[url] = None
            return None
