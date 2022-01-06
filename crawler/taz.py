import utilities as utl
import re


def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    easy_soup_tags = easy_soup.find_all(name="p", xmlns="", class_=True)
    easy_soup_tags = [tag for tag in easy_soup_tags if tag.find(name="em")]
    easy_soup_tags = [
        tag for tag in easy_soup_tags if tag.find(name="a", href=True)]

    if easy_soup_tags:
        a_tags = [href_tag for easy_soup_tag in easy_soup_tags for href_tag in easy_soup_tag.find_all(
            name="a", href=True)]

        for a_tag in a_tags:
            normal_url = utl.parse_url(
                a_tag["href"],
                base_url
            )

            normal_soup = utl.read_soup(normal_url)
            utl.save_parallel_soup(
                normal_soup, normal_url, easy_soup, easy_url)
    else:
        utl.log_missing_url(easy_url)


def main():
    base_url = "https://taz.de/"
    easy_url = "https://taz.de/Politik/Deutschland/Leichte-Sprache/!p5097/"

    soup = utl.read_soup(easy_url)
    soup_tags = soup.find_all(name="ul",
                              role="directory",
                              debug="x1",
                              class_="news directory")
    
    easy_urls = [utl.parse_url(link["href"], base_url)
                 for tag in soup_tags for link in tag.find_all(name="a", href=True)]

    easy_urls = [utl.parse_url(url[:url.find(";")], base_url)
                 for url in easy_urls]

    for i, easy_url in enumerate(easy_urls):
        print(f"{i+1:0>2}/{len(easy_urls)} Crawling {easy_url}")
        crawl_site(easy_url, base_url)


if __name__ == '__main__':
    main()
