from bs4 import BeautifulSoup
import urllib3
import re

http = urllib3.PoolManager()
base_link = "http://www.forroemvinil.com"


def main():
    content = BeautifulSoup(download_site(base_link), "html.parser")
    letters = content.find_all("ul", class_="box_conteudo_fechado")

    names = []
    for letter in letters:
        names.extend(map(lambda x: re.sub(" \[\d+\]", "", x.get_text().strip()), letter.find_all("li")))

    with open("artists", "w+") as f:
        for name in names:
            f.write(name + "\n")


def download_site(link):
    r = http.request("GET", link)
    if r.status != 200:
        print("Could not be processed (%s)" % link)
        return None
    return r.data


if __name__ == '__main__':
    main()
