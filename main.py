# =====================================================
#  Mercury Interpreter — m2.44 (Feature Update)
# =====================================================
import random
import sys
import os
import xml.etree.ElementTree as ET
import re
import ast
import warnings
import msvcrt
import time

# ================= Ignoring Warnings ================= #
warnings.filterwarnings("ignore", category=DeprecationWarning)
warnings.filterwarnings("ignore", category=UserWarning)
# ===================================================== #

# ================= Safe Evaluator ================= #
class SafeEvalVisitor(ast.NodeVisitor):
    SAFE_NODE_NAMES = [
        "Expression", "Constant", "Name", "Load",
        "BinOp", "UnaryOp", "BoolOp", "Compare", "Call",
        "List", "Tuple", "Dict", "Subscript",
        "Add", "Sub", "Mult", "Div", "Mod", "Pow", "FloorDiv",
        "USub", "UAdd", "And", "Or", "Eq", "NotEq",
        "Lt", "LtE", "Gt", "GtE", "In", "NotIn", "Not"
    ]
    SAFE_NODES = tuple(getattr(ast, name, None) for name in SAFE_NODE_NAMES if getattr(ast, name, None))
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

functions = {}
CLASSES = {}

def safe_eval(expr, env, lineno=None, context_tag=None):
    expr = expr.strip()
    if not expr:
        return None

    if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s*\(.*\)$', expr):
        cname = expr.split("(")[0].strip()
        if cname in CLASSES:
            cls = CLASSES[cname]
            instance = {"__class__": cname}
            instance.update(cls["fields"])
            instance["__methods__"] = cls["methods"]

            if cls.get("init"):
                local_env = env.copy()
                local_env.update(instance)
                local_env["self"] = instance
                execute_children(cls["init"], local_env)

            return instance

    try:
        tree = ast.parse(expr, mode="eval")
        SafeEvalVisitor(env).visit(tree)
        code = compile(tree, "<safe-eval>", "eval")
        safe_globals = {"__builtins__": None, **SafeEvalVisitor.SAFE_FUNCS}
        return eval(code, safe_globals, env)
    except Exception as e:
        line_info = f"Error in <{context_tag}> at line {lineno or 'unknown'}."
        print(f"{line_info} ({e})")
        return None


# ================= Utilities ================= #
def get_line(node):
    return getattr(node, 'sourceline', 'unknown')

def render_text_with_env(text, env):
    def repl(m):
        key = m.group(1)
        parts = key.split('.')
        val = env
        try:
            for part in parts:
                val = val[part] if isinstance(val, dict) else getattr(val, part)
            return str(val)
        except Exception:
            return "{" + key + "}"
    return re.sub(r'\{([A-Za-z_][A-Za-z0-9_\-\.]*)\}', repl, text)

def execute_children(node, env):
    for child in node:
        exec_node(child, env)

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
    lineno = get_line(node)
    if handler:
        handler(node, env)
    else:
        text = (node.text or "").strip()
        if node.attrib.get("value"):
            try:
                v = safe_eval(node.attrib["value"], env, lineno, tag_name)
            except Exception:
                v = node.attrib["value"]
            print(v)
        elif text:
            print(render_text_with_env(text, env))

# ================= Core Tag Handlers ================= #
@tag("print")
def handle_print(node, env):
    print(render_text_with_env(node.text or "", env))

@tag("rprint")
def handle_reverse(node, env):
    text = render_text_with_env(node.text or "", env)
    print(text[::-1])

@tag("var")
def handle_var(node, env):
    lineno = get_line(node)
    name = node.attrib.get("name") or node.attrib.get("n")
    value = node.attrib.get("value")
    text_content = (node.text or "").strip()
    if name and value:
        try:
            env[name] = safe_eval(value, env, lineno, "var")
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
                env[key] = safe_eval(val_expr, env, lineno, "var")
            except Exception:
                env[key] = val_expr

@tag("if")
def handle_if(node, env):
    lineno = get_line(node)
    cond = node.attrib.get("cond") or node.attrib.get("condition") or (node.text or "").strip()
    try:
        result = safe_eval(cond, env, lineno, "if")
        if result:
            for child in node:
                if child.tag.lower() != "else":
                    exec_node(child, env)
        else:
            for child in node:
                if child.tag.lower() == "else":
                    execute_children(child, env)
    except Exception as e:
        print(f"[if] Evaluation error at line {lineno}: {e}")

@tag("while")
def handle_while(node, env):
    lineno = get_line(node)
    cond = node.attrib.get("condition") or (node.text or "").strip()
    try:
        while safe_eval(cond, env, lineno, "while"):
            execute_children(node, env)
    except Exception as e:
        print(f"[while] error at line {lineno}: {e}")

@tag("for")
def handle_for(node, env):
    lineno = get_line(node)
    var = node.attrib.get("var") or "i"
    in_expr = node.attrib.get("range") or (node.text or "").strip()
    try:
        iterable = safe_eval(in_expr, env, lineno, "for")
        for v in iterable:
            env[var] = v
            execute_children(node, env)
    except Exception as e:
        print(f"[for] error at line {lineno}: {e}")

