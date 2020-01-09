
_bbc_rss_url = "https://feeds.bbci.co.uk/{}/rss.xml?edition=uk"

def bbc_feed(feed):
    if type(feed) is list:
        return [ _bbc_rss_url.format(f) for f in feed ]
    else:
        return _bbc_rss_url.format(feed)
