import re

with open("scratch/temp_check_0.js", "r", encoding="utf-8") as f:
    code = f.read()

# Check open/close braces, quotes, parens
stack = []
lines = code.split('\n')
print(f"Total lines in tecnico script: {len(lines)}")

# Simple string quote matching check line by line
syntax_errors = []
for i, l in enumerate(lines, 1):
    # Count single and double quotes not escaped
    sq = len(re.findall(r"(?<!\\)'", l))
    dq = len(re.findall(r'(?<!\\)"', l))
    bq = len(re.findall(r"(?<!\\)`", l))
    if sq % 2 != 0 or dq % 2 != 0:
        # Template literals might span multiple lines, check single and double
        if not ('`' in l or '/*' in l or '*/' in l):
            syntax_errors.append((i, l))

print(f"Line check found {len(syntax_errors)} potential syntax anomalies:")
for line_no, content in syntax_errors[:10]:
    print(f"Line {line_no}: {content.strip()}")
