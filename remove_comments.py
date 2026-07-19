import os
import json
import re

def strip_comments_from_python(code):
    # Pattern matches multiline strings, single line strings, and comments.
    pattern = r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|".*?"|\'.*?\')|(#.*)'
    
    def replacer(match):
        if match.group(2) is not None:
            return "" # Replace comment with nothing
        else:
            return match.group(1) # Keep string intact
            
    result = re.sub(pattern, replacer, code)
    
    # Remove lines that are now completely empty (but only if they were comment lines)
    # A simple way to clean up is to remove lines that contain only whitespace
    # But this removes all blank lines. Let's just leave the blank lines, they are harmless.
    # Actually, we can remove lines that are just whitespace to make it compact.
    final_lines = []
    for line in result.split('\n'):
        if line.strip() == '':
            continue
        final_lines.append(line)
        
    return '\n'.join(final_lines) + '\n'

def strip_comments_from_notebook(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        try:
            nb = json.load(f)
        except Exception as e:
            print(f"Error loading {filepath}: {e}")
            return
            
    modified = False
    for cell in nb.get('cells', []):
        if cell.get('cell_type') == 'code':
            code = ''.join(cell.get('source', []))
            new_code = strip_comments_from_python(code)
            
            # Format back to list of lines for notebook
            lines = [line + '\n' for line in new_code.split('\n')]
            if lines and lines[-1] == '\n':
                lines.pop()
            if lines and lines[-1].endswith('\n\n'):
                 lines[-1] = lines[-1][:-1]
                 
            cell['source'] = lines
            modified = True
                
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(nb, f, indent=1)
        print(f"Processed notebook: {filepath}")

def main():
    root_dir = r"c:\Users\Vivek\Desktop\vpn sentinel"
    for subdir, dirs, files in os.walk(root_dir):
        dirs[:] = [d for d in dirs if not d.startswith('.') and d != '__pycache__']
        for file in files:
            filepath = os.path.join(subdir, file)
            if file.endswith('.py') and file != 'remove_comments.py':
                with open(filepath, 'r', encoding='utf-8') as f:
                    code = f.read()
                new_code = strip_comments_from_python(code)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(new_code)
                print(f"Processed python file: {filepath}")
            elif file.endswith('.ipynb'):
                strip_comments_from_notebook(filepath)

if __name__ == '__main__':
    main()
