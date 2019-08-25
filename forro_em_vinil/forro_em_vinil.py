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


def fetch_download_links():
    start = time.time()
    print("#Fetching available years... ", end="")
    years = _get_years()
    print(str(time.time() - start))

    start = time.time()
    links_file = open(DOWNLOAD_LINKS, "w+")
    for year in years:
        links = _get_links_for_year(year)
        links_file.write("\n".join(links) + "\n")
        links_file.flush()

    print("Found {} links in {}s".format(len(links_file.readlines()), str(time.time() - start)))
    links_file.close()


def download():
    return subprocess.run([DOWNLOAD_SCRIPT, DOWNLOAD_LINKS], stdout=subprocess.PIPE).returncode


def extract():
    return subprocess.run([EXTRACT_SCRIPT], stdout=subprocess.PIPE).returncode


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

    links = []
    for i in range(1, max_page + 1):
        print("Fetching links for site (%s/%s)" % (i, max_page))
        if i is not 1:
            content = BeautifulSoup(_download_site(YEAR_PAGE_LINK % (year, i)), "html.parser")
        links.extend(_fetch_links(content))

    if len(links) == 0:
        print("WARN: Found no links for year %s" % year)

    return links


def _fetch_links(site_soup):
    articles = site_soup.find_all("article", class_="article")
    print("Found %s article(s)" % len(articles))

    links = []
    for article in articles:
        def contains_mega_link(p) -> bool:
            has_text = "Para baixar esse disco" in p.get_text()
            has_link = p.find("a") and "mega" in p.find("a")["href"]
            return has_text and has_link

        p_with_links = filter(contains_mega_link, article.find_all("p"))
        links.extend(list(map(lambda x: x.find("a")["href"], p_with_links)))

    print("")

    return links


def _download_site(link):
    http = urllib3.PoolManager()
    r = http.request("GET", link)
    if r.status != 200:
        print("Could not be processed (%s)" % link)
        return None
    return r.data
