import json
import re

with open('/tmp/gow1_script.txt', 'r') as f:
    p1_text = f.read()
with open('/tmp/gow2_script.txt', 'r') as f:
    p2_text = f.read()

p1_lines = p1_text.split('\n')
p2_lines = p2_text.split('\n')

# Characters and their search terms + color assignments
characters = {
    "shahid":    { "terms": ["SHAHID", "Shahid"], "color": "#8B0000" },
    "sardar":    { "terms": ["SARDAR", "Sardar"], "color": "#DC143C" },
    "faisal":    { "terms": ["FAISAL", "Faisal", "FAIZAL", "Faizal"], "color": "#FF4500" },
    "definite":  { "terms": ["DEFINITE", "Definite"], "color": "#FF8C00" },
    "ramadhir":  { "terms": ["RAMADHIR", "Ramadhir"], "color": "#333333" },
    "nasir":     { "terms": ["NASIR", "Nasir"], "color": "#D4A017" },
    "nagma":     { "terms": ["NAGMA", "Nagma"], "color": "#2E86C1" },
    "mohsina":   { "terms": ["MOHSINA", "Mohsina"], "color": "#5DADE2" },
    "durga":     { "terms": ["DURGA", "Durga"], "color": "#1A5276" },
    "sultan":    { "terms": ["SULTAN", "Sultan"], "color": "#6C3483" },
}

def count_chars_in_chunk(lines, characters):
    """Count character mentions in a chunk of lines."""
    counts = {}
    for char_id, info in characters.items():
        count = 0
        for line in lines:
            if any(term in line for term in info["terms"]):
                count += 1
        counts[char_id] = count
    return counts

def find_dominant(counts):
    """Find the character with most mentions in this chunk."""
    khans = ["shahid", "sardar", "faisal", "definite"]
    khan_counts = {k: counts.get(k, 0) for k in khans}
    max_khan = max(khan_counts, key=khan_counts.get) if any(khan_counts.values()) else None
    max_val = khan_counts.get(max_khan, 0) if max_khan else 0
    if max_val == 0:
        return None
    return max_khan

# Split scripts into pages
# P1: 118 pages from 3949 lines => ~33.5 lines/page
# P2: 170 pages from 4948 lines => ~29.1 lines/page

def split_into_pages(lines, num_pages):
    lines_per_page = len(lines) / num_pages
    pages = []
    for i in range(num_pages):
        start = int(i * lines_per_page)
        end = int((i + 1) * lines_per_page)
        pages.append(lines[start:end])
    return pages

p1_pages = split_into_pages(p1_lines, 118)
p2_pages = split_into_pages(p2_lines, 170)

# Build page-level data
ledger_data = []

# Part 1
for i, page_lines in enumerate(p1_pages):
    counts = count_chars_in_chunk(page_lines, characters)
    dominant = find_dominant(counts)
    
    # Check for Durga consequential action (phone call near end of P1)
    has_durga_action = False
    if i >= 115:  # Last few pages of P1
        for line in page_lines:
            if 'DURGA' in line or 'Durga' in line:
                if 'phone' in line.lower() or 'निकल' in line or 'nikal' in line.lower():
                    has_durga_action = True
    
    # Check for Nasir V.O.
    nasir_vo = sum(1 for l in page_lines if 'NASIR' in l and 'V.O' in l)
    
    ledger_data.append({
        "page": i + 1,
        "part": 1,
        "global_page": i + 1,
        "counts": counts,
        "dominant": dominant,
        "dominant_count": counts.get(dominant, 0) if dominant else 0,
        "ramadhir": counts.get("ramadhir", 0),
        "nasir_vo": nasir_vo,
        "women": counts.get("nagma", 0) + counts.get("mohsina", 0) + counts.get("durga", 0),
        "durga_action": has_durga_action,
    })

# Part 2
for i, page_lines in enumerate(p2_pages):
    counts = count_chars_in_chunk(page_lines, characters)
    dominant = find_dominant(counts)
    
    # Check for Durga at the very end of P2
    has_durga_action = False
    if i <= 2:  # Opening pages (phone call replay)
        for line in page_lines:
            if 'DURGA' in line or 'Durga' in line:
                has_durga_action = True
    if i >= 167:  # Final pages
        for line in page_lines:
            if 'Durga' in line and ('walks' in line.lower() or 'Definite' in line):
                has_durga_action = True
    
    nasir_vo = sum(1 for l in page_lines if 'NASIR' in l and 'V.O' in l)
    
    ledger_data.append({
        "page": i + 1,
        "part": 2,
        "global_page": 118 + i + 1,
        "counts": counts,
        "dominant": dominant,
        "dominant_count": counts.get(dominant, 0) if dominant else 0,
        "ramadhir": counts.get("ramadhir", 0),
        "nasir_vo": nasir_vo,
        "women": counts.get("nagma", 0) + counts.get("mohsina", 0) + counts.get("durga", 0),
        "durga_action": has_durga_action,
    })

# Verify
print(f"Total pages: {len(ledger_data)}")
print(f"Part 1 pages: {sum(1 for d in ledger_data if d['part'] == 1)}")
print(f"Part 2 pages: {sum(1 for d in ledger_data if d['part'] == 2)}")

# Dominance distribution
from collections import Counter
dom_dist = Counter(d['dominant'] for d in ledger_data)
print(f"\nDominance by character:")
for char, count in dom_dist.most_common():
    print(f"  {char or 'none'}: {count} pages")

# Durga action pages
durga_pages = [d['global_page'] for d in ledger_data if d['durga_action']]
print(f"\nDurga action pages: {durga_pages}")

# Ramadhir presence
ram_present = sum(1 for d in ledger_data if d['ramadhir'] > 0)
print(f"Ramadhir present on {ram_present} of {len(ledger_data)} pages ({100*ram_present//len(ledger_data)}%)")

# Pages with no Khan dominance
empty = sum(1 for d in ledger_data if d['dominant'] is None)
print(f"Pages with no khan dominance: {empty}")

# Export for viz
export = []
for d in ledger_data:
    export.append({
        "p": d["global_page"],
        "part": d["part"],
        "dom": d["dominant"],
        "dom_n": d["dominant_count"],
        "ram": d["ramadhir"],
        "nvo": d["nasir_vo"],
        "w": d["women"],
        "da": d["durga_action"],
        # All khan counts for blending
        "sh": d["counts"]["shahid"],
        "sa": d["counts"]["sardar"],
        "fa": d["counts"]["faisal"],
        "de": d["counts"]["definite"],
    })

with open('/tmp/gow-piece/public/ledger.json', 'w') as f:
    json.dump(export, f)

print(f"\nExported {len(export)} rows to ledger.json")

# Spot check: print first 10 and last 10
print("\nFirst 10 pages:")
for d in export[:10]:
    print(f"  p{d['p']:3d} | dom={d['dom'] or '---':10s} | sh={d['sh']:2d} sa={d['sa']:2d} fa={d['fa']:2d} de={d['de']:2d} | ram={d['ram']:2d} | w={d['w']:2d}")

print("\nLast 10 pages:")
for d in export[-10:]:
    print(f"  p{d['p']:3d} | dom={d['dom'] or '---':10s} | sh={d['sh']:2d} sa={d['sa']:2d} fa={d['fa']:2d} de={d['de']:2d} | ram={d['ram']:2d} | w={d['w']:2d}")
