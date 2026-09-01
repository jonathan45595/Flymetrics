with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\fronen\cliente.html", "r", encoding="utf-8") as f:
    lines = f.readlines()

out = []
keywords = ["calendar", "calendario", "renderCalendar", "nextMonth", "prevMonth", "tecnico", "tecnicos"]
for kw in keywords:
    out.append(f"=== Matches for '{kw}' ===")
    matches = 0
    for idx, line in enumerate(lines):
        if kw in line:
            safe_line = line.strip()[:140].encode('ascii', errors='replace').decode('ascii')
            out.append(f"  Line {idx+1}: {safe_line}")
            matches += 1
            if matches >= 15:
                out.append("  ... truncated ...")
                break

with open(r"c:\Users\MIGUEL\OneDrive\Desktop\flymetrics\scratch\calendar_results.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(out))
print("Search complete. Results written to scratch/calendar_results.txt")
