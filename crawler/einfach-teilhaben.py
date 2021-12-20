import requests
from bs4 import BeautifulSoup

import re

from datetime import datetime, timedelta
import time

START_URL = "https://www.einfach-teilhaben.de/DE/LS/Home/leichtesprache_node.html"
SUBPAGE_URL = "https://www.einfach-teilhaben.de/DE/LS/Themen/AlterRente/alterrente_node.html"
ARTICLE_URL = "https://www.einfach-teilhaben.de/DE/LS/Themen/AlterRente/RechtlicheBetreuung/rechtlichebetreuung_node.html"

HEADERS = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'}

SCRAPE_DELAY = 5

LAST_SCRAPE = None


def test(url):
    html = get_html_from_url(url)

    text_content = get_text_content(html)

    overview_content = get_overview_content(html)

    if text_content:
        einfache_sprache = extract_text(text_content)
        print("\n\nEINFACHE SPRACHE\n\n", einfache_sprache)

        alltags_url = url.replace('/LS/', '/AS/')

        alltagssprache = extract_text(get_text_content(get_html_from_url(alltags_url)))
        print("\n\nALLTAGSSPRACHE\n\n", alltagssprache)

    if overview_content:
        print("\n\nLinks found on the website:\n\n")
        print(extract_links(overview_content))


def get_text_content(html):
    return html.find('div', {'class': 'small-12 medium-10 large-8 columns'})


def get_overview_content(html):
    return html.find('ul', {'class': 'row small-up-2 medium-up-2 large-up-3 themen__teaser'})


def get_html_from_url(url):
    global LAST_SCRAPE

    if LAST_SCRAPE is not None:
        time_since_last = datetime.now() - LAST_SCRAPE

        sleep_time = timedelta(0, SCRAPE_DELAY) - time_since_last

        if sleep_time >= timedelta(0):
            time.sleep(sleep_time.seconds)

    response = requests.get(url, headers=HEADERS)
    LAST_SCRAPE = datetime.now()

    return BeautifulSoup(response.text, 'html.parser')


def extract_links(content):
    urls = []

    links = content.find_all('a')

    for l in links:
        link = 'https://www.einfach-teilhaben.de/' + l['href']
        link = re.sub(';jsessionid=.*', '', link)
        urls.append(link)

    return urls


def extract_text(content):
    return content.text


if __name__ == '__main__':
    print("START TEST")
    test(START_URL)

    print("SUBPAGE TEST")
    test(SUBPAGE_URL)

    print("ARTICLE TEST")
    test(ARTICLE_URL)
