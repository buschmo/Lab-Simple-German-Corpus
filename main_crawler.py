import crawler
import json
import urllib
import os
import time
import crawler.utilities as utl


def header_to_archive():
    utl = crawler.utilities
    for name in sorted(crawler.__all__):
        # if name != "mdr":
        #     continue

        base_url = getattr(crawler, name).base_url
        foldername, _ = utl.get_names_from_url(base_url)
        with open("Datasets/"+foldername+"/header.json") as fp:
            header = json.load(fp)

        path_archive_header = "Datasets/"+foldername+"/archive_header.json"
        if os.path.isfile(path_archive_header):
            with open(path_archive_header, "r") as fp:
                archive_header = json.load(fp)
        else:
            archive_header = {}

        for key in header:
            if key in archive_header.keys():
                continue
            url = header[key]["url"]
            try:
                with urllib.request.urlopen(f"http://web.archive.org/{url}") as f:
                    print(f"Already archived: {f.url}")
                    archive_header[key] = {
                        "url": f.url,
                        "crawl_date": header[key]["crawl_date"],
                        "easy": header[key]["easy"],
                        "publication_date": header[key]["publication_date"],
                        "matching_files": header[key]["matching_files"]
                    }
                    with open(path_archive_header, "w") as fp:
                        json.dump(archive_header, fp, indent=4)

            except:
                not_downloaded = True
                counter = 0
                while not_downloaded:
                    try:
                        with urllib.request.urlopen(f"http://web.archive.org/save/{url}") as f:
                            print(f"Newly archived: {f.url}")
                            archive_header[key] = {
                                "url": f.url,
                                "crawl_date": header[key]["crawl_date"],
                                "easy": header[key]["easy"],
                                "publication_date": header[key]["publication_date"],
                                "matching_files": header[key]["matching_files"]
                            }
                            with open(path_archive_header, "w") as fp:
                                json.dump(archive_header, fp, indent=4)
                            not_downloaded = False
                    except urllib.error.HTTPError as err:
                        time.sleep(60)
                        counter += 1
                        if counter > 4:
                            print(
                                f"{counter} failed to archive: {url}\n  {str(err)}\n")
                            # if counter >= 10:
                            print(f"Stopping {url}")
                            with open("ERROR", "a") as fp:
                                fp.write(url+"\n  "+str(err)+"\n\n")
                            not_downloaded = False


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
                soup = utl.read_soup(url)
                filepath = utl.get_crawled_path_from_url(url)
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
