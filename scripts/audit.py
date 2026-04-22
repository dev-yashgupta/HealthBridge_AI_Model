import os, glob, sys

# Set encoding to utf-8
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

print("=== data/ FOLDER ===")
for root, dirs, files in os.walk("data/"):
    dirs[:] = [d for d in dirs if not d.startswith('.')]
    level = root.replace("data/", "").count(os.sep)
    indent = "  " * level
    # Removed emojis for terminal compatibility
    print(f"{indent}[DIR] {os.path.basename(root)}/")
    for f in files:
        size = os.path.getsize(os.path.join(root, f))
        print(f"{indent}  [FILE] {f}  ({size//1024} KB)")

print("\n=== ROOT FOLDER ===")
# glob.glob finds files in the root folder according to pattern
for f in glob.glob("*.csv")+glob.glob("*.json")+glob.glob("*.zip")+glob.glob("*.xlsx"):
    print(f"  [FILE] {f}  ({os.path.getsize(f)//1024} KB)")

print("\n=== dataset/ FOLDER (if exists) ===")
# The user specified datasets/ in the previous command so I check that
if os.path.exists("datasets/"):
    for root, dirs, files in os.walk("datasets/"):
        for f in files:
            size = os.path.getsize(os.path.join(root, f))
            print(f"  [FILE] {os.path.join(root,f)}  ({size//1024} KB)")
else:
    print("  datasets/ folder nahi mila")
