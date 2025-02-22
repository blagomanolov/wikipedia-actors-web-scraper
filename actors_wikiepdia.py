import json
import re
from http.client import responses
from re import match
from traceback import format_list

import requests
from bs4 import BeautifulSoup

actors: dict = {}

def get_soup(url):
    response = requests.get(url)
    if response.status_code != 200:
        return None
    return BeautifulSoup(response.text, 'html.parser')

def get_wikipedia_actors_by_country(country_name, country_url):
    """Fetches a list of actors from a country's Wikipedia page."""
    base_url = f"https://en.wikipedia.org/wiki/List_of_{country_url}_actors"
    print(base_url)
    soup = get_soup(base_url)

    if not soup:
        return

    check_list_actor = soup.find('span', class_='mw-page-title-main')
    pattern = r'list of .* actors'

    if re.search(pattern, check_list_actor.text.lower().strip()):
        actors[country_name] = {}
        actor_containers = soup.find_all('div', class_='div-col')
        for actor_container in actor_containers:
            uls = actor_container.find_all('ul')
            for ul in uls:
                lis = ul.find_all('li')
                for li in lis:
                    actor_name = li.text if li.text else None
                    actors[country_name][actor_name] = {}
                    actor_url_part = li.find('a')['href'] if li.find('a') else None
                    actor_full_url = f'https://en.wikipedia.org/{actor_url_part}'
                    actor_soup = get_soup(actor_full_url)
                    if actor_soup:
                        actor_films_h2 = actor_soup.find('h2', {'id': 'Filmography'})
                        if actor_films_h2:
                            filmography = []
                            table_with_films = actor_films_h2.parent.find_next_sibling(lambda tag: tag and tag.name in ['table', 'ul'])
                            if table_with_films and table_with_films.name in ['table', 'ul']:
                                if table_with_films.name == 'table':
                                    tbody_container = table_with_films.find('tbody')
                                    if tbody_container:
                                        trs = tbody_container.find_all('tr')
                                        if trs:
                                            for tr in trs:
                                                tds = tr.find_all('td')
                                                if tds and len(tds) > 2:
                                                    filmography.append(tds[1].text.strip())
                                elif table_with_films.name  == 'ul':
                                    lis = table_with_films.find_all('li')
                                    for li in lis:
                                        filmography.append(li.text.strip())
                                actors[country_name][actor_name]['filmography'] = filmography
                        trs = actor_soup.find_all('tr') if actor_soup.find_all('tr') else None
                        if trs:
                            for tr in trs:
                                th = tr.find('th', class_='infobox-label') if tr.find('th', class_='infobox-label') else None
                                td = tr.find('td', class_='infobox-data') if tr.find('td', class_='infobox-data') else None
                                if th:
                                    if 'born' in th.text.lower():
                                        pattern = r'(\(\d{4}-\d{2}-\d{2}\)|\d{1,2} \w+ \d{4})\s*(.*)'
                                        matches = re.findall(pattern, td.text.strip())
                                        if matches:
                                            date = matches[0][0] if matches[0][0] else None
                                            place = matches[0][1] if matches[0][1] else None
                                            actors[country_name][actor_name]['born_date'] = date
                                            actors[country_name][actor_name]['born_place'] = place
                                    if 'active' in th.text.lower():
                                        if td:
                                            actors[country_name][actor_name]['years_of_active'] = td.text.strip() if td.text else None
                                    if 'died' in th.text.lower():
                                        death_date_pattern = r'(\d{1,2} \w+ \d{4})\((\d{4}-\d{2}-\d{2})\)'
                                        aged_death_pattern = r'\(aged\s*(\d+)\)'
                                        place_pattern = r'\(aged\s*\d+\)\s*([A-Za-zÀ-ÖØ-öø-ÿ ,.-]+)'
                                        place_matches = re.findall(place_pattern, td.text.strip())
                                        date_matches = re.findall(death_date_pattern, td.text.strip())
                                        aged_matches = re.findall(aged_death_pattern, td.text.strip())
                                        if date_matches:
                                            date_of_death = date_matches[0][1] if date_matches[0][1] else None
                                            actors[country_name][actor_name]['date_of_death'] = date_of_death
                                        if aged_matches:
                                            aged_of_death = aged_matches[0] if aged_matches[0][1] else None
                                            actors[country_name][actor_name]['aged_of_death'] = aged_of_death
                                        if place_matches:
                                            place_of_death = place_matches[0]
                                            actors[country_name][actor_name]['place_of_death'] = place_of_death

                    if 'filmography' not in actors[country_name][actor_name]:
                        actors[country_name][actor_name]['filmography'] = None
                    if 'born_date' not in actors[country_name][actor_name]:
                        actors[country_name][actor_name]['born_date'] = None
                    if 'born_place' not in actors[country_name][actor_name]:
                        actors[country_name][actor_name]['born_place'] = None
                    if 'date_of_death' not in actors[country_name][actor_name]:
                        actors[country_name][actor_name]['date_of_death'] = None
                    if 'aged_of_death' not in actors[country_name][actor_name]:
                        actors[country_name][actor_name]['aged_of_death'] = None
                    if 'place_of_death' not in actors[country_name][actor_name]:
                        actors[country_name][actor_name]['place_of_death'] = None
                    if 'years_of_active' not in actors[country_name][actor_name]:
                        actors[country_name][actor_name]['years_of_active'] = None


    else:
        return




