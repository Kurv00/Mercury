import ast
import re

class SafeEvalVisitor(ast.NodeVisitor):
    SAFE_NODE_NAMES = [
        "Expression", "Constant", "Name", "Load", "BinOp", "UnaryOp",
        "BoolOp", "Compare", "Call", "List", "Tuple", "Dict", "Subscript",
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

def safe_eval(expr, env, lineno=None, context_tag=None):
    expr = expr.strip()
    if not expr:
        return None
    try:
        tree = ast.parse(expr, mode="eval")
        SafeEvalVisitor(env).visit(tree)
        code = compile(tree, "<safe-eval>", "eval")
        safe_globals = {"__builtins__": None, **SafeEvalVisitor.SAFE_FUNCS}
        return eval(code, safe_globals, env)
    except Exception as e:
        print(f"Error in <{context_tag or 'unknown'}> at line {lineno or '?'}: {e}")
        return None
