import sys
from core.cli_mcx import run_line, run_script

def main():
    if len(sys.argv) > 1:
        script_path = sys.argv[1]
        if not script_path.endswith(".mcx" or ".mcy"):
            print("ERROR: Only .mcx files are supported.")
            return
        run_script(script_path)
    else:
        print("=== Mercury CLI ===")
        while True:
            try:
                line = input(">>> ")
                run_line(line)
            except KeyboardInterrupt:
                print("\nExiting...")
                break

if __name__ == "__main__":
    main()