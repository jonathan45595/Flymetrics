import re

def check_js_in_html(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    scripts = re.findall(r'<script>(.*?)</script>', content, re.DOTALL)
    print(f"Checking {filepath}: found {len(scripts)} script tags.")

    for idx, s in enumerate(scripts):
        # We can test by writing s to a temp js file and running node -c or python check
        temp_file = f"scratch/temp_check_{idx}.js"
        with open(temp_file, 'w', encoding='utf-8') as tf:
            tf.write(s)

check_js_in_html("frontend/tecnico.html")
check_js_in_html("frontend/cliente.html")
