import ttxutils
from ttxcolour import red,green,yellow,blue

import config
_config=config.Config().config

_newsconf = _config['pages']['news']

def newsheader(page, title):
    headers=[]
    category = title
    if title in ['Health']:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S | |h<$|,|h4h||4| | ',
            "€Wj $kj $kj 'k€T€]€S ¬#¬jw1¬#¬ju0j5 ¬#¬ ",
            '€W"###"###"###€T///,/,-,.,/,-,.-./,/,/////'
            ]

    elif title in ['Technology', 'Science & Environment']:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S  |,h<$|h<$|0|h<$|, ',
            "€Wj $kj $kj 'k€T€]€S  s¬ju0¬jw1¬+¬ju0¬s",
            '€W"###"###"###€T////,,-,.,-,.,/,-,.,,/////'
        ]
        category = 'scitech'
    elif title in [ 'Lancashire' ]:
        headers = [
            "€Wj#3kj#3kj#3k€T€]€S | `<thth4x,`<,",
            "€Wj $kj $kj 'k€T€]€S ¬pj7¬j7o5opbs?`0",
            '€W"###"###"###€T///,,-.,-.-.-,-,.-.///////'
        ]
    elif title in [ 'Manchester' ]:
        headers = [
            "€Wj#3kj#3kj#3k€T€]€S|||4xl0|0|`<$|h4 | |l0",
            "€Wj $kj $kj 'k€T€]€S¬jj5¬k5¬+¬*u0¬k5\"! ¬k4",
            '€W"###"###"###€T//,--.,-.,/,/,.,-.///,-.//'
        ]
    elif title in ['UK', "Business",
                   "Entertainment & Arts",
                   "London", "Family & Education",
                   "Cambridgeshire", "Shropshire", "Leicester",
                   "Norfolk", "Sheffield & South Yorkshire",
                   "Bristol", "Beds, Herts & Bucks", "Essex",
                   "England", "Sussex", "Wiltshire",
                   "Tyne & Wear", "Suffolk",
                   "Kent", "Leeds & West Yorkshire",
                   "Liverpool", "Birmingham & Black Country",
                   "Devon", "York & North Yorkshire",
                   "Lincolnshire", "Surrey", "Humberside",
                   "Derby", "Dorset", "Hereford & Worcester",
                   "Hampshire & Isle of Wight", "Nottingham",
                   "Oxford", "Tees"]:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S    h4h4|,|h<<|h<$',
            "€Wj $kj $kj 'k€T€]€S    j7k5¬p¬j55¬jw1",
            '€W"###"###"###€T//////-.-.,,,-..,-,.//////'
        ]

    elif title in [ "Scotland", "Edinburgh, Fife & East Scotland",
                    "Tayside and Central Scotland",
                    "NE Scotland, Orkney & Shetland",
                    "Glasgow & West Scotland",
                    "Hearts", "South Scotland",
                    "Scotland politics", "Highlands & Islands",
                    "Scotland business" ]:
        headers = [
            '€Wj#3kj#3kj#3k€D€]€Sx,h<$|l4l<h4 x,th|0|h<t ',
            "€Wj $kj $kj 'k€T€]€Ss?ju0¬z5j5ju0¬#¬j5+¬ju> ",
            '€W"###"###"###€T//,.-,.,,.-.-,.,/,-./,-,./'
        ]
        category = 'scotland'

    elif title in [ "Northern Ireland", "Foyle & West",
                    "N. Ireland Politics" ]:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S|0| h4|l4|,h4`<thth4|l0',
            "€Wj $kj $kj 'k€T€]€S¬+¬`j5¬k4¬sjuj7¬j7o5¬z%",
            '€W"###"###"###€T//,/,--.,-.,,-,-.,-.-.,,//'
        ]
        category = 'northern ireland'

    elif title in [ "Wales", "Wales politics",
                    "North West Wales", "North East Wales",
                    "South East Wales", "South West Wales" ]:
        headers = [
            '€Wj#3kj#3kj#3k€D€]€S   h44|`<l0| h<$x,',
            "€Wj $kj $kj 'k€T€]€S   *uu?j7k5¬pjw1s?",
            '€W"###"###"###€T//////,,.-.-.,,-,.,.//////'
        ]
        category = 'wales'

    elif title in [ "World", "Europe", "Latin America & Caribbean",
                    "Middle East", "US & Canada", "Africa",
                    "Australia", "India", "Asia", "China" ]:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S   |hh4|,|h<l4| h<l0',
            "€Wj $kj $kj 'k€T€]€S   ozz%¬p¬j7k4¬pjuz%",
            '€W"###"###"###€T/////-,,/,,,-.-.,,-,,/////'

        ]

    elif title in [ "Politics", "UK Politics" ]:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S h<|h<|h4 |(|$|h<$|,$ ',
            "€Wj $kj $kj 'k€T€]€S j7#ju¬ju0¬ ¬ ¬ju0s{5 ",
            '€W"###"###"###€T///-./-,,-,.,/,/,-,.,,.///'
        ]
        category = 'politics'

    elif title in [ 'headlines' ]:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€Sh4|h<h<|h<th4h4xl0|$|,  ',
            "€Wj $kj $kj 'k€T€]€Sj7¬jwj7¬ju?juj5¬j5¬1s¬  ",
            '€W"###"###"###€T//-.,-,-.,-,.-,-.,-.,.,,//'
        ]
    elif title in [ 'index' ]:
        headers = [
            '€D€]€S|h4|h4 `h44|`<th<|h4h<t hth4|$|hh4|,$',
            '€D€]€Soz%¬k48!*uu?*u?j7}juju? j7o5¬1ozz%s{5',
            '€T//-,/,-.///,,./,.-.,-,-,./-.-.,.-,,/,,.'
            ]
    elif title in [ 'summary' ]:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S|,$|h4|ll4|ll4|l4|l4|h4 ',
            "€Wj $kj $kj 'k€T€]€Ss{5¬z5¬jj5¬jj5¬k5¬k4s{5 ",
            '€W"###"###"###€T//,,.,,.,--.,--.,-.,-.,,./'
        ]

    elif title in ['scitechhead']:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S  x,$x,h4 (|$|,`<$|h4 ',
            "€Wj $kj $kj 'k€T€]€S  s{%opj5# ¬ ¬s*u0¬k5 ",
            '€W"###"###"###€T////,,/-,-.//,/,,/,.,-.///'
        ]

    else:
        headers = [
            '€Wj#3kj#3kj#3k€T€]€S     xl0|,h44|h,$',
            "€Wj $kj $kj 'k€T€]€S     ¬j5¬s*uu?bs5",
            '€W"###"###"###€T///////,-.,,/,,.-,.///////'
        ]

    line = 1
    for h in headers:
        page.addline(line, ttxutils.decode(h))
        line += 1

def newsfooter(page, category):
    nextpage = ttxutils.nextpage(page.page)
    lastpage = ttxutils.nextpage(_newsconf['main']['last'])
    lastregpage = ttxutils.nextpage(_newsconf['regional']['last'])
    if nextpage in [lastpage, lastregpage]:
        fastext = (
            red()    + 'In Depth ' +
            green()  + 'News Indx' +
            yellow() + 'Headlines' +
            blue()   + 'Main Menu' )
    else:
        fastext = (
            red()    + 'Next News' +
            green()  + 'News Indx' +
            yellow() + 'Headlines' +
            blue()   + 'Main Menu' )

    if category:
        lines = [
            '€T€]€GREGIONAL €CHeadlines€G160€CSport   €G390',
            '€D€]€GNATIONAL€C Main menu€G100€CWeather€G 400',
            fastext ]
    else:
        lines = [
            '€D€]€CHome news digest€G141€CWorld digest€G142',
            '€D€]€CNews Index€G102€CFlash€G150€CRegional€G160',
            fastext ]

    line = 22
    for l in lines:
        page.addline(line, ttxutils.decode(l))
        line += 1
    if nextpage > _newsconf['regional']['headlines']:
        page.addfasttext(nextpage, _newsconf['regional']['headlines'],
                         _newsconf['main']['headlines'], 0x100, 0x8ff, 0x199)
    else:
        page.addfasttext(nextpage, _newsconf['main']['index'],
                         _newsconf['main']['headlines'], 0x100, 0x8ff, 0x199)

def newsheadlinesfooter(page, category):
    if category:
        lines = [
            '€T€]€GREGIONAL €CHeadlines€G160€CSport   €G390',
            '€D€]€GNATIONAL€C Main menu€G100€CWeather€G 400',
            red()    + 'Next Page' +
            green()  + 'Top Story' +
            yellow() + 'Reg Sport' +
            blue()   + 'Main Menu'
        ]
    else:
        lines = [
            '€W€]€DGet BBC News on your mobile phone 153',
            '€D€]€CCATCH UP WITH REGIONAL NEWS      €G160',
            red()    + 'News Index' +
            green()  + 'Top Story' +
            yellow() + 'TV/Radio' +
            blue()   + 'Main Menu'
        ]
    line = 22
    for l in lines:
        page.addline(line, ttxutils.decode(l))
        line += 1
    if category:
        page.addfasttext(0x161, 0x161, 0x390, 0x100, 0x8ff, 0x199)
    else:
        page.addfasttext(0x102, 0x104, 0x600, 0x100, 0x8ff, 0x199)

def newsindexfooter(page):
    lines = [
        '€T€]€CSummary€G103€CExtra€G140€CFront page €G100',
        '€D€]€CLottery€G555€CFlash€G150€CRegional   €G160',
        '€ASummary €B1st story €CLocalNews€FMain Menu'
    ]
    line = 22
    for l in lines:
        page.addline(line, ttxutils.decode(l))
        line += 1
    page.addfasttext(0x103, 0x104, 0x160, 0x100, 0x8ff, 0x199)

def newssummaryfooter(page):
    lines = [
        '€D€]€CNews index€G102€CExtra€G140€CWeather €G400',
        '€D€]€CFront page€G100€CTV   €G600€CChildren€G500',
        '€A1st story€BNews Indx€CHeadlines€FMain Menu'
    ]
    line = 22
    for l in lines:
        page.addline(line, ttxutils.decode(l))
        line += 1
    page.addfasttext(0x104, 0x102, 0x101, 0x100, 0x8ff, 0x199)
