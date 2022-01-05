import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet
import os
import urllib
from pathlib import Path
import json
import re

from datetime import datetime, timedelta, date
import time

""" Scrapes news from mdr.de
"""


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'}

SCRAPE_DELAY = 5

LAST_SCRAPE = None


def read_soup(url: str):
    foldername, filename = url_to_paths(url)

    filepath = Path(foldername, filename)
    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            text = f.read()
            soup = BeautifulSoup(text, 'html.parser')
    else:
        soup = get_soup_from_url(url)

    return soup


def save_parallel_soup(normal_soup, normal_url: str, easy_soup, easy_url: str, publication_date=None):
    normal_foldername, normal_filename = url_to_paths(normal_url)
    easy_foldername, easy_filename = url_to_paths(easy_url)

    filepath = Path(normal_foldername, normal_filename)
    save_soup(normal_soup, filepath)
    save_header(filepath, normal_url, publication_date, easy_filename)

    filepath = Path(easy_foldername, easy_filename)
    save_soup(easy_soup, filepath)
    save_header(filepath, easy_url, publication_date, normal_filename)


def save_soup(soup, filepath: Path):
    if not os.path.exists(filepath.parent):
        os.mkdir(filepath.parent)

    if filepath.suffix != ".html":
        filepath = Path(str(filepath)+".html")

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(soup.prettify())
    else:
        log_resaving_file(filepath)


def save_header(filepath, url: str, publication_date, matching_file):
    headerpath = Path(filepath.parent, "header.json")

    if not os.path.exists(filepath.parent):
        os.mkdir(filepath.parent)

    # save header information
    if os.path.exists(headerpath):
        with open(headerpath, "r") as f:
            header = json.load(f)
    else:
        header = {}

    # if the file was already downloaded and used, simply append to the list
    if url in header.keys():
        header[url]["matching_file"].append(matching_file)
    else:
        header[url] = {
            "filename": filepath.name,
            "crawl_date": str(date.today()),
            "publication_date": publication_date,
            "matching_file": [matching_file]
        }
    with open(headerpath, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=4)


def url_to_paths(url: str):
    parsed_url = urllib.parse.urlparse(url)
    filename = parsed_url.netloc + parsed_url.path.replace("/", "__")
    foldername = urllib.parse.urlparse(url).netloc
    return foldername, filename


def get_soup_from_url(url: str):
    global LAST_SCRAPE
    if LAST_SCRAPE is not None:
        time_since_last = datetime.now() - LAST_SCRAPE

        sleep_time = timedelta(0, SCRAPE_DELAY) - time_since_last

        if sleep_time >= timedelta(0):
            time.sleep(sleep_time.seconds)

    response = requests.get(url, headers=HEADERS)
    LAST_SCRAPE = datetime.now()

    return BeautifulSoup(response.text, 'html.parser')


def get_urls_from_soup(soup, base_url: str, filter_args: dict = {}, recursive_filter_args: dict = {}) -> list[str]:
    if filter_args:
        blocks = soup.find_all(**filter_args)
        if recursive_filter_args:
            blocks = [block for block in blocks if block.find(
                **recursive_filter_args)]
    else:
        blocks = [soup]

    links = []
    for block in blocks:
        links.extend(block.find_all("a", href=True))

    urls = []
    for l in links:
        link = urllib.parse.urljoin(base_url, l['href'])
        urls.append(link)

    urls = list(set(urls))
    return urls


def parse_url(url, base_url):
    url = urllib.parse.urljoin(base_url, url)
    return url 


def filter_urls(urls: list, base_url: str) -> list:
    """ Removes urls that have already been crawled
    """
    foldername, filename = url_to_paths(urls[0])
    header_path = Path(foldername, "header.json")

    # remove urls leaving the website
    urls = [url for url in urls if base_url in url]
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)
            keys = header.keys()
            # remove already downloaded urls
            urls = [url for url in urls if url not in keys]
    return urls


def log_missing_url(url: str):
    if not already_logged(url):
        foldername, _ = url_to_paths(url)
        path = Path(foldername, "log.txt")
        if not os.path.exists(foldername):
            os.mkdir(foldername)

        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(f"{current_time} No matching url found for: {url}\n")


def log_multiple_url(url: str):
    if not already_logged(url):
        foldername, _ = url_to_paths(url)
        path = Path(foldername, "log.txt")
        if not os.path.exists(foldername):
            os.mkdir(foldername)
        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(
                f"{current_time} More than one matching url found for: {url}\n")


def log_resaving_file(filepath: Path):
    foldername = filepath.parent
    filename = filepath.name
    if not already_logged(filename):
        # print(f"File {str(filepath)} already exists.")
        path = Path(foldername, "log.txt")
        if not os.path.exists(foldername):
            os.mkdir(foldername)
        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(
                f"{current_time} The file is used for several matches: {filename}\n")


def already_logged(identifier: str) -> bool:
    foldername, _ = url_to_paths(identifier)
    path = Path(foldername, "log.txt")
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
            return bool(identifier in content)
