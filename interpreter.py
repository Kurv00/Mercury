import os
import time
from colorama import Fore, Style, init
init(autoreset=True)
variables = {}

def clear():
    if os.name == 'nt':
         _ = os.system('cls')
    elif os.name == 'posix':
         _ = os.system('clear')
    else:
        print(f"{Fore.RED}Error: Unsupported Operating System for '@clear' command.{Style.RESET_ALL}")

def run_line(line):
    line = line.strip()
    if not line:
        return
    if line == "@show_vars":
        print(f"{Fore.CYAN}Variables: {variables}")
        return
    if line == "@exit":
        print(f"{Fore.YELLOW}Exiting...")
        time.sleep(2)
        exit()
    if line == "@clear":
        clear()
        return
    if ':' not in line:
        print(f"{Fore.RED}Syntax Error:{Style.RESET_ALL} Unknown or invalid command --> '{line}'")
        return

    colon_index = line.find(':')
    semicolon_index = line.rfind(';')
    command = line[:colon_index].strip()
    content = line[colon_index + 1:semicolon_index if semicolon_index != -1 else None].strip()

    if command == "console.log":
        for key, val in variables.items():
            content = content.replace(f"{{{key}}}", str(val))
        print(f"{Fore.GREEN}{content}")

    elif command in ("int", "str", "bool"):
        if '=' not in content:
            print(f"{Fore.RED}Syntax Error:{Style.RESET_ALL} Expected '=' in declaration --> '{line}'")
            return

        name, value = map(str.strip, content.split('=', 1))

        if command == "int":
            try:
                variables[name] = int(value)
                print(f"{Fore.BLUE}Set int {name} = {variables[name]}")
            except ValueError:
                print(f"{Fore.RED}Type Error:{Style.RESET_ALL} Invalid integer value for: '{name}'")

        elif command == "str":
            variables[name] = value
            print(f"{Fore.BLUE}Set str {name} = '{variables[name]}'")

        elif command == "bool":
            if value.lower() == "true":
                variables[name] = True
            elif value.lower() == "false":
                variables[name] = False
            else:
                print(f"{Fore.RED}Type Error:{Style.RESET_ALL} Invalid boolean value for: '{name}'")
                return
            print(f"{Fore.BLUE}Set bool {name} = {variables[name]}")
    else:
        print(f"{Fore.RED}Syntax Error:{Style.RESET_ALL} Unknown command: '{command}'")


def run_script(file_path):
    try:
        with open(file_path, "r") as f:
            for line in f:
                run_line(line)
    except FileNotFoundError:
        print(f"{Fore.RED}File not found:{Style.RESET_ALL} {file_path}")
    except Exception as e:
        print(f"{Fore.RED}Error while running script:{Style.RESET_ALL} {e}")