# Example usage for "American" actors
country_to_demonym = {
    "Afghanistan": "Afghan",
    "Albania": "Albanian",
    "Algeria": "Algerian",
    "Andorra": "Andorran",
    "Angola": "Angolan",
    "Antigua and Barbuda": "Antiguan",
    "Argentina": "Argentine",
    "Armenia": "Armenian",
    "Australia": "Australian",
    "Austria": "Austrian",
    "Azerbaijan": "Azerbaijani",
    "Bahamas": "Bahamian",
    "Bahrain": "Bahraini",
    "Bangladesh": "Bangladeshi",
    "Barbados": "Barbadian",
    "Belarus": "Belarusian",
    "Belgium": "Belgian",
    "Belize": "Belizean",
    "Benin": "Beninese",
    "Bhutan": "Bhutanese",
    "Bolivia": "Bolivian",
    "Bosnia and Herzegovina": "Bosnian",
    "Botswana": "Botswanan",
    "Brazil": "Brazilian",
    "Brunei": "Bruneian",
    "Bulgaria": "Bulgarian",
    "Burkina Faso": "Burkinabe",
    "Burundi": "Burundian",
    "Cambodia": "Cambodian",
    "Cameroon": "Cameroonian",
    "Canada": "Canadian",
    "Cape Verde": "Cape Verdean",
    "Central African Republic": "Central African",
    "Chad": "Chadian",
    "Chile": "Chilean",
    "China": "Chinese",
    "Colombia": "Colombian",
    "Comoros": "Comorian",
    "Congo": "Congolese",
    "Costa Rica": "Costa Rican",
    "Croatia": "Croatian",
    "Cuba": "Cuban",
    "Cyprus": "Cypriot",
    "Czech Republic": "Czech",
    "Denmark": "Danish",
    "Djibouti": "Djiboutian",
    "Dominica": "Dominican",
    "Dominican Republic": "Dominican",
    "Ecuador": "Ecuadorian",
    "Egypt": "Egyptian",
    "El Salvador": "Salvadoran",
    "Equatorial Guinea": "Equatoguinean",
    "Eritrea": "Eritrean",
    "Estonia": "Estonian",
    "Eswatini": "Swazi",
    "Ethiopia": "Ethiopian",
    "Fiji": "Fijian",
    "Finland": "Finnish",
    "France": "French",
    "Gabon": "Gabonese",
    "Gambia": "Gambian",
    "Georgia": "Georgian",
    "Germany": "German",
    "Ghana": "Ghanaian",
    "Greece": "Greek",
    "Grenada": "Grenadian",
    "Guatemala": "Guatemalan",
    "Guinea": "Guinean",
    "Guinea-Bissau": "Bissau-Guinean",
    "Guyana": "Guyanese",
    "Haiti": "Haitian",
    "Honduras": "Honduran",
    "Hungary": "Hungarian",
    "Iceland": "Icelandic",
    "India": "Indian",
    "Indonesia": "Indonesian",
    "Iran": "Iranian",
    "Iraq": "Iraqi",
    "Ireland": "Irish",
    "Israel": "Israeli",
    "Italy": "Italian",
    "Ivory Coast": "Ivorian",
    "Jamaica": "Jamaican",
    "Japan": "Japanese",
    "Jordan": "Jordanian",
    "Kazakhstan": "Kazakh",
    "Kenya": "Kenyan",
    "Kiribati": "I-Kiribati",
    "Kosovo": "Kosovar",
    "Kuwait": "Kuwaiti",
    "Kyrgyzstan": "Kyrgyz",
    "Laos": "Lao",
    "Latvia": "Latvian",
    "Lebanon": "Lebanese",
    "Lesotho": "Basotho",
    "Liberia": "Liberian",
    "Libya": "Libyan",
    "Liechtenstein": "Liechtensteiner",
    "Lithuania": "Lithuanian",
    "Luxembourg": "Luxembourgish",
    "Madagascar": "Malagasy",
    "Malawi": "Malawian",
    "Malaysia": "Malaysian",
    "Maldives": "Maldivian",
    "Mali": "Malian",
    "Malta": "Maltese",
    "Marshall Islands": "Marshallese",
    "Mauritania": "Mauritanian",
    "Mauritius": "Mauritian",
    "Mexico": "Mexican",
    "Micronesia": "Micronesian",
    "Moldova": "Moldovan",
    "Monaco": "Monegasque",
    "Mongolia": "Mongolian",
    "Montenegro": "Montenegrin",
    "Morocco": "Moroccan",
    "Mozambique": "Mozambican",
    "Myanmar": "Burmese",
    "Namibia": "Namibian",
    "Nauru": "Nauruan",
    "Nepal": "Nepali",
    "Netherlands": "Dutch",
    "New Zealand": "New Zealand",
    "Nicaragua": "Nicaraguan",
    "Niger": "Nigerien",
    "Nigeria": "Nigerian",
    "North Korea": "North Korean",
    "North Macedonia": "Macedonian",
    "Norway": "Norwegian",
    "Oman": "Omani",
    "Pakistan": "Pakistani",
    "Palau": "Palauan",
    "Panama": "Panamanian",
    "Papua New Guinea": "Papua New Guinean",
    "Paraguay": "Paraguayan",
    "Peru": "Peruvian",
    "Philippines": "Filipino",
    "Poland": "Polish",
    "Portugal": "Portuguese",
    "Qatar": "Qatari",
    "Romania": "Romanian",
    "Russia": "Russian",
    "Rwanda": "Rwandan",
    "Saint Kitts and Nevis": "Kittitian",
    "Saint Lucia": "Saint Lucian",
    "Saint Vincent and the Grenadines": "Vincentian",
    "Samoa": "Samoan",
    "San Marino": "Sammarinese",
    "Sao Tome and Principe": "Sao Tomean",
    "Saudi Arabia": "Saudi",
    "Scotland": "Scottish",
    "Senegal": "Senegalese",
    "Serbia": "Serbian",
    "Seychelles": "Seychellois",
    "Sierra Leone": "Sierra Leonean",
    "Singapore": "Singaporean",
    "Slovakia": "Slovak",
    "Slovenia": "Slovene",
    "Solomon Islands": "Solomon Islander",
    "Somalia": "Somali",
    "South Africa": "South African",
    "South Korea": "South Korean",
    "Spain": "Spanish",
    "Sri Lanka": "Sri Lankan",
    "Sudan": "Sudanese",
    "Suriname": "Surinamese",
    "Sweden": "Swedish",
    "Switzerland": "Swiss",
    "Syria": "Syrian",
    "Taiwan": "Taiwanese",
    "Tajikistan": "Tajik",
    "Tanzania": "Tanzanian",
    "Thailand": "Thai",
    "Togo": "Togolese",
    "Tonga": "Tongan",
    "Trinidad and Tobago": "Trinidadian",
    "Tunisia": "Tunisian",
    "Turkey": "Turkish",
    "Turkmenistan": "Turkmen",
    "Tuvalu": "Tuvaluan",
    "Uganda": "Ugandan",
    "Ukraine": "Ukrainian",
    "United Arab Emirates": "Emirati",
    "United Kingdom": "British",
    "United States": "American",
    "Uruguay": "Uruguayan",
    "Uzbekistan": "Uzbek",
    "Vanuatu": "Ni-Vanuatu",
    "Vatican City": "Vatican",
    "Venezuela": "Venezuelan",
    "Vietnam": "Vietnamese",
    "Wales": "Welsh",
    "Yemen": "Yemeni",
    "Zambia": "Zambian",
    "Zimbabwe": "Zimbabwean"
}
for country, url_part in country_to_demonym.items():
    get_wikipedia_actors_by_country(country, url_part)
    sorted_data = {country: {actor: dict(sorted(details.items())) for actor, details in sorted(actors.items())}
                   for country, actors in sorted(actors.items())}

    if actors != {}:
        if actors[country] != {}:
            file_path = f'actors_by_country/actors_data_{country}.json'
            with open(file_path, 'w') as j:
                json.dump(sorted_data, j, indent=4)
    actors.clear()
