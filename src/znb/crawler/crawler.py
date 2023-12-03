import re
import requests

from typing import List
from bs4 import BeautifulSoup as bs


class LegalAct:
    name = ""
    number = 0
    year = 0
    pdf_url = ""
    published_date = None


def dziennik_ustaw_search_v2(year: int = 0) -> List[LegalAct]:
    site = "https://dziennikustaw.gov.pl"
    search_pattern = rf"/szukaj?pSize=0&diary=0&typact=7&_typact=1&year={year}&release=&number=&volume=&publicDateFrom=&publicDateTo=&releaseDateFrom=&releaseDateTo=&_group=1&_subject=1&title=broni&text=&sKey=year&sOrder=desc#list"
    regex_pattern = r"zakaz(.)*\s(noszenia|przemieszczania)+(.)*broni+"

    r = requests.get(f"{site}/{search_pattern}", verify=False)
    soup = bs(r.content, features="html.parser")

    lista = soup.find("div", id="lista")
    table = lista.find("table", class_="PapRedGrid")
    table_rows = table.find_all("tr")

    regex_rok = re.compile(r".*Rok.*")
    regex_pozycja = re.compile(r".*Pozycja.*")
    regex_pobierz = re.compile(r".*Pobierz.*")
    found_elements = []
    for row in table_rows:
        cells = row.find_all("td")
        if cells:
            act = LegalAct()
            for cell in cells:
                if cell.attrs.get("align") == "left":
                    # nazwa rozporzadzenia
                    name = cell.find("a").contents[0]
                    match = re.search(regex_pattern, name)
                    if not match:
                        break
                    # wydobycie szczegolowych danych z podstrony
                    link = cell.find("a")["href"]
                    detail_site = requests.get(f"{site}{link}", verify=False)
                    detail_parser = bs(detail_site.content, features="html.parser")
                    published_date = detail_parser.find("td", recursive=True, string=re.compile(r".*Data ogłoszenia.*")).find_next('td').text.strip()
                    year = detail_parser.find("td", recursive=True, string=regex_rok).find_next('td').text.strip()
                    number = detail_parser.find("td", recursive=True, string=regex_pozycja).find_next('td').text.strip()
                    pdf_url = detail_parser.find("p", recursive=True, string=regex_pobierz).find_next('td').find('a')['href']
                    act.published_date = '-'.join(reversed(published_date.split('-')))
                    act.year = int(year)
                    act.number = int(number)
                    act.pdf_url = f"{site}{pdf_url}"
                    act.name = name

                    found_elements.append(act)
    return found_elements
