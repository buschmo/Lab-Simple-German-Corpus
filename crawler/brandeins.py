import utilities as utl
import re


def crawl_site(url, base_url):
    soup = utl.read_soup(url)

    soup_main = soup.find(["main"])

    contains_easy_parts = bool(soup_main.find(
        name="span", style="color: #ff0000;"))

    if contains_easy_parts:
        filepath = utl.url_to_path(url)
        utl.save_soup(soup, filepath)
        utl.save_header(filepath, url, filepath)
    else:
        utl.log_missing_url(url)


def main():
    base_url = "https://www.brandeins.de/"
    easy_url = "https://www.brandeins.de/themen/rubriken/leichte-sprache"

    soup = utl.read_soup(easy_url)
    soup_tags = soup.find_all(name="div",
                              class_="column col-xs-12")

    urls = [utl.parse_url(link["href"], base_url)
            for tag in soup_tags for link in tag.find_all(name="a", href=True)]

    for i, url in enumerate(urls):
        print(f"{i+1:0>2}/{len(urls)} Crawling {url}")
        crawl_site(url, base_url)


if __name__ == '__main__':
    main()