@tag("calc")
def handle_calc(node, env):
    lineno = get_line(node)
    expr = (node.attrib.get("expression") or node.text or "").strip()
    expr = re.sub(r'\{([A-Za-z_][A-Za-z0-9_\-]*)\}', lambda m: str(env.get(m.group(1), "{" + m.group(1) + "}")), expr)
    try:
        result = safe_eval(expr, env, lineno, "calc")
        if result is not None:
            print(result)
    except Exception as e:
        print(f"[calc] error at line {lineno}: {e}")

@tag("wait")
def handle_wait(node, env):
    seconds = float(node.attrib.get("seconds", 1))
    print(f"Waiting {seconds} second{'s' if seconds != 1 else ''}...")
    time.sleep(seconds)

@tag("input")
def handle_input(node, env):
    var = node.attrib.get("var")
    prompt = node.attrib.get("prompt", "")
    if var:
        env[var] = input(prompt)

@tag("random")
def handle_random(node, env):
    var = node.attrib.get("var")
    start = int(node.attrib.get("start", 0))
    end = int(node.attrib.get("end", 10))
    if var:
        env[var] = random.randint(start, end)

@tag("clear")
def handle_clear(node, env):
    os.system('cls' if os.name == 'nt' else 'clear')

# ================= Function & Class System ================= #
@tag("function")
def handle_function(node, env):
    name = node.attrib.get("name")
    if name:
        functions[name] = node

@tag("class")
def handle_class(node, env):
    name = node.attrib.get("name")
    ignore = str(node.attrib.get("ignore-crf", "false")).lower() in ("true", "1", "yes")
    if not name:
        print("[class] Missing name attribute.")
        return

    methods = {}
    fields = {}
    init_node = None

    for child in node:
        tagname = child.tag.lower()
        if tagname == "function":
            func_name = child.attrib.get("name")
            if func_name:
                methods[func_name] = child
        elif tagname == "var":
            var_name = child.attrib.get("name") or child.attrib.get("n")
            value = child.attrib.get("value")
            if var_name:
                try:
                    fields[var_name] = safe_eval(value, env, get_line(child), f"{name}.var")
                except Exception:
                    fields[var_name] = value
        elif tagname == "init":
            init_node = child

    CLASSES[name] = {
        "fields": fields,
        "methods": methods,
        "init": init_node
    }

    if not ignore:
        print(f"[class] Registered class '{name}' with {len(methods)} method(s) and {len(fields)} field(s).")

@tag("call")
def handle_call(node, env):
    name = node.attrib.get("name")
    if not name:
        print("[call] Missing name attribute.")
        return

    match = re.match(r"([A-Za-z_][A-Za-z0-9_\.()]*)\s*\((.*?)\)$", name)
    args = []
    call_target = name
    if match:
        call_target = match.group(1)
        arg_text = match.group(2).strip()
        if arg_text:
            args = [safe_eval(arg.strip(), env, get_line(node), "call") for arg in arg_text.split(",")]

    if "." in call_target:
        obj_expr, method_name = call_target.split(".", 1)

        if obj_expr.endswith("()"):
            obj = safe_eval(obj_expr, env, get_line(node), "call")
        else:
            obj = env.get(obj_expr)

        if not obj or "__methods__" not in obj:
            print(f"[call] '{obj_expr}' is not an object.")
            return

        method_node = obj["__methods__"].get(method_name)
        if not method_node:
            print(f"[call] Method '{method_name}' not found in {obj_expr}.")
            return


        local_env = env.copy()
        local_env.update(obj)
        local_env["self"] = obj
        local_env["args"] = args

        for i, arg in enumerate(args, 1):
            local_env[f"arg{i}"] = arg

        execute_children(method_node, local_env)
        return

    func_node = functions.get(call_target)
    if func_node:
        local_env = env.copy()
        local_env["args"] = args
        for i, arg in enumerate(args, 1):
            local_env[f"arg{i}"] = arg
        execute_children(func_node, local_env)
    else:
        print(f"[call] function '{call_target}' not defined.")

@tag("import")
def handle_import(node, env):
    filename = node.attrib.get("file")
    if filename and os.path.exists(filename):
        tree = ET.parse(filename)
        execute_children(tree.getroot(), env)
    else:
        print(f"[import] File not found: {filename}")

# ================= Script Runner ================= #
def run_ks(source_text, filename="<string>"):
    env = {}
    wrapped = "<root>\n" + source_text + "\n</root>"
    try:
        parser = ET.XMLParser()
        tree = ET.ElementTree(ET.fromstring(wrapped, parser=parser))
        root = tree.getroot()
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
    print("=== Mercury Interpreter — m2.43 ===")
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
            print("=== Mercury Interpreter — m2.43 ===")

if __name__ == "__main__":
    main()