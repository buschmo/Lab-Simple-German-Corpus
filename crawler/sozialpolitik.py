import requests
from bs4 import BeautifulSoup
import os
import urllib
from pathlib import Path
import json

from datetime import datetime, timedelta, date
import time

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'}

SCRAPE_DELAY = 5

LAST_SCRAPE = None


def read_soup(url, foldername, filename=None):
    if not filename:
        parsed_url = urllib.parse.urlparse(url)
        filename = parsed_url.netloc + parsed_url.path.replace("/", "__")

    filepath = Path(foldername, filename)
    headerpath = Path(foldername, "header.json")
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            soup = BeautifulSoup(text, 'html.parser')
    else:
        soup = get_soup_from_url(url)
        
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(soup.prettify())

        if os.path.exists(headerpath):
            with open(headerpath, "r") as f:
                header = json.load(f)
        else:
            header = {}
        header[url]= {
            "filename": filename,
            "crawl_date": str(date.today()),
            "publication_date": None,
        }
        with open(headerpath, "w", encoding="utf-8") as f:
            json.dump(header, f, indent=4)

    return soup


def get_soup_from_url(url):
    global LAST_SCRAPE
    if LAST_SCRAPE is not None:
        time_since_last = datetime.now() - LAST_SCRAPE

        sleep_time = timedelta(0, SCRAPE_DELAY) - time_since_last

        if sleep_time >= timedelta(0):
            time.sleep(sleep_time.seconds)

    response = requests.get(url, headers=HEADERS)
    LAST_SCRAPE = datetime.now()

    return BeautifulSoup(response.text, 'html.parser')


def get_urls_from_soup(soup):
    themen = soup.find("section", {"class": "element-col bg-weiss"})
    links = themen.find_all("a")

    url = "https://www.sozialpolitik.com/"
    urls = []
    for l in links:
        link = urllib.parse.urljoin(url, l['href'])
        urls.append(link)
    return urls


def main():
    normal_url = "https://www.sozialpolitik.com/"
    easy_url = "https://www.sozialpolitik.com/es/"
    foldername = "sozialpolitik"

    soup = read_soup(normal_url, foldername)
    normal_urls = get_urls_from_soup(soup)

    soup = read_soup(easy_url, foldername)
    easy_urls = get_urls_from_soup(soup)

    for i in range(len(easy_urls)):
        url = normal_urls[i]
        read_soup(url, foldername)

        # to use the same title
        parsed_url = urllib.parse.urlparse(url)
        filename = parsed_url.netloc + "__es" + \
            parsed_url.path.replace("/", "__")
        url = easy_urls[i]
        read_soup(url, foldername, filename)


if __name__ == '__main__':
    main()
