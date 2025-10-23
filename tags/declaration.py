def handle(content, runtime):
    parts = content.split("=")
    if len(parts) != 2:
        raise SyntaxError(f"Invalid declaration: {content}")
    
    name = parts[0].strip()
    raw_val = parts[1].strip().rstrip(";").strip()

    # Detect and convert types
    if raw_val.lower() in ("true", "false"):
        value = raw_val.lower() == "true"
        type_name = "bool"
    else:
        try:
            if "." in raw_val:
                value = float(raw_val)
                type_name = "float"
            else:
                value = int(raw_val)
                type_name = "int"
        except ValueError:
            value = raw_val.strip('"').strip("'")
            type_name = "str"

    runtime.set_var(name, type_name, value)