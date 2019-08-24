#!/usr/bin/env python3
from bs4 import BeautifulSoup
from shutil import copyfile

import os
import urllib3

BASE_LINk = "http://www.forroemvinil.com"
YEAR_PAGE_LINK = "http://www.forroemvinil.com/tag/%s/page/%s"

DIR = os.path.dirname(__file__)
DATA_DIR = DIR + "/progress-data/%s"

print(DATA_DIR)

exit(0)


def main():
    print("# Fetching available years")
    years = get_years()
    print("")

    dl_links_file = DATA_DIR % "download_links"
    if os.path.isfile(dl_links_file):
        copyfile(dl_links_file, DATA_DIR % "download_links_old")

    links_file = open(dl_links_file, "w+")
    for year in years:
        links = get_links_for_year(year)
        links_file.write("\n".join(links) + "\n")
        links_file.flush()

    links_file.close()


def get_years():
    """ Checks for which years forro_em_vinil has music """
    soup = BeautifulSoup(download_site(BASE_LINk), "html.parser")
    return list(map(lambda x: x.get_text(), soup.find_all("a", class_="tag-cloud-link")))


def get_links_for_year(year):
    print("# Fetching album links for year %s" % year)
    content = BeautifulSoup(download_site(YEAR_PAGE_LINK % (year, 1)), "html.parser")

    # get number of pages
    navigation = content.find("div", class_="wp-pagenavi")
    max_page = 1
    if navigation:
        max_page = int(navigation.find_all("a", class_="page-numbers")[-2].get_text())

    links = []
    for i in range(1, max_page + 1):
        print("Fetching links for site (%s/%s)" % (i, max_page))
        if i is not 1:
            content = BeautifulSoup(download_site(YEAR_PAGE_LINK % (year, i)), "html.parser")
        links.extend(fetch_links(content))

    if len(links) == 0:
        print("WARN: Found no links for year %s" % year)

    return links


def fetch_links(site_soup):
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


def download_site(link):
    http = urllib3.PoolManager()
    r = http.request("GET", link)
    if r.status != 200:
        print("Could not be processed (%s)" % link)
        return None
    return r.data


if __name__ == '__main__':
    main()
