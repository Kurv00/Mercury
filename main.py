import os, sys
import time
from cryptography.fernet import Fernet

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

class PasswordManager:
    def __init__(self):
        self.key = None
        self.password_dict = {}

    # ---------- KEY HANDLING ----------
    def create_or_load_key(self, path="top_secret.key"):
        if os.path.exists(path):
            with open(path, "rb") as f:
                self.key = f.read()
            print("Encryption key loaded successfully.")
        else:
            self.key = Fernet.generate_key()
            with open(path, "wb") as f:
                f.write(self.key)
            print("New encryption key generated.")

    # ---------- FILE HANDLING ----------
    def get_site_filename(self, site):
        site = site.lower().strip()
        safe = "".join(ch for ch in site if ch.isalnum() or ch in ("-", "_"))
        if not safe:
            safe = "site"
        directory = "vault-mcx"
        if not os.path.exists(directory):
            os.makedirs(directory)
        return os.path.join(directory, f"{safe}.mcx")

    # ---------- ADD PASSWORD ----------
    def add_password(self, site, username, password):
        filename = self.get_site_filename(site)
        encrypted_data = Fernet(self.key).encrypt(f"{username}\n{password}".encode("utf-8"))
        with open(filename, "wb") as f:
            f.write(encrypted_data)
        self.password_dict[site.lower()] = (username, password)
        clear_console()
        print(f"(Credentials saved for '{site}')\nUsername: {username}\nPassword: {password}\n")

    # ---------- LOAD SITE (SHOW CREDENTIALS) ----------
    def load_site(self, site):
        filename = self.get_site_filename(site)
        if not os.path.exists(filename):
            print(f"ERROR: No saved credentials for '{site}'. You can always add new ones!")
            return
        try:
            with open(filename, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = Fernet(self.key).decrypt(encrypted_data).decode("utf-8")
            username, password = decrypted_data.split("\n", 1)
            self.password_dict[site.lower()] = (username, password)
            clear_console()
            print(f"[Credentials for '{site}']\nUsername: {username}\nPassword: {password}\n")
        except Exception as e:
            print(f"ERROR: Failed to decrypt or load '{site}' — possibly wrong key or corrupted file.")
            print("DETAILS:", e)

    # ---------- VIEW PASSWORD ----------
    def get_password(self, site):
        site = site.lower().strip()
        if site not in self.password_dict:
            self.load_site(site)
            return
        username, password = self.password_dict[site]
        clear_console()
        print(f"(Credentials for '{site}')\nUsername: {username}\nPassword: {password}\n")


# ---------- MAIN INTERFACE ----------
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
            result = secondary_options()
            if result == "back":
                continue
        elif choice == "2":
            site = input("Enter the site name to load: ").strip()
            pm.load_site(site)
            result = secondary_options()
            if result == "back":
                continue
        elif choice == "3":
            site = input("Enter the site name to view credentials: ").strip()
            pm.get_password(site)
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