import ast, re

content = open("src/app.py", "r", encoding="utf-8").read()

# Syntax
try:
    ast.parse(content)
    print("Syntax: OK")
except SyntaxError as e:
    print(f"SYNTAX ERROR: {e}")
    import sys; sys.exit(1)

# Empty button labels
empty = re.findall(r'st\.button\(""\s*[,)]', content)
print(f"Empty button labels: {len(empty)}")

# Euro signs outside comments
euro_lines = [i+1 for i, l in enumerate(content.split("\n"))
              if "\u20ac" in l and not l.strip().startswith("#")]
print(f"Euro signs in code: {len(euro_lines)} -> {euro_lines[:5]}")

# Broken icon= params
bad_icons = re.findall(r'icon="[^"]*[\x80-\xFF][^"]*"', content)
print(f"Broken icon= params: {len(bad_icons)}")

print(f"Lines: {content.count(chr(10))}")
print(f"Emojis/non-ASCII: {sum(1 for c in content if ord(c)>127)}")
