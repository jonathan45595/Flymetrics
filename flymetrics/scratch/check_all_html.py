import re

def check_html_file(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
    for idx, s in enumerate(scripts):
        with open(f"scratch/check_{idx}.js", "w", encoding="utf-8") as out:
            out.write(s)
        lines = s.split('\n')
        print(f"{filepath} script {idx}: {len(lines)} lines")

check_html_file("frontend/cliente.html")
check_html_file("frontend/tecnico.html")
