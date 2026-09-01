filepath = "fronen/cliente.html"

with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

terms = ["finishBlockingVerification", "showBlockingVerificationUI", "fm_email", "fm_verified"]

for term in terms:
    print(f"Matches for '{term}':")
    lines = content.splitlines()
    for i, line in enumerate(lines):
        if term in line:
            print(f"  Line {i+1}: {line.strip()}")
