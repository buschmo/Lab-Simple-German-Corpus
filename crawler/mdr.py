from utilities import *
import re

""" MDR
There are three content pages on mdr.de
    - The main page contains up to 3 blocks of daily news, one block for each past day consisting of 4 articles
    - a block with 3 articles giving general information in simple german
    -
"""


def crawl_article(easy_urls, base_url):
    for easy_url in easy_urls:
        easy_soup = read_soup(easy_url)

        publication_date = str(easy_soup.find(
            "p", {"class": "webtime"}).find_all("span")[1])[6:-9]

        normal_urls = get_urls_from_soup(
            easy_soup,
            base_url,
            ["div", {
                "class": "con cssBoxTeaserStandard conInline"
                }], 
            ["Hier können Sie diese Nachricht auch in schwerer Sprache lesen", 
            "Hier können Sie die Nachrichte auch in schwerer Sprache nachlesen",
            ])
        try:
            normal_url = normal_urls[0]
        except IndexError as e:
            log_missing_url(easy_url)
            continue

        normal_soup = read_soup(normal_url)

        save_parallel_soup(normal_soup, normal_url,
                           easy_soup, easy_url, publication_date)


def main():
    base_url = "https://www.mdr.de/"
    home_url = "https://www.mdr.de/nachrichten-leicht/index.html"

    # crawl current news articles
    main_soup = read_soup(home_url)
    easy_news_urls = get_urls_from_soup(
        main_soup, base_url, ["div", {"class": "sectionWrapper section1er audioApp cssPageAreaWithoutContent"}])

    crawl_article(easy_news_urls, base_url)


    # crawl archived articles
    archive_urls = [
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-sachsen-anhalt-100.html",
        "https://www.mdr.de/nachrichten-leicht/rueckblick/leichte-sprache-rueckblick-buendelgruppe-thueringen-100.html"
    ]

    for archive_url in archive_urls:
        archive_soup = read_soup(archive_url)
        string = "targetNode-nachrichten-leichte-sprache"
        easy_information_urls = get_urls_from_soup(
            archive_soup, base_url, ["div", {"class": string}])

        crawl_article(easy_information_urls, base_url)


if __name__ == '__main__':
    main()
