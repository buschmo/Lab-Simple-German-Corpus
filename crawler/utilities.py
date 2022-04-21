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

from_archive = False


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
                easy_filepath, False, publication_date)

    save_soup(easy_soup, easy_filepath)
    save_header(easy_filepath, easy_url,
                normal_filepath, True, publication_date)


def save_soup(soup, filepath: Path):
    if not os.path.exists(filepath.parent):
        os.makedirs(filepath.parent)

    if not os.path.exists(filepath):
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(soup.prettify())
    # else:
    #     log_resaving_file(filepath)


def load_header(url: str) -> dict:
    headerpath = get_headerpath_from_url(url)
    # save header information
    if os.path.exists(headerpath):
        with open(headerpath, "r") as f:
            header = json.load(f)
    else:
        header = {}
    return header


def save_header(filepath, url: str, matching_filepath: Path, bool_easy: bool = False, publication_date=None):
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
        if matching_filepath.name not in header[key]["matching_files"]:
            header[key]["matching_files"].append(matching_filepath.name)
    else:
        header[key] = {
            "url": url,
            "crawl_date": str(date.today()),
            "easy": bool_easy,
            "publication_date": publication_date,
            "matching_files": [matching_filepath.name]
        }
    with open(headerpath, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=4)


def remove_header_entry(url: str, main_key: str):
    """ Removes an entry and deletes all corresponding files.
    """
    header = load_header(url)
    # already deleted
    if not main_key in header.keys():
        return

    # delete crawled file
    crawled_path = get_crawled_path_from_url(header[main_key]["url"])
    if os.path.exists(crawled_path):
        os.remove(crawled_path)
    # delete parsed file
    parsed_path = get_parsed_path_from_url(header[main_key]["url"])
    if os.path.exists(parsed_path):
        os.remove(parsed_path)

    matching_files = header[main_key]["matching_files"]
    for key in matching_files:
        header[key]["matching_files"].remove(main_key)
        # remove files with no matching files
        if not header[key]["matching_files"]:
            # delete crawled file
            crawled_path = get_crawled_path_from_url(header[key]["url"])
            if os.path.exists(crawled_path):
                os.remove(crawled_path)
            # delete parsed file
            parsed_path = get_parsed_path_from_url(header[key]["url"])
            if os.path.exists(parsed_path):
                os.remove(parsed_path)
            del header[key]

    del header[main_key]
    headerpath = get_headerpath_from_url(url)
    with open(headerpath, "w", encoding="utf-8") as f:
        json.dump(header, f, indent=4)


def get_names_from_url(url: str) -> [str, str]:
    if from_archive:
        if "//web.archive.org/web/" in url:
            url = re.sub("\w+://web.archive.org/web/\d+/", "", url)
    if not url.startswith("http"):
        print(f"{url} did not specify a scheme, thus it will be added.")
        url = "https://" + url
    parsed_url = urllib.parse.urlparse(url)
    foldername = parsed_url.netloc
    filename = parsed_url.netloc + parsed_url.path.replace("/", "__")
    if not filename.endswith(".html"):
        filename += ".html"
    if filename.endswith("__.html"):
        filename = filename[:-len("__.html")] + ".html"
    if filename.startswith("www."):
        filename = filename[4:]
    if not foldername.startswith("www."):
        foldername = "www." + foldername
    return foldername, filename


def get_headerpath_from_url(url: str, parsed: bool = False) -> Path:
    foldername, _ = get_names_from_url(url)
    if parsed:
        return Path("Datasets", foldername, "parsed_header.json")
    elif from_archive:
        return Path("Datasets", foldername, "archive_header.json")
    else:
        return Path("Datasets", foldername, "header.json")


def get_log_path_from_url(url: str):
    foldername, _ = get_names_from_url(url)
    return Path("Datasets", foldername, "log.txt")


def get_parsed_path_from_url(url: str) -> Path:
    foldername, filename = get_names_from_url(url)
    return Path("Datasets", foldername, "parsed", filename + ".txt")


def get_crawled_path_from_url(url: str) -> Path:
    foldername, filename = get_names_from_url(url)
    return Path("Datasets", foldername, "crawled", filename)


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


# TODO this function should be removed as its usage is unnecessary
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


def parse_soups(base_url, parser: Callable[[BeautifulSoup], BeautifulSoup]):
    header = load_header(base_url)
    parsed_header_path = get_headerpath_from_url(base_url, parsed=True)
    parsed_header = {}
    l_remove = []
    for filename in header.keys():
        url = header[filename]["url"]
        path = get_parsed_path_from_url(url)
        # skip already if already parsed
        # if os.path.exists(path):
        #     continue

        # get soup for parsing
        soup = read_soup(url)
        parsed_content = parser(soup)

        # filter out empty results as no parsable entry exists
        if parsed_content and parsed_content.contents:
            if not os.path.exists(path.parent):
                os.makedirs(path.parent)

            string = ""
            for tag in parsed_content.contents:
                text = tag.get_text()
                # clean up of text
                text = re.sub("\s+", " ", text)
                text = text.strip()
                # # remove empty lines
                if not text:
                    continue
                for sentence in re.split(r"([?.:!] )", text):
                    # Move punctuation to the correct position, i.e. the previous line
                    if sentence in [". ", ": ", "? ", "! "]:
                        string = string[:-1]
                    string += f"{sentence}\n"
            if string:
                with open(path, "w", encoding="utf-8") as fp:
                    fp.write(string)
                parsed_header[filename] = header[filename]
                continue
        print(
            f"No content for {url}. No header entry is created.\n\tCorresponding matching entries will be adapted.")
        l_remove.append(filename)

    # clean-up of empty files
    for filename in l_remove:
        for matching in header[filename]["matching_files"]:
            # check if it was parsed
            if matching in parsed_header:
                parsed_header[matching]["matching_files"].remove(filename)
                if not parsed_header[matching]["matching_files"]:
                    # delete the entry and its parsed file, if no matching files remain
                    parsed_path = get_parsed_path_from_url(
                        parsed_header[matching]["url"])
                    os.remove(parsed_path)
                    del parsed_header[matching]
                    print(
                        f"Removed {matching}, as no matching file remained after {filename} was removed.")
    with open(parsed_header_path, "w", encoding="utf-8") as fp:
        json.dump(parsed_header, fp, indent=4)


def filter_urls(urls: list, base_url: str) -> list:
    """ Removes urls that have already been crawled
    """
    file_path = get_crawled_path_from_url(urls[0])
    header_path = get_headerpath_from_url(urls[0])

    # remove urls leaving the website
    urls = [url for url in urls if base_url in url]
    if os.path.exists(header_path):
        with open(header_path, "r", encoding="utf-8") as f:
            header = json.load(f)
            keys = header.keys()
            # remove already downloaded urls
            urls = [url for url in urls if get_crawled_path_from_url(
                url).name not in keys]
    return urls


### LOGGING UTILITIES ###

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
