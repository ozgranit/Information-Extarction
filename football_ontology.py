import requests
import lxml.html
import rdflib


# aux func
def clean_string(some_str):
    #some_str = "".join(some_str.splitlines())
    return some_str.strip().replace("\n", "").replace(" ", "_")


wiki_prefix = "http://en.wikipedia.org"
example_prefix = "http://example.org/"

# i use global ontology for faster run time
ontology = rdflib.Graph()

# player edges
playsFor_edge = rdflib.URIRef(example_prefix + "playsFor")
birthPlace_edge = rdflib.URIRef(example_prefix + "birthPlace")
birthDate_edge = rdflib.URIRef(example_prefix + "birthDate")
position_edge = rdflib.URIRef(example_prefix + "position")

# team edges
league_edge = rdflib.URIRef(example_prefix + "league")
homeCity_edge = rdflib.URIRef(example_prefix + "homeCity")

# league edges
country_edge = rdflib.URIRef(example_prefix + "country")

# city edges
located_in_edge = rdflib.URIRef(example_prefix + "located_in")


def get_player_info(url, player):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    wiki_infobox = doc.xpath("//table[contains(@class, 'infobox')]")
    try:
        # date of birth
        b = wiki_infobox[0].xpath("//table//th[contains(text(), 'Date of birth')]")
        date = b[0].xpath("./../td//span[@class='bday']//text()")[0]
        date = clean_string(date)
        dob = rdflib.Literal(date, datatype=rdflib.XSD.date)
        ontology.add((player, birthDate_edge, dob))
    except:
        pass
    try:
        # place of birth
        c = wiki_infobox[0].xpath("//table//th[contains(text(), 'Place of birth')]")
        pob_str = c[0].xpath("./../td//a/text()")[0]
        pob_str = clean_string(pob_str)
        pob = rdflib.URIRef(example_prefix + pob_str)
        ontology.add((player, birthPlace_edge, pob))
        try:
            pob_link = wiki_prefix + c[0].xpath("./../td//a/@href")[0]
            get_city_info(pob_link, pob)
        except:
            pass
    except:
        pass
    try:
        # player position
        d = wiki_infobox[0].xpath("//table//th[contains(text(), 'Playing position')]")
        str_pos = d[0].xpath("./../td//a/text()")[0].replace(" ", "_")
        str_pos = clean_string(str_pos)
        player_pos = rdflib.URIRef(example_prefix + str_pos)
        ontology.add((player, position_edge, player_pos))
    except:
        pass


def get_city_info(url, city):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)

    try:
        wiki_infobox = doc.xpath("//table[contains(@class, 'infobox')]")[0]
        country = wiki_infobox.xpath("//table//th[contains(.,'country')] | //table//th[contains(.,'Country')]")

        try:
            country_str = country[0].xpath("./../td//a//text()")[0].replace(" ", "_")
        except IndexError:
            country_str = country[0].xpath("./../td//text()")[0].replace(" ", "_")

    except IndexError:
        return None
    country = rdflib.URIRef(example_prefix + country_str)
    ontology.add((city, located_in_edge, country))
    return country


def get_team_info(url, team):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    playerTable = doc.xpath(
        "(//table[.//th/text()[contains(., 'Position')] and .//th/text()[contains(., 'Player')]])[not(position("
        ")>3)]/tbody/tr")

    for i in range(1, len(playerTable)):
        try:
            row = playerTable[i].xpath(".//text()")
            new_row = [x for x in row if x != '\n']

            player_str = clean_string(new_row[2])
            player = rdflib.URIRef(example_prefix + player_str)
            player_url = wiki_prefix + playerTable[i].xpath(".//@href")[2]

            if team is not None:
                ontology.add((player, playsFor_edge, team))
            get_player_info(player_url, player)
        except IndexError:
            continue


def get_league_info(url):
    res = requests.get(url)
    doc = lxml.html.fromstring(res.content)
    teamTable = doc.xpath(
        "//table[.//th/text() [contains(., 'Team')] and .//th/text() [contains(., 'Location')]]/tbody/tr")

    league_name = doc.xpath("//h1[@id='firstHeading']/text()")[0].replace(" ", "_")
    league = rdflib.URIRef(example_prefix + league_name)

    for i in range(1, len(teamTable)):
        try:
            print("team#" + str(i))
            row = teamTable[i].xpath(".//text()")
            new_row = [x for x in row if x != '\n']

            team_str = clean_string(new_row[0])
            team = rdflib.URIRef(example_prefix + team_str)
            team_url = wiki_prefix + teamTable[i].xpath(".//td[1]//@href")[0]

            city_str = clean_string(new_row[1])
            city = rdflib.URIRef(example_prefix + city_str)
            city_url = wiki_prefix + teamTable[i].xpath(".//td[2]//@href")[0]

            ontology.add((team, league_edge, league))
            ontology.add((team, homeCity_edge, city))
            # country is a URIref or None
            country = get_city_info(city_url, city)
            get_team_info(team_url, team)
            # maybe add different countries to the same league, that is ok
            if country is not None:
                ontology.add((league, country_edge, country))
        except IndexError:
            continue


if __name__ == '__main__':
    print("running...")

    get_league_info("https://en.wikipedia.org/wiki/2019%E2%80%9320_Premier_League")
    ontology.serialize("ontology.nt", format="nt")

    print("done.")
