


  

# Mercury

### A minimal, XML-based scripting language built with Python
![Python](https://img.shields.io/badge/Made%20with-Python-blue?style=for-the-badge&logo=python)
![Version](https://img.shields.io/badge/Version-2.42-red?style=for-the-badge)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Stable-success?style=for-the-badge)
</div>

## 🌌 Overview
**Mercury** is a lightweight scripting language designed for simplicity, readability, and safety.

It allows you to execute tag-based code (`.mc` files) using a custom Python-built interpreter.

Think of it as a blend between XML and a programming language — clean, flexible, and secure.

## ⚙️ Features
✅ Safe expression evaluation using Python’s `ast`

✅ Simple tag-based syntax (`<var>`, `<print>`, `<if>`, `<for>`)

✅ Plugin support — easily add your own custom tags

✅ Only executes `.mc` scripts (for safety)

✅ Cross-platform CLI interface

✅ Built-in delay, input, and looping mechanisms

  

  

## 🧠 Example Mercury Script

  

Here’s an example `.mc` script you can run with Mercury:

  

```xml
<var name="x" value="5"/>
<for var="i" in="(0, x)">
	<print>Count: {i}</print>
</for>

<if condition="x == 5">
	<print>All done!</print>
</if>
```

  

**Output:**

```
Count: 0
Count: 1
Count: 2
Count: 3
Count: 4
All done!
```

  



  

## 🧩 Adding New Tags

  

Mercury supports custom tags through a **plugin system**
Create a new folder inside the root 'plugins', then create a '.py' file, and write something like this:

```python
# plugins/hello.py
from main import tag
  
@tag("hello")
def  handle_hello(node, env):
print("Hello from a custom tag!")
```

  

Now, you can use it directly in your `.mc` scripts:

```xml
<hello/>
```

## 🚀 How to Run

1. Download the 'main.exe' file from the 'dist' directory.
2. Run the 'main.exe' file
3. Enter the path to your `.mc` file when prompted:
```
Enter path to .mc file (example.mc):
```
4. Enjoy the magic ✨
## 🧾 File Structure
```
Mercury/
│
├── main.py (Core Mercury interpreter)
├── plugins/
│ └── hello.py
├── examples/
│ └── test.mc
├── .gitattributes
└── README.md
```
## 🪶 Language Recognition on GitHub
To ensure GitHub detects Mercury correctly:
```gitattributes
*.py linguist-language=Python
*.mc linguist-language=Mercury
```
## 🧑‍💻 Development Notes

  

Mercury prioritizes safety:

- No direct file or system access inside scripts.
- All code evaluation passes through `safe_eval` with `ast` node whitelisting.
- Ideal for controlled environments or educational interpreters.

## 📜 License
This project is licensed under the [MIT License](LICENSE).

Made by <a  href="https://github.com/Kurv00">Kurv00</a>
</div>
