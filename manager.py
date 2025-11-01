import os
from cryptography.fernet import Fernet

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
        return True

    # ---------- LOAD SITE (SHOW CREDENTIALS) ----------
    def load_site(self, site):
        filename = self.get_site_filename(site)
        if not os.path.exists(filename):
            print(f"ERROR: No saved credentials for '{site}'. You can always add new ones!")
            return None
        try:
            with open(filename, "rb") as f:
                encrypted_data = f.read()
            decrypted_data = Fernet(self.key).decrypt(encrypted_data).decode("utf-8")
            username, password = decrypted_data.split("\n", 1)
            self.password_dict[site.lower()] = (username, password)
            return username, password
        except Exception as e:
            print(f"ERROR: Failed to decrypt or load '{site}' — possibly wrong key or corrupted file.")
            print("DETAILS:", e)
            return None

    # ---------- VIEW PASSWORD ----------
    def get_password(self, site):
        site = site.lower().strip()
        if site not in self.password_dict:
            creds = self.load_site(site)
            if not creds:
                return None
        return self.password_dict[site.lower()]