import os
import sys
import xml.etree.ElementTree as ET
from core.handlers_core import TAG_HANDLERS
from core.utils import render_text_with_env

def exec_node(node, env):
    tag_name = node.tag.lower()
    handler = TAG_HANDLERS.get(tag_name)
    if handler:
        handler(node, env)
    else:
        text = (node.text or "").strip()
        if text:
            print(render_text_with_env(text, env))
def execute_children(node, env):
    for child in node:
        exec_node(child, env)
def run_ks(source_text, filename="<string>"):
    env = {}
    wrapped = f"<root>\n{source_text}\n</root>"
    try:
        tree = ET.ElementTree(ET.fromstring(wrapped))
        root = tree.getroot()
    except ET.ParseError as e:
        print("[parse error]:", e)
        return
    for child in root:
        exec_node(child, env)
def load_plugins(directory="plugins"):
    import importlib
    if getattr(sys, 'frozen', False):
        base_dir = sys._MEIPASS
        directory = os.path.join(base_dir, directory)
    if not os.path.exists(directory):
        return
    sys.path.insert(0, directory)
    for file in os.listdir(directory):
        if file.endswith(".py"):
            importlib.import_module(file[:-3])