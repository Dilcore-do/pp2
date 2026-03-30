import psycopg2
import csv

# Подключение к базе
conn = psycopg2.connect(
    host="localhost",
    database="PhoneBook",
    user="postgres",       
    password="FadeQewzi2007!"  
)
cur = conn.cursor()

# Добавление контакта с консоли
def add_contact_console():
    first_name = input("First name: ")
    last_name = input("Last name: ")
    phone = input("Phone: ")
    email = input("Email (optional): ")
    cur.execute(
        "INSERT INTO contacts (first_name, last_name, phone_number, email) VALUES (%s,%s,%s,%s)",
        (first_name, last_name, phone, email)
    )
    conn.commit()
    print("Contact added!")

# Добавление контактов из CSV
def add_contacts_csv(filename):
    with open(filename, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            cur.execute(
                "INSERT INTO contacts (first_name, last_name, phone_number, email) VALUES (%s,%s,%s,%s)",
                (row['first_name'], row['last_name'], row['phone_number'], row.get('email', None))
            )
    conn.commit()
    print("Contacts from CSV added!")

# Обновление контакта
def update_contact():
    phone = input("Enter phone to update: ")
    new_first_name = input("New first name: ")
    new_phone = input("New phone (press enter to skip): ")
    if new_phone.strip() == "":
        cur.execute("UPDATE contacts SET first_name=%s WHERE phone_number=%s", (new_first_name, phone))
    else:
        cur.execute("UPDATE contacts SET first_name=%s, phone_number=%s WHERE phone_number=%s", (new_first_name, new_phone, phone))
    conn.commit()
    print("Contact updated!")

# Удаление контакта
def delete_contact():
    choice = input("Delete by name or phone? (name/phone): ")
    if choice.lower() == "name":
        name = input("Enter first name: ")
        cur.execute("DELETE FROM contacts WHERE first_name=%s", (name,))
    else:
        phone = input("Enter phone: ")
        cur.execute("DELETE FROM contacts WHERE phone_number=%s", (phone,))
    conn.commit()
    print("Contact deleted!")

# Просмотр контактов
def query_contacts():
    cur.execute("SELECT * FROM contacts")
    rows = cur.fetchall()
    for row in rows:
        print(row)

# Главное меню
def main():
    while True:
        print("\n1. Add contact (console)")
        print("2. Add contacts from CSV")
        print("3. Update contact")
        print("4. Delete contact")
        print("5. Show all contacts")
        print("6. Exit")
        choice = input("Choose: ")
        if choice == "1":
            add_contact_console()
        elif choice == "2":
            filename = input("CSV filename: ")
            add_contacts_csv(filename)
        elif choice == "3":
            update_contact()
        elif choice == "4":
            delete_contact()
        elif choice == "5":
            query_contacts()
        elif choice == "6":
            break
        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()
    cur.close()
    conn.close()