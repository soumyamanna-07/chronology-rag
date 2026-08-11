from pathlib import Path

root = Path("../Data/html")

files = list(root.rglob("march-1890.html"))

with open(files[0], "r", encoding="utf-8", errors="ignore") as f:
    text = f.read()

# Find the <body> tag
index = text.find("<body")

print("BODY starts at:", index)

# Print from the body tag onward
print(text[index:index+5000])