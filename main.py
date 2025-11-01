import os, sys, time
from manager import PasswordManager

def secondary_options():
    print("""
─────────────── OPTIONS ───────────────
1. Back to main menu
2. Exit
───────────────────────────────────────
    """)
    while True:
        choice = input("Enter your choice (1-2): ").strip()
        if choice == "1":
            clear_console()
            return "back"
        elif choice == "2":
            print("Exiting Mercury...")
            time.sleep(1)
            clear_console()
            sys.exit(0)
        else:
            print("ERROR: Invalid choice — please enter 1 or 2.")

def clear_console():
    if os.name == 'nt':
        os.system('cls')
    elif os.name == 'posix':
        os.system('clear')
    else:
        print("ERROR: Unrecognized operating system. Cannot clear console")

def main():
    pm = PasswordManager()
    pm.create_or_load_key()
    while True:
        clear_console()
        print("Welcome to Mercury")
        print("""
─────────────── MAIN MENU ───────────────
1. Add site credentials
2. Load site credentials
3. View saved site credentials
4. Exit
─────────────────────────────────────────
        """)
        choice = input("Enter your choice (1-4): ").strip()
        if choice == "1":
            site = input("Enter the site name: ").strip()
            username = input("Enter the username: ").strip()
            password = input("Enter the password: ").strip()
            pm.add_password(site, username, password)
            clear_console()
            print(f"(Credentials saved for '{site}')\nUsername: {username}\nPassword: {password}\n")
            result = secondary_options()
            if result == "back":
                continue
        elif choice == "2":
            site = input("Enter the site name to load: ").strip()
            creds = pm.load_site(site)
            clear_console()
            if creds:
                username, password = creds
                print(f"[Credentials for '{site}']\nUsername: {username}\nPassword: {password}\n")
            result = secondary_options()
            if result == "back":
                continue
        elif choice == "3":
            site = input("Enter the site name to view credentials: ").strip()
            creds = pm.get_password(site)
            clear_console()
            if creds:
                username, password = creds
                print(f"(Credentials for '{site}')\nUsername: {username}\nPassword: {password}\n")
            result = secondary_options()
            if result == "back":
                continue
        elif choice == "4":
            print("Exiting Mercury...")
            time.sleep(1.5)
            clear_console()
            sys.exit(0)
        else:
            print("ERROR: Invalid choice — please select from 1 to 4.")

if __name__ == "__main__":
    main()