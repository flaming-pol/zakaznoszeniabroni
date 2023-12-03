---

# ZakazNoszeniaBroni.pl

Serwis służy dostarczaniu informacji o zakazach noszenia i przemieszczania broni palnej na terenie Polski, tj. działań Urzędu na podstawie art. 33 ust. 1 Ustawy o Broni i Amunicji.

Serwis dostarcza informacje przy pomocy:
  * interfejsu graficznego na stronie internetowej <a href="https://zakaznoszeniabroni.pl" target="_blank">https://zakaznoszeniabroni.pl</a>
  * interfejsu JSON na stronie internetowej <a href="https://zakaznoszeniabroni.pl/json.php" target="_blank">https://zakaznoszeniabroni.pl/json.php</a>
  * powiadomień wysyłanych na e-mail

Aktualne kanały powiadomień:
  * e-mail

Działanie serwisu polega na:
  * cyklicznym odpytywaniu strony <a href="https://dziennikustaw.gov.pl/DU" target="_blank">Dziennika Ustaw RP</a> w celu wyszukania wszystkich rozporządzeń zawierających w tytule słowo "<code>broni</code>";
  * przetwarzaniu otrzymanej treści przy pomocy wyrażenia regularnego <code>zakaz(.)*\s(noszenia|przemieszczania)+(.)*broni+</code>;
  * ekstrakcji szczegółowych danych ze zwróconych rozporządzeń;
  * sprawdzeniu czy pojawiło się nowe rozporządzenie. Jeśli tak, następuje wysyłka powiadomienia do zarejestrowanych użytkowników.

Serwis podzielony jest na dwa komponenty:
  * **backend** - odpowiedzialny za przetwarzanie treści Dziennika Ustaw oraz wysyłkę powiadomień (katalog <code>src</code> tego repozytorium);
  * **frontend** - stronę internetową w technologii PHP odpowiedzialną za prezentowanie zawartości bazy danych (katalog <code>web</code> tego repozytorium).

## Technologie

Backend:
  * **Python 3.11**
  * SQLAlchemy
  * BeautifulSoup4
  * MySQL 8
  * Docker

Frontend:
  * **PHP 8.1**
  * PDO MySQL
  * Memcached

## Konfiguracja programu

W zależności od trybu uruchomienia (środowisko deweloperskie czy produkcyjne) należy odpowiednio skonfigurować program. Konfigurację można przeprowadzić przy pomocy zmiennych środowiskowych i pliku *dotEnv* (lokalizacja: <code>src/.env</code>).

Opis parametrów konfiguracyjnych znajduje się w pliku <code>.env</code>.


## Środowisko deweloperskie

Konfiguracja znajduje się w pliku <code>.env</code> (link symboliczny do <code>src/.env</code>).

```console
  docker-compose up
```

Zostaną uruchomione komponenty:
  * **db** - baza danych MySQL 8, port <code>3306</code>
  * **phpmyadmin**, port <code>8080</code>
  * **memcached**
  * **apache** - hostujący frontend serwisu, port <code>8081</code>
  * **mailhog**, port <code>8025</code> do obsługi webaplikacji, <code>1025</code> do przyjmowania e-maili;
  * **prog** - kontener z backendem aplikacji

Aplikacja (program backendu) nie jest uruchamiana automatycznie. Należy zalogować się do kontenera <code>prog</code> i uruchomić program ręcznie:

```console
  docker-compose exec prog bash
  python znb.py
```

## Środowisko produkcyjne

Konfiguracja znajduje się w pliku <code>src/.env-prod</code>.

W środowisku produkcyjnym uruchamiany jest tylko jeden kontener <code>prog-prod</code>. Obecnie wykorzystywana jest zdalna baza danych oraz memcached zlokalizowane na tym samym hostingu co frontend.

```console
  docker-compose -f docker-compose-prod.yml up
```

W kontenerze produkcyjnym aplikacja backendu uruchamia się automatycznie po uruchomieniu kontenera.

Kontener ma ustawioną politykę restartu na <code>on-failure</code>.

