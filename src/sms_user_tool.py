import sys

from znb.db import SmsContactCRUD
from znb.db.session import SessionLocal


db_session = SessionLocal()
db_contacts = SmsContactCRUD()


def number_input(text: str):
    phone_number = input(text)
    phone_number = phone_number.replace('-', '')  # usuniecie ew. spacji
    if len(phone_number) != 9:
        print("Błąd! Numer musi mieć 9 cyfr.")
        sys.exit(1)


def activate_user():
    print("\n*** Aktywacja lub deaktywacja numeru w baziw ***")
    phone_number = number_input("\nPodaj numer telefonu do edycji:  ")
    out = db_contacts.get(db_session, phone_number)
    if not out:
        print(f"\nBłąd! Brak numeru {phone_number} w bazie!")
        sys.exit(1)
    if out.is_active:
        a = input("Numer aktywny. Czy deaktywować? [t/N]  ")
        if a not in ['t', 'T']:
            sys.exit(0)
        out.is_active = False
        db_contacts.update(db_session, out)
    else:
        a = input("Numer nieaktywny. Czy aktywować? [t/N]  ")
        if a not in ['t', 'T']:
            sys.exit(0)
        out.is_active = True
        db_contacts.update(db_session, out)


def add_user():
    print("\n*** Dodawanie nowego numeru do bazy ***")
    phone_number = number_input("\nPodaj numer telefonu do dodania:  ")
    comment = input("Komentarz do wpisu w bazie:  ")
    activate = input("Czy aktywować numer [t/N]:  ")
    act = True if activate in ['t', 'T'] else False

    in_base = db_contacts.get(db_session, phone_number)
    if in_base:
        print("\nBłąd! Taki numer jest już w bazie!")
        sys.exit(1)
    out = db_contacts.create(
        db_session,
        phone_number,
        act,
        comment
    )
    if not out:
        print("\nBłąd! Nie udało się dodać wpisu do bazy!")
        sys.exit(1)
    print(f"\nDodano wpis do bazy pod id={out.id}")


def del_user():
    print("\n*** Usuwanie numeru z bazy ***")
    phone_number = number_input("\nPodaj numer telefonu do usunięcia:  ")
    print(f"\nUsuwanie numeru: {phone_number}")
    in_base = db_contacts.get(db_session, phone_number)
    if in_base:
        db_contacts.delete(db_session, phone_number)
    else:
        print(f"\nBłąd! Brak numeru {phone_number} w bazie!")
        sys.exit(1)


def get_users(all: bool = False, number: str = ""):
    if all:
        contacts = db_contacts.get_all(db_session)
    elif number:
        c = db_contacts.get(db_session, number)
        if c:
            contacts = [c]
        else:
            return
    else:
        return
    for c in contacts:
        t = f"{c.phone_number[:3]}-{c.phone_number[3:6]}-{c.phone_number[6:]}"
        print(f"id={c.id} --> tel: {t} {'<A>' if c.is_active else '<X>'}"
              f" data utworzenia: {c.date_created} ({c.comments})")


def find_numer():
    print("\n*** Wyszukiwanie numeru w bazie ***")
    phone_number = number_input("\nPodaj numer telefonu wyszukania:  ")
    get_users(number=phone_number)


def show_users():
    print("\n*** Wszystkie numery w bazie ***")
    get_users(all=True)


def main():
    print("*** Program do obsługi numerów w module SMS ***\n\n")
    print("1. Wyświetl wszystkie numery w bazie")
    print("2. Wyszukaj numer w bazie")
    print("3. Dodaj numer do bazy")
    print("4. Aktywuj/deaktywuj numer")
    print("5. Usuń numer z bazy")
    print("\n")
    opt = input("Wybierz opcję lub wciśnij dowolny klawisz aby wyjść:  ")
    try:
        opt_int = int(opt)
    except ValueError:
        sys.exit(1)
    if opt_int < 1 or opt_int > 5:
        sys.exit(1)
    match opt_int:
        case 1:
            show_users()
        case 2:
            find_numer()
        case 3:
            add_user()
        case 4:
            activate_user()
        case 5:
            del_user()
    db_session.close()


if __name__ == "__main__":
    main()
