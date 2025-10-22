import os
import random
import time
from core.utils import render_text_with_env, get_line
from core.evaluator import safe_eval
TAG_HANDLERS = {}

def tag(name):
    def wrapper(func):
        TAG_HANDLERS[name.lower()] = func
        return func
    return wrapper

def execute_children(node, env):
    for child in node:
        exec_node(child, env)

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

# ==================== Core Handlers ==================== #
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
        for ln in text_content.splitlines():
            ln = ln.strip()
            if not ln or ln.startswith(("//", "#", "::")):
                continue
            parts = ln.split(":", 1)
            if len(parts) == 2:
                key, val_expr = parts
                try:
                    env[key.strip()] = safe_eval(val_expr.strip(), env, lineno, "var")
                except Exception:
                    env[key.strip()] = val_expr.strip()

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

@tag('for')
def handle_for(node, env):
    var = node.attrib.get('var')
    range_expr = node.attrib.get('range')
    if not var or not range_expr:
        print(f"[error @ for:{node.sourceline}] Missing 'var' or 'range' attribute.")
        return

    result = safe_eval(range_expr, env, node.sourceline, 'for')
    if isinstance(result, range):
        iterable = result
    elif isinstance(result, (list, tuple)) and len(result) == 2:
        start, end = result
        iterable = range(int(start), int(end))
    else:
        print(f"[warn @ for:{node.sourceline}] Invalid range expression: {range_expr}")
        return

@tag("calc")
def handle_calc(node, env):
    lineno = get_line(node)
    expr = (node.attrib.get("expression") or node.text or "").strip()
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
