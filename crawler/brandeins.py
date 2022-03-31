import crawler.utilities as utl
import re
from bs4 import BeautifulSoup
from pathlib import Path
import json
import os


def crawl_site(url, base_url):
    soup = utl.read_soup(url)

    soup_main = soup.find(["main"])

    contains_easy_parts = bool(soup_main.find(
        name="span", style="color: #ff0000;") or soup_main.find(name="span", style="color: #800000;"))

    if contains_easy_parts:
        filepath = utl.get_crawled_path_from_url(url)
        utl.save_soup(soup, filepath)
        utl.save_header(filepath, url, filepath)
    else:
        utl.log_missing_url(url)


def crawling(base_url):
    easy_url = "https://www.brandeins.de/themen/rubriken/leichte-sprache"

    soup = utl.read_soup(easy_url)
    soup_tags = soup.find_all(name="div",
                              class_="column col-xs-12")

    urls = [utl.parse_url(link["href"], base_url)
            for tag in soup_tags for link in tag.find_all(name="a", href=True)]

    for i, url in enumerate(urls):
        print(f"{i+1:0>2}/{len(urls)} Crawling {url}")
        crawl_site(url, base_url)


def parse_soups(base_url: str):
    """ Contrary to other webpages brandeins needs it's own parse_soup method
    """
    headerpath = utl.get_headerpath_from_url(base_url)
    headerpath_old = Path(headerpath.parent, "header_old.json")
    if not os.path.exists(headerpath_old):
        header = utl.load_header(base_url)
        with open(headerpath_old, "w", encoding="utf-8") as f:
            json.dump(header, f, indent=4)
    else:
        with open(headerpath_old, "r") as f:
            header = json.load(f)
    foldername, _ = utl.get_names_from_url(base_url)

    output_folder = utl.get_parsed_path_from_url(base_url)
    if not os.path.exists(output_folder.parent):
        os.mkdir(output_folder.parent)

    new_header = {}
    
    for filename in header.keys():
        # ignore special case
        if filename == "www.brandeins.de__magazine__brand-eins-wirtschaftsmagazin__2019__qualitaet__ich-tu-mir-so-leid-deswegen-will-ich-jetzt-zaubern-lernen.html":
            continue

        # check if file has not been parsed
        url = header[filename]["url"]
        easy_filepath = utl.get_parsed_path_from_url(url + "_easy")
        normal_filepath = utl.get_parsed_path_from_url(url + "_normal")

        # save new header information
        new_header[easy_filepath.stem] = {
            "url": header[filename]["url"],
            "crawl_date": header[filename]["crawl_date"],
            "easy": True,
            "publication_date": header[filename]["publication_date"],
            "matching_files": [normal_filepath.stem]
        }

        new_header[normal_filepath.stem] = {
            "url": header[filename]["url"],
            "crawl_date": header[filename]["crawl_date"],
            "easy": False,
            "publication_date": header[filename]["publication_date"],
            "matching_files": [easy_filepath.stem]
        }

        # parse contents
        soup = utl.read_soup(url)

        texts = soup.find_all(
            "section", attrs={"class": "textblock container"})

        text_easy = []
        text_normal = []
        for text in texts:
            paragraphs = text.find_all("p")
            for paragraph in paragraphs:
                if paragraph.find("span", attrs={"style": "color: #ff0000;"}):
                    text_easy.append(paragraph)
                else:
                    text_normal.append(paragraph)

        # empty texts are not saved
        if (not text_easy) or (not text_normal):
            del new_header[easy_filepath.stem]
            del new_header[normal_filepath.stem]
            continue
        
        with open(easy_filepath, "w", encoding="utf-8") as f:
            for paragraph in text_easy:
                text = paragraph.get_text()
                # clean up of text
                text = re.sub("\s+", " ", text)
                text = text.strip()
                # # remove empty lines
                if not text:
                    continue
                for j, sentence in enumerate(re.split(r"([?.:!] )", text)):
                    # print(f"{i}-{j}#{sentence}")
                    # Move punctuation to the correct position
                    if sentence in [". ", ": ", "? ", "! "]:
                        f.seek(f.tell()-1)
                    f.write(f"{sentence}\n")

        with open(normal_filepath, "w", encoding="utf-8") as f:
            for paragraph in text_normal:
                text = paragraph.get_text()
                # clean up of text
                text = re.sub("\s+", " ", text)
                text = text.strip()
                # # remove empty lines
                if not text:
                    continue
                for j, sentence in enumerate(re.split(r"([?.:!] )", text)):
                    # print(f"{i}-{j}#{sentence}")
                    # Move punctuation to the correct position
                    if sentence in [". ", ": ", "? ", "! "]:
                        f.seek(f.tell()-1)
                    f.write(f"{sentence}\n")

    with open(utl.get_headerpath_from_url(base_url), "w", encoding="utf-8") as f:
        json.dump(new_header, f, indent=4)



def main():
    base_url = "https://www.brandeins.de/"
    crawling(base_url)
    parse_soups(base_url)


if __name__ == '__main__':
    main()
