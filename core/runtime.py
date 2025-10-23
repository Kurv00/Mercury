class Runtime:
    def __init__(self):
        self.vars = {}

    def set_var(self, name, type_name, value):
        if name in self.vars:
            old_type, _ = self.vars[name]
            if old_type != type_name:
                raise TypeError(f"Cannot change type of {name} from {old_type} to {type_name}")
        self.vars[name] = (type_name, value)

    def get_var(self, name):
        if name not in self.vars:
            raise NameError(f"Undefined variable '{name}'")
        return self.vars[name][1]