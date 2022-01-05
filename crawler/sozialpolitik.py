import utilities as utl
import re

def crawl_site(easy_url, base_url):
    easy_soup = utl.read_soup(easy_url)

    normal_url = utl.parse_url(
        easy_soup.find(name="a", hreflang="de-DE", class_="underline easy",
                       string=re.compile("Standardsprache", flags=re.I))["href"],
        base_url
    )
    normal_soup = utl.read_soup(normal_url)
    utl.save_parallel_soup(normal_soup, normal_url, easy_soup, easy_url)

def main():
    base_url = "https://www.sozialpolitik.com/"
    easy_url = "https://www.sozialpolitik.com/es/"

    soup = utl.read_soup(easy_url)
    easy_urls = utl.get_urls_from_soup(
        soup,
        base_url,
        filter_args={"name": "section",
                     "class_": "element-col bg-weiss"
                     }
    )

    for i, easy_url in enumerate(easy_urls):
        print(f"{i+1:0>2}/{len(easy_urls)} Crawling {easy_url}")
        crawl_site(easy_url, base_url)


if __name__ == '__main__':
    main()
