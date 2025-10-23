from tags import console_log, declaration

class TagHandler:
    def __init__(self, runtime):
        self.runtime = runtime
        self.handlers = {
            "console.log": console_log.handle,
            "int": declaration.handle,
            "str": declaration.handle,
            "float": declaration.handle,
            "bool": declaration.handle,
        }

    def handle(self, tag, content):
        tag = tag.lower()
        if tag not in self.handlers:
            raise SyntaxError(f"Unknown tag '{tag}'")
        return self.handlers[tag](content, self.runtime)