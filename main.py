import sys
import os
import xml.etree.ElementTree as ET
import re
import ast
import warnings
import msvcrt
import time

# =====================================================
#  Mercury Interpreter — m2.36 (October Patch 2025)
# =====================================================

warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)


# ---------------- Safe Evaluator ---------------- #
class SafeEvalVisitor(ast.NodeVisitor):
    SAFE_NODES = (
        ast.Expression, ast.Constant,
        ast.BinOp, ast.UnaryOp,
        ast.BoolOp, ast.Compare, ast.Name, ast.Load, ast.Call,
        ast.List, ast.Tuple, ast.Dict, ast.Subscript,
        ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv,
        ast.USub, ast.UAdd, ast.And, ast.Or, ast.Eq, ast.NotEq,
        ast.Lt, ast.LtE, ast.Gt, ast.GtE, ast.In, ast.NotIn, ast.Not
    )

    SAFE_FUNCS = {
        "abs": abs, "min": min, "max": max, "sum": sum,
        "len": len, "range": range, "round": round,
        "int": int, "float": float, "str": str, "bool": bool
    }

    def __init__(self, env):
        self.env = env

    def visit(self, node):
        if not isinstance(node, self.SAFE_NODES):
            raise ValueError(f"Unsafe expression element: {type(node).__name__}")
        return super().visit(node)


def safe_eval(expr, env, lineno=None, context_tag=None):
    expr = expr.strip()
    try:
        tree = ast.parse(expr, mode="eval")
        SafeEvalVisitor(env).visit(tree)
        code = compile(tree, "<safe-eval>", "eval")
        safe_globals = {"__builtins__": None, **SafeEvalVisitor.SAFE_FUNCS}
        return eval(code, safe_globals, env)
    except Exception as e:
        line_info = f"Error in <{context_tag}> at line {lineno}." if lineno else f"Error in <{context_tag}>."
        print(f"{line_info} ({e})")
        return None


# ================= Tag System ================= #
TAG_HANDLERS = {}

def tag(name):
    def wrapper(func):
        TAG_HANDLERS[name.lower()] = func
        return func
    return wrapper


def exec_node(node, env):
    tag_name = node.tag.lower()
    handler = TAG_HANDLERS.get(tag_name)

    if handler:
        handler(node, env)
    else:
        text = (node.text or "").strip()
        if node.attrib.get("value"):
            try:
                v = safe_eval(node.attrib["value"], env, node.sourceline, tag_name)
            except Exception:
                v = node.attrib["value"]
            print(v)
        elif text:
            print(render_text_with_env(text, env))


def render_text_with_env(text, env):
    def repl(m):
        key = m.group(1)
        return str(env.get(key, "{" + key + "}"))
    return re.sub(r'\{([A-Za-z_][A-Za-z0-9_\-]*)\}', repl, text)


# ================= Core Tag Handlers ================= #
@tag("print")
def handle_print(node, env):
    print(render_text_with_env(node.text or "", env))

@tag("var")
def handle_var(node, env):
    name = node.attrib.get("name") or node.attrib.get("n")
    value = node.attrib.get("value")
    text_content = (node.text or "").strip()

    if name and value:
        try:
            env[name] = safe_eval(value, env, node.sourceline, "var")
        except Exception:
            env[name] = value
    elif not name and text_content:
        lines = [ln.strip() for ln in text_content.splitlines() if ln.strip()]
        for ln in lines:
            if ln.startswith("//") or ln.startswith("#") or ln.startswith("::"):
                continue
            m = re.match(r'^([A-Za-z_][A-Za-z0-9_\-]*)\s*:\s*(.+?);?$', ln)
            if not m:
                continue
            key, val_expr = m.group(1), m.group(2).strip()
            try:
                env[key] = safe_eval(val_expr, env)
            except Exception:
                env[key] = val_expr


@tag("if")
def handle_if(node, env):
    cond = node.attrib.get("condition") or (node.text or "").strip()
    try:
        if safe_eval(cond, env, node.sourceline, "if"):
            for child in node:
                exec_node(child, env)
    except Exception:
        pass


@tag("for")
def handle_for(node, env):
    var = node.attrib.get("var") or "i"
    in_expr = node.attrib.get("in") or (node.text or "").strip()
    try:
        if re.match(r'^\(\s*\d+\s*,\s*\d+\s*\)$', in_expr):
            start, end = [int(x.strip()) for x in in_expr[1:-1].split(",")]
            iterable = range(start, end)
        else:
            iterable = safe_eval(in_expr, env, node.sourceline, "for")

        for v in iterable:
            env[var] = v
            for child in node:
                exec_node(child, env)
    except Exception:
        pass


@tag("calc")
def handle_calc(node, env):
    expr = (node.text or "").strip()
    expr = re.sub(r'\{([A-Za-z_][A-Za-z0-9_\-]*)\}', lambda m: str(env.get(m.group(1), "{" + m.group(1) + "}")), expr)
    try:
        result = safe_eval(expr, env, node.sourceline, "calc")
        if result is not None:
            print(result)
    except Exception:
        pass


@tag("wait")
def handle_wait(node, env):
    seconds = float(node.attrib.get("seconds", 1))
    print(f"[waiting {seconds} sec]")
    time.sleep(seconds)


@tag("input")
def handle_input(node, env):
    prompt = render_text_with_env(node.attrib.get("prompt", ""), env)
    var_name = node.attrib.get("var") or node.attrib.get("name")
    if var_name:
        env[var_name] = input(prompt)


# ================= Script Runner ================= #
def run_ks(source_text, filename="<string>"):
    env = {}

    wrapped = "<root>\n" + source_text + "\n</root>"
    try:
        parser = ET.XMLParser(target=ET.TreeBuilder())
        root = ET.fromstring(wrapped, parser=parser)
    except ET.ParseError as e:
        print("[parse error]:", e)
        return

    for child in root:
        exec_node(child, env)


# ================= Plugin Loader ================= #
def load_plugins(directory="plugins"):
    if not os.path.exists(directory):
        return
    sys.path.insert(0, directory)
    for file in os.listdir(directory):
        if file.endswith(".py"):
            __import__(file[:-3])


# ================= CLI ================= #
def main():
    os.system('cls' if os.name == 'nt' else 'clear')
    print("=== Mercury Interpreter (Safe Mode) ===")

    load_plugins()

    while True:
        path = input("Enter path to .mc file (example.mc): ").strip()
        if not path:
            print("No file provided. Exiting...")
            return

        if not path.lower().endswith(".mc"):
            path += ".mc"

        if not os.path.exists(path):
            print("File not found.")
            continue

        if not path.lower().endswith(".mc"):
            print("Invalid file type.")
            continue

        try:
            with open(path, 'r', encoding='utf-8') as f:
                src = f.read()
        except Exception as e:
            print("Could not read file:", e)
            continue

        print(f"\n--- Running {path} ---\n")
        run_ks(src, filename=path)
        print(f"\n--- Done ---")

        print("\nPress 'M' to exit, any other key to run a new file...")
        key = msvcrt.getch()
        if key.lower() == b'm':
            print("Exiting...")
            time.sleep(1)
            sys.exit(0)
        else:
            os.system('cls')
            print("=== Mercury Interpreter (Safe Mode) ===")


if __name__ == "__main__":
    main()
