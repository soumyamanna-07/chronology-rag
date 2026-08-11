from pathlib import Path

# Folder where all chronology HTML files are stored
root = Path("../Data/html")

# Find every HTML file
html_files = list(root.rglob("*.html"))

print("=" * 50)
print("Swami Vivekananda Chronology Scanner")
print("=" * 50)

print(f"\nTotal HTML files found: {len(html_files)}\n")

print("First 10 HTML files:\n")

for file in html_files[:10]:
    print(file)