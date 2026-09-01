files = ['fronen/index.html', 'fronen/js/app.js']

for file_path in files:
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Standardize to Flymetrics (case-sensitive)
    new_content = content.replace('Flymtric', 'Flymetrics').replace('flymetric', 'Flymetrics').replace('FlyMetrics', 'Flymetrics')
    
    if new_content != content:
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"Branding updated in {file_path}")
    else:
        print(f"No changes needed for {file_path}")
