import re

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
