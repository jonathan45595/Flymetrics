import os
import re

def check_js_syntax_deep(script_text, filename):
    lines = script_text.split('\n')
    stack = []
    in_single_quote = False
    in_double_quote = False
    in_backtick = False
    in_regex = False
    in_line_comment = False
    in_block_comment = False
    errors = []

    for line_idx, line in enumerate(lines, 1):
        i = 0
        in_line_comment = False
        while i < len(line):
            ch = line[i]
            prev = line[i-1] if i > 0 else ''
            
            if in_block_comment:
                if ch == '/' and prev == '*':
                    in_block_comment = False
                i += 1
                continue
            
            if in_line_comment:
                break
                
            if in_single_quote:
                if ch == "'" and prev != '\\':
                    in_single_quote = False
                i += 1
                continue
                
            if in_double_quote:
                if ch == '"' and prev != '\\':
                    in_double_quote = False
                i += 1
                continue
                
            if in_backtick:
                if ch == '`' and prev != '\\':
                    in_backtick = False
                i += 1
                continue

            if in_regex:
                if ch == '/' and prev != '\\':
                    in_regex = False
                i += 1
                continue
                
            if ch == '/' and i + 1 < len(line) and line[i+1] == '/':
                in_line_comment = True
                i += 2
                continue
            elif ch == '/' and i + 1 < len(line) and line[i+1] == '*':
                in_block_comment = True
                i += 2
                continue
            elif ch == '/':
                # Check if it is a regex literal (preceded by =, (, ,, :, [, !, return, etc.)
                prefix = line[:i].rstrip()
                if not prefix or prefix[-1] in '=(,:[!~?;&|' or prefix.endswith('return') or prefix.endswith('replace') or prefix.endswith('match') or prefix.endswith('test'):
                    in_regex = True
                    i += 1
                    continue
            elif ch == "'":
                in_single_quote = True
            elif ch == '"':
                in_double_quote = True
            elif ch == '`':
                in_backtick = True
            elif ch in '({[':
                stack.append((ch, line_idx))
            elif ch in ')}]':
                if not stack:
                    errors.append(f"Unmatched '{ch}' at line {line_idx}")
                else:
                    open_ch, open_line = stack.pop()
                    match_map = {')': '(', '}': '{', ']': '['}
                    if match_map[ch] != open_ch:
                        errors.append(f"Mismatched bracket: opened '{open_ch}' at line {open_line}, closed '{ch}' at line {line_idx}")
            i += 1
            
    if in_backtick:
        errors.append("Unclosed template literal (`) in script")
    if in_single_quote:
        errors.append("Unclosed single quote (') in script")
    if in_double_quote:
        errors.append("Unclosed double quote (\") in script")
    for open_ch, open_line in stack:
        errors.append(f"Unclosed '{open_ch}' opened at line {open_line}")
        
    return errors

frontend_dir = r"c:\Users\migue\OneDrive\Desktop\este es el verdadero - copia\flymetrics\frontend"
for f in ["cliente.html", "admin.html", "tecnico.html"]:
    path = os.path.join(frontend_dir, f)
    print(f"=== CHECKING {f} ===")
    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
        content = fp.read()
    
    script_blocks = re.findall(r'<script(?:\s[^>]*)?>(.*?)</script>', content, re.DOTALL | re.IGNORECASE)
    for idx, s in enumerate(script_blocks):
        errs = check_js_syntax_deep(s, f)
        if errs:
            print(f"Errors in {f} script #{idx+1}:")
            for e in errs:
                print("  -", e)
        else:
            print(f"Script #{idx+1} in {f} is completely VALID!")
