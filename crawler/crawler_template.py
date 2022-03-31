import crawler.utilities as utl


def crawl_site(easy_url: str, base_url: str):
    """ Saves the parallel articles

    Args:
        easy_url: the easy article to find the normal article in
        base_url: the base hostname of the website
    """
    easy_soup = utl.read_soup(easy_url)

    # Find the corresponding normal url in the easy soup

    if normals_url:
        # save the parallel articles
        utl.save_parallel_soup(normal_soup, normal_url, easy_soup, easy_url)
    else:
        utl.log_missing_url(easy_url)


def crawling(base_url: str):
    """ Starts the crawling process

    Args:
        base_url: the base hostname of the website
    """
    home_url_easy = ""

    # get urls from easy main page
    easy_soup = utl.read_soup(home_url_easy)

    # read the corresponding articles
    for i, easy_url in enumerate(easy_urls):
        print(f"[{i+1}/{len(easy_urls)}] Crawling {easy_url}")
        crawl_site(easy_url, base_url)


def parser(soup: BeautifulSoup) -> BeautifulSoup:
    """ Parse the texts from the previously downloaded articles

    Args:
        soup: BeautifulSoup object of the webpage to be parsed

    Returns:
        BeautifulSoup object containing the the text to be extracted (See utl.parse_soups() for context)
    """

    result = BeautifulSoup("", "html.parser")
    # # add all contents to result
    # for tag in content:
    #     if "──────────────────" in tag.get_text():
    #         continue
    #     result.append(tag)
    return result
