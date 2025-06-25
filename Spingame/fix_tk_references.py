import re
import sys

def fix_tk_references(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        content = file.read()
    
    # Replace all tk.X with X
    content = re.sub(r'tk\.([A-Za-z]+)', r'\1', content)
    
    # Replace all tk.END with "end"
    content = re.sub(r'tk\.END', r'"end"', content)
    
    with open(file_path, 'w', encoding='utf-8') as file:
        file.write(content)
    
    print(f"Fixed tk references in {file_path}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        fix_tk_references(sys.argv[1])
    else:
        print("Please provide a file path")