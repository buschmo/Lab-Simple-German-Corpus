import utilities as utl
import re


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    easy_soup_tag = easy_soup.find(name="a",
                                         title=re.compile(
                                             "Lesen Sie den Artikel .* in Alltagssprache", flags=re.I),
                                         class_="c-language-switch__l c-language-switch__l--as",
                                         string="Alltagssprache"
                                         )

    if easy_soup_tag:
        normal_url = utl.parse_url(
            easy_soup_tag["href"],
            base_url
        )
        normal_soup = utl.read_soup(normal_url)
        utl.save_parallel_soup(normal_soup, normal_url, easy_soup, easy_url)
    else:
        utl.log_missing_url(easy_url)


def main():
    base_url = "https://www.behindertenbeauftragter.de/"
    easy_url = "https://www.behindertenbeauftragter.de/DE/LS/startseite/startseite-node.html"

    soup = utl.read_soup(easy_url)
    soup_tags = soup.find_all(name="div", class_="menu fl-1")
    easy_urls = [link["href"]
                 for tag in soup_tags for link in tag.find_all(name="a", href=True)]

    easy_urls = [utl.parse_url(url[:url.find(";")], base_url)
                 for url in easy_urls]

    for i, easy_url in enumerate(easy_urls):
        print(f"{i+1:0>2}/{len(easy_urls)} Crawling {easy_url}")
        crawl_site(easy_url, base_url)


if __name__ == '__main__':
    main()
