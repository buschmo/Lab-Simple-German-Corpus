#!/usr/bin/python3.10
import utilities as utl
import re
from bs4 import BeautifulSoup

""" Lebenshilfe Main Taunus
Ignore /dokument/

"""


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    # find the a tag containing said string
    easy_url_tag = easy_soup.find(
        name="a",
        string=re.compile("Diese Seite in Alltags-Sprache lesen", flags=re.I)
    )
    # convert the tag class to BeautifulSoup class
    easy_url_soup = BeautifulSoup(str(easy_url_tag), "html.parser")

    # get the url from this
    normal_urls = utl.get_urls_from_soup(
        easy_url_soup,
        base_url
    )

    try:
        normal_url = normal_urls[0]
        normal_soup = utl.read_soup(normal_url)

        utl.save_parallel_soup(normal_soup, normal_url,
                               easy_soup, easy_url)
    except IndexError as e:
        print("Err")
        utl.log_missing_url(easy_url)


def filter_urls(urls, base_url):
    urls = utl.filter_urls(urls, base_url)
    # remove download links of docs
    urls = [url for url in urls if (
        "index.php?menuid=" not in url) and ("/ls/" in url)]
    return urls


def main():
    base_url = "https://www.stadt-koeln.de/"
    home_url_easy = "https://www.stadt-koeln.de/leben-in-koeln/soziales/informationen-leichter-sprache"

    # get urls
    easy_soup = utl.read_soup(home_url_easy)
    easy_urls = utl.get_urls_from_soup(
        easy_soup,
        base_url,
        {"name": "section",
         "attrs": {"class": "trefferliste_flex trefferliste"}}
    )

    for i, easy_url in enumerate(easy_urls):
        print(f"[{i+1:0>2}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)


if __name__ == '__main__':
    main()
