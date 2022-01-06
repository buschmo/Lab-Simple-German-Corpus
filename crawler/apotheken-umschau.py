#!/usr/bin/python3.10
import utilities as utl
import re
from bs4 import BeautifulSoup


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    # find the a tag containing said string
    if len(easy_soup.find_parents(name="a", attrs={"class": "btn btn-primary mb-3"})) > 1:
        print("Error! More than one parent was found for the links.")
        return

    easy_url_tags = easy_soup.find_all(
        name="a",
        attrs={"class": "btn btn-primary mb-3"}
    )

    normals_urls = [utl.parse_url(tag["href"], base_url)
                    for tag in easy_url_tags]

    for normal_url in normals_urls:
        normal_soup = utl.read_soup(normal_url)

        utl.save_parallel_soup(normal_soup, normal_url,
                               easy_soup, easy_url)


def filter_urls(urls, base_url):
    urls = utl.filter_urls(urls, base_url)
    # remove download links of docs
    urls = [url for url in urls if (
        "index.php?menuid=" not in url) and ("/ls/" in url)]
    return urls


def crawling(base_url):
    home_url_easy = "https://www.apotheken-umschau.de/einfache-sprache/"

    # get urls
    easy_soup = utl.read_soup(home_url_easy)

    easy_url_tags = easy_soup.find_all(
        name="a",
        href=lambda x: "einfache-sprache" in x
    )
    easy_urls = list(set([utl.parse_url(tag["href"], base_url)
                     for tag in easy_url_tags]))

    for i, easy_url in enumerate(easy_urls):
        print(f"[{i+1:0>3}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def main():
    base_url = "https://www.apotheken-umschau.de/"
    crawling(base_url)


if __name__ == '__main__':
    main()
