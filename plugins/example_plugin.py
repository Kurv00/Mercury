from core.handlers_core import tag

@tag("hello")
def handle_hello(node, env):
    print("Hello from sample plugin!")