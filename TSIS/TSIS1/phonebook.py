import psycopg2
import csv
import json

# Подключение к базе
conn = psycopg2.connect(
    host="localhost",
    database="PhoneBook",
    user="postgres",
    password="FadeQewzi2007!"
)
cur = conn.cursor()


# ------------------------
# ADD CONTACT 
# ------------------------
def add_contact_console():
    first_name = input("First name: ")
    last_name = input("Last name: ")
    phone = input("Phone: ")
    email = input("Email: ")
    birthday = input("Birthday (YYYY-MM-DD): ")
    group = input("Group (Family/Work/Friend/Other): ")

    # -------------------------
    # GET OR CREATE GROUP
    # -------------------------
    cur.execute("SELECT id FROM groups WHERE name=%s", (group,))
    group_row = cur.fetchone()

    if group_row:
        group_id = group_row[0]
    else:
        cur.execute(
            "INSERT INTO groups(name) VALUES(%s) RETURNING id",
            (group,)
        )
        group_id = cur.fetchone()[0]

    # -------------------------
    # INSERT CONTACT
    # -------------------------
    cur.execute("""
        INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
        VALUES (%s, %s, %s, %s, %s)
        RETURNING id
    """, (first_name, last_name, email, birthday, group_id))

    contact_id = cur.fetchone()[0]

    # -------------------------
    # INSERT PHONES
    # -------------------------
    phones = []

    while True:
        phone = input("Phone (empty to stop): ")
        if phone == "":
            break

        phone_type = input("Type (home/work/mobile): ")

        if phone_type not in ("home", "work", "mobile"):
            print("Invalid type, set to mobile")
            phone_type = "mobile"

        phones.append((phone, phone_type))

    for phone, phone_type in phones:
        cur.execute("""
            INSERT INTO phones (contact_id, phone, type)
            VALUES (%s, %s, %s)
        """, (contact_id, phone, phone_type))

    conn.commit()
    print("Contact added!")