W celu automatyzacji i integracji z Linux-em przygotowano konfigurację dla <code>systemd</code> - jest ona zlokalizowana w katalogu <code>systemd</code> repozytorium.

### SPAM

Zmasowane wysyłanie powiadomień na e-mail jest obarczone ryzykiem klasyfikacji korespondencji jako niechcianej. Pomimo dochowania wszelkich starań nie mam wpływu na to, że filtr serwera poczty sklasyfikuje wiadomość wysłaną z serwisu jako SPAM. Jako właściciel <a href="https://zakaznoszeniabroni.pl" target="_blank">https://zakaznoszeniabroni.pl</a> swój serwer *Postfix* oraz domenę obudowałem następującymi mechanizmami zmniejszającymi ryzyko klasyfikacji maila jako SPAM:
  * rekord <a href="https://en.wikipedia.org/wiki/Sender_Policy_Framework" target="_blank">SPF</a> w DNS;
  * rekord <a href="https://en.wikipedia.org/wiki/DMARC" target="_blank">DMARC</a> w DNS;
  * sygnatura <a href="https://en.wikipedia.org/wiki/DomainKeys_Identified_Mail" target="_blank">DKIM</a> dołączana do wiadomości;
  * szyfrowanie SSL/TLS.

W celu wyeliminowania ryzyka klasyfikacji e-maili z systemu jako SPAM zaleca się dodanie wyjątków / "whitelistowanie" dla dwóch domen:
  * zakaznoszeniabroni.pl - podstawowa domena serwisu;
  * zakazynoszeniabroni.pl - **z tej domeny będzie głównie kierowana korespondencja e-mail**.

W chwili pisania tego dokumentu serwis wysyłki maili został przetestowany z następującymi odbiorcami poczty. Żaden z nich nie sklasyfikował korespondencji jako SPAM:
  * gmail
  * protonmail
  * poczta wp
  * poczta interia / int.pl

## Pseudo-API

Zrozumiałe jest, że część użytkownik nie będzie zainteresowana powiadomieniami e-mail. Serwis posiada opcję integracji z własnymi narzędziami przy pomocy prostego pseudo-api. Pod adresem <a href="https://zakaznoszeniabroni.pl/json.php">https://zakaznoszeniabroni.pl/json.php</a> serwis zwraca zawartość bazy w formacie JSON:

```json5
{
  "version": 1,   // wersja struktury danych
  "last_parser_run": "2023-12-02 13:35:11",   // kiedy ostatni raz został uruchomiony backend
  "last_db_update": "2023-11-29 23:08:11",   // kiedy ostatni raz aktualizowano zawartość bazy zakazów
  "count": 26,   // ilość rozporządzeń w bazie
  "data": [   // lista rozporządzeń
    {
      "name": "Rozporządzenie ...",   // tytuł rozporządzenia
      "number": 2439,   // numer w Dzienniku Ustaw
      "year": 2023,   // rok ogłoszenia
      "pdf_url": "https://dzienn...",   // link do treści rozporządzenia
      "published_date": "09-11-2023"   // data ogłoszenia
    }
  ]
}
```

Data w polu <code>last_parser_run</code> powinna zmieniać się w interwałach ok. 30 minutowych. Taki jest aktualnie ustawiony interwał uruchamiania crawlera.

## Inne metody powiadomień

Obecnie trwają prace koncepcyjne nad przygotowaniem aplikacji na telefony z systemem Android, która byłaby w stanie wysłać powiadomienie *push* o nowych zakazach.

Najpewniejszą metodą powiadomień są wiadomości SMS. Jednak usługa ich wysyłania jest stosunkowo droga co powoduje sceptycyzm u autora projektu oraz naturalne "odsunięcie na dalszy plan" tej metody powiadomień. Możliwe, że w przyszłości jednak pojawi się taka opcja w serwisie.

## Kontakt

Kontakt do autora projektu: <a href="mailto:kontakt@zakaznoszeniabroni.pl">kontakt@zakaznoszeniabroni.pl</a>

Jeśli widzisz błędy lub perspektywy usprawnienia aplikacji - będę wdzięczny za kontakt i ewentualne *commit-a* ;-)
