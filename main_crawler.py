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
    # TODO download all files from the header_archive.json
    utl = crawler.utilities
    utl.from_archive = from_archive

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
    return
    for name in crawler.__all__:
        website_module = getattr(crawler, name)
        print(f"Parsing {website_module.base_url}")
        if name == "brandeins":
            # brandeins.de needs special treatment
            website_module.parse_soups(website_module.base_url)
        else:
            # continue
            utl.parse_soups(website_module.base_url, website_module.parser)


def renaming():
    for folder in os.listdir("Datasets/"):
        folderpath = f"Datasets/{folder}/"
        import json
        with open(folderpath + "header.json") as fp:
            header = json.load(fp)
        with open(folderpath + "archive_header.json") as fp:
            archive_header = json.load(fp)
        replace = []
        for key in header:
            if key.startswith("www."):
                replace.append(key)
            elif key.endswith("__.html"):
                replace.append(key)
        if replace:
            # print(replace)
            for key in list(set(replace)):
                new_key = key
                if new_key.startswith("www."):
                    new_key = new_key[4:]
                if new_key.endswith("__.html"):
                    new_key = new_key[:-len("__.html")]+".html"

                try:
                    header[new_key] = header[key]
                except KeyError:
                    print(f"{new_key}, {key}")
                del header[key]
                archive_header[new_key] = archive_header[key]
                del archive_header[key]

                if folder == "www.brandeins.de":
                    if header[new_key]["easy"]:
                        os.rename(f"{folderpath}crawled/{key[:-len('_easy.html')]}.html",
                                  f"{folderpath}crawled/{new_key[:-len('_easy.html')]}.html")
                else:
                    os.rename(f"{folderpath}crawled/{key}",
                              f"{folderpath}crawled/{new_key}")
            with open(folderpath + "header.json", "w") as fp:
                json.dump(header, fp, indent=4)
            with open(folderpath + "archive_header.json", "w") as fp:
                json.dump(archive_header, fp, indent=4)


if __name__ == "__main__":
    main(True)