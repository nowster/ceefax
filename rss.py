
_bbc_feeds = {
    'uk_news': 'news/uk/',
    'world_news': 'news/world',
    'entertainment': 'news/entertainment_and_arts',
    'politics': 'news/politics',
    'business': 'news/business',
    'scitech' : 'news/technology',
    'sport': 'sport',
    'football': 'sport/football',
    'formula1': 'sport/formula1',
    'cricket' : 'sport/cricket',
    'tennis' : 'sport/tennis',
    'rugby_union' : 'sport/rugby-union',
    'rugby_league' : 'sport/rugby-league',
    'golf' : 'sport/golf',
}

_bbc_rss_url = "https://feeds.bbci.co.uk/{}/rss.xml?edition=uk"

def bbc_feed(name, region=None):
    if region:
        return _bbc_rss_url.format(f"news/{region}")
    elif name in _bbc_feeds:
        return _bbc_rss_url.format(_bbc_feeds[name])
    else:
        return None
