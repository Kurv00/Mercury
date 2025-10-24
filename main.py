import sys
from core.cli_mcx import run_line, run_script
Current_Version = 3.42
# Last Edited: October 24, 2025 (6:24 PM) by Pippo and MiKASA

def main():
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        if not script_path.endswith(".mcx" or ".mcy"):
            print("ERROR: Only .mcx files are supported.")
            return
        run_script(script_path)
    else:
        while True:
            try:
                line = input(">>> ")
                run_line(line)
            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == "__main__":
    main()