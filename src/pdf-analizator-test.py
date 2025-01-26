import re

from znb.pdf import parser, scan_pdf


def main():
    z1()
    z2()
    z3()
    z4()
    z5()
    other()


def run(data, test=False):
    if test:
        data2 = re.sub(r"\s+", r"_", data)
        out = parser(data2)
    else:
        print(f"--> {data}")
        out = scan_pdf(data)
    for x in out:
        print(f" obszar: {x.get('area')}\n data: {x.get('dates')}\n")
    return out


def z1():
    # ======================================================================================
    #  Z1  - najprostsza grupa: zawiera tylko datę obowiązywania
    # ======================================================================================
    retval = run("pdf-tests/Z1/1.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy oraz miasta Wrocławia',
                      'dates': {'ranges': [], 'days': ['11-11-2023']}}]

    retval = run("pdf-tests/Z1/2.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [], 'days': ['05-04-2023']}}]

    retval = run("pdf-tests/Z1/5.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy, miasta Krakowa i miasta Wrocławia',
                       'dates': {'ranges': [], 'days': ['11-11-2022']}}]

    retval = run("pdf-tests/Z1/8.pdf")
    assert retval == [{'area': 'miasta Oświęcim i miejscowości Brzezinka w gminie Oświęcim w województwie małopolskim',
                       'dates': {'ranges': [], 'days': ['27-01-2020']}}]

    retval = run("pdf-tests/Z1/9.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [], 'days': ['11-11-2019']}}]


def z2():
    # ======================================================================================
    #  Z2  - zawiera tylko datę obowiązywania zapisaną jako przedział dat
    # ======================================================================================
    retval = run("pdf-tests/Z2/10.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [['30-08-2019', '02-09-2019']], 'days': []}}]

    retval = run("pdf-tests/Z2/11.pdf")
    assert retval == [{'area': 'gminy Kostrzyn nad Odrą i sołectwa Dąbroszyn w gminie Witnica w województwie lubuskim',
                       'dates': {'ranges': [['29-07-2019', '06-08-2019']], 'days': []}}]

    retval = run("pdf-tests/Z2/12.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [['11-02-2019', '15-02-2019']], 'days': []}}]

    retval = run("pdf-tests/Z2/14.pdf")
    assert retval == [{'area': 'gminy Kostrzyn nad Odrą i sołectwa Dąbroszyn w gminie Witnica w województwie lubuskim',
                       'dates': {'ranges': [['30-07-2018', '08-08-2018']], 'days': []}}]

    retval = run("pdf-tests/Z2/3.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [['20-02-2023', '22-02-2023']], 'days': []}}]

    retval = run("pdf-tests/Z2/4.pdf")
    assert retval == [{'area': 'miasta Łodzi',
                       'dates': {'ranges': [['29-11-2022', '03-12-2022']], 'days': []}}]

    retval = run("pdf-tests/Z2/6.pdf")
    assert retval == [{'area': 'województwa podlaskiego i lubelskiego przyległym do granicy państwowej z Republiką Białorusi',
                       'dates': {'ranges': [['02-03-2022', '30-06-2022']], 'days': []}}]

    retval = run("pdf-tests/Z2/7.pdf")
    assert retval == [{'area': 'województwa podlaskiego i lubelskiego przyległym do granicy państwowej z Republiką Białorusi',
                       'dates': {'ranges': [['01-12-2021', '01-03-2022']], 'days': []}}]


def z3():
    # ======================================================================================
    #  Z3  - zawiera więcej niż jeden podpunkt dotyczący obszaru zakazu
    # ======================================================================================
    retval = run("pdf-tests/Z3/13.pdf")
    assert retval == [{'area': 'miasta Krakowa',
                       'dates': {'ranges': [['19-10-2018', '25-10-2018']], 'days': []}},
                      {'area': 'województwa śląskiego i województwa małopolskiego',
                       'dates': {'ranges': [['01-12-2018', '15-12-2018']], 'days': []}}]

    retval = run("pdf-tests/Z3/15.pdf")
    assert retval == [{'area': 'województwa małopolskiego',
                       'dates': {'ranges': [['01-07-2017', '13-07-2017']], 'days': []}},
                      {'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [['05-07-2017', '07-07-2017']], 'days': []}},
                      {'area': 'województwa dolnośląskiego',
                       'dates': {'ranges': [['18-07-2017', '31-07-2017']], 'days': []}}]

    retval = run("pdf-tests/Z3/16.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [['04-07-2016', '10-07-2016']], 'days': []}},
                      {'area': 'województwa małopolskiego oraz województwa śląskiego',
                       'dates': {'ranges': [['20-07-2016', '01-08-2016']], 'days': []}}]

    retval = run("pdf-tests/Z3/17.pdf")
    assert retval == [{'area': 'miasta Oświęcim, gminy wiejskiej Oświęcim',
                       'dates': {'ranges': [], 'days': ['27-01-2015']}}]


def z4():
    # ======================================================================================
    #  Z4  - zawiera dane w układzie dwukolumnowym
    # ======================================================================================
    retval = run("pdf-tests/Z4/18.pdf")
    assert retval == [{'area': 'miasta stołecznego Warszawy',
                       'dates': {'ranges': [], 'days': ['17-04-2010']}},
                      {'area': 'miasta Krakowa',
                       'dates': {'ranges': [], 'days': ['18-04-2010']}}]

    retval = run("pdf-tests/Z4/19.pdf")
    assert retval == [{'area': 'miasta Krakowa',
                       'dates': {'ranges': [['18-02-2009', '20-02-2009']], 'days': []}}]

    retval = run("pdf-tests/Z4/20.pdf")
    assert retval == [{'area': 'miasta Poznania',
                       'dates': {'ranges': [['27-11-2008', '15-12-2008']], 'days': []}}]


def z5():
    retval = run("pdf-tests/Z5/21.pdf")
    assert retval == [{'area': 'miasta sto∏ecznego Warszawy',
                       'dates': {'ranges': [], 'days': ['25-05-2006', '26-05-2006']}},
                      {'area': 'miasta Cz´stochowy',
                       'dates': {'ranges': [], 'days': ['26-05-2006']}},
                      {'area': 'województwa ma∏opolskiego',
                       'dates': {'ranges': [], 'days': ['26-05-2006', '27-05-2006', '28-05-2006']}}]

    retval = run("pdf-tests/Z5/22.pdf")
    assert retval == [{'area': 'miasta sto∏ecznego Warszawy.',
                       'dates': {'ranges': [['15-05-2005', '18-05-2005']], 'days': []}}]

    retval = run("pdf-tests/Z5/25.pdf")
    assert retval == [{'area': 'województwa ma∏opolskiego',
                       'dates': {'ranges': [['16-08-2002', '19-08-2002']], 'days': []}}]


def other():
    # składnia podobna do Z5/25.pdf
    test1 = "§ Wprowadza się zakaz noszenia broni na obszarze miasta Poznania w dniach 27-29 listopada 2008 r. §"
    print(f"--> synthetic: {test1}")
    retval = run(test1, test=True)
    assert retval == [{'area': 'miasta Poznania',
                      'dates': {'ranges': [['27-11-2008', '29-11-2008']], 'days': []}}]

    test1 = "§ Wprowadza się zakaz noszenia broni na obszarze miasta Poznania w dniach 27-29 i 31 listopada 2008 r.§"
    print(f"--> synthetic: {test1}")
    retval = run(test1, test=True)
    assert retval == [{'area': 'miasta Poznania',
                      'dates': {'ranges': [['27-11-2008', '29-11-2008']], 'days': ['31-11-2008']}}]

    test1 = "§ Wprowadza się zakaz noszenia broni na obszarze miasta Poznania w dniach 27 i 29-31 listopada 2008 r.§"
    print(f"--> synthetic: {test1}")
    retval = run(test1, test=True)
    assert retval == [{'area': 'miasta Poznania',
                      'dates': {'ranges': [['29-11-2008', '31-11-2008']], 'days': ['27-11-2008']}}]

    # składnia podobna do Z5/23.pdf i Z5/24.pdf
    test1 = "§ Wprowadza się zakaz noszenia broni na obszarze miasta Poznania w dniach 27 listopada - 03 grudnia 2008 r.§"
    print(f"--> synthetic: {test1}")
    retval = run(test1, test=True)
    assert retval == [{'area': 'miasta Poznania',
                      'dates': {'ranges': [['27-11-2008', '03-12-2008']], 'days': []}}]

    test1 = "§ Wprowadza się zakaz noszenia broni na obszarze miasta Poznania w dniach 27-29 września 2008 r. i 30-31 listopada 2008 r.§"
    print(f"--> synthetic: {test1}")
    retval = run(test1, test=True)
    assert retval == [{'area': 'miasta Poznania',
                      'dates': {'ranges': [['27-09-2008', '29-09-2008'], ['30-11-2008', '31-11-2008']], 'days': []}}]

    test1 = "§ Wprowadza się w dniach 27, 28 i 30 listopada 2008 r. zakaz noszenia broni na obszarze miasta Poznania §"
    print(f"--> synthetic: {test1}")
    retval = run(test1, test=True)
    assert retval == [{'area': 'miasta Poznania',
                      'dates': {'ranges': [], 'days': ['27-11-2008', '28-11-2008', '30-11-2008']}}]

    test1 = "§ Wprowadza się w dniach 27, 28 i 30 listopada 2008 r. na obszarze miasta Poznania zakaz noszenia broni §"
    print(f"--> synthetic: {test1}")
    retval = run(test1, test=True)
    assert retval == [{'area': 'miasta Poznania',
                      'dates': {'ranges': [], 'days': ['27-11-2008', '28-11-2008', '30-11-2008']}}]


main()
