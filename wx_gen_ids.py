import metoffer
import pprint

key = ""  # Met Office API key
M = metoffer.MetOffer(key)


def ids_of(sitelist):
    try:
        sites = [
            (s["name"], s["id"]) for s in sitelist["Locations"]["Location"]
        ]
    except KeyError:
        sites = [
            (s["@name"], s["@id"]) for s in sitelist["Locations"]["Location"]
        ]
    return dict(sites)


def print_cities(forecast_sites):

    cities = [
        "Inverness",
        "Pitlochry",
        "Edinburgh",
        "Newcastle Upon Tyne",
        "Manchester",
        "Belfast",
        "Birmingham",
        "Cardiff",
        "Plymouth",
        "Cambridge",
        "London",
    ]

    city_ids = dict()
    for c in cities:
        city_ids[c.lower().split()[0]] = forecast_sites[c]

    print("city_ids = ", end="")
    pprint.pprint(city_ids)
    print()


def print_region_locs(forecast_sites):
    region_locs = [
        ("Mallaig", "highlands"),
        ("Aberdeen", "grampian"),
        ("Dundee", "tayside"),
        ("Livingston", "central"),
        ("Cookstown", "nireland"),
        ("Durham", "northeast"),
        ("Preston", "northwest"),
        ("Selby", "yorks"),
        ("Machynlleth", "wales"),
        ("Stoke", "midlands"),
        ("Stroud", "west"),
        ("Thetford", "east"),
        ("Winchester", "south"),
        ("Royal Tunbridge Wells", "southeast"),
        ("Launceston", "southwest"),
    ]

    region_ids = dict()
    for c, r in region_locs:
        region_ids[r] = forecast_sites[c]

    print("region_ids = ", end="")
    pprint.pprint(region_ids)
    print()


def print_regions():
    region_ids = ids_of(
        M.text_forecast(metoffer.REGIONAL_FORECAST, metoffer.SITELIST)
    )

    region_txt = [
        ("he", "highlands"),
        ("gr", "grampian"),
        ("ta", "tayside"),
        ("st", "central"),
        ("dg", "borders"),
        ("ni", "nireland"),
        ("ne", "northeast"),
        ("nw", "northwest"),
        ("yh", "yorks"),
        ("wl", "wales"),
        ("wm", "wmidlands"),
        ("em", "emidlands"),
        ("wm", "west"),
        ("ee", "east"),
        ("sw", "south"),
        ("se", "southeast"),
        ("sw", "southwest"),
        ("uk", "uk"),
    ]

    regions = dict()
    for abbr, region in region_txt:
        regions[abbr] = region_ids[abbr]
    print("regions = ", end="")
    pprint.pprint(regions)
    print()


def print_obs():
    observation_sites = ids_of(M.loc_observations(metoffer.SITELIST))

    obs_locs = [
        ("Aberdeen", "Aberdeen Airport"),
        ("Aberdaron", "Aberdaron"),
        ("Belfast", "Belfast International Airport"),
        ("Birmingham", "Coleshill"),
        ("Bristol", "Lyneham"),
        ("Cardiff", "St-Athan"),
        ("Eastbourne", "Herstmonceux West End"),
        ("Edinburgh", "Edinburgh/Gogarbank"),
        ("Glasgow", "Glasgow/Bishopton"),
        ("Inverness", "Aviemore"),
        ("Ipswich", "Wattisham"),
        ("Isle of Man", "Ronaldsway"),
        ("Leeds", "Bingley Samos"),
        ("Lerwick", "Lerwick (S. Screen)"),
        ("Lincoln", "Waddington"),
        ("London", "Northolt"),
        ("Manchester", "Rostherne No 2"),
        ("Margate", "Manston"),
        ("Norwich", "Weybourne"),
        ("Newcastle", "Albemarle"),
        ("Newquay", "Camborne"),
        ("Oxford", "Benson"),
        ("Peterborough", "Wittering"),
        ("Plymouth", "Mount Batten"),
        ("St Andrews", "Leuchars"),
        ("St Helier", "Jersey"),
        ("Salisbury", "Boscombe Down"),
        ("Shrewsbury", "Shawbury"),
        ("Southampton", "Middle Wallop"),
        ("York", "Linton On Ouse"),
    ]

    observation_ids = dict()
    for name, loc in obs_locs:
        observation_ids[name] = observation_sites[loc]

    print("observation_ids = ", end="")
    pprint.pprint(observation_ids)
    print()


def print_fivedays(forecast_sites):

    fivedays = [
        ("Aberdeen", "Aberdeen"),
        ("Aberystwyth", "Aberystwyth"),
        ("Llangefni", "Anglesey"),
        ("Ayr", "Ayr"),
        ("Belfast", "Belfast"),
        ("Birmingham", "Birmingham"),
        ("Bristol", "Bristol"),
        ("Cardiff", "Cardiff"),
        ("Carlisle", "Carlisle"),
        ("Douglas (Isle Of Man)", "Douglas, I of Man"),
        ("Dover", "Dover"),
        ("Edinburgh", "Edinburgh"),
        ("Exeter", "Exeter"),
        ("Glasgow", "Glasgow"),
        ("Hull", "Hull"),
        ("Inverness", "Inverness"),
        ("Leeds", "Leeds"),
        ("Lerwick", "Lerwick"),
        ("Lincoln", "Lincoln"),
        ("Liverpool", "Liverpool"),
        ("London", "London"),
        ("Londonderry (Derry)", "Londonderry"),
        ("Manchester", "Manchester"),
        ("Newcastle Upon Tyne", "Newcastle"),
        ("Norwich", "Norwich"),
        ("Nottingham", "Nottingham"),
        ("Oban", "Oban"),
        ("Penzance", "Penzance"),
        ("Peterborough", "Peterborough"),
        ("Plymouth", "Plymouth"),
        ("St Helier", "St Helier"),
        ("St Peter Port", "St Peter Port"),
        ("Salisbury", "Salisbury"),
        ("Scarborough", "Scarborough"),
        ("Sheffield", "Sheffield"),
        ("Shrewsbury", "Shrewsbury"),
        ("Southampton", "Southampton"),
        ("Stranraer", "Stranraer"),
        ("Worcester", "Worcester"),
        ("York", "York"),
    ]

    fiveday_ids = dict()
    for real, screen in fivedays:
        fiveday_ids[screen] = forecast_sites[real]

    print("fiveday_ids = ", end="")
    pprint.pprint(fiveday_ids)
    print()


def main():
    forecast_sites = ids_of(M.loc_forecast(metoffer.SITELIST, ""))
    print_cities(forecast_sites)
    print_region_locs(forecast_sites)
    print_regions()
    print_obs()
    print_fivedays(forecast_sites)


if __name__ == "__main__":
    main()
