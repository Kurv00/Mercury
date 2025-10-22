import re
from core.evaluator import safe_eval
from core.utils import get_line
from core.runtime import execute_children
from core.handlers_core import tag
functions = {}
CLASSES = {}


def register_function(name, node):
    functions[name] = node
def register_class(name, data):
    CLASSES[name] = data


@tag("function")
def handle_function(node, env):
    name = node.attrib.get("name")
    if name:
        register_function(name, node)

@tag("class")
def handle_class(node, env):
    name = node.attrib.get("name")
    if not name:
        print("[class] Missing name attribute.")
        return
    methods, fields, init_node = {}, {}, None
    for child in node:
        tagname = child.tag.lower()
        if tagname == "function":
            func_name = child.attrib.get("name")
            if func_name:
                methods[func_name] = child
        elif tagname == "var":
            var_name = child.attrib.get("name") or child.attrib.get("n")
            value = child.attrib.get("value")
            fields[var_name] = safe_eval(value, env, get_line(child), f"{name}.var") if value else None
        elif tagname == "init":
            init_node = child
    register_class(name, {"fields": fields, "methods": methods, "init": init_node})
    print(f"[class] Registered '{name}' ({len(methods)} method(s), {len(fields)} field(s)).")

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
        obj = safe_eval(obj_expr, env, get_line(node), "call") if obj_expr.endswith("()") else env.get(obj_expr)
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