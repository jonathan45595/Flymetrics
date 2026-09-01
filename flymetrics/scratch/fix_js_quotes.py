import re
import glob

targets = [
    'frontend/admin.html',
    'frontend/cliente.html',
    'frontend/tecnico.html',
    'frontend/index.html',
    'frontend/staff.html',
    'frontend/agendar.html',
    'frontend/js/admin.js',
    'frontend/js/app.js'
]

# Look for patterns like `innerHTML = "..."<i class="fa-solid fa-check"></i>"..."`
# or unescaped double quotes inside JS string literals.

def fix_unquoted_fa(content):
    # Pattern 1: `="...<i class="fa...` inside a double-quoted string
    # Replace `<i class="fa-...` with `<i class='fa-...` inside JS string assignments
    lines = content.split('\n')
    fixed_lines = []
    for line in lines:
        # If line contains innerHTML = "..." or similar double quote literal containing <i class="...
        if re.search(r'innerHTML\s*=\s*"[^"]*<i\s+class="', line) or re.search(r'showToast\("[^"]*<i\s+class="', line):
            # Replace internal double quotes in tag attributes with single quotes
            line = re.sub(r'<i\s+class="([^"]+)"(\s+style="([^"]+)")?>', r"<i class='\1' style='\3'>", line)
            line = line.replace("style=''>", ">")
        # Also fix any dangling `="... <i class="fa...`
        if 'innerHTML = "' in line and 'class="' in line:
            line = line.replace('class="', "class='").replace('">', "'>").replace(";'\"", ";'")
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)

for filepath in targets:
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        fixed_content = fix_unquoted_fa(content)

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(fixed_content)
        print(f"Validated and sanitized quotes in {filepath}")
    except Exception as e:
        print(f"Error: {e}")
