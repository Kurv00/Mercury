import sys
from pathlib import Path
from core.runtime import Runtime
from core.tag_handler import TagHandler
import re

def run_file(filename: str):
    path = Path(filename)
    if not path.exists():
        print(f"[error] File not found: {filename}")
        return

    code = path.read_text(encoding="utf-8")
    run_code(code)

def run_code(code: str):
    runtime = Runtime()
    handler = TagHandler(runtime)

    # Basic lexer – find patterns like `int: a = 10;` or `console.log: {a} Lmao;`
    pattern = re.compile(r'([\w\.]+)\s*:\s*(.*?);')
    matches = pattern.findall(code)

    for tag, content in matches:
        try:
            handler.handle(tag, content.strip())
        except Exception as e:
            print(f"[error] {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: python console/console.py <file.mcx>")
        return

    filename = sys.argv[1]
    run_file(filename)

if __name__ == "__main__":
    main()