# ------------------------
# CSV IMPORT 
# ------------------------
def add_contacts_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)

        for row in reader:
            cur.execute("SELECT id FROM groups WHERE name = %s", (row['group'],))
            group_row = cur.fetchone()
            group_id = group_row[0] if group_row else None

            cur.execute("""
                INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id
            """, (
                row['first_name'],
                row['last_name'],
                row['email'],
                row['birthday'],
                group_id
            ))

            contact_id = cur.fetchone()[0]

            cur.execute("""
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (
                contact_id,
                row['phone'],
                row['type']
            ))

    conn.commit()
    print("CSV imported (extended)!")


# ------------------------
# UPDATE CONTACT
# ------------------------
def update_contact():
    phone = input("Enter phone to update: ")
    new_first_name = input("New first name: ")
    new_phone = input("New phone (optional): ")

    cur.execute("""
        SELECT c.id
        FROM contacts c
        JOIN phones p ON p.contact_id = c.id
        WHERE p.phone = %s
    """, (phone,))

    result = cur.fetchone()
    if not result:
        print("Contact not found")
        return

    contact_id = result[0]

    cur.execute("""
        UPDATE contacts
        SET first_name = %s
        WHERE id = %s
    """, (new_first_name, contact_id))

    if new_phone.strip():
        cur.execute("""
            UPDATE phones
            SET phone = %s
            WHERE contact_id = %s
        """, (new_phone, contact_id))

    conn.commit()
    print("Contact updated!")


# ------------------------
# DELETE CONTACT 
# ------------------------
def delete_contact():
    choice = input("Delete by name or phone? ")

    if choice.lower() == "name":
        name = input("Enter first name: ")
        cur.execute("CALL delete_contact(%s, NULL)", (name,))
    else:
        phone = input("Enter phone: ")
        cur.execute("CALL delete_contact(NULL, %s)", (phone,))

    conn.commit()
    print("Deleted!")


# ------------------------
# SHOW ALL CONTACTS
# ------------------------
def query_contacts():
    cur.execute("""
        SELECT c.first_name, c.last_name, c.email, c.birthday,
               g.name,
               p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
    """)

    for row in cur.fetchall():
        print(row)


# ------------------------
# SORT CONTACTS 
# ------------------------
def sort_contacts():
    print("Sort by:")
    print("1 Name")
    print("2 Birthday")
    print("3 Date added")

    choice = input("Choose: ")

    if choice == "1":
        order = "c.first_name"
    elif choice == "2":
        order = "c.birthday"
    elif choice == "3":
        order = "c.created_at"
    else:
        print("Invalid choice")
        return

    query = f"""
        SELECT c.first_name, c.last_name, c.email, c.birthday,
               g.name,
               p.phone, p.type
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        ORDER BY {order}
    """

    cur.execute(query)

    for row in cur.fetchall():
        print(row)


# ------------------------
# SEARCH FUNCTION
# ------------------------
def search_contacts():
    pattern = input("Search: ")
    cur.execute("SELECT * FROM search_contacts(%s)", (pattern,))
    for row in cur.fetchall():
        print(row)


# ------------------------
# PAGINATION FUNCTION
# ------------------------
def paginate_contacts():
    limit = 3
    offset = 0

    while True:
        cur.execute("SELECT * FROM get_contacts_paginated(%s, %s)", (limit, offset))
        rows = cur.fetchall()

        for r in rows:
            print(r)

        action = input("\n[n] next [p] prev [q] quit: ")

        if action == "n":
            offset += limit
        elif action == "p" and offset >= limit:
            offset -= limit
        elif action == "q":
            break


# ------------------------
# FILTER BY GROUP
# ------------------------
def filter_by_group():
    group = input("Group: ")

    cur.execute("""
        SELECT c.first_name, c.last_name, g.name, p.phone
        FROM contacts c
        JOIN groups g ON c.group_id = g.id
        LEFT JOIN phones p ON c.id = p.contact_id
        WHERE g.name = %s
    """, (group,))

    for row in cur.fetchall():
        print(row)


# ------------------------
# SEARCH BY EMAIL
# ------------------------
def search_by_email():
    email = input("Email search: ")

    cur.execute("""
        SELECT c.first_name, c.last_name, c.email, g.name
        FROM contacts c
        LEFT JOIN groups g ON c.group_id = g.id
        WHERE c.email ILIKE %s
    """, ('%' + email + '%',))

    for row in cur.fetchall():
        print(row)


# ------------------------
# EXPORT JSON
# ------------------------
def export_to_json():
    cur.execute("""
        SELECT c.first_name, c.last_name, c.email, c.birthday, g.name,
               json_agg(json_build_object('phone', p.phone, 'type', p.type)) as phones
        FROM contacts c
        LEFT JOIN phones p ON c.id = p.contact_id
        LEFT JOIN groups g ON c.group_id = g.id
        GROUP BY c.id, g.name
    """)

    data = cur.fetchall()

    result = []
    for row in data:
        result.append({
            "first_name": row[0],
            "last_name": row[1],
            "email": row[2],
            "birthday": str(row[3]),
            "group": row[4],
            "phones": row[5]
        })

    with open("contacts.json", "w") as f:
        json.dump(result, f, indent=4)

    print("Export done")


# ------------------------
# IMPORT JSON
# ------------------------
def import_from_json():
    with open("contacts.json", "r") as f:
        data = json.load(f)

    for c in data:
        cur.execute("SELECT id FROM contacts WHERE first_name=%s AND last_name=%s",
                    (c["first_name"], c["last_name"]))

        existing = cur.fetchone()

        if existing:
            action = input(f"Contact {c['first_name']} {c['last_name']} exists (skip/overwrite): ")
            if action.lower() == "skip":
                continue
            contact_id = existing[0]

            cur.execute("DELETE FROM phones WHERE contact_id=%s", (contact_id,))

            cur.execute("""
                UPDATE contacts
                SET email=%s, birthday=%s,
                    group_id=(SELECT id FROM groups WHERE name=%s)
                WHERE id=%s
            """, (c["email"], c["birthday"], c["group"], contact_id))

        else:
            cur.execute("""
                INSERT INTO contacts (first_name, last_name, email, birthday, group_id)
                VALUES (%s, %s, %s, %s,
                (SELECT id FROM groups WHERE name=%s))
                RETURNING id
            """, (c["first_name"], c["last_name"], c["email"], c["birthday"], c["group"]))

            contact_id = cur.fetchone()[0]

        for p in c["phones"]:
            cur.execute("""
                INSERT INTO phones (contact_id, phone, type)
                VALUES (%s, %s, %s)
            """, (contact_id, p["phone"], p["type"]))

    conn.commit()
    print("Imported!")


# ------------------------
# MAIN MENU
# ------------------------
def main():
    while True:
        print("\n--- PHONEBOOK ---")
        print("1 Add contact")
        print("2 CSV import")
        print("3 Update")
        print("4 Delete")
        print("5 Show all")
        print("6 Search")
        print("7 Pagination")
        print("8 Filter group")
        print("9 Search email")
        print("10 Export JSON")
        print("11 Import JSON")
        print("12 Exit")
        print("13 Sort")

        choice = input("Choose: ")

        if choice == "1":
            add_contact_console()
        elif choice == "2":
            add_contacts_csv(input("CSV file: "))
        elif choice == "3":
            update_contact()
        elif choice == "4":
            delete_contact()
        elif choice == "5":
            query_contacts()
        elif choice == "6":
            search_contacts()
        elif choice == "7":
            paginate_contacts()
        elif choice == "8":
            filter_by_group()
        elif choice == "9":
            search_by_email()
        elif choice == "10":
            export_to_json()
        elif choice == "11":
            import_from_json()
        elif choice == "12":
            break
        elif choice == "13":
            sort_contacts()


if __name__ == "__main__":
    main()
    cur.close()
    conn.close()