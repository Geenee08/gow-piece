import json
import re

with open('/tmp/gow1_script.txt', 'r') as f:
    p1_lines = f.read().split('\n')
with open('/tmp/gow2_script.txt', 'r') as f:
    p2_lines = f.read().split('\n')

characters = {
    "shahid":   ["SHAHID", "Shahid"],
    "sardar":   ["SARDAR", "Sardar"],
    "faisal":   ["FAISAL", "Faisal", "FAIZAL", "Faizal"],
    "definite": ["DEFINITE", "Definite"],
    "ramadhir": ["RAMADHIR", "Ramadhir"],
    "nasir":    ["NASIR", "Nasir"],
    "nagma":    ["NAGMA", "Nagma"],
    "mohsina":  ["MOHSINA", "Mohsina"],
    "durga":    ["DURGA", "Durga"],
    "sultan":   ["SULTAN", "Sultan"],
}

def split_into_pages(lines, num_pages):
    lpp = len(lines) / num_pages
    pages = []
    for i in range(num_pages):
        s = int(i * lpp)
        e = int((i + 1) * lpp)
        pages.append(lines[s:e])
    return pages

p1_pages = split_into_pages(p1_lines, 118)
p2_pages = split_into_pages(p2_lines, 170)

all_pages = [(1, p) for p in p1_pages] + [(2, p) for p in p2_pages]

register = []

for global_idx, (part, page_lines) in enumerate(all_pages):
    page_len = len(page_lines)
    if page_len == 0:
        page_len = 1

    page_data = {
        "p": global_idx + 1,
        "part": part,
        "n": page_len,  # lines in this page
        "marks": {},     # char_id -> list of fractional y-positions (0=top, 1=bottom)
    }

    # Check for Durga action pages
    is_durga_action = False
    if part == 1 and global_idx >= 115:
        for line in page_lines:
            if ('DURGA' in line or 'Durga' in line) and ('phone' in line.lower() or 'निकल' in line):
                is_durga_action = True
    if part == 2 and global_idx <= 119:  # first few pages of P2
        for line in page_lines:
            if 'DURGA' in line or 'Durga' in line:
                is_durga_action = True
    if part == 2 and global_idx >= 285:  # last few pages
        for line in page_lines:
            if 'Durga' in line and ('walks' in line.lower() or 'Definite' in line):
                is_durga_action = True
    page_data["da"] = is_durga_action

    # For each character, find line positions within this page
    for char_id, terms in characters.items():
        positions = []
        for line_idx, line in enumerate(page_lines):
            if any(term in line for term in terms):
                # Fractional position: 0 = top of page, 1 = bottom
                y = line_idx / max(page_len - 1, 1)
                positions.append(round(y, 3))
        if positions:
            page_data["marks"][char_id] = positions

    register.append(page_data)

# Compact export — JSON with marks as nested dict
# Each page: {p, part, n, da, marks: {char: [y1, y2, ...]}}
with open('/tmp/gow-piece/public/register.json', 'w') as f:
    json.dump(register, f, separators=(',', ':'))

# Stats
total_marks = sum(sum(len(v) for v in p["marks"].values()) for p in register)
pages_with_marks = sum(1 for p in register if p["marks"])
durga_action_pages = [p["p"] for p in register if p["da"]]

print(f"Pages: {len(register)}")
print(f"Total marks (all chars): {total_marks}")
print(f"Pages with at least one mark: {pages_with_marks}")
print(f"Durga action pages: {durga_action_pages}")

# Sample: show page 10 and page 119
for sample in [9, 118, 287]:
    p = register[sample]
    print(f"\nPage {p['p']} (Part {p['part']}, {p['n']} lines, durga_action={p['da']}):")
    for char, positions in p["marks"].items():
        print(f"  {char}: {len(positions)} marks at y={positions}")

# Mark density stats per character
for char_id in characters:
    total = sum(len(p["marks"].get(char_id, [])) for p in register)
    pages = sum(1 for p in register if char_id in p["marks"])
    print(f"{char_id}: {total} marks across {pages} pages")
