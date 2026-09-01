import glob
import re
import subprocess

html_files = glob.glob('frontend/**/*.html', recursive=True)

for h in html_files:
    with open(h, 'r', encoding='utf-8', errors='ignore') as f:
        html = f.read()

    # Extract all <script>...</script>
    scripts = re.findall(r'<script(?:\s+[^>]*)?>(.*?)</script>', html, re.DOTALL | re.IGNORECASE)
    print(f"Checking {len(scripts)} scripts in {h}...")
    for idx, s in enumerate(scripts):
        if not s.strip():
            continue
        # Test with node / quick syntax check if available or py mini parser
        with open('scratch/temp_check.js', 'w', encoding='utf-8') as tf:
            tf.write(s)
        
        # Check matching quotes and backticks in lines
        lines = s.split('\n')
        for lno, l in enumerate(lines):
            # Check for unescaped double quotes inside double quotes: e.g. " ... "fa-solid..." ... "
            # Match `= " ... <i class="`
            if re.search(r'=\s*"[^"]*<i\s+class="', l) or re.search(r'\("[^"]*<i\s+class="', l):
                print(f"  [!] Potential unescaped double-quote at line {lno+1}: {l.strip()}")
