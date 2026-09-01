with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

keywords = ["verificado", "finishBlockingVerification", "me", "_clientProfile", "showBlockingVerificationUI", "loadProfileData"]
out = []
for keyword in keywords:
    out.append(f"=== Matches for '{keyword}' ===")
    matches = 0
    for idx, line in enumerate(lines):
        if keyword in line:
            safe_line = line.strip()[:140].encode('ascii', errors='replace').decode('ascii')
            out.append(f"  Line {idx+1}: {safe_line}")
            matches += 1
            if matches >= 25:
                out.append("  ... more matches found, truncating ...")
                break

with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\scratch\search_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("Search complete. Results written to scratch/search_results.txt")
