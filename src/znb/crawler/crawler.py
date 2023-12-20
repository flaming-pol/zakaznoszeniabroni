import logging
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
    if r.status_code != 200:
        logging.error("Przy próbie pobranie strony Dziennika Ustaw otrzymano kod "
                      f"http {r.status_code}")
        return []
    soup = bs(r.content, features="html.parser")

    lista = soup.find("div", id="lista")
    if not lista:
        logging.error("Podczas analizy DU nie odnaleziono <div id=lista>")
        return []

    table = lista.find("table", class_="PapRedGrid")
    if not table:
        logging.error("Podczas analizy DU nie odnaleziono <table class=PapRedGrid>")
        return []

    table_rows = table.find_all("tr")
    if not table_rows:
        logging.error("Podczas analizy DU nie odnaleziono żadnego <tr>")
        return []

    regex_data = re.compile(r".*Data ogłoszenia.*")
    regex_rok = re.compile(r".*Rok.*")
    regex_pozycja = re.compile(r".*Pozycja.*")
    regex_pobierz = re.compile(r".*Pobierz.*")
    found_elements = []
    for row in table_rows:
        cells = row.find_all("td")
        if not cells:
            continue
        for cell in cells:
            if cell.attrs.get("align") != "left":
                continue
            # nazwa rozporzadzenia
            name = cell.find("a")
            if not name:
                continue
            name = name.contents[0]
            match = re.search(regex_pattern, name)
            if not match:
                continue
            # wydobycie szczegolowych danych z podstrony
            link = get_link(cell)
            if not link:
                logging.error(f"Dopasowano wiersz name={name}, ale nie znalziono linku")
                continue
            detail_site = requests.get(f"{site}{link}", verify=False)
            if detail_site.status_code != 200:
                logging.error(f"Nie udało się wywołać strony: {link}, "
                              f"otrzymano kod http: {detail_site.status_code}")
                continue
            detail_parser = bs(detail_site.content, features="html.parser")
            published_date = detail_parser.find("td", recursive=True, string=regex_data)
            published_date = strip_text_from_td(published_date)
            year = detail_parser.find("td", recursive=True, string=regex_rok)
            year = strip_text_from_td(year)
            number = detail_parser.find("td", recursive=True, string=regex_pozycja)
            number = strip_text_from_td(number)
            pdf_url = detail_parser.find("p", recursive=True, string=regex_pobierz)
            pdf_url = get_link_from_td(pdf_url)

            if not (published_date and year and number and pdf_url):
                logging.error("Błędna wartość jednego z pól: "
                              f"published_date={published_date}, "
                              f"year={year}, "
                              f"number={number}, "
                              f"pdf_url={pdf_url}")
                continue
            act = LegalAct()
            act.published_date = '-'.join(reversed(published_date.split('-')))
            act.year = int(year)
            act.number = int(number)
            act.pdf_url = f"{site}{pdf_url}"
            act.name = name
            found_elements.append(act)
    return found_elements


def strip_text_from_td(data):
    if not data:
        return None
    stage1 = data.find_next('td')
    if not stage1:
        return None
    stage2 = stage1.text
    if not stage2 or not isinstance(stage2, str):
        return None
    return stage2.strip()


def get_link_from_td(data):
    if not data:
        return None
    stage1 = data.find_next('td')
    if not stage1:
        return False
    return get_link(stage1)


def get_link(data):
    if not data:
        return None
    link = data.find('a')
    if not link:
        return None
    return link.get('href')
