import crawler
import json
import urllib
import os
import time
import crawler.utilities as utl


def main(from_archive: bool = False):
    utl = crawler.utilities
    utl.from_archive = from_archive

    # Crawling
    if from_archive:
        for name in crawler.__all__:
            website_module = getattr(crawler, name)
            # if name != "taz":
            #     continue
            print(f"Crawling {website_module.base_url}")
            header = utl.load_header(website_module.base_url)
            for key in header:
                url = header[key]["url"]
                filepath = utl.get_crawled_path_from_url(url)
                if not os.path.exists(filepath):
                    soup = utl.get_soup_from_url(url)
                    utl.save_soup(soup, filepath)
    else:
        # TODO Implement crawling directly from the website
        print("Unaccounted case.")


    # Parsing
    for name in crawler.__all__:
        website_module = getattr(crawler, name)
        print(f"Parsing {website_module.base_url}")
        if name == "brandeins":
            # brandeins.de needs special treatment
            website_module.parse_soups()
        else:
            # continue
            utl.parse_soups(website_module.base_url, website_module.parser)


if __name__ == "__main__":
    main(True)
