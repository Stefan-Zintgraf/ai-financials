
import os
import re

search_path = r"C:/Users/HMz/Documents/Source/McpServer/ibapi-mcp-server"

print(f"Scanning {search_path} for print statements...")

for root, dirs, files in os.walk(search_path):
    if "venv" in root or "__pycache__" in root or ".git" in root or "build" in root or "dist" in root:
        continue
        
    for file in files:
        if file.endswith(".py"):
            file_path = os.path.join(root, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    
                for i, line in enumerate(lines):
                    # Check for print(, but ignore comments
                    # This is a simple regex, might catch comments if "print(" is inside them, but good enough
                    if re.search(r'^\s*print\(', line):
                        # check if it prints to file=sys.stderr
                        if "sys.stderr" not in line:
                            print(f"{file}: Line {i+1}: {line.strip()}")
            except Exception as e:
                pass
