#!/usr/bin/env python3
from pathlib import Path

from bs4 import BeautifulSoup
import time
import os
import urllib3
import subprocess
import sys
from slugify import slugify

BASE_LINK = "http://www.forroemvinil.com"
TAG_PAGE_LINK = "http://www.forroemvinil.com/tag/%s/page/%s"
CATEGORY_LINK = "http://www.forroemvinil.com/category/%s/page/%s"
CATEGORIES = ["lps", "78-rpm", "compactos", "8-polegadas", "10polegadas", "cds"]

DIR = os.path.dirname(__file__)
DATA_DIR = DIR + "/progress-data/%s"
DOWNLOAD_LINKS = DATA_DIR % "download_links"

CACHE_DIR = DIR + "/cache/"
CACHING = False

SCRIPT_DIR = DIR + "/scripts/%s"
DOWNLOAD_SCRIPT = SCRIPT_DIR % "download.sh"
EXTRACT_SCRIPT = SCRIPT_DIR % "extract.sh"

HTTP = urllib3.PoolManager()


def main():
    fetch_category_links()
    pass


def _fetch_links(link_template, crawl_values, link_fetcher):
    """

    :param link_template: Link which can be formatted with a single value of the crawl values and a page number to make a valid link
    :param crawl_values: List of values like categories, tags or artists
    :param link_fetcher: Method which is fetching mega-dl-links from the link assembled by the other parameters
    """
    start = time.time()
    links = set()
    try:
        for value in crawl_values:
            print("# Fetching links for '%s'" % value)
            page_content = _download_site(link_template % (value, 1))
            if not page_content:
                continue

            max_pages = _get_number_of_pages(page_content)

            for i in range(1, max_pages + 1):
                print("\tpage (%s/%s)... " % (i, max_pages), end="")
                if i != 1:
                    page_content = _download_site(link_template % (value, i))

                if not page_content:
                    continue

                page_links = link_fetcher(page_content)
                print("found %s" % str(len(page_links)))
                links.update(page_links)
                sys.stdout.flush()
    finally:
        if len(links) > 0:
            print("Found {} links in {}s".format(len(links), str(time.time() - start)))
            with open(DOWNLOAD_LINKS, "a") as links_file:
                links_file.write("\n".join(links) + "\n")


def fetch_all():
    fetch_category_links()
    fetch_year_links()
    fetch_artist_links()


def fetch_artist_links():
    print("# Fetching all artists")
    _fetch_links(TAG_PAGE_LINK, _get_artists(), _fetch_links_from_page)


def fetch_year_links():
    print("# Fetching all years")
    _fetch_links(TAG_PAGE_LINK, _get_years(), _fetch_links_from_page)


def fetch_category_links():
    _fetch_links(CATEGORY_LINK, CATEGORIES, _fetch_links_from_all_articles)


def download():
    return subprocess.run([DOWNLOAD_SCRIPT, DOWNLOAD_LINKS]).returncode


def extract():
    return subprocess.run([EXTRACT_SCRIPT]).returncode


def _get_artists():
    content = _download_site(BASE_LINK)
    if not content:
        return []

    letters = content.find_all("ul", class_="box_conteudo_fechado")

    names = []
    for letter in letters:
        names.extend(map(lambda a: a["href"].split("/")[-2], letter.find_all("a")))

    return names


def _fetch_links_from_all_articles(page_content):
    links = set()
    for link in _fetch_links_to_articles(page_content):
        content = _download_site(link)
        if not content:
            continue
        links_of_page = _fetch_links_from_page(content)

        if len(links_of_page) == 0:
            _warn("No links found on %s" % link)
        links.update(links_of_page)
    return links


def _fetch_links_to_articles(page_content):
    articles = page_content.find_all("article", class_="article")
    titles = map(lambda x: x.find("h3", class_="title"), articles)
    return set(map(lambda x: x.find("a")["href"], titles))


def _get_years():
    """ Checks for which years forro_em_vinil has music """
    soup = _download_site(BASE_LINK)
    if not soup:
        return []
    return list(map(lambda x: x.get_text(), soup.find_all("a", class_="tag-cloud-link")))


def _get_number_of_pages(page_content):
    navigation = page_content.find("div", class_="wp-pagenavi")
    max_page = 1
    if navigation:
        max_page = int(navigation.find_all("a", class_="page-numbers")[-2].get_text())
    return max_page


def _fetch_links_from_page(page_soup):
    # articles = page_soup.find_all("article", class_="article")
    links = set()

    def contains_mega_link(a) -> bool:
        # has_text = "Para baixar esse disco" in p.get_text()
        if not a:
            return False

        try:
            href = a["href"]
        except KeyError:
            return False

        return "mega.co.nz" in href or "mega.nz" in href

    mega_links = filter(contains_mega_link, page_soup.find_all("a"))
    links.update(set(map(lambda x: x["href"], mega_links)))

    return links


def _warn(message):
    print("[WARN] %s" % message)


def _download_site(link):
    file_name = os.path.join(CACHE_DIR + slugify(link))

    # fetch cache
    if CACHING and os.path.isfile(file_name):
        return BeautifulSoup(Path(file_name).read_text(), "html.parser")

    r = HTTP.request("GET", link)
    if r.status != 200:
        _warn("Could not be processed (%s): %s" % (r.status, link))
        return None

    # Write cache
    if CACHING:
        with open(file_name, "w") as f:
            f.write(r.data.decode("UTF-8"))

    return BeautifulSoup(r.data, "html.parser")


if __name__ == '__main__':
    main()
