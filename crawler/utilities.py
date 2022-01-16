import requests
from bs4 import BeautifulSoup
from bs4.element import ResultSet
import os
import urllib
from pathlib import Path
import json
import re
from collections.abc import Callable

from datetime import datetime, timedelta, date
import time


HEADERS = {
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:94.0) Gecko/20100101 Firefox/94.0'}

SCRAPE_DELAY = 5

LAST_SCRAPE = None


def read_soup(url: str):
    filepath = get_crawled_path_from_url(url)

    if os.path.exists(filepath):
        with open(filepath, "r", encoding="utf-8") as f:
            soup = BeautifulSoup(f, 'html.parser')
    else:
        soup = get_soup_from_url(url)

    return soup


def save_parallel_soup(normal_soup, normal_url: str, easy_soup, easy_url: str, publication_date=None):
    normal_filepath = get_crawled_path_from_url(normal_url)
    easy_filepath = get_crawled_path_from_url(easy_url)

    save_soup(normal_soup, normal_filepath)
    save_header(normal_filepath, normal_url,
                easy_filepath, publication_date)

    save_soup(easy_soup, easy_filepath)
    save_header(easy_filepath, easy_url,
                easy_filepath, publication_date)


def save_soup(soup, filepath: Path):
    if not os.path.exists(filepath.parent):
        os.makedirs(filepath.parent)

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(soup.prettify())
    # else:
    #     log_resaving_file(filepath)


def load_header(url):
    headerpath = get_headerpath_from_url(url)
    # save header information
    if os.path.exists(headerpath):
        with open(headerpath, "r") as f:
            header = json.load(f)
    else:
        header = {}
    return header


def save_header(filepath, url: str, matching_filepath: Path, publication_date=None):
    key = filepath.name
    headerpath = get_headerpath_from_url(url)

    if not os.path.exists(filepath.parent):
        os.makedirs(filepath.parent)

    # save header information
    if os.path.exists(headerpath):
        with open(headerpath, "r") as f:
            header = json.load(f)
    else:
        header = {}

    # if the file was already downloaded and used, simply append to the list
    if key in header.keys():
        header[key]["matching_files"].append(matching_filepath.name)
    else:
        header[key] = {
            "url": url,
            "crawl_date": str(date.today()),
            "publication_date": publication_date,
            "matching_files": [matching_filepath.name]
        }
    with open(headerpath, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=4)


def get_headerpath_from_url(url: str) -> Path:
    return Path(urllib.parse.urlparse(url).netloc, "header.json")


def get_names_from_url(url: str) -> [str, str]:
    parsed_url = urllib.parse.urlparse(url)
    foldername = parsed_url.netloc
    filename = parsed_url.netloc + parsed_url.path.replace("/", "__")
    if not filename.endswith(".html"):
        filename += ".html"
    if not foldername.startswith("www."):
        foldername = "www." + foldername
    return foldername, filename


def get_parsed_path_from_url(url: str) -> Path:
    foldername, filename = get_names_from_url(url)
    return Path(foldername, "parsed", filename + ".txt")


def get_crawled_path_from_url(url: str) -> Path:
    foldername, filename = get_names_from_url(url)
    return Path(foldername, "crawled", filename)


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
        link = parse_url(l["href"], base_url)
        urls.append(link)

    urls = list(set(urls))
    return urls


def parse_url(url, base_url):
    if base_url not in url:
        url = urllib.parse.urljoin(base_url, url)
    return url


def parse_soup(base_url, parser: Callable[[BeautifulSoup], BeautifulSoup]):
    header = load_header(base_url)
    for filename in header.keys():
        url = header[filename]["url"]
        soup = read_soup(url)
        parsed_content = parser(soup)
        if not parsed_content:
            continue

        path = get_parsed_path_from_url(url)
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)
        with open(path, "w", encoding="utf-8") as f:
            for i, tag in enumerate(parsed_content.contents):
                for j, sentence in enumerate(tag.get_text().split(".")):
                    # clean up of sentences
                    sentence = re.sub("\n", " ", sentence)
                    sentence = re.sub(" +", " ", sentence)
                    sentence = sentence.strip()
                    # remove empty lines
                    if not sentence:
                        continue
                    # add punctuation if necessary
                    if not sentence[-1] in [".", ":", "?", "!"]:
                        sentence += "."
                    # if the sentence is only a single word, merge it with the following one
                    if not " " in sentence:
                        f.write(f"{sentence}")
                    else:
                        f.write(f"{sentence}\n")


def filter_urls(urls: list, base_url: str) -> list:
    """ Removes urls that have already been crawled
    """
    file_path = get_crawled_path_from_url(urls[0])
    header_path = get_headerpath_from_url(url)

    # remove urls leaving the website
    urls = [url for url in urls if base_url in url]
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)
            keys = header.keys()
            # remove already downloaded urls
            urls = [url for url in urls if url not in keys]
    return urls


def get_log_path_from_url(url: str):
    return Path(urllib.parse.urlparse(url).netloc, "log.txt")


def log_missing_url(url: str):
    if not already_logged(url):
        path = get_log_path_from_url(url)
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)

        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(f"{current_time} No matching url found for: {url}\n")


def log_multiple_url(url: str):
    if not already_logged(url):
        path = get_headerpath_from_url(url)
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)
        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(
                f"{current_time} More than one matching url found for: {url}\n")


# TODO this method may be removed
def log_resaving_file(filepath: Path):
    foldername = filepath.parent
    filename = filepath.name
    if not already_logged(filename):
        path = get_headerpath_from_url(url)
        if not os.path.exists(path.parent):
            os.makedirs(path.parent)
        with open(path, "a", encoding="utf-8") as f:
            current_time = datetime.now().isoformat(timespec="seconds")
            f.write(
                f"{current_time} The file is used for several matches: {filename}\n")


def already_logged(url: str) -> bool:
    path = get_headerpath_from_url(url)
    if os.path.exists(path):
        with open(path, "r") as f:
            content = f.read()
            return bool(url in content)
