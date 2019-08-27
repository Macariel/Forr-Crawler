#!/usr/bin/env python3
from bs4 import BeautifulSoup
import time
import os
import urllib3
import subprocess

BASE_LINK = "http://www.forroemvinil.com"
YEAR_PAGE_LINK = "http://www.forroemvinil.com/tag/%s/page/%s"

DIR = os.path.dirname(__file__)
DATA_DIR = DIR + "/progress-data/%s"
DOWNLOAD_LINKS = DATA_DIR % "download_links"
SCRIPT_DIR = DIR + "/scripts/%s"
DOWNLOAD_SCRIPT = SCRIPT_DIR % "download.sh"
EXTRACT_SCRIPT = SCRIPT_DIR % "extract.sh"

HTTP = urllib3.PoolManager()


def fetch_download_links():
    start = time.time()
    print("# Fetching available years... ", end="")
    years = _get_years()
    print(str(time.time() - start))

    start = time.time()
    links = set()
    try:
        for year in years:
            links.update(_get_links_for_year(year))
    finally:
        print("Found {} links in {}s".format(len(links), str(time.time() - start)))
        with open(DOWNLOAD_LINKS, "w+") as links_file:
            links_file.write("\n".join(links) + "\n")


def download():
    return subprocess.run([DOWNLOAD_SCRIPT, DOWNLOAD_LINKS]).returncode


def extract():
    return subprocess.run([EXTRACT_SCRIPT]).returncode


def _get_years():
    """ Checks for which years forro_em_vinil has music """
    soup = BeautifulSoup(_download_site(BASE_LINK), "html.parser")
    return list(map(lambda x: x.get_text(), soup.find_all("a", class_="tag-cloud-link")))


def _get_links_for_year(year):
    print("# Fetching album links for year %s" % year)
    content = BeautifulSoup(_download_site(YEAR_PAGE_LINK % (year, 1)), "html.parser")

    # get number of pages
    navigation = content.find("div", class_="wp-pagenavi")
    max_page = 1
    if navigation:
        max_page = int(navigation.find_all("a", class_="page-numbers")[-2].get_text())

    links = set()
    for i in range(1, max_page + 1):
        print("Fetching links for page (%s/%s)" % (i, max_page))
        if i is not 1:
            content = BeautifulSoup(_download_site(YEAR_PAGE_LINK % (year, i)), "html.parser")
        links.update(_fetch_links_from_page(content))

    if len(links) == 0:
        print("WARN: Found no links for year %s" % year)

    return links


def _fetch_links_from_page(page_soup):
    articles = page_soup.find_all("article", class_="article")
    print("Found %s article(s)" % len(articles))

    links = set()
    for article in articles:
        def contains_mega_link(p) -> bool:
            has_text = "Para baixar esse disco" in p.get_text()
            has_link = p.find("a") and "mega" in p.find("a")["href"]
            return has_text and has_link

        p_with_links = filter(contains_mega_link, article.find_all("p"))
        links.update(set(map(lambda x: x.find("a")["href"], p_with_links)))

    print("")

    return links


def _download_site(link):
    r = HTTP.request("GET", link)
    if r.status != 200:
        print("[WARN] Could not be processed (%s): %s" % (r.status, link))
        return ""
    return r.data
