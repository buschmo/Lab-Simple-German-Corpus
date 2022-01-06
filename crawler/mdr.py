#!/usr/bin/python3.10
import utilities as utl
import re

""" MDR
There are three content pages on mdr.de
    - The main page contains up to 3 blocks of daily news, one block for each past day consisting of 4 articles
    - a block with 3 articles giving general information in simple german
    -
"""


def crawl_site(easy_urls, base_url):
    easy_soup = utl.read_soup(easy_url)

    publication_date = str(easy_soup.find(
        "p", {"class": "webtime"}).find_all("span")[1])[6:-9].strip()

    if publication_date.endswith(","):
        publication_date = publication_date[:-1]

    normal_urls = utl.get_urls_from_soup(
        easy_soup,
        base_url,
        filter_args={
            "name": "div",
            "attrs": {"class": "con cssBoxTeaserStandard conInline"}
        },
        recursive_filter_args={
            "string": re.compile("auch in schwerer Sprache", flags=re.I)
        }
    )

    try:
        normal_url = normal_urls[0]
        normal_soup = utl.read_soup(normal_url)

        utl.save_parallel_soup(normal_soup, normal_url,
                               easy_soup, easy_url, publication_date)
    except IndexError as e:
        utl.log_missing_url(easy_url)


def daily():
    base_url = "https://www.mdr.de/"
    home_url = "https://www.mdr.de/nachrichten-leicht/index.html"

    # crawl current news articles
    main_soup = utl.read_soup(home_url)
    easy_news_urls = utl.get_urls_from_soup(
        main_soup,
        base_url,
        {"name": "div",
         "attrs": {"class": "sectionWrapper section1er audioApp cssPageAreaWithoutContent"}
         })

    for easy_url in easy_news_urls:
        print(f"[{i+1}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_news_url, base_url)


def main():
    base_url = "https://www.mdr.de/"
    home_url = "https://www.mdr.de/nachrichten-leicht/index.html"

    # crawl current news articles
    main_soup = utl.read_soup(home_url)
    easy_news_urls = utl.get_urls_from_soup(
        main_soup,
        base_url,
        {"name": "div",
         "attrs": {"class": "sectionWrapper section1er audioApp cssPageAreaWithoutContent"}
         })

    crawl_site(easy_news_urls, base_url)

    # crawl archived articles
    archive_urls = [
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-anhalt-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-thueringen-100.html"
    ]

    for url in archive_urls:
        archive_soup = utl.read_soup(url)
        string = "targetNode-nachrichten-leichte-sprache"
        easy_information_urls = utl.get_urls_from_soup(
            archive_soup,
            base_url,
            {"name": "div",
             "attrs": {"class": string}
             })

        for easy_url in easy_information_urls:
            print(f"[{i+1}/{len(easy_information_urls)}] Crawling {easy_url}")
            crawl_site(easy_information_urls, base_url)


if __name__ == '__main__':
    main()
