import re

def handle(content, runtime):
    def replace_var(match):
        varname = match.group(1)
        try:
            return str(runtime.get_var(varname))
        except Exception:
            return f"{{{varname}}}"

    # Replace {var} tokens
    output = re.sub(r"\{([A-Za-z_]\w*)\}", replace_var, content)
    print(output)