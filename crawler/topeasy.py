import utilities as utl
import re


def crawl_site(url):
    soup = utl.read_soup(url)

    filepath = utl.get_crawled_path_from_url(url)
    utl.save_soup(soup, filepath)
    utl.save_header(filepath, url, filepath)


def crawling(base_url, overview_url="https://www.unsere-zeitung.at/category/nachrichten/topeasy/"):
    overview_soup = utl.read_soup(overview_url)

    article_tag = overview_soup.find(name="div",
                                     class_="article-container")
    article_images = article_tag.find_all(name="div",
    class_="featured-image")
    article_urls = [image.find(name="a", href=True)["href"] for image in article_images]

    for i, url in enumerate(article_urls):
        print(f"{i+1:0>2}/{len(article_urls)} Crawling {url}")
        crawl_site(url)
    
    # Go onto the next page
    next_overview_url = overview_soup.find(
        name="a",
        attrs={
            "class": "nextpostslink",
            "rel": "next",
            "aria-label": "Next Page"
        }
    )
    if next_overview_url:
        print("Opening next page.")
        crawling(base_url, next_overview_url["href"])

def main():
    base_url = "https://www.unsere-zeitung.at/"
    crawling(base_url)


if __name__ == '__main__':
    main()
