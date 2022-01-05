#!/usr/bin/python3.10
import utilities as utl
import re
from bs4 import BeautifulSoup


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    easy_url_tag_previous = easy_soup.find(
        name="div",
        class_="p-fnt_std-bold--xs-uc p-fnt_letter-spacing--zero-five p-clr_sld-primary p-dsply_blck p-pad_b-l",
        # string=re.compile("Lesen Sie dazu auch", flags=re.I)
    )

    if easy_url_tag_previous:
        easy_url_tags = easy_url_tag_previous.find_next_sibling("div")
        easy_url_tags = easy_url_tags.find_all(name="a", href=True)
        normals_urls = [utl.parse_url(url["href"], base_url) for url in easy_url_tags]

        for normal_url in normals_urls:
            normal_soup = utl.read_soup(normal_url)

            utl.save_parallel_soup(normal_soup, normal_url,
                                easy_soup, easy_url)

    else:
        utl.log_missing_url(easy_url)



def filter_urls(urls, base_url):
    urls = utl.filter_urls(urls, base_url)
    # remove download links of docs
    urls = [url for url in urls if (
        "index.php?menuid=" not in url) and ("/ls/" in url)]
    return urls


def main():
    base_url = "https://www.augsburger-allgemeine.de/"
    home_url_easy = "https://www.augsburger-allgemeine.de/special/nachrichten-in-leichter-sprache/"

    # get urls
    easy_soup = utl.read_soup(home_url_easy)

    easy_url_tags = easy_soup.find_all(
        name="a",
        class_="p-swatch_topdown-nice p-blocklink p-block p-marg_v-xl",
        title=True,
        href=True
    )
    easy_urls = list(set(
        [utl.parse_url(tag["href"], base_url) for tag in easy_url_tags]
    ))

    for i, easy_url in enumerate(easy_urls):
        print(f"[{i+1:0>2}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)


if __name__ == '__main__':
    main()
