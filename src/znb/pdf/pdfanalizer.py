import fitz

import logging
import re

# UWAGA!
#
# Parser PDF rozporządzeń. Wesja 1.0
#
# Parser działa prawidłowo dla rozporządzeń publikowanych od 2007 roku jednak
# zaleca się stosowanie go do rozporządzeń od 2008 roku.

MONTHS_REGEX = r"stycznia|lutego|marca|kwietnia|maja|czerwca|lipca|sierpnia|września|października|listopada|grudnia"


def date_converter(date_in):
    # zamienia date z formatu: 14_czerwca_1992 na 14-06-1992
    if not re.match(rf"\d+\_({MONTHS_REGEX})(\_\d)?", date_in.strip()):
        return date_in
    date = date_in.split("_")
    months = MONTHS_REGEX.split("|")
    m = dict((month, index) for index, month in enumerate(months, 1))
    new_list = [str(elem) if not m.get(elem) else str(m.get(elem)) for elem in date]
    return '-'.join([elem.zfill(2) for elem in new_list])


def range_converter(data_list):
    # zmienia date z: ['11_lipca_2023', '15_lipca_2023']
    #  na: ['11-07-2023', '15-07-2023']
    # uzupełnia ubytki: ['11-07', '15-07-2023'] => ['11-07-2023', '15-07-2023']
    if isinstance(data_list, list) and len(data_list) != 2:
        return data_list
    a = date_converter(data_list[0])
    b = date_converter(data_list[1])
    if len(a) < 6 and len(a) > 2 and len(b) == 10:
        a += '-' + b.split('-')[2]
    elif len(a) < 3 and len(b) == 10:
        a += '-'.join(b.split('-')[1:3])
    return [a, b]


def month_and_year(buff, start_index):
    # wyszukuje miesiąc i rok na podstawie położenia w buforze zmiennej określającej dni
    year_regex = r"\d{4}"
    month_r = re.search(MONTHS_REGEX, buff[start_index:])
    month = month_r.group()
    year_r = re.search(year_regex, buff[start_index:])
    year = year_r.group()
    return (month, year)


def date_proc(data):
    # przykładowe dane wej.: "27i29-31_listopada_2008_"
    #  dane wyj.: {'ranges': [['29-11-2008', '31-11-2008']], 'days': ['27-11-2008']}}
    ranges = []
    days = []
    range_regex = r"(\_|i)?\d{1,2}-\d{1,2}(\_|i)"
    multi_month_regex = fr"\d{{1,2}}\_({MONTHS_REGEX})(\_\d{{4}})?\_\-\_\d{{1,2}}\_({MONTHS_REGEX})\_\d{{4}}"
    days_regex = r"(?<!(\-|\d))(\d{1,2})(?=(,|_|i))"

    multi_range = re.search(multi_month_regex, data)
    if multi_range:
        range_tmp = multi_range.group().split("_-_")
        ranges.append(range_converter(range_tmp))
        data = re.sub(multi_month_regex, "", data)

    d_ranges = [(x.group().strip("i,_"), x.span()) for x in re.finditer(range_regex, data)]
    d_days = [(x.group().strip("i,_"), x.span()) for x in re.finditer(days_regex, data)]
    for elem in d_ranges:
        r = elem[0].split('-')
        idx = elem[1]
        month, year = month_and_year(data, idx[1])
        if month and year:
            range_begin = f"{r[0]}_{month}_{year}"
            range_end = f"{r[1]}_{month}_{year}"
            ranges.append(range_converter([range_begin, range_end]))
    for elem in d_days:
        r = elem[0]
        idx = elem[1]
        month, year = month_and_year(data, idx[1])
        if month and year:
            date = f"{r}_{month}_{year}"
            days.append(date_converter(date))

    return {'ranges': ranges, 'days': days}


def scan_pdf(filename=None, stream=None):
    if not filename and not stream:
        return []
    if filename:
        doc = fitz.open(filename)
    elif stream:
        doc = fitz.open(stream=stream)
    for page in doc:
        text = page.get_text(flags=fitz.TEXTFLAGS_TEXT | fitz.TEXT_DEHYPHENATE)
        break  # tylko pierwsza strona
    text_dash = re.sub(r"\s+", r"_", text)
    return parser(text_dash)


def parser(text_dash):
    found_substrings = []
    days_separ = r"w_dniu|w_dniach|w_okresie|na_okres"
    para_regex = r"\§((?!\§).)*?(zakaz).*(noszenia).*(broni).*(obszarze|terenie).*?\§"
    para_regex2 = r"\§((?!\§).)*?(obszarze|terenie).*(zakaz).*(noszenia).*(broni).*?\§"
    dir1_regex = rf"(zakaz).*({days_separ})"
    dir2_regex = rf"({days_separ}).*(zakaz)"
    end_regex = rf"({MONTHS_REGEX})\_\d{{4}}"

    para_match_obj = re.search(para_regex, text_dash) or re.search(para_regex2, text_dash)
    if not para_match_obj:
        logging.error("Analiza PDF zakończyła się błędem: nie znalaziono paragrafu :(")
        return []
    para_match = para_match_obj.group().strip('§').strip('_')

    phase0 = re.split(r"obszarze|terenie", para_match)
    if re.search(dir1_regex, para_match):
        # obsługa składni: Wprowadza się zakaz [..] na obszarze [..] w dniach [...]
        phase0.pop(0)  # wyrzucamy wszystko co jest przed "obszarem"
    elif re.search(dir2_regex, para_match):
        # obsługa składni: Wprowadza się w dniach [..] na obszarze [..] zakaz.
        search_obj = re.search(days_separ, para_match)
        phase0[1] = phase0[1].split("zakaz")[0]
        phase0[0] = phase0[1]+phase0[0][search_obj.span()[0]:]
        phase0.pop(1)
    else:
        logging.error("Analiza PDF zakończyła się błędem nie udało się poprawnie "
                      "ustalić kierunku przetwarzania :(")
        return []

    if phase0[0].startswith(':'):
        # obsługa sytuacji gdy po "obszarze" jest kilka podpunktów kończących się ";"
        tmp = phase0.pop(0)
        phase0 += tmp.split(';')
    for phase1 in phase0:
        phase2 = phase1.strip(":;._ ")
        end_match_list = [m.end() for m in re.finditer(end_regex, phase2)]
        if not end_match_list:
            return []
        phase3 = phase2[:end_match_list.pop()]
        phase4 = re.split(days_separ, phase3)
        phase5 = [s.strip(" ,;-–_") for s in phase4]
        area = phase5[0]
        date = phase5[1]
        if len(phase5) != 2:
            logging.error("Analiza PDF zakończyła się błędem: nie udało się poprawnie "
                          "przetworzyć danych - faza 5 :(")
            return []
        area = re.sub(r"\d+\)\_", "", area)
        date = date.replace("od_dnia_", "")
        date = date.replace("_do_dnia", "-")
        date = date.replace("—", "-")
        date = date.replace("r.", "")
        date = re.sub(r"oraz", r"i", date)
        date = re.sub(r"\_i\_", r"i", date)
        date_out = date_proc(date)
        if area and date_out:
            found_substrings.append({"area": area.replace("_", " "), "dates": date_out})
        else:
            logging.error("Analiza PDF zakończyła się błędem: nie udało się poprawnie "
                          "przetworzyć danych - faza 6 :(")
            return []
    return found_substrings
