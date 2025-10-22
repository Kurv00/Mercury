import os
import sys
import time
import msvcrt
from core.runtime import run_ks, load_plugins
Current_Version = "m3.68"

def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(f"=== Mercury Interpreter — (X-TDSL) ===")
    load_plugins()
    
    while True:
        path = input("Enter path to .mc file: ").strip()
        if not path:
            print("No file provided. Exiting...")
            return
        if not os.path.exists(path):
            print("File not found.")
            continue
        try:
            with open(path, "r", encoding="utf-8") as f:
                src = f.read()
        except Exception as e:
            print("Could not read file:", e)
            continue
        print(f"\n=== Running {path} ===\n")
        run_ks(src, filename=path)
        print(f"\n=== Done ===")
        print("\nINFO: Press 'M' to exit, any other key to run a new file...")
        key = msvcrt.getch()
        if key.lower() == b'm':
            print("INFO: Exiting...")
            time.sleep(1)
            sys.exit(0)
        os.system('cls')
        print(f"=== Mercury Interpreter — (X-TDSL) ===")


if __name__ == "__main__":
    main()
